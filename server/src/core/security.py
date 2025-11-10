"""
Utilitários de segurança para autenticação e autorização.
Implementa JWT tokens e hashing de senhas usando bcrypt.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets

from .config import settings

# Configurar contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class SecurityUtils:
    """Utilitários de segurança centralizados"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha fornecida confere com o hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash seguro da senha"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Cria um JWT token de acesso

        Args:
            data: Dados a serem incluídos no token
            expires_delta: Tempo de expiração customizado

        Returns:
            str: Token JWT codificado
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica e decodifica um JWT token

        Args:
            token: JWT token para verificar

        Returns:
            dict: Payload do token decodificado

        Raises:
            HTTPException: Se o token for inválido
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception

            return payload

        except JWTError:
            raise credentials_exception

    @staticmethod
    def generate_api_key() -> str:
        """Gera uma chave API segura"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nome de arquivo para evitar problemas de segurança

        Args:
            filename: Nome do arquivo original

        Returns:
            str: Nome do arquivo sanitizado
        """
        import re

        # Remove caracteres perigosos
        filename = re.sub(r'[^\w\-_\.]', '_', filename)

        # Limita tamanho
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')

        return filename

    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: list) -> bool:
        """
        Valida se o tipo de arquivo é permitido

        Args:
            filename: Nome do arquivo
            allowed_extensions: Lista de extensões permitidas

        Returns:
            bool: True se o arquivo é permitido
        """
        if '.' not in filename:
            return False

        extension = filename.rsplit('.', 1)[1].lower()
        return extension in [ext.lower() for ext in allowed_extensions]

# Instância global
security = SecurityUtils()

# Exceptions customizadas
class SecurityException(HTTPException):
    """Exception base para erros de segurança"""
    pass

class InvalidTokenException(SecurityException):
    """Token inválido ou expirado"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

class InsufficientPermissionsException(SecurityException):
    """Permissões insuficientes"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões insuficientes para esta operação"
        )