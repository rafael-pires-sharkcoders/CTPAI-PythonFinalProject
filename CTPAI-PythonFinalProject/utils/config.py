# Configurações do detector de objetos

# Configurações da câmera
CAMERA_INDEX = 0  # 0 para câmera padrão, 1 para externa
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Buffer da câmera para reduzir lag
CAMERA_BUFFER_SIZE = 1

# Configurações do modelo YOLO
MODEL_PATH = "yolov8n.pt"  # Modelo leve e rápido
CONFIDENCE_THRESHOLD = 0.4  # Reduzido para detectar mais objetos
IOU_THRESHOLD = 0.5       # Threshold para Non-Maximum Suppression

# Performance settings
SKIP_FRAMES = 2  # Processar apenas 1 em cada 3 frames para melhor performance
MAX_DETECTIONS = 50  # Limitar número de detecções por frame

# Configurações visuais
BOX_COLOR = (0, 255, 0)    # Verde (BGR)
TEXT_COLOR = (255, 255, 255)  # Branco
BOX_THICKNESS = 2
FONT_SCALE = 0.5  # Reduzido para melhor performance
FONT_THICKNESS = 1  # Reduzido

# Cores predefinidas para melhor performance
PREDEFINED_COLORS = [
    (255, 0, 0),    # Azul
    (0, 255, 0),    # Verde
    (0, 0, 255),    # Vermelho
    (255, 255, 0),  # Ciano
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Amarelo
    (128, 0, 128),  # Roxo
    (255, 165, 0),  # Laranja
    (0, 128, 255),  # Azul claro
    (128, 255, 0),  # Verde claro
]

# Teclas de controle
EXIT_KEY = ord('q')
PAUSE_KEY = ord(' ')
RESET_KEY = ord('r')  # Nova tecla para resetar 