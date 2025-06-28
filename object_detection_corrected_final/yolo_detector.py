import cv2
import numpy as np
from ultralytics import YOLO
import time
import threading
from utils.config import (
    MODEL_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD, 
    PREDEFINED_COLORS, MAX_DETECTIONS
)
from utils.draw import draw_bounding_box

class YOLODetector:
    """Detector de objetos usando YOLO com otimizações de performance e anti-flickering."""
    
    def __init__(self, model_path=None, confidence_threshold=None, iou_threshold=None):
        """
        Inicializa o detector YOLO.
        
        Args:
            model_path: Caminho para o modelo YOLO
            confidence_threshold: Threshold de confiança
            iou_threshold: Threshold para NMS
        """
        self.model_path = model_path or MODEL_PATH
        self.confidence_threshold = confidence_threshold or CONFIDENCE_THRESHOLD
        self.iou_threshold = iou_threshold or IOU_THRESHOLD
        
        # Sistema anti-flickering
        self.detection_buffer = []
        self.buffer_size = 3
        self.position_tolerance = 30
        self.confidence_smoothing = 0.8
        
        # Carregar modelo com tratamento de erro
        print(f"Carregando modelo YOLO: {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
            # Fazer uma predição teste para "aquecer" o modelo
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            _ = self.model(dummy_frame, verbose=False)
            print("Modelo carregado e aquecido com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            raise
        
        # Cache de cores para cada classe (usando cores predefinidas)
        self.class_colors = {}
        self.color_index = 0
        
        # Estatísticas de performance
        self.detection_times = []
        self.total_detections = 0
        
        # Thread lock para operações thread-safe
        self.lock = threading.Lock()
        
    def get_class_color(self, label):
        """Obtém cor para uma classe, usando cache."""
        if label not in self.class_colors:
            color = PREDEFINED_COLORS[self.color_index % len(PREDEFINED_COLORS)]
            self.class_colors[label] = color
            self.color_index += 1
        return self.class_colors[label]
        
    def detect_objects(self, frame):
        """
        Detecta objetos no frame com otimizações de performance e anti-flickering.
        
        Args:
            frame: Frame da câmera
            
        Returns:
            Lista de detecções [(x1, y1, x2, y2, label, confidence)]
        """
        start_time = time.time()
        
        try:
            # Executar detecção com configurações otimizadas
            results = self.model(
                frame, 
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False,
                device='cpu',  # Forçar CPU para estabilidade
                half=False     # Desabilitar half precision para estabilidade
            )
            
            current_detections = []
            
            # Processar resultados
            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    # Limitar número de detecções para melhor performance
                    boxes = result.boxes[:MAX_DETECTIONS]
                    
                    for box in boxes:
                        try:
                            # Extrair coordenadas
                            xyxy = box.xyxy[0].cpu().numpy()
                            x1, y1, x2, y2 = xyxy
                            
                            # Verificar se as coordenadas são válidas
                            if x1 >= x2 or y1 >= y2:
                                continue
                                
                            # Extrair classe e confiança
                            class_id = int(box.cls[0].cpu().numpy())
                            confidence = float(box.conf[0].cpu().numpy())
                            
                            # Verificar se a classe existe no modelo
                            if class_id not in self.model.names:
                                continue
                                
                            label = self.model.names[class_id]
                            
                            current_detections.append((x1, y1, x2, y2, label, confidence))
                            
                        except Exception as e:
                            print(f"Erro ao processar detecção: {e}")
                            continue
            
            # Aplicar sistema anti-flickering
            stable_detections = self._stabilize_detections(current_detections)
            
            # Atualizar estatísticas
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            if len(self.detection_times) > 100:  # Manter apenas últimas 100 medições
                self.detection_times.pop(0)
            
            self.total_detections += len(stable_detections)
            
            return stable_detections
            
        except Exception as e:
            print(f"Erro durante detecção: {e}")
            return []
    
    def _stabilize_detections(self, current_detections):
        """
        Estabiliza detecções para eliminar flickering.
        
        Args:
            current_detections: Detecções do frame atual
            
        Returns:
            Detecções estabilizadas
        """
        # Adicionar detecções atuais ao buffer
        self.detection_buffer.append(current_detections)
        
        # Manter tamanho do buffer
        if len(self.detection_buffer) > self.buffer_size:
            self.detection_buffer.pop(0)
        
        # Se não temos frames suficientes, retornar detecções atuais
        if len(self.detection_buffer) < 2:
            return current_detections
        
        # Encontrar detecções estáveis
        stable_detections = []
        
        for detection in current_detections:
            x1, y1, x2, y2, label, confidence = detection
            
            # Verificar se esta detecção aparece em frames anteriores
            stability_count = 1
            total_confidence = confidence
            stable_x1, stable_y1, stable_x2, stable_y2 = x1, y1, x2, y2
            
            for prev_detections in self.detection_buffer[:-1]:
                for prev_detection in prev_detections:
                    px1, py1, px2, py2, plabel, pconf = prev_detection
                    
                    # Mesma classe e posição próxima
                    if (label == plabel and 
                        abs(x1 - px1) < self.position_tolerance and 
                        abs(y1 - py1) < self.position_tolerance):
                        
                        stability_count += 1
                        total_confidence += pconf
                        
                        # Suavizar posição
                        stable_x1 = (stable_x1 + px1) / 2
                        stable_y1 = (stable_y1 + py1) / 2
                        stable_x2 = (stable_x2 + px2) / 2
                        stable_y2 = (stable_y2 + py2) / 2
                        break
            
            # Só incluir se detectado em pelo menos 2 frames
            if stability_count >= 2:
                # Suavizar confiança
                avg_confidence = total_confidence / stability_count
                smooth_confidence = (self.confidence_smoothing * confidence + 
                                   (1 - self.confidence_smoothing) * avg_confidence)
                
                stable_detection = (stable_x1, stable_y1, stable_x2, stable_y2, 
                                  label, smooth_confidence)
                stable_detections.append(stable_detection)
        
        return stable_detections
    
    def draw_detections(self, frame, detections):
        """
        Desenha as detecções no frame de forma otimizada.
        
        Args:
            frame: Frame da câmera
            detections: Lista de detecções
        """
        try:
            for x1, y1, x2, y2, label, confidence in detections:
                # Obter cor da classe
                color = self.get_class_color(label)
                
                # Desenhar caixa e label
                draw_bounding_box(frame, x1, y1, x2, y2, label, confidence, color)
                
        except Exception as e:
            print(f"Erro ao desenhar detecções: {e}")
    
    def get_performance_stats(self):
        """Retorna estatísticas de performance."""
        if not self.detection_times:
            return {
                'avg_detection_time': 0,
                'fps_estimate': 0,
                'total_detections': self.total_detections
            }
        
        avg_time = sum(self.detection_times) / len(self.detection_times)
        fps_estimate = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            'avg_detection_time': avg_time,
            'fps_estimate': fps_estimate,
            'total_detections': self.total_detections
        }
    
    def reset_stats(self):
        """Reseta as estatísticas de performance e buffer anti-flickering."""
        with self.lock:
            self.detection_times = []
            self.total_detections = 0
            self.detection_buffer = []  # Limpar buffer anti-flickering
    
    def get_model_info(self):
        """Retorna informações sobre o modelo."""
        return {
            'model_path': self.model_path,
            'confidence_threshold': self.confidence_threshold,
            'iou_threshold': self.iou_threshold,
            'classes': list(self.model.names.values()),
            'num_classes': len(self.model.names)
        } 