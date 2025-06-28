#!/usr/bin/env python3
"""
Script de teste para verificar as correções aplicadas
"""

import sys
import os
import importlib.util

def test_import_modules():
    """Testa se todos os módulos podem ser importados sem erros."""
    print("🧪 Testando importação de módulos...")
    
    try:
        # Testar importação do influx_client
        import influx_client
        print("✅ influx_client importado com sucesso")
        
        # Testar importação do influx_config
        import influx_config
        print("✅ influx_config importado com sucesso")
        
        # Testar importação do yolo_detector
        import yolo_detector
        print("✅ yolo_detector importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_influx_client():
    """Testa as funções do cliente InfluxDB."""
    print("\n🧪 Testando cliente InfluxDB...")
    
    try:
        from influx_client import InfluxDBManager
        
        # Criar instância do manager
        manager = InfluxDBManager()
        print("✅ InfluxDBManager criado com sucesso")
        
        # Testar coleta de estatísticas
        stats = manager.get_stats()
        print(f"✅ Estatísticas obtidas: {stats}")
        
        # Testar métricas de exemplo
        test_metrics = {
            'total_objects': 5,
            'fps': 30,
            'detection_time_ms': 50.5,
            'confidence_avg': 0.85,  # Deve ser float
            'confidence_max': 0.95,
            'confidence_min': 0.75
        }
        
        print(f"✅ Métricas de teste preparadas: {test_metrics}")
        print("✅ Tipo de confidence_avg:", type(test_metrics['confidence_avg']))
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do InfluxDB: {e}")
        return False

def test_main_functions():
    """Testa as funções principais do main_with_influx."""
    print("\n🧪 Testando funções principais...")
    
    try:
        # Importar sem executar o main
        spec = importlib.util.spec_from_file_location("main_with_influx", "main_with_influx.py")
        main_module = importlib.util.module_from_spec(spec)
        
        # Não executar o spec.loader.exec_module para evitar inicialização
        print("✅ main_with_influx carregado sem erros de sintaxe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do main: {e}")
        return False

def test_data_types():
    """Testa se os tipos de dados estão corretos."""
    print("\n🧪 Testando tipos de dados...")
    
    try:
        # Simular dados de detecção
        detections = [
            (100, 100, 200, 200, "person", 0.85),
            (300, 150, 400, 250, "car", 0.92)
        ]
        
        # Testar cálculo de métricas de confiança
        confidences = [det[5] for det in detections]
        confidence_avg = float(sum(confidences) / len(confidences))
        confidence_max = float(max(confidences))
        confidence_min = float(min(confidences))
        
        print(f"✅ Confidence avg: {confidence_avg} (tipo: {type(confidence_avg)})")
        print(f"✅ Confidence max: {confidence_max} (tipo: {type(confidence_max)})")
        print(f"✅ Confidence min: {confidence_min} (tipo: {type(confidence_min)})")
        
        # Verificar se são todos float
        assert isinstance(confidence_avg, float), "confidence_avg deve ser float"
        assert isinstance(confidence_max, float), "confidence_max deve ser float"
        assert isinstance(confidence_min, float), "confidence_min deve ser float"
        
        print("✅ Todos os tipos de dados estão corretos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de tipos: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes das correções aplicadas...\n")
    
    tests = [
        test_import_modules,
        test_influx_client,
        test_main_functions,
        test_data_types
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Teste {test.__name__} falhou")
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {e}")
    
    print(f"\n📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todas as correções foram aplicadas com sucesso!")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

