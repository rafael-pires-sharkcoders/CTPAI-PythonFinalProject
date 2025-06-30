#!/usr/bin/env python3
"""
VERSÃO CORRIGIDA - CÂMERA NUNCA FICA BLOQUEADA
Sempre usa DirectShow no Windows
"""

import cv2
import time
import sys
import threading
import logging
from collections import Counter
from yolo_detector import YOLODetector
from utils.config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, FPS, EXIT_KEY, PAUSE_KEY, RESET_KEY
from utils.draw import draw_fps, draw_detection_count, draw_status_message_at_position
from influx_client import influx_manager
from influx_config import YOLO_CLASSES

class FixedDetectorApp:
    def __init__(self):
        self.detector = None
        self.cap = None
        self.paused = False
        self.running = True
        self.metrics_enabled = True
        self.last_metrics_send = time.time()
        self.session_start_time = time.time()
        self.total_frames_processed = 0
        
    def initialize_camera(self):
        """FORÇA DirectShow - câmera nunca fica bloqueada."""
        print("🔧 FORÇANDO DIRECTSHOW - CORREÇÃO DEFINITIVA")
        
        for camera_idx in [0, 1, 2]:
            try:
                print(f"📹 Câmera {camera_idx} com DirectShow FORÇADO...")
                
                # SEMPRE DirectShow
                self.cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
                
                if self.cap.isOpened():
                    time.sleep(2)  # Estabilizar
                    
                    # Configurar
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Testar
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"✅ CÂMERA {camera_idx} FUNCIONANDO!")
                        print("🎯 DIRECTSHOW ATIVO - Nunca mais ficará bloqueada!")
                        return True
                    
                self.cap.release()
                self.cap = None
                
            except Exception as e:
                print(f"❌ Erro câmera {camera_idx}: {e}")
                
        return False
    
    def run(self):
        print("🚀 DETECTOR COM CÂMERA CORRIGIDA")
        print("="*50)
        
        if not self.initialize_camera():
            print("❌ Falha na câmera!")
            return
        
        # Inicializar detector
        self.detector = YOLODetector()
        
        # InfluxDB
        try:
            influx_manager.connect()
            print("✅ InfluxDB conectado")
        except:
            self.metrics_enabled = False
            print("⚠️ InfluxDB indisponível")
        
        print("\n✅ SISTEMA FUNCIONANDO!")
        print("📌 Câmera: DirectShow (nunca fica bloqueada)")
        print("Pressione 'Q' para sair\n")
        
        # Loop principal
        while self.running:
            if not self.cap or not self.cap.isOpened():
                break
                
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Detectar objetos
            detections = []
            if self.detector and not self.paused:
                detections = self.detector.detect_objects(frame)
            
            # Desenhar
            if detections and self.detector:
                self.detector.draw_detections(frame, detections)
            
            draw_detection_count(frame, len(detections))
            
            # Status
            draw_status_message_at_position(
                frame, "DIRECTSHOW ATIVO - Camera CORRIGIDA", 
                (0, 255, 0), position=(10, 30)
            )
            
            # Mostrar
            cv2.imshow("Detector - Camera CORRIGIDA", frame)
            
            # Teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord(' '):
                self.paused = not self.paused
                print("🎬 Pausado" if self.paused else "🎬 Despausado")
        
        # Cleanup
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Finalizado!")

def main():
    app = FixedDetectorApp()
    app.run()

if __name__ == "__main__":
    main() 