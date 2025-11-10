"""
Rotas de autenticação e autorização.
Gerencia login, registro e validação de tokens JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from ...core.database import get_db
from ...core.security import security, ACCESS_TOKEN_EXPIRE_MINUTES
from ...models.user import User
from ...schemas.common import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()
security_scheme = HTTPBearer()

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca usuário por email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Busca usuário por username"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Autentica usuário com email e senha"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obter usuário atual a partir do token JWT
    """
    try:
        # Verificar token
        payload = security.verify_token(credentials.credentials)
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        # Buscar usuário
        user = get_user_by_email(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário inativo"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar credenciais"
        )

# =============================================================================
# ROTAS PÚBLICAS
# =============================================================================

@router.post("/register", response_model=UserResponse, summary="Registrar novo usuário")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema
    """
    # Verificar se email já existe
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )

    # Verificar se username já existe (se fornecido)
    if user_data.username and get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso"
        )

    # Criar usuário
    hashed_password = security.get_password_hash(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        username=user_data.username,
        bio=user_data.bio
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/login", response_model=Token, summary="Fazer login")
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica usuário e retorna token JWT
    """
    # Autenticar usuário
    user = authenticate_user(db, user_credentials.email, user_credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    # Atualizar último login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
        "user": user
    }

# =============================================================================
# ROTAS PROTEGIDAS
# =============================================================================

@router.get("/me", response_model=UserResponse, summary="Obter usuário atual")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    return current_user

@router.put("/me", response_model=UserResponse, summary="Atualizar perfil")
async def update_profile(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza informações do perfil do usuário
    """
    # Campos permitidos para atualização
    allowed_fields = {'full_name', 'username', 'bio'}

    for field, value in user_update.items():
        if field in allowed_fields and value is not None:
            # Verificar username único se está sendo alterado
            if field == 'username' and value != current_user.username:
                if get_user_by_username(db, value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username já está em uso"
                    )

            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user

@router.post("/change-password", summary="Alterar senha")
async def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera a senha do usuário
    """
    current_password = password_data.get('current_password')
    new_password = password_data.get('new_password')

    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual e nova senha são obrigatórias"
        )

    # Verificar senha atual
    if not security.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )

    # Validar nova senha
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ter pelo menos 8 caracteres"
        )

    # Atualizar senha
    current_user.hashed_password = security.get_password_hash(new_password)
    db.commit()

    return {"message": "Senha alterada com sucesso"}

@router.post("/logout", summary="Fazer logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Endpoint de logout (principalmente para registrar ação)
    """
    # Em uma implementação mais robusta, aqui seria adicionado
    # o token a uma blacklist ou similar
    return {"message": "Logout realizado com sucesso"}

@router.delete("/delete-account", summary="Deletar conta")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta a conta do usuário e todos os dados relacionados
    """
    # Em produção, seria importante implementar soft delete
    # e manter dados por um período para auditoria

    # Por ora, apenas marcar como inativo
    current_user.is_active = False
    db.commit()

    return {"message": "Conta desativada com sucesso"}