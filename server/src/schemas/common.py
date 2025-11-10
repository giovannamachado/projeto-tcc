"""
Schemas Pydantic para validação de dados de entrada e saída da API.
Define a estrutura dos dados que a API aceita e retorna.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# =============================================================================
# SCHEMAS BASE
# =============================================================================

class BaseSchema(BaseModel):
    """Schema base com configurações comuns"""

    class Config:
        from_attributes = True
        validate_assignment = True

# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserCreate(BaseSchema):
    """Schema para criação de usuário"""
    email: EmailStr
    password: str
    full_name: str
    username: Optional[str] = None
    bio: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        return v

    @validator('username')
    def validate_username(cls, v):
        if v and len(v) < 3:
            raise ValueError('Username deve ter pelo menos 3 caracteres')
        return v

class UserLogin(BaseSchema):
    """Schema para login de usuário"""
    email: EmailStr
    password: str

class UserUpdate(BaseSchema):
    """Schema para atualização de usuário"""
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(BaseSchema):
    """Schema de resposta do usuário (sem dados sensíveis)"""
    id: int
    email: str
    full_name: str
    username: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    @property
    def display_name(self) -> str:
        return self.full_name or self.username or self.email.split('@')[0]

# =============================================================================
# AUTH SCHEMAS
# =============================================================================

class Token(BaseSchema):
    """Schema para token de autenticação"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseSchema):
    """Schema para dados do token"""
    username: Optional[str] = None

# =============================================================================
# PERSONA SCHEMAS
# =============================================================================

class BrandVoice(BaseSchema):
    """Schema para configurações de tom de voz"""
    traits: List[str] = []  # Ex: ["amigável", "profissional", "descontraído"]
    tone: str = "neutro"  # formal, informal, neutro
    personality: str = "profissional"  # jovem, maduro, inovador, etc.
    language_style: str = "claro"  # técnico, simples, elaborado
    emojis_usage: str = "moderado"  # nunca, pouco, moderado, muito

class TargetAudience(BaseSchema):
    """Schema para definição de público-alvo"""
    age_range: str = "25-35"
    gender: str = "todos"  # masculino, feminino, todos
    interests: List[str] = []
    location: str = "Brasil"
    income_level: str = "médio"  # baixo, médio, alto
    education_level: str = "superior"  # fundamental, médio, superior
    behavior_traits: List[str] = []

class VisualGuidelines(BaseSchema):
    """Schema para diretrizes visuais"""
    primary_colors: List[str] = []  # Cores hex
    secondary_colors: List[str] = []
    fonts: List[str] = []
    image_style: str = "moderno"  # minimalista, colorido, vintage, etc.
    logo_usage: bool = True
    brand_elements: List[str] = []

class ContentGuidelines(BaseSchema):
    """Schema para diretrizes de conteúdo"""
    topics: List[str] = []  # Temas a abordar
    avoid_topics: List[str] = []  # Temas a evitar
    hashtags: List[str] = []  # Hashtags padrão
    call_to_actions: List[str] = []
    content_pillars: List[str] = []  # Pilares de conteúdo
    posting_frequency: str = "3-5 por semana"

class InstagramSettings(BaseSchema):
    """Schema para configurações específicas do Instagram"""
    post_types: List[str] = ["foto", "carrossel", "reel"]
    story_frequency: str = "diário"
    reel_frequency: str = "2-3 por semana"
    caption_length: str = "médio"  # curto, médio, longo
    hashtag_strategy: str = "mix"  # populares, nicho, mix

class PersonaCreate(BaseSchema):
    """Schema para criação de persona"""
    name: str
    description: Optional[str] = None
    brand_voice: Optional[BrandVoice] = None
    target_audience: Optional[TargetAudience] = None
    visual_guidelines: Optional[VisualGuidelines] = None
    content_guidelines: Optional[ContentGuidelines] = None
    instagram_settings: Optional[InstagramSettings] = None
    is_default: bool = False

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Nome da persona deve ter pelo menos 2 caracteres')
        return v.strip()

class PersonaUpdate(BaseSchema):
    """Schema para atualização de persona"""
    name: Optional[str] = None
    description: Optional[str] = None
    brand_voice: Optional[BrandVoice] = None
    target_audience: Optional[TargetAudience] = None
    visual_guidelines: Optional[VisualGuidelines] = None
    content_guidelines: Optional[ContentGuidelines] = None
    instagram_settings: Optional[InstagramSettings] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class PersonaResponse(BaseSchema):
    """Schema de resposta da persona"""
    id: int
    name: str
    description: Optional[str]
    brand_voice: Optional[Dict[str, Any]]
    target_audience: Optional[Dict[str, Any]]
    visual_guidelines: Optional[Dict[str, Any]]
    content_guidelines: Optional[Dict[str, Any]]
    instagram_settings: Optional[Dict[str, Any]]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]
    owner_id: int

    @property
    def brand_voice_summary(self) -> str:
        if not self.brand_voice:
            return "Não definido"
        traits = self.brand_voice.get('traits', [])
        return ', '.join(traits[:3]) if traits else "Não definido"