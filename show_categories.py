#!/usr/bin/env python3
"""
Sumário visual das categorias de profissionais disponíveis.
"""

from app.core.constants import PROFESSIONAL_CATEGORIES


def main():
    print("\n" + "="*80)
    print("  📋 CATEGORIAS DE PROFISSIONAIS DISPONÍVEIS - SEUSERVIÇO API")
    print("="*80)
    
    print(f"\n✅ Total de categorias: {len(PROFESSIONAL_CATEGORIES)}\n")
    
    # Ordenar alfabeticamente por nome
    sorted_categories = sorted(
        PROFESSIONAL_CATEGORIES.items(),
        key=lambda x: x[1]['name']
    )
    
    # Exibir em formato de tabela
    print(f"{'#':<3} {'ID':<20} {'Nome':<20} {'Ícone':<8} {'Descrição':<35}")
    print("-" * 95)
    
    for idx, (cat_id, cat_data) in enumerate(sorted_categories, 1):
        desc = cat_data['description'][:33] + ".." if len(cat_data['description']) > 35 else cat_data['description']
        print(f"{idx:<3} {cat_id:<20} {cat_data['name']:<20} {cat_data['icon']:<8} {desc:<35}")
    
    print("\n" + "="*80)
    print("  🔗 ENDPOINTS DISPONÍVEIS")
    print("="*80)
    
    endpoints = [
        ("/api/v1/categories/professionals", "Retorna categorias em formato objeto/dicionário"),
        ("/api/v1/categories/professionals/list", "Retorna categorias em formato lista (ideal para UI)"),
        ("/api/v1/categories/service-types", "Retorna tipos de serviço (pontual, recorrente, etc)"),
        ("/api/v1/categories/service-status", "Retorna status possíveis (pendente, aceito, etc)"),
        ("/api/v1/categories/user-types", "Retorna tipos de usuário (client, professional, admin)"),
        ("/api/v1/categories/all", "⭐ Retorna tudo de uma vez - IDEAL PARA INICIALIZAR APP"),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n  GET {endpoint}")
        print(f"      → {description}")
    
    print("\n" + "="*80)
    print("  📱 COMO USAR NO FLUTTER")
    print("="*80)
    
    example_code = """
Exemplo: Carregar categorias na inicialização
================================================

import 'package:http/http.dart' as http;
import 'dart:convert';

class CategoryService {
  static const String API_URL = 'http://sua-api.com/api/v1';
  
  // Carregar tudo de uma vez (recomendado)
  static Future<Map<String, dynamic>> loadAllCategories() async {
    final response = await http.get(
      Uri.parse('$API_URL/categories/all'),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success']) {
        return data['data'];  // Contém tudo
      }
    }
    throw Exception('Falha ao carregar categorias');
  }
  
  // Ou carregar só profissionais
  static Future<List> getProfessionalCategories() async {
    final response = await http.get(
      Uri.parse('$API_URL/categories/professionals/list'),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success']) {
        return data['data'];
      }
    }
    throw Exception('Falha ao carregar categorias');
  }
}

// Na tela de registro do profissional:
Dropdown(
  items: categories
    .map((cat) => DropdownMenuItem(
      value: cat['id'],
      child: Row(
        children: [
          Text(cat['icon']),
          SizedBox(width: 8),
          Text(cat['name']),
        ],
      ),
    ))
    .toList(),
  onChanged: (value) {
    setState(() => selectedCategory = value);
  },
)
"""
    
    print(example_code)
    
    print("="*80)
    print("  ✨ CARACTERÍSTICAS")
    print("="*80)
    
    features = [
        "✅ 25 categorias diferentes",
        "✅ Cada categoria tem ícone emoji",
        "✅ Descrições claras em português",
        "✅ Padrão de resposta consistente",
        "✅ Pronto para produção",
        "✅ Escalável para adicionar mais",
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n" + "="*80)
    print(f"  ✅ API PRODUCTION-READY")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
