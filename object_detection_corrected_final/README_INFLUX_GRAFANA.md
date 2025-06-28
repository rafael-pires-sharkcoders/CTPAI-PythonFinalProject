# Detector de Objetos em Tempo Real com InfluxDB e Grafana

Um detector de objetos em tempo real usando **OpenCV** e **YOLO** que identifica objetos através da webcam, com integração completa ao **InfluxDB** para armazenamento de métricas e **Grafana** para visualização em tempo real.

## 🚀 Funcionalidades

### Detecção de Objetos
- **Detecção em tempo real** via webcam usando YOLOv8
- **Caixas delimitadoras** coloridas para cada objeto
- **Labels com nome e confiança** dos objetos
- **Sistema anti-flickering** para estabilizar detecções
- **Contador de FPS** em tempo real
- **Contador de objetos** detectados
- **Controles de teclado** (pausar/despausar, tela cheia, etc.)

### Monitorização e Métricas
- **Integração com InfluxDB** para armazenamento de métricas
- **Dashboard Grafana** para visualização em tempo real
- **Métricas coletadas**:
  - FPS (Frames por segundo)
  - Número de objetos detectados por frame
  - Tempo de detecção por frame
  - Confiança média, máxima e mínima das detecções
  - Contagem de objetos por classe
  - Duração da sessão
  - Frames processados

### Visualização
- **Dashboard interativo** no Grafana
- **Gráficos em tempo real** de todas as métricas
- **Gráfico de pizza** com distribuição de objetos por classe
- **Atualização automática** a cada 5 segundos
- **Histórico** configurável (últimos 5 minutos por padrão)

## 🛠 Tecnologias Utilizadas

- **Python 3.8+** - Linguagem principal
- **OpenCV** - Captura de vídeo e processamento de imagem
- **YOLOv8** (Ultralytics) - Modelo de detecção de objetos
- **InfluxDB 2.7** - Base de dados de séries temporais
- **Grafana 10.2** - Plataforma de visualização
- **Docker & Docker Compose** - Containerização dos serviços
- **NumPy** - Processamento numérico
- **PyTorch** - Backend do YOLO

## 📁 Estrutura do Projeto

```
detector_objetos_influx/
├── main_with_influx.py        # Script principal com InfluxDB
├── main.py                    # Script original (sem InfluxDB)
├── yolo_detector.py           # Lógica de detecção YOLO
├── config.py                  # Configurações gerais
├── draw.py                    # Funções de desenho
├── influx_config.py           # Configurações do InfluxDB
├── influx_client.py           # Cliente InfluxDB
├── docker-compose.yml         # Configuração dos serviços
├── requirements.txt           # Dependências Python
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── influxdb.yml   # Configuração da fonte de dados
│       └── dashboards/
│           ├── dashboard.yml  # Configuração dos dashboards
│           └── object-detection-dashboard.json
└── README_INFLUX_GRAFANA.md   # Esta documentação
```

## 🔧 Instalação e Configuração

### Pré-requisitos

1. **Python 3.8+**
2. **Docker** e **Docker Compose**
3. **Webcam** conectada ao computador

### Passo 1: Clonar/Baixar o projeto

```bash
# Se for um repositório Git
git clone <url-do-repositorio>
cd detector_objetos_influx

# Ou simplesmente baixar os arquivos para uma pasta
```

### Passo 2: Instalar dependências Python

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Passo 3: Iniciar serviços InfluxDB e Grafana

```batch
start_services.bat
```

**Nota**: No Windows, certifique-se de que o Docker Desktop está em execução e que o Docker Compose (ou `docker compose` V2) está disponível no seu PATH.


### Passo 4: Verificar serviços

Aguarde alguns segundos e verifique se os serviços estão funcionando:

- **InfluxDB**: http://localhost:8086
- **Grafana**: http://localhost:3000

### Passo 5: Executar o detector

```bash
# Versão com InfluxDB (recomendada)
python main_with_influx.py

# Versão original (sem métricas)
python main.py
```

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| `Q` ou `ESC` | Sair do programa |
| `Espaço` | Pausar/Despausar detecção |
| `R` | Resetar estatísticas |
| `P` | Mostrar/Ocultar info de performance |
| `S` | Salvar screenshot |
| `F` | Alternar tela cheia |
| `M` | Habilitar/Desabilitar métricas InfluxDB |

## 📊 Dashboard Grafana

### Acesso

1. Abra o navegador em: http://localhost:3000
2. Faça login com:
   - **Usuário**: admin
   - **Senha**: adminpassword
