"""
core/constants.py

Constantes e configurações da aplicação.
Define categorias de profissionais, tipos de serviços, etc.
"""

# ── Categorias de Profissionais ───────────────────────────────────────────────
PROFESSIONAL_CATEGORIES = {
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
    "pedreiro": {
        "name": "Pedreiro",
        "icon": "🧱",
        "description": "Construção e alvenaria"
    },
    "pintor": {
        "name": "Pintor",
        "icon": "🎨",
        "description": "Pintura de ambientes"
    },
    "marceneiro": {
        "name": "Marceneiro",
        "icon": "🪵",
        "description": "Trabalhos em madeira"
    },
    "jardineiro": {
        "name": "Jardineiro",
        "icon": "🌱",
        "description": "Jardinagem e paisagismo"
    },
    "limpeza": {
        "name": "Limpeza",
        "icon": "🧹",
        "description": "Serviços de limpeza"
    },
    "manutencao": {
        "name": "Manutenção",
        "icon": "🔨",
        "description": "Manutenção predial"
    },
    "reparo_movel": {
        "name": "Reparo de Móvel",
        "icon": "🛋️",
        "description": "Conserto e restauração de móveis"
    },
    "vidraceiro": {
        "name": "Vidraceiro",
        "icon": "🪟",
        "description": "Serviços com vidro"
    },
    "mecanico": {
        "name": "Mecânico",
        "icon": "🔧",
        "description": "Serviços automotivos"
    },
    "informatica": {
        "name": "Informática",
        "icon": "💻",
        "description": "Suporte técnico e informática"
    },
    "fotografia": {
        "name": "Fotografia",
        "icon": "📸",
        "description": "Serviços fotográficos"
    },
    "aula_particular": {
        "name": "Aula Particular",
        "icon": "📚",
        "description": "Tutoria e aulas privadas"
    },
    "consultor": {
        "name": "Consultor",
        "icon": "💼",
        "description": "Consultoria profissional"
    },
    "cabeleireiro": {
        "name": "Cabeleireiro",
        "icon": "✂️",
        "description": "Serviços de cabelo"
    },
    "massagem": {
        "name": "Massagem",
        "icon": "💆",
        "description": "Serviços de massagem e bem-estar"
    },
    "personal_trainer": {
        "name": "Personal Trainer",
        "icon": "💪",
        "description": "Treinamento personalizado"
    },
    "nutricionista": {
        "name": "Nutricionista",
        "icon": "🥗",
        "description": "Consultoria nutricional"
    },
    "psicologista": {
        "name": "Psicólogo",
        "icon": "🧠",
        "description": "Atendimento psicológico"
    },
    "lawyer": {
        "name": "Advogado",
        "icon": "⚖️",
        "description": "Consultoria jurídica"
    },
    "contador": {
        "name": "Contador",
        "icon": "📊",
        "description": "Serviços contábeis"
    },
    "designer": {
        "name": "Designer",
        "icon": "🎨",
        "description": "Design gráfico e visual"
    },
    "desenvolvedor": {
        "name": "Desenvolvedor",
        "icon": "👨‍💻",
        "description": "Desenvolvimento de software"
    },
    "marketing": {
        "name": "Marketing",
        "icon": "📢",
        "description": "Consultoria de marketing"
    },
}

# Para facilitar buscas e validação
CATEGORY_KEYS = list(PROFESSIONAL_CATEGORIES.keys())
CATEGORY_NAMES = {k: v["name"] for k, v in PROFESSIONAL_CATEGORIES.items()}


# ── Tipos de Serviço ──────────────────────────────────────────────────────────

SERVICE_TYPES = {
    "pontual": "Serviço Pontual",
    "recorrente": "Serviço Recorrente",
    "contrato": "Contrato",
    "consultoria": "Consultoria",
}

SERVICE_TYPE_KEYS = list(SERVICE_TYPES.keys())


# ── Status de Serviço ─────────────────────────────────────────────────────────

SERVICE_STATUS = {
    "pendente": "Aguardando Aceitação",
    "aceito": "Aceito",
    "iniciado": "Em Andamento",
    "concluido": "Concluído",
    "cancelado": "Cancelado",
    "disputado": "Em Disputa",
}

SERVICE_STATUS_KEYS = list(SERVICE_STATUS.keys())


# ── Tipos de Usuário ──────────────────────────────────────────────────────────

USER_TYPES = {
    "client": "Cliente",
    "professional": "Profissional",
    "admin": "Administrador",
}


# ── Validações ────────────────────────────────────────────────────────────────

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128

MIN_RATING = 0.0
MAX_RATING = 5.0

MIN_HOURLY_RATE = 10.0
MAX_HOURLY_RATE = 10000.0

# Rate limiting
RATE_LIMIT_LOGIN_ATTEMPTS = 5
RATE_LIMIT_LOGIN_WINDOW_MINUTES = 15

RATE_LIMIT_REGISTER_ATTEMPTS = 3
RATE_LIMIT_REGISTER_WINDOW_MINUTES = 60
