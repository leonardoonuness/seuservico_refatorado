# SeuServiço API — Refatorado v2.0

Backend refatorado para produção (Render + PostgreSQL), compatível com o app Flutter existente.

---

## O que foi corrigido

### Erro 500 em `/auth/register` e outras rotas críticas
| Antes | Depois |
|---|---|
| `IntegrityError` não tratado → 500 | `IntegrityError` capturado → **409 Conflict** |
| Enum SQLAlchemy causava erros de migração | `String` simples + `CheckConstraint` no banco |
| Rollback não era feito em falhas | `get_db()` faz rollback automático em toda exceção |
| Stacktrace vazava para o cliente | Handler global retorna mensagem genérica, log interno |
| Senha podia aparecer em erros de serialização | `UserResponse` nunca inclui `hashed_password` |

### Mapa completo de status HTTP
| Situação | Código |
|---|---|
| Dados inválidos (Pydantic) | 422 Unprocessable Entity |
| E-mail já cadastrado | 409 Conflict |
| Credenciais erradas | 401 Unauthorized |
| Token inválido/expirado | 401 Unauthorized |
| Conta bloqueada | 403 Forbidden |
| Recurso não encontrado | 404 Not Found |
| Erro inesperado | 500 (mensagem genérica, stacktrace só no log) |

---

## Estrutura

```
app/
├── main.py               # Entrypoint: app, middlewares, lifespan, error handler
├── core/
│   ├── config.py         # Settings via pydantic-settings (.env)
│   ├── security.py       # JWT, bcrypt — funções puras, sem efeitos colaterais
│   └── dependencies.py   # get_current_user, require_admin, require_professional
├── db/
│   ├── base.py           # DeclarativeBase
│   └── session.py        # Engine com pool_pre_ping, get_db com rollback
├── models/
│   ├── user.py           # user_type como String (sem Enum nativo)
│   ├── professional.py
│   ├── service_request.py
│   └── review.py
├── schemas/
│   └── user.py           # UserRegisterRequest aceita "type" do Flutter
│                         # UserResponse retorna "type" via alias
├── routes/               # Thin controllers — sem lógica de negócio
│   ├── auth.py
│   ├── users.py
│   ├── professionals.py
│   ├── services.py
│   └── admin.py
└── services/             # Toda a lógica de negócio
    ├── auth_service.py
    └── user_service.py
```

---

## Compatibilidade com Flutter

O app Flutter envia `"type"` e recebe `"type"` — o campo interno no banco é `user_type`.
Isso é tratado de forma transparente via alias do Pydantic:

```python
# schema recebe do Flutter:
class UserRegisterRequest(BaseModel):
    type: UserType  # "client" | "professional"

# model salva como:
user.user_type = data.type

# schema retorna para o Flutter:
class UserResponse(BaseModel):
    type: str = Field(alias="user_type")  # Flutter lê como "type"
```

**Nenhuma alteração necessária no app Flutter.**

---

## Deploy na Render

### Variáveis de ambiente obrigatórias
| Variável | Exemplo |
|---|---|
| `DATABASE_URL` | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | string longa e aleatória |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` |

### Start command
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

As tabelas são criadas automaticamente no startup (`Base.metadata.create_all`).

---

## Desenvolvimento local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Preencha DATABASE_URL e SECRET_KEY

uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

## Testes

```bash
pytest tests/ -v
```

---

## Sugestões futuras (sem quebrar o MVP)

1. **Blacklist de refresh tokens** — armazenar tokens revogados no Redis para logout seguro
2. **Rate limiting** — `slowapi` para prevenir brute-force no `/auth/login`
3. **Alembic migrations** — substituir `create_all` por migrações versionadas em produção
4. **Paginação padronizada** — schema `PaginatedResponse[T]` reutilizável
5. **Upload de avatar** — endpoint `/users/me/avatar` com validação de tipo MIME