3. O dashboard "Object Detection Dashboard" será carregado automaticamente

### Painéis Disponíveis

1. **FPS em Tempo Real**
   - Gráfico de linha mostrando os frames por segundo
   - Atualização contínua
   - Útil para monitorizar performance

2. **Objetos Detectados**
   - Número total de objetos detectados por frame
   - Permite identificar picos de atividade
   - Gráfico de linha temporal

3. **Tempo de Detecção (ms)**
   - Tempo necessário para processar cada frame
   - Importante para otimização de performance
   - Mostra latência do sistema

4. **Confiança Média (%)**
   - Confiança média das detecções
   - Indica qualidade das detecções
   - Valores mais altos = detecções mais confiáveis

5. **Distribuição de Objetos por Classe**
   - Gráfico de pizza mostrando tipos de objetos detectados
   - Atualização baseada no período selecionado
   - Útil para análise de padrões

### Personalização

- **Período de tempo**: Altere no canto superior direito (padrão: últimos 5 minutos)
- **Atualização**: Configurado para 5 segundos (modificável)
- **Zoom**: Clique e arraste nos gráficos para fazer zoom
- **Filtros**: Use os filtros do Grafana para análises específicas

## ⚙️ Configurações

### Configurações da Câmera (config.py)

```python
CAMERA_INDEX = 0          # 0 = câmera padrão, 1 = câmera externa
FRAME_WIDTH = 640         # Largura do vídeo
FRAME_HEIGHT = 480        # Altura do vídeo
FPS = 30                  # Frames por segundo
```

### Configurações do YOLO (config.py)

```python
MODEL_PATH = "yolov8n.pt"        # Modelo (n=nano, s=small, m=medium, l=large, x=extra)
CONFIDENCE_THRESHOLD = 0.4       # Confiança mínima (0.0 a 1.0)
IOU_THRESHOLD = 0.5             # Threshold para NMS
```

### Configurações do InfluxDB (influx_config.py)

```python
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "rgR64HQYPQ6Bd6Jq0aem9ZVX_VDJj1iLOsJJwS-3bt-BSnd4EntBb6fnYWVMeZHZKt_JXwoHhRDO96ps7Spi1w=="
INFLUXDB_ORG = "object-detection-org"
INFLUXDB_BUCKET = "object-detection"
```

### Configurações de Métricas

```python
METRICS_INTERVAL = 1.0    # Intervalo de envio de métricas (segundos)
BATCH_SIZE = 100          # Número de pontos por lote
```

## 🔍 Métricas Coletadas

### Métricas Principais (object_detection_metrics)

| Campo | Descrição | Unidade |
|-------|-----------|---------|
| `total_objects` | Número de objetos detectados no frame | count |
| `fps` | Frames por segundo atual | fps |
| `detection_time_ms` | Tempo de detecção por frame | ms |
| `frame_width` | Largura do frame | pixels |
| `frame_height` | Altura do frame | pixels |
| `confidence_avg` | Confiança média das detecções | 0.0-1.0 |
| `confidence_max` | Confiança máxima das detecções | 0.0-1.0 |
| `confidence_min` | Confiança mínima das detecções | 0.0-1.0 |
| `frames_processed` | Total de frames processados | count |
| `session_duration` | Duração da sessão atual | seconds |

### Métricas por Classe (object_counts)

| Campo | Descrição | Tags |
|-------|-----------|------|
| `count` | Número de objetos da classe | `class`: nome da classe |

### Tags Padrão

- `device`: "webcam"
- `model`: "yolov8n"
- `location`: "default"

## 🐛 Solução de Problemas

### Câmera não abre

```bash
# Verificar câmeras disponíveis
ls /dev/video*

# Testar câmera
python test_camera.py
```

**Soluções**:
- Certifique-se que a câmera não está sendo usada por outro programa
- Tente alterar `CAMERA_INDEX` para 1 ou 2### InfluxDB não conecta

**Verificar serviços**:
```batch
docker compose ps
```

**Logs do InfluxDB**:
```batch
docker compose logs influxdb
```

**Soluções**:
- Aguarde alguns segundos após iniciar os serviços
- Verifique se as portas 8086 e 3000 não estão ocupadas
- Reinicie os serviços: `docker compose restart`

**Nota**: Se `docker compose` não funcionar, tente `docker-compose`.


### Grafana não carrega dashboard

**Verificar logs**:
```batch
docker compose logs grafana
```

**Soluções**:
- Aguarde o Grafana terminar de inicializar
- Verifique se o arquivo de dashboard está correto
- Acesse manualmente: http://localhost:3000

