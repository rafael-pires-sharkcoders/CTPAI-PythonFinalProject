#!/usr/bin/env python3
"""
Correção Simples da Câmera - Força DirectShow sem fechar programas
"""

import cv2
import time

def force_directshow_camera():
    """Força o uso do DirectShow com configurações agressivas."""
    print("🔧 FORÇANDO DIRECTSHOW - CORREÇÃO SIMPLES")
    print("="*50)
    
    for camera_idx in [0, 1, 2]:
        print(f"\n📹 Testando câmera {camera_idx}...")
        
        try:
            # FORÇA DirectShow especificamente
            print(f"  🎯 Forçando DirectShow na câmera {camera_idx}...")
            cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
            
            if not cap.isOpened():
                print(f"  ❌ Falha ao abrir com DirectShow")
                continue
            
            # Aguardar estabilizar
            print(f"  ⏳ Aguardando estabilização...")
            time.sleep(3)  # Tempo maior para estabilizar
            
            # Configurar agressivamente
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Aguardar configurações aplicarem
            time.sleep(1)
            
            # Teste múltiplas capturas para confirmar
            print(f"  🧪 Testando capturas múltiplas...")
            successful_captures = 0
            
            for test in range(10):  # 10 testes
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    successful_captures += 1
                    print(f"    Captura {test+1}: ✅")
                else:
                    print(f"    Captura {test+1}: ❌")
                time.sleep(0.1)
            
            success_rate = (successful_captures / 10) * 100
            print(f"  📊 Taxa de sucesso: {success_rate}%")
            
            if successful_captures >= 7:  # 70% de sucesso
                print(f"  🎉 CÂMERA {camera_idx} FUNCIONANDO!")
                
                # Teste visual rápido
                print(f"  👀 Iniciando teste visual (5 segundos)...")
                
                start_time = time.time()
                frame_count = 0
                
                while time.time() - start_time < 5:  # 5 segundos
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        frame_count += 1
                        
                        # Desenhar info na tela
                        cv2.putText(frame, f"CAMERA CORRIGIDA!", (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, f"DirectShow funcionando", (10, 70), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(frame, f"Frames: {frame_count}", (10, 110), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        cv2.imshow("CAMERA CORRIGIDA - FUNCIONANDO!", frame)
                        cv2.waitKey(1)
                
                cap.release()
                cv2.destroyAllWindows()
                
                print(f"  ✅ {frame_count} frames capturados em 5 segundos!")
                print(f"  🎯 CÂMERA {camera_idx} TOTALMENTE FUNCIONAL!")
                return True
            else:
                print(f"  ❌ Câmera {camera_idx} instável ({successful_captures}/10)")
                cap.release()
                
        except Exception as e:
            print(f"  ❌ Erro na câmera {camera_idx}: {e}")
            continue
    
    return False

def main():
    """Executa a correção."""
    print("🚀 CORREÇÃO SIMPLES DA CÂMERA")
    print("Não fecha outros programas, apenas força DirectShow")
    print()
    
    success = force_directshow_camera()
    
    if success:
        print("\n🎉 PROBLEMA RESOLVIDO!")
        print("✅ Câmera funcionando com DirectShow")
        print()
        print("🚀 AGORA EXECUTE:")
        print("python main_with_influx.py")
        print()
        print("💡 A câmera deve aparecer normal agora!")
    else:
        print("\n❌ CORREÇÃO FALHOU")
        print("💡 SOLUÇÕES:")
        print("1. Feche manualmente: Edge, Chrome, Teams")
        print("2. Execute: python camera_force_fix.py (fecha automaticamente)")
        print("3. Reinicie o computador")

if __name__ == "__main__":
    main() 