# 🎯 Detector de Objetos em Tempo Real - InfluxDB & Grafana

**Sistema completo de detecção de objetos em tempo real usando YOLOv8 com monitorização avançada via InfluxDB e Grafana.**

## 🚀 Funcionalidades

### Detecção de Objetos
- ✅ **Detecção em tempo real** via webcam usando YOLOv8
- ✅ **Sistema anti-flickering** para estabilizar detecções
- ✅ **Caixas delimitadoras** coloridas para cada objeto
- ✅ **Labels com nome e confiança** dos objetos detectados
- ✅ **Contador de FPS** em tempo real
- ✅ **Múltiplos backends de câmera** (DirectShow, MSMF, Auto)

### Monitorização e Métricas
- ✅ **Integração com InfluxDB** para armazenamento de métricas
- ✅ **Dashboard Grafana** para visualização em tempo real
- ✅ **Métricas coletadas**:
  - FPS (Frames por segundo)
  - Número de objetos detectados por frame
  - Tempo de detecção por frame
  - Confiança média, máxima e mínima das detecções
  - Contagem de objetos por classe (person, car, etc.)
  - Duração da sessão e frames processados

### Interface e Controles
- ✅ **Controles de teclado** completos
- ✅ **Modo tela cheia**
- ✅ **Screenshots automáticos**
- ✅ **Interface visual** informativa

## 🛠 Tecnologias

- **Python 3.8+** - Linguagem principal
- **OpenCV** - Captura de vídeo e processamento
- **YOLOv8** (Ultralytics) - Detecção de objetos
- **InfluxDB 2.7** - Base de dados temporal
- **Grafana 10.2** - Visualização de dados
- **Docker & Docker Compose** - Containerização

## 📁 Estrutura do Projeto

```
object_detection_corrected_final/
├── main_with_influx.py               # ⭐ Script principal (recomendado)
├── main.py                           # Script simples (sem métricas)
├── yolo_detector.py                  # Detector YOLO otimizado
├── influx_client.py                  # Cliente InfluxDB
├── influx_config.py                  # Configurações InfluxDB  
├── camera.py                         # Módulo de câmera
├── utils/
│   ├── config.py                     # Configurações gerais
│   └── draw.py                       # Funções de desenho
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── influxdb.yml          # Configuração datasource
│       └── dashboards/
│           ├── dashboard.yml         # Configuração dashboards
│           └── object-detection-dashboard.json
├── docker-compose.yml                # Serviços InfluxDB/Grafana
├── start_services.bat                # Script de inicialização Windows
├── requirements.txt                  # Dependências Python
├── object-detection-dashboard.json   # Dashboard Grafana
├── yolov8n.pt                        # Modelo YOLO pré-treinado (6.5MB)
└── README.md                         # Esta documentação
```

## ⚡ Instalação Rápida

### 1️⃣ Pré-requisitos
- **Docker Desktop** (versão mais recente)
- **Python 3.8+**
- **Webcam** conectada

### 2️⃣ Instalar Dependências
```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3️⃣ Iniciar Serviços
```bash
# Windows
.\start_services.bat

# Manual
docker compose up -d
```

### 4️⃣ Executar Detector
```bash
# Versão completa com InfluxDB (RECOMENDADA)
python main_with_influx.py