### Performance baixa

**Otimizações**:
- Use modelo menor: `yolov8n.pt` (mais rápido)
- Reduza resolução em `config.py`
- Aumente `CONFIDENCE_THRESHOLD`
- Desabilite métricas temporariamente (tecla `M`)

### Erro de dependências

```bash
# Instalar dependências uma por uma
pip install opencv-python
pip install ultralytics
pip install influxdb-client
pip install numpy
pip install pillow
```

## 📈 Performance

### Modelos YOLO Disponíveis

| Modelo | Velocidade | Precisão | Tamanho | Recomendação |
|--------|------------|----------|---------|--------------|
| YOLOv8n | ⚡⚡⚡ | ⭐⭐ | ~6MB | Tempo real |
| YOLOv8s | ⚡⚡ | ⭐⭐⭐ | ~22MB | Balanceado |
| YOLOv8m | ⚡ | ⭐⭐⭐⭐ | ~52MB | Precisão |
| YOLOv8l | 🐌 | ⭐⭐⭐⭐⭐ | ~87MB | Máxima precisão |

### Benchmarks Típicos

- **YOLOv8n**: 15-30 FPS (CPU), 60+ FPS (GPU)
- **Resolução 640x480**: Recomendada para tempo real
- **Latência InfluxDB**: < 10ms por envio
- **Uso de memória**: 200-500MB (dependendo do modelo)

## 🔒 Segurança

### Credenciais Padrão

**⚠️ IMPORTANTE**: Altere as credenciais padrão em produção!

**InfluxDB**:
- Token: `rgR64HQYPQ6Bd6Jq0aem9ZVX_VDJj1iLOsJJwS-3bt-BSnd4EntBb6fnYWVMeZHZKt_JXwoHhRDO96ps7Spi1w==`
- Usuário: `admin`
- Senha: `adminpassword`

**Grafana**:
- Usuário: `admin`
- Senha: `adminpassword`

### Alterando Credenciais

1. **InfluxDB**: Edite `docker-compose.yml` e `influx_config.py`
2. **Grafana**: Edite `docker-compose.yml`
3. **Reinicie os serviços**: `docker-compose down && docker-compose up -d`

## 🚀 Uso Avançado

### Executar sem Docker

Se preferir instalar InfluxDB e Grafana localmente:

1. Instale InfluxDB 2.7+
2. Instale Grafana 10.2+
3. Configure manualmente as fontes de dados
4. Importe o dashboard JSON

### Integração com Outros Sistemas

O cliente InfluxDB pode ser facilmente integrado com:
- **Alertas**: Configure alertas no Grafana
- **APIs**: Exponha métricas via API REST
- **Relatórios**: Gere relatórios automáticos
- **ML**: Use dados para treinar modelos

### Personalização de Métricas

Adicione novas métricas editando `main_with_influx.py`:

```python
def collect_custom_metrics(self, detections):
    # Suas métricas personalizadas aqui
    custom_metrics = {
        'custom_field': custom_value
    }
    return custom_metrics
```

## 📝 Logs e Debugging

### Logs da Aplicação

Os logs são exibidos no console durante a execução:
- ✅ Sucessos em verde
- ⚠️ Avisos em amarelo  
- ❌ Erros em vermelho

### Logs dos Serviços

```batch
# Logs do InfluxDB
docker compose logs -f influxdb

# Logs do Grafana
docker compose logs -f grafana

# Todos os logs
docker compose logs -f
```

**Nota**: Se `docker compose` não funcionar, tente `docker-compose`.


### Debug Mode

Para debug detalhado, edite `main_with_influx.py`:

```python
# Alterar nível de logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Áreas para Contribuição

- **Novos modelos YOLO**: Suporte a outros modelos
- **Métricas adicionais**: Novas métricas de performance
- **Dashboards**: Novos dashboards especializados
- **Otimizações**: Melhorias de performance
- **Documentação**: Melhorias na documentação
- **Testes**: Testes automatizados

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Ultralytics** pelo excelente framework YOLOv8
- **OpenCV** pela biblioteca de visão computacional
- **InfluxDB** pela base de dados de séries temporais
- **Grafana** pela plataforma de visualização
- **Docker** pela containerização

## 📞 Suporte

Se tiver problemas ou dúvidas:

1. **Verifique a documentação** acima
2. **Consulte os logs** dos serviços
3. **Teste com configurações padrão**
4. **Abra uma issue** no repositório

---

**Desenvolvido com ❤️ usando Python, OpenCV, YOLO, InfluxDB e Grafana**

*Última atualização: Dezembro 2024*

