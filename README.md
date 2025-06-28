Projeto de Deteção de Objetos com YOLO, InfluxDB e Grafana

Este projeto implementa um sistema de deteção de objetos em tempo real utilizando o modelo YOLOv8. Os dados de deteção, como o número de objetos, FPS e tempo de deteção, são enviados para um banco de dados de séries temporais (InfluxDB) e visualizados num dashboard interativo (Grafana).

Funcionalidades

•
Deteção de Objetos em Tempo Real: Utiliza a câmara do seu computador para detetar objetos em tempo real.

•
Registo de Métricas: Regista métricas de desempenho e deteção, como FPS, tempo de deteção, número de objetos, etc.

•
Armazenamento de Dados: Armazena os dados de séries temporais no InfluxDB para análise histórica.

•
Visualização de Dados: Apresenta os dados num dashboard do Grafana, permitindo a monitorização em tempo real.

Pré-requisitos

•
Docker

•
Docker Compose

Instalação e Configuração

1.
Clone o repositório:

2.
Verifique as configurações:

•
docker-compose.yml: Este ficheiro contém a configuração dos serviços (InfluxDB e Grafana). Verifique se as portas e volumes estão configurados de acordo com as suas necessidades.

•
influx_config.py: Contém a configuração para a conexão com o InfluxDB (URL, token, organização, bucket). Certifique-se de que estes valores correspondem à configuração no docker-compose.yml.

•
config.yaml: Contém as configurações da aplicação, como a fonte da câmara e o modelo YOLO a ser utilizado.



Como Executar a Aplicação

1.
Inicie os serviços (InfluxDB e Grafana):

2.
Execute a aplicação de deteção de objetos:

Utilização

•
InfluxDB UI: Aceda a http://localhost:8086 no seu navegador para aceder à interface do InfluxDB. Pode explorar os seus dados, criar queries e gerir os seus buckets.

•
Grafana Dashboard: Aceda a http://localhost:3000 no seu navegador para aceder ao Grafana. O dashboard de deteção de objetos deve ser carregado automaticamente. Se não for, pode importá-lo a partir do ficheiro grafana/provisioning/dashboards/object-detection-dashboard.json.

Estrutura do Projeto

Plain Text


.
├── grafana/                    # Ficheiros de configuração do Grafana
│   └── provisioning/
│       └── dashboards/          # Ficheiros de provisionamento do dashboard
├── utils/                      # Funções de utilidade
├── __pycache__/                # Ficheiros de cache do Python
├── ANTI_FLICKER_README.md      # Documentação sobre anti-flicker
├── camera.py                   # Módulo para gestão da câmara
├── config.yaml                 # Ficheiro de configuração da aplicação
├── dashboard.yml               # Ficheiro de provisionamento do dashboard (alternativo)
├── detector.log                # Log da deteção de objetos
├── display.py                  # Módulo para exibir o vídeo
├── docker-compose.yml          # Ficheiro de configuração do Docker Compose
├── enhanced_detector.py        # Versão melhorada do detetor
├── influx_client.py            # Cliente para enviar dados para o InfluxDB
├── influx_config.py            # Configuração do cliente InfluxDB
├── influxdb.yml                # Ficheiro de provisionamento da fonte de dados do Grafana
├── main.py                     # Ficheiro principal da aplicação (sem InfluxDB)
├── main_with_influx.py         # Ficheiro principal da aplicação (com InfluxDB)
├── object-detection-dashboard.json # Ficheiro JSON do dashboard do Grafana
├── requirements.txt            # Dependências do Python
├── state.py                    # Módulo para gerir o estado da aplicação
├── test_*.py                    # Ficheiros de teste
├── tracking.py                 # Módulo para rastreamento de objetos
├── yolo_detector.py            # Módulo para o detetor YOLO
└── yolov8n.pt                  # Modelo YOLOv8 pré-treinado


