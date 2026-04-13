#!/usr/bin/env python3
"""
Script para testar os endpoints de categorias.

Demonstra como usar a API de categorias profissionais.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def pretty_print(title: str, data: dict):
    """Imprime JSON de forma legível."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_professional_categories():
    """Testa GET /categories/professionals"""
    try:
        response = requests.get(f"{BASE_URL}/categories/professionals")
        pretty_print("📋 Categorias Profissionais (formato objeto)", response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_professional_categories_list():
    """Testa GET /categories/professionals/list"""
    try:
        response = requests.get(f"{BASE_URL}/categories/professionals/list")
        data = response.json()
        pretty_print("📋 Categorias Profissionais (formato lista)", data)
        
        # Contagem
        if data.get('success') and data.get('data'):
            categories = data['data']
            print(f"\n✅ Total de categorias: {len(categories)}")
            print("\nTabela resumida:")
            print(f"{'ID':<20} {'Nome':<20} {'Ícone':<5}")
            print("-" * 50)
            for cat in categories[:5]:
                print(f"{cat['id']:<20} {cat['name']:<20} {cat['icon']:<5}")
            if len(categories) > 5:
                print(f"... e mais {len(categories)-5} categorias")
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_service_types():
    """Testa GET /categories/service-types"""
    try:
        response = requests.get(f"{BASE_URL}/categories/service-types")
        pretty_print("📦 Tipos de Serviço", response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_service_status():
    """Testa GET /categories/service-status"""
    try:
        response = requests.get(f"{BASE_URL}/categories/service-status")
        pretty_print("🔄 Status de Serviço", response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_user_types():
    """Testa GET /categories/user-types"""
    try:
        response = requests.get(f"{BASE_URL}/categories/user-types")
        pretty_print("👥 Tipos de Usuário", response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_all_categories():
    """Testa GET /categories/all"""
    try:
        response = requests.get(f"{BASE_URL}/categories/all")
        data = response.json()
        
        print(f"\n{'='*70}")
        print(f"  🎯 TODAS AS CATEGORIAS (Um único endpoint)")
        print(f"{'='*70}")
        
        if data.get('success'):
            categories_data = data['data']
            print(f"\n✅ Dados carregados com sucesso!")
            print(f"\n📊 Resumo:")
            print(f"  • Categorias profissionais: {len(categories_data.get('professional_categories', []))}")
            print(f"  • Tipos de serviço: {len(categories_data.get('service_types', []))}")
            print(f"  • Status de serviço: {len(categories_data.get('service_status', []))}")
            print(f"  • Tipos de usuário: {len(categories_data.get('user_types', []))}")
            
            print(f"\n✅ Ideal para inicializar a app Flutter na primeira execução!")
        else:
            print("❌ Falha ao carregar categorias")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("  🧪 TESTE DE ENDPOINTS DE CATEGORIAS")
    print("="*70)
    print(f"\n📍 Base URL: {BASE_URL}")
    print("\nExecutando testes...\n")
    
    try:
        # Testar cada endpoint
        test_professional_categories_list()
        test_service_types()
        test_service_status()
        test_user_types()
        test_all_categories()
        
        print("\n" + "="*70)
        print("  ✅ TODOS OS TESTES COMPLETADOS!")
        print("="*70)
        print("\n📚 Documentação: PROFESSIONAL_CATEGORIES.md")
        print("\n💡 Dica: Use /categories/all para inicializar a app Flutter")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor")
        print(f"   Certifique-se de que o servidor está rodando em {BASE_URL}")
        print("\n   Para iniciar o servidor:")
        print("   $ uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
