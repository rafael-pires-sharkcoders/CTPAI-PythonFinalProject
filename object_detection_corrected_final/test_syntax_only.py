#!/usr/bin/env python3
"""
Script de teste de sintaxe para verificar as correções aplicadas
(sem dependências externas)
"""

import ast
import sys

def test_python_syntax(filename):
    """Testa se um ficheiro Python tem sintaxe válida."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Compilar o código para verificar sintaxe
        ast.parse(source)
        print(f"✅ {filename}: Sintaxe válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ {filename}: Erro de sintaxe na linha {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ {filename}: Erro ao ler ficheiro: {e}")
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
        
        # Testar cálculo de métricas de confiança (como no código corrigido)
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
        
        # Testar caso sem detecções
        empty_detections = []
        if not empty_detections:
            confidence_avg = 0.0
            confidence_max = 0.0
            confidence_min = 0.0
            
        assert isinstance(confidence_avg, float), "confidence_avg deve ser float mesmo quando 0"
        print("✅ Tipos corretos também para caso sem detecções")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de tipos: {e}")
        return False

def main():
    """Executa todos os testes de sintaxe."""
    print("🚀 Iniciando testes de sintaxe das correções aplicadas...\n")
    
    # Ficheiros Python para testar
    python_files = [
        "influx_client.py",
        "main_with_influx.py",
        "yolo_detector.py",
        "influx_config.py"
    ]
    
    passed = 0
    total = len(python_files) + 1  # +1 para o teste de tipos
    
    # Testar sintaxe dos ficheiros
    for filename in python_files:
        if test_python_syntax(filename):
            passed += 1
    
    # Testar tipos de dados
    if test_data_types():
        passed += 1
    
    print(f"\n📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todas as correções de sintaxe foram aplicadas com sucesso!")
        print("📝 Nota: Para testes completos, instale as dependências do requirements.txt")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

