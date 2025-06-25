#!/usr/bin/env python3
"""
Teste rápido das melhorias anti-flickering.
"""

import cv2
from detector.yolo_detector import YOLODetector
from utils.draw import draw_fps, draw_detection_count
import time

def test_anti_flicker():
    """Testa o sistema anti-flickering."""
    print("🔍 Testando sistema anti-flickering...")
    
    # Inicializar detector
    try:
        detector = YOLODetector()
        print("✅ Detector inicializado")
    except Exception as e:
        print(f"❌ Erro ao carregar detector: {e}")
        return
    
    # Inicializar câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erro: Câmera não encontrada!")
        return
    
    print("✅ Câmera inicializada")
    print("\n🎮 CONTROLES:")
    print("   'Q' - Sair")
    print("   'R' - Resetar buffer anti-flickering")
    print("   'ESPAÇO' - Pausar/Despausar")
    print("\n🚀 Iniciando teste... (As detecções devem ser mais estáveis agora)")
    
    paused = False
    fps_count = 0
    fps_timer = time.time()
    current_fps = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Erro ao capturar frame")
                continue
            
            if not paused:
                # Detectar objetos com sistema anti-flickering
                detections = detector.detect_objects(frame)
                
                # Desenhar detecções
                detector.draw_detections(frame, detections)
                
                # Mostrar informações
                draw_detection_count(frame, len(detections))
                draw_fps(frame, current_fps)
                
                # Mensagem de status
                cv2.putText(frame, "ANTI-FLICKER ATIVO", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "PAUSADO - Pressione ESPACO", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Calcular FPS
            fps_count += 1
            if time.time() - fps_timer > 1.0:
                current_fps = fps_count / (time.time() - fps_timer)
                fps_count = 0
                fps_timer = time.time()
            
            # Mostrar frame
            cv2.imshow("Teste Anti-Flickering", frame)
            
            # Processar teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' ou ESC
                break
            elif key == ord(' '):  # Espaço
                paused = not paused
                status = "pausado" if paused else "despausado"
                print(f"🎬 {status.capitalize()}")
            elif key == ord('r'):  # 'r'
                detector.reset_stats()
                print("🔄 Buffer anti-flickering resetado")
    
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Teste finalizado")

if __name__ == "__main__":
    test_anti_flicker() 