# Versão simples (sem métricas)
python main.py
```

## 🎮 Controles

| Tecla | Função |
|-------|--------|
| `Q` ou `ESC` | Sair do programa |
| `Espaço` | Pausar/Despausar detecção |
| `R` | Resetar estatísticas |
| `P` | Mostrar/Ocultar info de performance |
| `S` | Salvar screenshot |
| `F` | Alternar tela cheia |
| `M` | Habilitar/Desabilitar métricas InfluxDB |

## 📊 Dashboard Grafana

### Acesso
1. **URL**: http://localhost:3000
2. **Login**: admin / adminpassword
3. **Dashboard**: "Object Detection Dashboard" (carrega automaticamente)

### Painéis Disponíveis
1. **📈 FPS em Tempo Real** - Performance do sistema
2. **🎯 Objetos Detectados** - Contagem por frame
3. **⏱ Tempo de Detecção** - Latência de processamento
4. **🎲 Confiança Média** - Qualidade das detecções
5. **🥧 Distribuição por Classe** - Tipos de objetos detectados

## ⚙️ Configurações

### Câmera (`utils/config.py`)
```python
CAMERA_INDEX = 0          # 0 = padrão, 1 = externa
FRAME_WIDTH = 640         # Largura do vídeo
FRAME_HEIGHT = 480        # Altura do vídeo
FPS = 30                  # Frames por segundo
```

### YOLO (`utils/config.py`)
```python
MODEL_PATH = "yolov8n.pt"        # Modelo (n/s/m/l/x)
CONFIDENCE_THRESHOLD = 0.4       # Confiança mínima
IOU_THRESHOLD = 0.5             # NMS threshold
```

### InfluxDB (`influx_config.py`)
```python
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_ORG = "object-detection-org"
INFLUXDB_BUCKET = "object-detection"
```

## 🔐 Credenciais Padrão

**InfluxDB:**
- **URL**: http://localhost:8086
- **Usuário**: admin
- **Senha**: adminpassword

**Grafana:**
- **URL**: http://localhost:3000
- **Usuário**: admin
- **Senha**: adminpassword

**⚠️ IMPORTANTE**: Altere estas credenciais em produção!

## 🔧 Resolução de Problemas

### ❌ Docker não inicia
```bash
# Reiniciar Docker Desktop
# Limpar sistema
docker system prune -a --volumes
```

### ❌ Câmera não funciona
- Feche outros programas que usam câmera (Teams, Skype, Chrome)
- O sistema tenta automaticamente diferentes backends
- Verifique se a câmera não está fisicamente bloqueada

### ❌ Grafana sem dados
- Aguarde alguns segundos para dados aparecerem
- Verifique se o detector está rodando
- Altere período para "Last 5 minutes"

### ❌ Performance baixa
```python
# Em utils/config.py:
CONFIDENCE_THRESHOLD = 0.6  # Aumentar
SKIP_FRAMES = 4            # Processar menos frames
FRAME_WIDTH = 480          # Reduzir resolução
```

## 🚀 Comandos Úteis

### Docker
```bash
# Status dos serviços
docker compose ps

# Logs
docker compose logs -f

# Reiniciar
docker compose restart

# Parar tudo
docker compose down
```

### URLs de Monitorização
- **InfluxDB**: http://localhost:8086
- **Grafana**: http://localhost:3000
- **Health InfluxDB**: http://localhost:8086/health
- **Health Grafana**: http://localhost:3000/api/health

## 📈 Objetos Detectados

O modelo YOLO pode detectar **80 classes** de objetos:
- **Pessoas** (person)
- **Veículos** (car, truck, bus, motorcycle, bicycle)
- **Animais** (dog, cat, bird, horse, cow)
- **Eletrônicos** (cell phone, laptop, tv, mouse, keyboard)
- **Móveis** (chair, couch, table, bed)
- **Comida** (apple, banana, pizza, cake)
- **E muito mais...**

## 💡 Otimizações Implementadas

### Sistema Anti-Flickering
- **Buffer de detecções** para estabilizar resultados
- **Suavização de confiança** entre frames
- **Tolerância de posição** para objetos em movimento

### Performance
- **Múltiplos backends** de câmera (DirectShow, MSMF)
- **Skip frames** configurável
- **Buffer de câmera** otimizado
- **Threading** para métricas InfluxDB

### Robustez
- **Verificações de None** em todos os métodos
- **Tratamento de exceções** abrangente
- **Reconexão automática** de câmera
- **Fallback** para diferentes backends

## 🎯 Casos de Uso

- **Segurança** - Monitorização de espaços
- **Automação** - Contagem de pessoas/objetos
- **Análise** - Estatísticas de movimento
- **Desenvolvimento** - Teste de algoritmos de CV
- **Educação** - Aprendizado de Computer Vision

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT**.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

---

## 🆘 Suporte

**Se tiver problemas:**
1. Verifique se Docker Desktop está rodando
2. Execute: `docker compose ps` para ver status dos serviços
3. Consulte a seção "Resolução de Problemas" acima
4. Verifique logs: `docker compose logs`

**Desenvolvido com ❤️ usando Python, OpenCV, YOLO, InfluxDB e Grafana**

*Última atualização: Janeiro 2025* 