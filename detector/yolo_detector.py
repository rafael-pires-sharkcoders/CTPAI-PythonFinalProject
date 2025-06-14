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
    """Detector de objetos usando YOLO com otimizações de performance."""
    
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
        Detecta objetos no frame com otimizações de performance.
        
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
            
            detections = []
            
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
                            
                            detections.append((x1, y1, x2, y2, label, confidence))
                            
                        except Exception as e:
                            print(f"Erro ao processar detecção: {e}")
                            continue
            
            # Atualizar estatísticas
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            if len(self.detection_times) > 100:  # Manter apenas últimas 100 medições
                self.detection_times.pop(0)
            
            self.total_detections += len(detections)
            
            return detections
            
        except Exception as e:
            print(f"Erro durante detecção: {e}")
            return []
    
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
        """Reseta as estatísticas de performance."""
        with self.lock:
            self.detection_times = []
            self.total_detections = 0
    
    def get_model_info(self):
        """Retorna informações sobre o modelo."""
        return {
            'model_path': self.model_path,
            'confidence_threshold': self.confidence_threshold,
            'iou_threshold': self.iou_threshold,
            'classes': list(self.model.names.values()),
            'num_classes': len(self.model.names)
        } 