"""
Modelo de dados para personas de marca.
Define as características, tom de voz e diretrizes que guiam a geração de conteúdo.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base

class Persona(Base):
    """
    Modelo para personas de marca

    Uma persona define a identidade, tom de voz, público-alvo e diretrizes
    que a IA deve seguir ao gerar conteúdo. Cada usuário pode ter múltiplas
    personas para diferentes marcas ou campanhas.
    """

    __tablename__ = "personas"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Relacionamento com usuário
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Configurações da marca
    brand_voice = Column(JSON)  # Tom de voz, personalidade, estilo
    target_audience = Column(JSON)  # Público-alvo, demografia, interesses
    visual_guidelines = Column(JSON)  # Cores, fontes, estilo visual
    content_guidelines = Column(JSON)  # Temas, hashtags, call-to-actions

    # Configurações específicas do Instagram
    instagram_settings = Column(JSON)  # Formato de posts, stories, reels

    # Status e metadados
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    owner = relationship("User", back_populates="personas")
    knowledge_bases = relationship("KnowledgeBase", back_populates="persona", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Persona(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"

    @property
    def brand_voice_summary(self) -> str:
        """Retorna um resumo do tom de voz da marca"""
        if not self.brand_voice:
            return "Não definido"

        voice_traits = self.brand_voice.get('traits', [])
        return ', '.join(voice_traits[:3]) if voice_traits else "Não definido"

    @property
    def target_audience_summary(self) -> str:
        """Retorna um resumo do público-alvo"""
        if not self.target_audience:
            return "Não definido"

        age_range = self.target_audience.get('age_range', '')
        interests = self.target_audience.get('interests', [])

        summary_parts = []
        if age_range:
            summary_parts.append(f"Idade: {age_range}")
        if interests:
            summary_parts.append(f"Interesses: {', '.join(interests[:2])}")

        return ' | '.join(summary_parts) if summary_parts else "Não definido"