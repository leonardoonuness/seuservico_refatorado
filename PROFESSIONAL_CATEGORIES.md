# 📋 Categorias de Profissionais Disponíveis

## 📊 Resumo

O sistema **SeuServiço** possui **25 categorias** de profissionais pré-definidas, cada uma com:
- **ID**: Identificador único (slug)
- **Nome**: Nome em português
- **Ícone**: Emoji representativo
- **Descrição**: O que o profissional oferece

---

## 🔗 Endpoints de Categorias

### 1. **Listar todas as categorias (formato objeto)**
```http
GET /api/v1/categories/professionals
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "encanador": {
      "name": "Encanador",
      "icon": "🔧",
      "description": "Serviços de encanamento e hidráulica"
    },
    "eletricista": {
      "name": "Eletricista",
      "icon": "⚡",
      "description": "Serviços elétricos e instalações"
    },
    ...
  },
  "count": 25,
  "message": "Encontradas 25 categorias de profissionais"
}
```

---

### 2. **Listar categorias (formato lista)**
```http
GET /api/v1/categories/professionals/list
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "encanador",
      "name": "Encanador",
      "icon": "🔧",
      "description": "Serviços de encanamento e hidráulica"
    },
    {
      "id": "eletricista",
      "name": "Eletricista",
      "icon": "⚡",
      "description": "Serviços elétricos e instalações"
    },
    ...
  ],
  "count": 25,
  "message": "Encontradas 25 categorias"
}
```

---

### 3. **Listar tipos de serviço**
```http
GET /api/v1/categories/service-types
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    { "id": "pontual", "name": "Serviço Pontual" },
    { "id": "recorrente", "name": "Serviço Recorrente" },
    { "id": "contrato", "name": "Contrato" },
    { "id": "consultoria", "name": "Consultoria" }
  ],
  "count": 4,
  "message": "Encontrados 4 tipos de serviço"
}
```

---

### 4. **Listar status de serviço**
```http
GET /api/v1/categories/service-status
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    { "id": "pendente", "name": "Aguardando Aceitação" },
    { "id": "aceito", "name": "Aceito" },
    { "id": "iniciado", "name": "Em Andamento" },
    { "id": "concluido", "name": "Concluído" },
    { "id": "cancelado", "name": "Cancelado" },
    { "id": "disputado", "name": "Em Disputa" }
  ],
  "count": 6,
  "message": "Encontrados 6 status de serviço"
}
```

---

### 5. **Listar tudo de uma vez (ideal para inicializar a app)**
```http
GET /api/v1/categories/all
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "professional_categories": [
      {
        "id": "encanador",
        "name": "Encanador",
        "icon": "🔧",
        "description": "Serviços de encanamento e hidráulica"
      },
      ...
    ],
    "service_types": [
      { "id": "pontual", "name": "Serviço Pontual" },
      ...
    ],
    "service_status": [
      { "id": "pendente", "name": "Aguardando Aceitação" },
      ...
    ],
    "user_types": [
      { "id": "client", "name": "Cliente" },
      { "id": "professional", "name": "Profissional" },
      { "id": "admin", "name": "Administrador" }
    ]
  },
  "message": "Categorias e tipos carregados com sucesso"
}
```

---

## 📋 Lista Completa de Categorias

| ID | Nome | Ícone | Descrição |
|---|---|---|---|
| `encanador` | Encanador | 🔧 | Serviços de encanamento e hidráulica |
| `eletricista` | Eletricista | ⚡ | Serviços elétricos e instalações |
| `pedreiro` | Pedreiro | 🧱 | Construção e alvenaria |
| `pintor` | Pintor | 🎨 | Pintura de ambientes |
| `marceneiro` | Marceneiro | 🪵 | Trabalhos em madeira |
| `jardineiro` | Jardineiro | 🌱 | Jardinagem e paisagismo |
| `limpeza` | Limpeza | 🧹 | Serviços de limpeza |
| `manutencao` | Manutenção | 🔨 | Manutenção predial |
| `reparo_movel` | Reparo de Móvel | 🛋️ | Conserto e restauração de móveis |
| `vidraceiro` | Vidraceiro | 🪟 | Serviços com vidro |
| `mecanico` | Mecânico | 🔧 | Serviços automotivos |
| `informatica` | Informática | 💻 | Suporte técnico e informática |
| `fotografia` | Fotografia | 📸 | Serviços fotográficos |
| `aula_particular` | Aula Particular | 📚 | Tutoria e aulas privadas |
| `consultor` | Consultor | 💼 | Consultoria profissional |
| `cabeleireiro` | Cabeleireiro | ✂️ | Serviços de cabelo |
| `massagem` | Massagem | 💆 | Serviços de massagem e bem-estar |
| `personal_trainer` | Personal Trainer | 💪 | Treinamento personalizado |
| `nutricionista` | Nutricionista | 🥗 | Consultoria nutricional |
| `psicologista` | Psicólogo | 🧠 | Atendimento psicológico |
| `lawyer` | Advogado | ⚖️ | Consultoria jurídica |
| `contador` | Contador | 📊 | Serviços contábeis |
| `designer` | Designer | 🎨 | Design gráfico e visual |
| `desenvolvedor` | Desenvolvedor | 👨‍💻 | Desenvolvimento de software |
| `marketing` | Marketing | 📢 | Consultoria de marketing |

---

## 🎯 Como Usar no Flutter

### 1. **Carregar categorias na inicialização**
```dart
Future<void> loadCategories() async {
  final response = await http.get(
    Uri.parse('${API_URL}/api/v1/categories/professionals/list'),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    if (data['success']) {
      categories = List.from(data['data']);
      setState(() {});
    }
  }
}
```

### 2. **Usar em um Dropdown**
```dart
DropdownButton(
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
```

### 3. **Mostrar ícone da categoria**
```dart
Text(
  '${category['icon']} ${category['name']}',
  style: TextStyle(fontSize: 16),
)
```

---

## 🔍 Exemplos com cURL

### Listar categorias profissionais:
```bash
curl -X GET "http://localhost:8000/api/v1/categories/professionals/list"
```

### Listar tudo:
```bash
curl -X GET "http://localhost:8000/api/v1/categories/all"
```

### Filtrar profissionais por categoria (existente):
```bash
curl -X GET "http://localhost:8000/api/v1/professionals/?category=eletricista"
```

---

## 📝 Notas Importantes

1. **IDs são únicos** e devem ser usados para buscas/filtros
2. **Ícones são emojis** para melhor UX na app
3. **Sempre usar categoria válida** ao registrar profissional
4. **Adicionar novas categorias** requer atualização em `app/core/constants.py`

---

## 🚀 API Production-Ready

✅ Padrão de resposta consistente  
✅ Tratamento global de erros  
✅ Documentação completa  
✅ Pronto para Flutter  
✅ Escalável para adicionar mais categorias  

