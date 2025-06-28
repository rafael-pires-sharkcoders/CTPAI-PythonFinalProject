"""
Cliente InfluxDB para envio de métricas do detector de objetos
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influx_config import (
    INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET,
    MEASUREMENT_NAME, DEFAULT_TAGS, BATCH_SIZE, FLUSH_INTERVAL, TIMEOUT
)

class InfluxDBManager:
    """Gerenciador para comunicação com InfluxDB."""
    
    def __init__(self):
        """Inicializa o cliente InfluxDB."""
        self.client = None
        self.write_api = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
        # Estatísticas
        self.points_sent = 0
        self.errors_count = 0
        self.last_send_time = None
        
    def connect(self) -> bool:
        """
        Conecta ao InfluxDB.
        
        Returns:
            bool: True se conectado com sucesso, False caso contrário
        """
        try:
            self.client = InfluxDBClient(
                url=INFLUXDB_URL,
                token=INFLUXDB_TOKEN,
                org=INFLUXDB_ORG,
                timeout=TIMEOUT
            )
            
            # Testar conexão
            health = self.client.health()
            if health.status == "pass":
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.connected = True
                self.logger.info(f"Conectado ao InfluxDB: {INFLUXDB_URL}")
                return True
            else:
                self.logger.error(f"InfluxDB não está saudável: {health.message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao InfluxDB: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconecta do InfluxDB."""
        try:
            if self.write_api:
                self.write_api.close()
            if self.client:
                self.client.close()
            self.connected = False
            self.logger.info("Desconectado do InfluxDB")
        except Exception as e:
            self.logger.error(f"Erro ao desconectar do InfluxDB: {e}")
    
    def send_detection_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Envia métricas de detecção para o InfluxDB.
        
        Args:
            metrics: Dicionário com as métricas a serem enviadas
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            # Criar ponto de dados
            point = Point(MEASUREMENT_NAME)
            
            # Adicionar tags padrão
            for tag_key, tag_value in DEFAULT_TAGS.items():
                point = point.tag(tag_key, tag_value)
            
            # Adicionar timestamp
            point = point.time(datetime.utcnow(), WritePrecision.MS)
            
            # Adicionar campos de métricas
            for field_name, field_value in metrics.items():
                if field_value is not None:
                    # Converter confidence_avg para float explicitamente
                    if field_name == 'confidence_avg' and isinstance(field_value, (int, float)):
                        point = point.field(field_name, float(field_value))
                    else:
                        point = point.field(field_name, field_value)
            
            # Enviar ponto
            self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
            
            # Atualizar estatísticas
            self.points_sent += 1
            self.last_send_time = time.time()
            
            return True
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(f"Erro ao enviar métricas para InfluxDB: {e}")
            
            # Tentar reconectar em caso de erro de conexão
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                self.connected = False
            
            return False
    
    def send_object_counts(self, object_counts: Dict[str, int]) -> bool:
        """
        Envia contagem de objetos por classe para o InfluxDB.
        
        Args:
            object_counts: Dicionário com contagem por classe de objeto
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            points = []
            timestamp = datetime.utcnow()
            
            for class_name, count in object_counts.items():
                if count > 0:  # Só enviar se houver objetos detectados
                    point = (Point("object_counts")
                            .tag("class", class_name)
                            .tag("device", DEFAULT_TAGS["device"])
                            .tag("model", DEFAULT_TAGS["model"])
                            .field("count", count)
                            .time(timestamp, WritePrecision.MS))
                    points.append(point)
            
            if points:
                self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
                self.points_sent += len(points)
                self.last_send_time = time.time()
            
            return True
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(f"Erro ao enviar contagem de objetos para InfluxDB: {e}")
            
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                self.connected = False
            
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cliente InfluxDB.
        
        Returns:
            Dict com estatísticas do cliente
        """
        return {
            "connected": self.connected,
            "points_sent": self.points_sent,
            "errors_count": self.errors_count,
            "last_send_time": self.last_send_time,
            "success_rate": (self.points_sent / (self.points_sent + self.errors_count)) * 100 
                           if (self.points_sent + self.errors_count) > 0 else 0
        }
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o InfluxDB.
        
        Returns:
            bool: True se a conexão estiver funcionando
        """
        try:
            if not self.client:
                return self.connect()
            
            health = self.client.health()
            return health.status == "pass"
            
        except Exception as e:
            self.logger.error(f"Erro ao testar conexão InfluxDB: {e}")
            return False

# Instância global do gerenciador InfluxDB
influx_manager = InfluxDBManager()



