#!/usr/bin/env python3
"""
Detector de Objetos em Tempo Real - Versão Otimizada
Usando OpenCV + YOLO para detecção de objetos via webcam
"""

import cv2
import time
import sys
import threading
from detector.yolo_detector import YOLODetector
from utils.config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, FPS,
    EXIT_KEY, PAUSE_KEY, RESET_KEY, SKIP_FRAMES, CAMERA_BUFFER_SIZE
)
from utils.draw import (
    draw_fps, draw_detection_count, draw_performance_info, 
    draw_status_message
)

class ObjectDetectorApp:
    """Aplicação principal do detector de objetos - Versão Otimizada."""
    
    def __init__(self):
        """Inicializa a aplicação."""
        self.detector = None
        self.cap = None
        self.paused = False
        self.show_performance = False
        self.frame_count = 0
        self.last_detections = []
        self.fullscreen = False  # Estado da tela cheia
        
        # Controle de threads
        self.running = True
        self.detection_lock = threading.Lock()
        
    def initialize_camera(self):
        """Inicializa a câmera com configurações otimizadas."""
        print("Inicializando câmera...")
        
        # Tentar diferentes índices de câmera se necessário
        for camera_idx in [CAMERA_INDEX, 0, 1, 2]:
            try:
                self.cap = cv2.VideoCapture(camera_idx)
                if self.cap.isOpened():
                    print(f"Câmera encontrada no índice {camera_idx}")
                    break
                else:
                    self.cap.release()
            except Exception as e:
                print(f"Erro ao tentar câmera {camera_idx}: {e}")
                continue
        
        if not self.cap or not self.cap.isOpened():
            print("Erro: Não foi possível abrir nenhuma câmera!")
            return False
        
        # Configurar propriedades da câmera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
        
        # Verificar resolução real
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"Câmera configurada: {actual_width}x{actual_height} @ {actual_fps}fps")
        
        # Teste de captura
        ret, test_frame = self.cap.read()
        if not ret:
            print("Erro: Não foi possível capturar frame de teste!")
            return False
        
        print("Câmera inicializada com sucesso!")
        return True
    
    def initialize_detector(self):
        """Inicializa o detector YOLO."""
        try:
            print("Inicializando detector YOLO...")
            self.detector = YOLODetector()
            print("Detector inicializado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao carregar detector: {e}")
            print("Verifique se as dependências estão instaladas corretamente.")
            return False
    
    def process_frame(self, frame):
        """Processa um frame para detecção de objetos."""
        if self.paused:
            return self.last_detections
        
        # Skip frames para melhor performance (reduzido para eliminar piscar)
        self.frame_count += 1
        if self.frame_count % (1 + 1) != 0:  # Processar mais frames
            return self.last_detections
        
        try:
            # Detectar objetos
            detections = self.detector.detect_objects(frame)
            
            with self.detection_lock:
                self.last_detections = detections
            
            return detections
            
        except Exception as e:
            print(f"Erro durante processamento: {e}")
            return []
    
    def draw_interface(self, frame, detections, current_fps):
        """Desenha toda a interface na tela."""
        try:
            # Desenhar detecções
            if detections:
                self.detector.draw_detections(frame, detections)
            
            # Desenhar informações básicas
            draw_detection_count(frame, len(detections))
            draw_fps(frame, current_fps)
            
            # Desenhar informações de performance se habilitado
            if self.show_performance:
                stats = self.detector.get_performance_stats()
                draw_performance_info(frame, stats)
            
            # Desenhar status de pausa
            if self.paused:
                draw_status_message(frame, "PAUSADO - Pressione ESPACO para continuar", (0, 0, 255))
            
        except Exception as e:
            print(f"Erro ao desenhar interface: {e}")
    
    def print_controls(self):
        """Exibe os controles disponíveis."""
        print("\n" + "="*60)
        print("    🎯 DETECTOR DE OBJETOS EM TEMPO REAL - V2.0")
        print("="*60)
        print("📖 CONTROLES:")
        print("   'Q' ou 'ESC'    - Sair do programa")
        print("   'ESPAÇO'        - Pausar/Despausar detecção")
        print("   'R'             - Resetar estatísticas")
        print("   'P'             - Mostrar/Ocultar info de performance")
        print("   'S'             - Salvar screenshot")
        print("   'F'             - Alternar tela cheia")
        print("="*60)
        print("🚀 Iniciando detector...")
        print()
    
    def handle_key_press(self, key):
        """Trata as teclas pressionadas."""
        if key == EXIT_KEY or key == 27:  # 'q' ou ESC
            return False
        elif key == PAUSE_KEY:  # Espaço
            self.paused = not self.paused
            status = "Pausado" if self.paused else "Despausado"
            print(f"🎬 {status}")
        elif key == RESET_KEY:  # 'r'
            if self.detector:
                self.detector.reset_stats()
                print("📊 Estatísticas resetadas")
        elif key == ord('p'):  # 'p' para performance
            self.show_performance = not self.show_performance
            status = "ativadas" if self.show_performance else "desativadas"
            print(f"📈 Informações de performance {status}")
        elif key == ord('s'):  # 's' para screenshot
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            if hasattr(self, 'current_frame'):
                cv2.imwrite(filename, self.current_frame)
                print(f"📸 Screenshot salvo: {filename}")
        elif key == ord('f'):  # 'f' para tela cheia
            self.toggle_fullscreen()
        
        return True
    
    def toggle_fullscreen(self):
        """Alterna entre modo janela e tela cheia."""
        try:
            self.fullscreen = not self.fullscreen
            
            if self.fullscreen:
                # Ativar tela cheia
                cv2.namedWindow("Detector de Objetos - V2.0", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Detector de Objetos - V2.0", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                print("🖥️ Tela cheia ATIVADA (Pressione 'F' para sair)")
            else:
                # Voltar ao modo janela
                cv2.setWindowProperty("Detector de Objetos - V2.0", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Detector de Objetos - V2.0", 800, 600)
                print("🪟 Modo janela ATIVADO")
                
        except Exception as e:
            print(f"❌ Erro ao alternar tela cheia: {e}")
    
    def run(self):
        """Executa o loop principal da aplicação."""
        self.print_controls()
        
        # Inicializar componentes
        if not self.initialize_camera():
            return
        
        if not self.initialize_detector():
            return
        
        # Variáveis para cálculo de FPS
        fps_counter = 0
        fps_timer = time.time()
        current_fps = 0
        
        print("✅ Sistema inicializado! Pressione 'Q' para sair.\n")
        
        try:
            while self.running:
                # Capturar frame
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️  Erro: Não foi possível capturar frame!")
                    time.sleep(0.1)
                    continue
                
                self.current_frame = frame.copy()
                
                # Processar frame
                detections = self.process_frame(frame)
                
                # Desenhar interface
                self.draw_interface(frame, detections, current_fps)
                
                # Calcular FPS
                fps_counter += 1
                if time.time() - fps_timer > 1.0:
                    current_fps = fps_counter / (time.time() - fps_timer)
                    fps_counter = 0
                    fps_timer = time.time()
                
                # Mostrar frame
                cv2.imshow("Detector de Objetos - V2.0", frame)
                
                # Verificar teclas pressionadas
                key = cv2.waitKey(1) & 0xFF
                if key != 255:  # Alguma tecla foi pressionada
                    if not self.handle_key_press(key):
                        break
        
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        
        except Exception as e:
            print(f"❌ Erro durante execução: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpa recursos de forma segura."""
        print("\n🧹 Finalizando aplicação...")
        self.running = False
        
        if self.cap:
            self.cap.release()
            print("📹 Câmera liberada")
        
        cv2.destroyAllWindows()
        print("🖼️  Janelas fechadas")
        
        # Mostrar estatísticas finais
        if self.detector:
            stats = self.detector.get_performance_stats()
            print(f"\n📊 ESTATÍSTICAS FINAIS:")
            print(f"   Total de objetos detectados: {stats.get('total_detections', 0)}")
            print(f"   Tempo médio de detecção: {stats.get('avg_detection_time', 0)*1000:.1f}ms")
        
        print("✅ Finalizado com sucesso!")

def main():
    """Função principal."""
    try:
        app = ObjectDetectorApp()
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 