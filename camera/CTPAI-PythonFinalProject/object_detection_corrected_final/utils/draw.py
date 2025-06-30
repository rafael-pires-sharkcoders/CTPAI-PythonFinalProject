import cv2
import numpy as np
from utils.config import BOX_COLOR, TEXT_COLOR, BOX_THICKNESS, FONT_SCALE, FONT_THICKNESS

def draw_bounding_box(frame, x1, y1, x2, y2, label, confidence, color=None):
    """
    Desenha uma caixa delimitadora com label no frame de forma otimizada.
    
    Args:
        frame: Frame do vídeo
        x1, y1, x2, y2: Coordenadas da caixa
        label: Nome do objeto
        confidence: Confiança da detecção
        color: Cor da caixa (opcional)
    """
    try:
        if color is None:
            color = BOX_COLOR
        
        # Converter coordenadas para inteiros e validar
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Garantir que as coordenadas estão dentro dos limites do frame
        height, width = frame.shape[:2]
        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width - 1))
        y2 = max(0, min(y2, height - 1))
        
        # Validar se a caixa é válida
        if x1 >= x2 or y1 >= y2:
            return
        
        # Desenhar caixa
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, BOX_THICKNESS)
        
        # Preparar texto com confiança
        text = f"{label}: {confidence:.1f}"  # Reduzir precisão para economizar espaço
        
        # Calcular tamanho do texto
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS
        )
        
        # Verificar se o texto cabe acima da caixa
        text_y = y1 - 10
        if text_y - text_height < 0:
            text_y = y2 + text_height + 10
        
        # Garantir que o fundo do texto não saia da imagem
        bg_x1 = max(0, x1)
        bg_y1 = max(0, text_y - text_height - 5)
        bg_x2 = min(width, x1 + text_width + 5)
        bg_y2 = min(height, text_y + 5)
        
        # Desenhar fundo do texto apenas se for válido
        if bg_x1 < bg_x2 and bg_y1 < bg_y2:
            cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, -1)
        
        # Desenhar texto
        text_x = max(0, min(x1, width - text_width))
        text_y = max(text_height, min(text_y, height - 5))
        
        cv2.putText(
            frame, 
            text, 
            (text_x, text_y), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            FONT_SCALE, 
            TEXT_COLOR, 
            FONT_THICKNESS,
            cv2.LINE_AA  # Anti-aliasing para melhor qualidade
        )
        
    except Exception as e:
        print(f"Erro ao desenhar caixa: {e}")

# Função get_random_color removida - agora usando cores predefinidas

def draw_fps(frame, fps):
    """Desenha o FPS no canto superior direito com melhor formatação."""
    try:
        fps_text = f"FPS: {fps:.1f}"
        
        # Posição no canto superior direito
        text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        x = frame.shape[1] - text_size[0] - 10
        y = 30
        
        # Fundo para melhor legibilidade
        cv2.rectangle(frame, (x - 5, y - 20), (x + text_size[0] + 5, y + 5), (0, 0, 0), -1)
        
        cv2.putText(
            frame, 
            fps_text, 
            (x, y), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            (0, 255, 255),  # Amarelo
            2,
            cv2.LINE_AA
        )
    except Exception as e:
        print(f"Erro ao desenhar FPS: {e}")

def draw_detection_count(frame, count):
    """Desenha o número de objetos detectados no canto superior esquerdo."""
    try:
        count_text = f"Objetos: {count}"
        
        # Fundo para melhor legibilidade
        text_size = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (5, 5), (text_size[0] + 15, 35), (0, 0, 0), -1)
        
        cv2.putText(
            frame, 
            count_text, 
            (10, 25), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            (255, 255, 0),  # Ciano
            2,
            cv2.LINE_AA
        )
    except Exception as e:
        print(f"Erro ao desenhar contador: {e}")

def draw_performance_info(frame, stats):
    """Desenha informações de performance na tela."""
    try:
        if not stats:
            return
            
        # Preparar textos
        detection_time = stats.get('avg_detection_time', 0) * 1000  # em ms
        total_detections = stats.get('total_detections', 0)
        
        info_text = f"Detecao: {detection_time:.1f}ms | Total: {total_detections}"
        
        # Posição na parte inferior
        text_size = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        x = 10
        y = frame.shape[0] - 10
        
        # Fundo para melhor legibilidade
        cv2.rectangle(frame, (x - 5, y - 20), (x + text_size[0] + 5, y + 5), (0, 0, 0), -1)
        
        cv2.putText(
            frame, 
            info_text, 
            (x, y), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (200, 200, 200),  # Cinza claro
            1,
            cv2.LINE_AA
        )
    except Exception as e:
        print(f"Erro ao desenhar info de performance: {e}")

def draw_status_message(frame, message, color=(0, 0, 255)):
    """Desenha uma mensagem de status centralizada."""
    try:
        # Calcular posição central
        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        x = (frame.shape[1] - text_size[0]) // 2
        y = (frame.shape[0] + text_size[1]) // 2
        
        # Fundo para melhor legibilidade
        cv2.rectangle(
            frame, 
            (x - 10, y - 30), 
            (x + text_size[0] + 10, y + 10), 
            (0, 0, 0), 
            -1
        )
        
        cv2.putText(
            frame, 
            message, 
            (x, y), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.8, 
            color, 
            2,
            cv2.LINE_AA
        )
    except Exception as e:
        print(f"Erro ao desenhar mensagem de status: {e}") 
def draw_status_message_at_position(frame, message, color=(0, 0, 255), position=(10, 30)):
    """Desenha uma mensagem de status em posição específica."""
    try:
        x, y = position
        
        # Calcular tamanho do texto
        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        
        # Fundo para melhor legibilidade
        cv2.rectangle(
            frame, 
            (x - 5, y - 20), 
            (x + text_size[0] + 5, y + 5), 
            (0, 0, 0), 
            -1
        )
        
        cv2.putText(
            frame, 
            message, 
            (x, y), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            color, 
            1,
            cv2.LINE_AA
        )
    except Exception as e:
        print(f"Erro ao desenhar mensagem de status: {e}")

