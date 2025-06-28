#!/usr/bin/env python3
"""
Script de teste para verificar a integração InfluxDB + Grafana
"""

import time
import logging
import sys
from influx_client import influx_manager
from influx_config import YOLO_CLASSES

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_influxdb_connection():
    """Testa a conexão com o InfluxDB."""
    print("🔍 Testando conexão com InfluxDB...")
    
    try:
        if influx_manager.connect():
            print("✅ Conexão com InfluxDB estabelecida com sucesso!")
            return True
        else:
            print("❌ Falha ao conectar com InfluxDB")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com InfluxDB: {e}")
        return False

def test_send_sample_metrics():
    """Envia métricas de exemplo para testar o envio."""
    print("📊 Enviando métricas de exemplo...")
    
    try:
        # Métricas de exemplo
        sample_metrics = {
            'total_objects': 5,
            'fps': 25.5,
            'detection_time_ms': 45.2,
            'frame_width': 640,
            'frame_height': 480,
            'confidence_avg': 0.85,
            'confidence_max': 0.95,
            'confidence_min': 0.75,
            'frames_processed': 100,
            'session_duration': 120.5
        }
        
        success = influx_manager.send_detection_metrics(sample_metrics)
        if success:
            print("✅ Métricas principais enviadas com sucesso!")
        else:
            print("❌ Falha ao enviar métricas principais")
            return False
        
        # Contagem de objetos de exemplo
        sample_object_counts = {
            'person': 2,
            'car': 1,
            'bicycle': 1,
            'dog': 1
        }
        
        success = influx_manager.send_object_counts(sample_object_counts)
        if success:
            print("✅ Contagem de objetos enviada com sucesso!")
        else:
            print("❌ Falha ao enviar contagem de objetos")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar métricas: {e}")
        return False

def test_continuous_metrics(duration=30):
    """Envia métricas continuamente por um período para testar o dashboard."""
    print(f"🔄 Enviando métricas continuamente por {duration} segundos...")
    print("   (Use Ctrl+C para parar)")
    
    try:
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            frame_count += 1
            
            # Simular métricas variáveis
            import random
            
            metrics = {
                'total_objects': random.randint(0, 10),
                'fps': random.uniform(20.0, 30.0),
                'detection_time_ms': random.uniform(30.0, 60.0),
                'frame_width': 640,
                'frame_height': 480,
                'confidence_avg': random.uniform(0.7, 0.9),
                'confidence_max': random.uniform(0.9, 1.0),
                'confidence_min': random.uniform(0.5, 0.7),
                'frames_processed': frame_count,
                'session_duration': time.time() - start_time
            }
            
            # Simular contagem de objetos
            classes_detected = random.sample(YOLO_CLASSES[:10], random.randint(1, 5))
            object_counts = {cls: random.randint(1, 3) for cls in classes_detected}
            
            # Enviar métricas
            influx_manager.send_detection_metrics(metrics)
            influx_manager.send_object_counts(object_counts)
            
            # Mostrar progresso
            if frame_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"   📈 {frame_count} frames enviados ({elapsed:.1f}s)")
            
            time.sleep(1)  # Enviar a cada segundo
        
        print("✅ Teste de métricas contínuas concluído!")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
        return True
    except Exception as e:
        print(f"❌ Erro durante teste contínuo: {e}")
        return False

def test_influxdb_stats():
    """Mostra estatísticas do cliente InfluxDB."""
    print("📊 Estatísticas do cliente InfluxDB:")
    
    try:
        stats = influx_manager.get_stats()
        print(f"   Conectado: {stats['connected']}")
        print(f"   Pontos enviados: {stats['points_sent']}")
        print(f"   Erros: {stats['errors_count']}")
        print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
        
        if stats['last_send_time']:
            last_send = time.time() - stats['last_send_time']
            print(f"   Último envio: {last_send:.1f}s atrás")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return False

def test_grafana_access():
    """Verifica se o Grafana está acessível."""
    print("🌐 Testando acesso ao Grafana...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Grafana está acessível em http://localhost:3000")
            print("   👤 Login: admin / adminpassword")
            return True
        else:
            print(f"❌ Grafana retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao Grafana")
        print("   💡 Verifique se o Docker Compose está rodando")
        return False
    except ImportError:
        print("⚠️  Biblioteca 'requests' não encontrada, pulando teste do Grafana")
        return True
    except Exception as e:
        print(f"❌ Erro ao testar Grafana: {e}")
        return False

def main():
    """Função principal do teste."""
    print("🧪 TESTE DE INTEGRAÇÃO INFLUXDB + GRAFANA")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Teste 1: Conexão InfluxDB
    if test_influxdb_connection():
        tests_passed += 1
    
    print()
    
    # Teste 2: Envio de métricas
    if test_send_sample_metrics():
        tests_passed += 1
    
    print()
    
    # Teste 3: Estatísticas
    if test_influxdb_stats():
        tests_passed += 1
    
    print()
    
    # Teste 4: Acesso Grafana
    if test_grafana_access():
        tests_passed += 1
    
    print()
    
    # Teste 5: Métricas contínuas (opcional)
    print("🔄 Teste de métricas contínuas (opcional)")
    response = input("Deseja executar teste de métricas contínuas? (s/N): ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        duration = input("Duração em segundos (padrão: 30): ")
        try:
            duration = int(duration) if duration else 30
        except ValueError:
            duration = 30
        
        if test_continuous_metrics(duration):
            tests_passed += 1
    else:
        print("⏭️  Pulando teste de métricas contínuas")
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"📋 RESULTADO: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("🎉 Todos os testes passaram! Integração funcionando corretamente.")
        print()
        print("🚀 Próximos passos:")
        print("   1. Execute: python main_with_influx.py")
        print("   2. Abra o Grafana: http://localhost:3000")
        print("   3. Visualize as métricas em tempo real!")
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
        print()
        print("🔧 Soluções:")
        print("   1. Verifique se o Docker Compose está rodando")
        print("   2. Execute: docker-compose ps")
        print("   3. Verifique os logs: docker-compose logs")
    
    # Desconectar
    influx_manager.disconnect()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        influx_manager.disconnect()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal durante teste: {e}")
        influx_manager.disconnect()
        sys.exit(1)

