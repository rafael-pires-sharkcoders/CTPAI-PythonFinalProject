# 🚀 Guia Rápido - Detector com InfluxDB e Grafana

## ⚡ Início Rápido (5 minutos)

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar serviços
```batch
start_services.bat
```

### 3. Testar integração
```bash
python test_integration.py
```

### 4. Executar detector
```bash
python main_with_influx.py
```

### 5. Abrir dashboard
Acesse: http://localhost:3000
- **Usuário**: admin
- **Senha**: adminpassword

## 🎮 Controles Principais

- **Q**: Sair
- **Espaço**: Pausar/Despausar
- **M**: Habilitar/Desabilitar métricas
- **F**: Tela cheia

## 📊 URLs Importantes

- **Grafana**: http://localhost:3000
- **InfluxDB**: http://localhost:8086

## 🔧 Solução Rápida de Problemas

### Serviços não iniciam
```bash
docker-compose down
docker-compose up -d
```

### Câmera não funciona
Edite `config.py`:
```python
CAMERA_INDEX = 1  # Tente 0, 1, 2...
```

### Performance baixa
Edite `config.py`:
```python
MODEL_PATH = "yolov8n.pt"  # Modelo mais rápido
CONFIDENCE_THRESHOLD = 0.6  # Menos detecções
```

## 📁 Arquivos Principais

- `main_with_influx.py` - Detector com métricas
- `config.py` - Configurações
- `docker-compose.yml` - Serviços
- `test_integration.py` - Teste da integração

## 🆘 Precisa de Ajuda?

1. Leia o `README_INFLUX_GRAFANA.md` completo
2. Execute `python test_integration.py`
3. Verifique logs: `docker-compose logs`

