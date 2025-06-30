#!/usr/bin/env python3
"""
Detector de Objetos - Versão com correção forçada para DirectShow
Resolve problemas de câmera no Windows
"""

import cv2
import time
import sys
import threading
import logging
from collections import Counter
from yolo_detector import YOLODetector
from utils.config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, FPS,
    EXIT_KEY, PAUSE_KEY, RESET_KEY, SKIP_FRAMES, CAMERA_BUFFER_SIZE
)
from utils.draw import (
    draw_fps, draw_detection_count, draw_performance_info, 
    draw_status_message, draw_status_message_at_position
)
from influx_client import influx_manager
from influx_config import YOLO_CLASSES

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectDetectorApp:
    """Aplicação do detector com correção de câmera."""
    
    def __init__(self):
        """Inicializa a aplicação."""
        self.detector = None
        self.cap = None
        self.paused = False
        self.show_performance = False
        self.frame_count = 0
        self.last_detections = []
        self.fullscreen = False
        
        # Controle de threads
        self.running = True
        self.detection_lock = threading.Lock()
        
        # Métricas para InfluxDB
        self.metrics_enabled = True
        self.last_metrics_send = time.time()
        self.metrics_interval = 1.0
        
        # Estatísticas de sessão
        self.session_start_time = time.time()
        self.total_frames_processed = 0
        
    def initialize_camera(self):
        """Inicializa a câmera forçando DirectShow."""
        print("🔧 Inicializando câmera com correção para Windows...")
        
        # FORÇAR DirectShow - mais estável no Windows
        print("Forçando uso do DirectShow (correção Windows)...")
        
        for camera_idx in [CAMERA_INDEX, 0, 1, 2]:
            try:
                print(f"Tentando câmera {camera_idx} com DirectShow...")
                
                # FORÇA DirectShow sempre
                self.cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
                
                if self.cap.isOpened():
                    # Aguardar estabilizar
                    time.sleep(1)
                    
                    # Configurar primeiro
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FPS, FPS)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Aguardar mais um pouco
                    time.sleep(0.5)
                    
                    # Teste de captura múltipla
                    success_count = 0
                    for i in range(3):
                        ret, frame = self.cap.read()
                        if ret and frame is not None:
                            success_count += 1
                        time.sleep(0.1)
                    
                    if success_count >= 2:
                        print(f"✅ Câmera {camera_idx} funcionando com DirectShow!")
                        
                        # Verificar resolução real
                        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                        
                        print(f"Câmera configurada: {actual_width}x{actual_height} @ {actual_fps}fps")
                        print("🎯 Problema de câmera corrigido!")
                        return True
                    else:
                        print(f"⚠️ DirectShow instável na câmera {camera_idx}")
                        self.cap.release()
                        self.cap = None
                else:
                    print(f"❌ DirectShow não abriu câmera {camera_idx}")
                    
            except Exception as e:
                print(f"Erro com câmera {camera_idx}: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
                continue
        
        print("❌ Falha na correção da câmera!")
        print("💡 Soluções:")
        print("1. Feche TODOS os programas que usam câmera (Chrome, Teams, etc.)")
        print("2. Reinicie o computador")
        print("3. Execute como Administrador")
        return False
    
    def initialize_detector(self):
        """Inicializa o detector YOLO."""
        try:
            print("Inicializando detector YOLO...")
            self.detector = YOLODetector()
            print("Detector inicializado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao carregar detector: {e}")
            return False
    
    def initialize_influxdb(self):
        """Inicializa conexão com InfluxDB."""
        try:
            print("Conectando ao InfluxDB...")
            if influx_manager.connect():
                print("✅ Conectado ao InfluxDB com sucesso!")
                self.metrics_enabled = True
                return True
            else:
                print("⚠️  InfluxDB não disponível. Métricas desabilitadas.")
                self.metrics_enabled = False
                return False
        except Exception as e:
            print(f"❌ Erro InfluxDB: {e}")
            self.metrics_enabled = False
            return False
    
    def process_frame(self, frame):
        """Processa um frame para detecção."""
        if self.paused or self.detector is None:
            return self.last_detections
        
        self.frame_count += 1
        if self.frame_count % (1 + 1) != 0:
            return self.last_detections
        
        try:
            detections = self.detector.detect_objects(frame)
            with self.detection_lock:
                self.last_detections = detections
            self.total_frames_processed += 1
            return detections
        except Exception as e:
            print(f"Erro durante processamento: {e}")
            return []
    
    def draw_interface(self, frame, detections, current_fps):
        """Desenha a interface."""
        try:
            if detections and self.detector is not None:
                self.detector.draw_detections(frame, detections)
            
            draw_detection_count(frame, len(detections))
            draw_fps(frame, current_fps)
            
            if self.show_performance and self.detector is not None:
                stats = self.detector.get_performance_stats()
                draw_performance_info(frame, stats)
            
            if self.paused:
                draw_status_message(frame, "PAUSADO - Pressione ESPACO para continuar", (0, 0, 255))
            
            # Status da câmera
            draw_status_message_at_position(frame, "Camera: DirectShow (Corrigida)", (0, 255, 0), position=(10, 30))
            
        except Exception as e:
            print(f"Erro ao desenhar: {e}")
    
    def handle_key_press(self, key):
        """Trata teclas pressionadas."""
        if key == EXIT_KEY or key == 27:
            return False
        elif key == PAUSE_KEY:
            self.paused = not self.paused
            status = "Pausado" if self.paused else "Despausado"
            print(f"🎬 {status}")
        elif key == RESET_KEY:
            if self.detector is not None:
                self.detector.reset_stats()
                print("📊 Estatísticas resetadas")
        elif key == ord('p'):
            self.show_performance = not self.show_performance
            status = "ativadas" if self.show_performance else "desativadas"
            print(f"📈 Informações de performance {status}")
        elif key == ord('s'):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            if hasattr(self, 'current_frame'):
                cv2.imwrite(filename, self.current_frame)
                print(f"📸 Screenshot salvo: {filename}")
        
        return True
    
    def run(self):
        """Executa o loop principal."""
        print("\n" + "="*60)
        print("🎯 DETECTOR DE OBJETOS - CORREÇÃO DE CÂMERA WINDOWS")
        print("="*60)
        print("📖 CONTROLES:")
        print("   'Q' ou 'ESC' - Sair")
        print("   'ESPAÇO'     - Pausar/Despausar")
        print("   'R'          - Resetar estatísticas")
        print("   'P'          - Performance info")
        print("   'S'          - Screenshot")
        print("="*60)
        
        # Inicializar componentes
        if not self.initialize_camera():
            print("\n❌ Falha na inicialização da câmera!")
            return
        
        if not self.initialize_detector():
            print("\n❌ Falha na inicialização do detector!")
            return
        
        # Tentar InfluxDB (opcional)
        self.initialize_influxdb()
        
        # Loop principal
        fps_counter = 0
        fps_timer = time.time()
        current_fps = 0
        
        print("\n✅ Sistema funcionando! Pressione 'Q' para sair.\n")
        
        try:
            while self.running:
                # Verificar câmera
                if self.cap is None or not self.cap.isOpened():
                    print("⚠️ Câmera desconectada!")
                    break
                
                # Capturar frame
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️ Falha na captura!")
                    time.sleep(0.1)
                    continue
                
                self.current_frame = frame.copy()
                
                # Processar
                detections = self.process_frame(frame)
                
                # Desenhar
                self.draw_interface(frame, detections, current_fps)
                
                # Calcular FPS
                fps_counter += 1
                if time.time() - fps_timer > 1.0:
                    current_fps = fps_counter / (time.time() - fps_timer)
                    fps_counter = 0
                    fps_timer = time.time()
                
                # Mostrar frame
                cv2.imshow("Detector de Objetos - Câmera Corrigida", frame)
                
                # Teclas
                key = cv2.waitKey(1) & 0xFF
                if key != 255:
                    if not self.handle_key_press(key):
                        break
        
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpa recursos."""
        print("\n🧹 Finalizando...")
        self.running = False
        
        if self.cap is not None:
            self.cap.release()
            print("📹 Câmera liberada")
        
        cv2.destroyAllWindows()
        print("🖼️ Janelas fechadas")
        
        if self.metrics_enabled:
            influx_manager.disconnect()
            print("📊 InfluxDB desconectado")
        
        print("✅ Finalizado!")

def main():
    """Função principal."""
    try:
        app = ObjectDetectorApp()
        app.run()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 