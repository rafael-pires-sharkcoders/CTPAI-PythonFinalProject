"""
Configurações para integração com InfluxDB
"""

# Configurações do InfluxDB
INFLUXDB_URL = "http://localhost:8086"  # URL do servidor InfluxDB
INFLUXDB_TOKEN = "rgR64HQYPQ6Bd6Jq0aem9ZVX_VDJj1iLOsJJwS-3bt-BSnd4EntBb6fnYWVMeZHZKt_JXwoHhRDO96ps7Spi1w=="  # Token de autenticação
INFLUXDB_ORG = "object-detection-org"   # Organização
INFLUXDB_BUCKET = "object-detection"    # Bucket para armazenar dados

# Configurações de medição
MEASUREMENT_NAME = "object_detection_metrics"

# Configurações de envio
BATCH_SIZE = 100                        # Número de pontos por lote
FLUSH_INTERVAL = 1000                   # Intervalo de flush em ms
TIMEOUT = 10000                         # Timeout em ms

# Tags padrão (metadados que não mudam frequentemente)
DEFAULT_TAGS = {
    "device": "webcam",
    "model": "yolov8n",
    "location": "default"
}

# Campos que serão enviados para o InfluxDB
METRICS_FIELDS = [
    "total_objects",      # Número total de objetos detectados no frame
    "fps",                # Frames por segundo
    "detection_time_ms",  # Tempo de detecção em milissegundos
    "frame_width",        # Largura do frame
    "frame_height",       # Altura do frame
    "confidence_avg",     # Confiança média das detecções
    "confidence_max",     # Confiança máxima das detecções
]

# Classes de objetos YOLO (para contagem por classe)
YOLO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
    'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
    'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
    'toothbrush'
]

