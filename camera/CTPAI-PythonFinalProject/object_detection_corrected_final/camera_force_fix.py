#!/usr/bin/env python3
"""
CORREÇÃO DEFINITIVA DA CÂMERA - Resolve problema do Edge/Chrome
"""

import cv2
import time
import sys
import subprocess
import os
from yolo_detector import YOLODetector
from utils.config import FRAME_WIDTH, FRAME_HEIGHT, FPS
from utils.draw import draw_fps, draw_detection_count

def kill_camera_blocking_processes():
    """Mata processos que estão bloqueando a câmera."""
    print("🔥 ELIMINANDO PROCESSOS QUE BLOQUEIAM A CÂMERA...")
    
    # Processos que costumam interferir com câmera
    blocking_processes = [
        "msedge.exe",
        "chrome.exe", 
        "firefox.exe",
        "Teams.exe",
        "Skype.exe",
        "obs64.exe",
        "obs32.exe"
    ]
    
    killed_count = 0
    
    for process in blocking_processes:
        try:
            # Comando para matar processo
            result = subprocess.run(
                ["taskkill", "/F", "/IM", process], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                print(f"✅ Eliminado: {process}")
                killed_count += 1
            # Silencioso se processo não existir
        except:
            pass
    
    if killed_count > 0:
        print(f"🎯 {killed_count} processos eliminados!")
        print("⏳ Aguardando sistema estabilizar...")
        time.sleep(3)  # Aguardar sistema liberar câmera
    else:
        print("ℹ️ Nenhum processo interferente encontrado")

def force_camera_initialization():
    """Força inicialização da câmera com configurações agressivas."""
    print("💪 INICIALIZANDO CÂMERA COM FORÇA TOTAL...")
    
    # Tentar múltiplas vezes com diferentes configurações
    for attempt in range(3):
        print(f"\n🔄 Tentativa {attempt + 1}/3...")
        
        for camera_idx in [0, 1, 2]:
            try:
                print(f"📹 Forçando câmera {camera_idx} com DirectShow...")
                
                # FORÇA DirectShow com configurações específicas
                cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
                
                if cap.isOpened():
                    print(f"  ⏳ Estabilizando câmera {camera_idx}...")
                    time.sleep(2)  # Mais tempo para estabilizar
                    
                    # Configurações agressivas
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Configurações específicas DirectShow
                    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                    cap.set(cv2.CAP_PROP_EXPOSURE, -6)
                    
                    time.sleep(1)  # Aguardar configurações aplicarem
                    
                    # Teste múltiplas capturas
                    success_frames = 0
                    for test in range(5):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            success_frames += 1
                        time.sleep(0.2)
                    
                    if success_frames >= 3:
                        print(f"🎉 CÂMERA {camera_idx} FUNCIONANDO! ({success_frames}/5 frames)")
                        return cap
                    else:
                        print(f"❌ Câmera {camera_idx} instável ({success_frames}/5)")
                        cap.release()
                else:
                    print(f"❌ Não conseguiu abrir câmera {camera_idx}")
                    
            except Exception as e:
                print(f"❌ Erro câmera {camera_idx}: {e}")
                continue
        
        if attempt < 2:
            print("⏳ Aguardando antes da próxima tentativa...")
            time.sleep(2)
    
    return None

def run_camera_test():
    """Executa teste completo da câmera."""
    print("🚀 TESTE DEFINITIVO DE CÂMERA - FORÇANDO FUNCIONAMENTO")
    print("="*60)
    
    # Passo 1: Eliminar processos interferentes
    kill_camera_blocking_processes()
    
    # Passo 2: Forçar inicialização
    cap = force_camera_initialization()
    
    if cap is None:
        print("\n❌ FALHA TOTAL!")
        print("💡 SOLUÇÕES EXTREMAS:")
        print("1. REINICIE O COMPUTADOR")
        print("2. Execute como ADMINISTRADOR")
        print("3. Desconecte e reconecte a câmera")
        print("4. Atualize drivers da câmera")
        return False
    
    # Passo 3: Teste visual
    print("\n🎯 CÂMERA FUNCIONANDO! Iniciando teste visual...")
    print("Pressione 'Q' para parar o teste")
    
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Falha na captura!")
                break
            
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Desenhar informações
            cv2.putText(frame, f"CAMERA CORRIGIDA - FPS: {fps:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, "Pressione 'Q' para sair", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            cv2.imshow("CAMERA FUNCIONANDO - TESTE DEFINITIVO", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Teste finalizado!")
        return True

def main():
    """Executa correção definitiva."""
    try:
        success = run_camera_test()
        
        if success:
            print("\n🎉 PROBLEMA RESOLVIDO!")
            print("Agora você pode executar:")
            print("python main_with_influx.py")
        else:
            print("\n💥 Problemas persistem. Tente as soluções extremas sugeridas.")
            
    except Exception as e:
        print(f"❌ Erro durante correção: {e}")

if __name__ == "__main__":
    print("⚠️  ATENÇÃO: Esta correção vai fechar Edge/Chrome/Teams automaticamente!")
    print("Pressione ENTER para continuar ou CTRL+C para cancelar...")
    try:
        input()
        main()
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário") 