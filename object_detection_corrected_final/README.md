# Detector de Objetos em Tempo Real

Um detector de objetos em tempo real usando **OpenCV** e **YOLO** que identifica objetos através da webcam, desenhando caixas delimitadoras e labels com o nome dos objetos detectados.

##  Funcionalidades

-  **Detecção em tempo real** via webcam
-  **Caixas delimitadoras** coloridas para cada objeto
-  **Labels com nome e confiança** dos objetos
-  **Contador de FPS** em tempo real
-  **Contador de objetos** detectados
-  **Controles de teclado** (pausar/despausar)
-  **Interface visual** limpa e informativa

## Tecnologias Utilizadas

- **Python 3.8+**
- **OpenCV** - Captura de vídeo e processamento de imagem
- **YOLOv8** (Ultralytics) - Modelo de detecção de objetos
- **NumPy** - Processamento numérico
- **PyTorch** - Backend do YOLO (instalado automaticamente)

##  Estrutura do Projeto

```
detetor_objetos/
├── main.py                    # Script principal
├── detector/
│   ├── __init__.py
│   └── yolo_detector.py       # Lógica de detecção YOLO
├── utils/
│   ├── __init__.py
│   ├── config.py              # Configurações
│   └── draw.py                # Funções de desenho
├── requirements.txt           # Dependências
└── README.md                  # Este arquivo
```

##  Instalação

### 1. Clonar/Baixar o projeto
```bash
# Se for um repositório Git
git clone <url-do-repositorio>
cd detetor_objetos

# Ou simplesmente baixar os arquivos para uma pasta
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Executar o programa
```bash
python main.py
```

##  Controles

| Tecla | Ação |
|-------|------|
| `Q` | Sair do programa |
| `Espaço` | Pausar/Despausar detecção |
| `ESC` | Fechar janela |

##  Configurações

Você pode ajustar as configurações no arquivo `utils/config.py`:

### Câmera
```python
CAMERA_INDEX = 0          # 0 = câmera padrão, 1 = câmera externa
FRAME_WIDTH = 640         # Largura do vídeo
FRAME_HEIGHT = 480        # Altura do vídeo
FPS = 30                  # Frames por segundo
```

### Modelo YOLO
```python
MODEL_PATH = "yolov8n.pt"        # Modelo (n=nano, s=small, m=medium, l=large, x=extra)
CONFIDENCE_THRESHOLD = 0.5       # Confiança mínima (0.0 a 1.0)
IOU_THRESHOLD = 0.45            # Threshold para NMS
```

### Visual
```python
BOX_COLOR = (0, 255, 0)         # Cor padrão das caixas (BGR)
TEXT_COLOR = (255, 255, 255)    # Cor do texto
BOX_THICKNESS = 2               # Espessura das caixas
```

##  Objetos Detectados

O modelo YOLO padrão pode detectar **80 classes** diferentes de objetos, incluindo:

-  **Pessoas** (person)
-  **Veículos** (car, truck, bus, motorcycle, bicycle)
-  **Animais** (dog, cat, bird, horse, cow, etc.)
-  **Objetos** (cell phone, laptop, mouse, keyboard)
-  **Móveis** (chair, couch, table, bed)
-  **Comida** (apple, banana, pizza, cake)

##  Personalização

### Trocar Modelo YOLO
```python
# Em utils/config.py, altere:
MODEL_PATH = "yolov8s.pt"  # Para modelo mais preciso (mas mais lento)
MODEL_PATH = "yolov8x.pt"  # Para máxima precisão
```

### Ajustar Sensibilidade
```python
# Detecção mais sensível (mais objetos, pode ter falsos positivos)
CONFIDENCE_THRESHOLD = 0.3

# Detecção menos sensível (menos objetos, mais precisão)
CONFIDENCE_THRESHOLD = 0.7
```

##  Solução de Problemas

### Câmera não abre
- Certifique-se que a câmera não está sendo usada por outro programa
- Tente alterar `CAMERA_INDEX` para 1 ou 2
- Verifique se a câmera está conectada

### Detecção muito lenta
- Use um modelo menor: `yolov8n.pt` (mais rápido)
- Reduza a resolução em `config.py`
- Aumente `CONFIDENCE_THRESHOLD`

### Erro de instalação
```bash
# Instalar dependências uma por uma
pip install opencv-python
pip install ultralytics
pip install numpy
pip install pillow
```

##  Performance

| Modelo | Velocidade | Precisão | Tamanho |
|--------|------------|----------|---------|
| YOLOv8n | ⚡⚡⚡ | ⭐⭐ | ~6MB |
| YOLOv8s | ⚡⚡ | ⭐⭐⭐ | ~22MB |
| YOLOv8m | ⚡ | ⭐⭐⭐⭐ | ~52MB |
| YOLOv8l | 🐌 | ⭐⭐⭐⭐⭐ | ~87MB |

##  Licença

Este projeto é open source e está disponível sob a licença MIT.

##  Contribuição

Sinta-se à vontade para contribuir com melhorias:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

##  Suporte

Se tiver problemas ou dúvidas:
- Abra uma issue no repositório
- Verifique a documentação do OpenCV e Ultralytics
- Consulte a seção "Solução de Problemas" acima

---

**Divirta-se detectando objetos! 🎉** 
