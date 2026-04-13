"""
routes/categories.py

Endpoints para listar categorias de profissionais,tipos de serviço, etc.
Útil para preencher dropdowns no Cliente (Flutter).
"""
import logging
from fastapi import APIRouter
from app.core.constants import (
    PROFESSIONAL_CATEGORIES,
    SERVICE_TYPES,
    SERVICE_STATUS,
    USER_TYPES,
)
from app.core.responses import success_response, list_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get(
    "/professionals",
    summary="Listar categorias de profissionais",
    description="Retorna todas as categorias de profissionais disponíveis para filtros e registros"
)
def get_professional_categories():
    """
    Retorna todas as categorias de profissionais disponíveis.
    
    Útil para:
    - Dropdown de registro de profissional
    - Filtros de busca
    - Validação de categorias
    
    Exemplo de resposta:
    {
        "success": true,
        "data": {
            "encanador": {
                "name": "Encanador",
                "icon": "🔧",
                "description": "Serviços de encanamento e hidráulica"
            },
            ...
        },
        "count": 25
    }
    """
    return list_response(
        data=PROFESSIONAL_CATEGORIES,
        message=f"Encontradas {len(PROFESSIONAL_CATEGORIES)} categorias de profissionais"
    )


@router.get(
    "/professionals/list",
    summary="Listar categorias (formato lista)",
    description="Retorna categorias em formato de lista simples"
)
def get_professional_categories_list():
    """
    Retorna categorias de profissionais em formato de lista simples.
    Cada item tem: id, name, icon, description
    
    Exemplo:
    {
        "success": true,
        "data": [
            {
                "id": "encanador",
                "name": "Encanador",
                "icon": "🔧",
                "description": "Serviços de encanamento e hidráulica"
            },
            ...
        ]
    }
    """
    categories_list = [
        {
            "id": category_id,
            **category_data
        }
        for category_id, category_data in PROFESSIONAL_CATEGORIES.items()
    ]
    return list_response(
        data=categories_list,
        message=f"Encontradas {len(categories_list)} categorias"
    )


@router.get(
    "/service-types",
    summary="Listar tipos de serviço",
    description="Retorna todos os tipos de serviço disponíveis"
)
def get_service_types():
    """
    Retorna tipos de serviço.
    """
    service_types_list = [
        {"id": stype_id, "name": name}
        for stype_id, name in SERVICE_TYPES.items()
    ]
    return list_response(
        data=service_types_list,
        message=f"Encontrados {len(service_types_list)} tipos de serviço"
    )


@router.get(
    "/service-status",
    summary="Listar status de serviço",
    description="Retorna todos os status possíveis de um serviço"
)
def get_service_status():
    """
    Retorna status de serviço.
    """
    status_list = [
        {"id": status_id, "name": name}
        for status_id, name in SERVICE_STATUS.items()
    ]
    return list_response(
        data=status_list,
        message=f"Encontrados {len(status_list)} status de serviço"
    )


@router.get(
    "/user-types",
    summary="Listar tipos de usuário",
    description="Retorna tipos de usuário do sistema"
)
def get_user_types():
    """
    Retorna tipos de usuário.
    """
    user_types_list = [
        {"id": utype_id, "name": name}
        for utype_id, name in USER_TYPES.items()
    ]
    return list_response(
        data=user_types_list,
        message=f"Encontrados {len(user_types_list)} tipos de usuário"
    )


@router.get(
    "/all",
    summary="Listar todas as categorias/tipos",
    description="Retorna categorias, tipos de serviço, status e tipos de usuário"
)
def get_all_categories():
    """
    Retorna todas as categorias e tipos em um único endpoint.
    Útil para inicializar a aplicação Flutter.
    
    Exemplo de resposta:
    {
        "success": true,
        "data": {
            "professional_categories": {...},
            "service_types": [...],
            "service_status": [...],
            "user_types": [...]
        }
    }
    """
    categories_list = [
        {
            "id": category_id,
            **category_data
        }
        for category_id, category_data in PROFESSIONAL_CATEGORIES.items()
    ]
    
    service_types_list = [
        {"id": stype_id, "name": name}
        for stype_id, name in SERVICE_TYPES.items()
    ]
    
    status_list = [
        {"id": status_id, "name": name}
        for status_id, name in SERVICE_STATUS.items()
    ]
    
    user_types_list = [
        {"id": utype_id, "name": name}
        for utype_id, name in USER_TYPES.items()
    ]
    
    return success_response(
        data={
            "professional_categories": categories_list,
            "service_types": service_types_list,
            "service_status": status_list,
            "user_types": user_types_list,
        },
        message="Categorias e tipos carregados com sucesso"
    )
