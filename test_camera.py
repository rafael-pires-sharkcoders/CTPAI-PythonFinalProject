#!/usr/bin/env python3
"""
Teste simples de câmera para validar se o OpenCV está funcionando.
"""

import cv2
import sys

def test_camera():
    """Testa se a câmera está funcionando."""
    print("🔍 Testando câmera...")
    
    # Tentar abrir diferentes índices de câmera
    for i in range(3):
        print(f"Tentando câmera {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Câmera {i} funcionando!")
                print(f"   Resolução: {frame.shape[1]}x{frame.shape[0]}")
                
                # Mostrar imagem por 3 segundos
                cv2.imshow(f"Teste Câmera {i}", frame)
                cv2.waitKey(3000)
                cv2.destroyAllWindows()
                
                cap.release()
                return True
            else:
                print(f"❌ Câmera {i} não consegue capturar frame")
        else:
            print(f"❌ Câmera {i} não disponível")
        
        cap.release()
    
    print("❌ Nenhuma câmera funcionando encontrada!")
    return False

def test_yolo():
    """Testa se o YOLO está funcionando."""
    print("\n🧠 Testando YOLO...")
    
    try:
        from ultralytics import YOLO
        import numpy as np
        
        # Carregar modelo
        model = YOLO("yolov8n.pt")
        print("✅ Modelo YOLO carregado!")
        
        # Teste com imagem dummy
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = model(dummy_image, verbose=False)
        print("✅ YOLO funcionando!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no YOLO: {e}")
        return False

def main():
    """Função principal de teste."""
    print("🧪 TESTE DO SISTEMA DE DETECÇÃO")
    print("=" * 40)
    
    # Teste 1: Câmera
    camera_ok = test_camera()
    
    # Teste 2: YOLO
    yolo_ok = test_yolo()
    
    # Resultado final
    print("\n📊 RESULTADO DOS TESTES:")
    print(f"   Câmera: {'✅ OK' if camera_ok else '❌ FALHA'}")
    print(f"   YOLO:   {'✅ OK' if yolo_ok else '❌ FALHA'}")
    
    if camera_ok and yolo_ok:
        print("\n🎉 Sistema pronto para usar!")
        print("Execute: python main.py")
    else:
        print("\n⚠️  Sistema com problemas. Verifique as dependências.")
        if not camera_ok:
            print("   - Verifique se a câmera está conectada e funcionando")
        if not yolo_ok:
            print("   - Execute: pip install ultralytics")

if __name__ == "__main__":
    main() 