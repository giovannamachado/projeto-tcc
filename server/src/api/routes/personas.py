"""
Rotas para gerenciamento de personas.
CRUD completo para personas de marca com validações e relacionamentos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ...core.database import get_db
from ...models.user import User
from ...models.persona import Persona
from ...schemas.common import PersonaCreate, PersonaUpdate, PersonaResponse
from ..routes.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_persona_by_id(db: Session, persona_id: int, user_id: int) -> Optional[Persona]:
    """Busca persona por ID, garantindo que pertence ao usuário"""
    return db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.owner_id == user_id
    ).first()

def validate_persona_ownership(persona: Persona, user: User):
    """Valida se a persona pertence ao usuário"""
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona não encontrada"
        )

    if persona.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a esta persona"
        )

# =============================================================================
# ROTAS CRUD
# =============================================================================

@router.post("/", response_model=PersonaResponse, summary="Criar nova persona")
async def create_persona(
    persona_data: PersonaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova persona para o usuário
    """
    try:
        # Verificar se já existe uma persona padrão se esta for marcada como padrão
        if persona_data.is_default:
            existing_default = db.query(Persona).filter(
                Persona.owner_id == current_user.id,
                Persona.is_default == True
            ).first()

            if existing_default:
                # Remover status padrão da persona existente
                existing_default.is_default = False

        # Criar nova persona
        db_persona = Persona(
            name=persona_data.name,
            description=persona_data.description,
            owner_id=current_user.id,
            brand_voice=persona_data.brand_voice.dict() if persona_data.brand_voice else None,
            target_audience=persona_data.target_audience.dict() if persona_data.target_audience else None,
            visual_guidelines=persona_data.visual_guidelines.dict() if persona_data.visual_guidelines else None,
            content_guidelines=persona_data.content_guidelines.dict() if persona_data.content_guidelines else None,
            instagram_settings=persona_data.instagram_settings.dict() if persona_data.instagram_settings else None,
            is_default=persona_data.is_default
        )

        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)

        logger.info(f"✅ Nova persona criada: {db_persona.name} (ID: {db_persona.id})")

        return db_persona

    except Exception as e:
        logger.error(f"❌ Erro ao criar persona: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar persona"
        )

@router.get("/", response_model=List[PersonaResponse], summary="Listar personas do usuário")
async def list_personas(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    active_only: bool = Query(True, description="Filtrar apenas personas ativas")
):
    """
    Lista todas as personas do usuário com paginação
    """
    query = db.query(Persona).filter(Persona.owner_id == current_user.id)

    if active_only:
        query = query.filter(Persona.is_active == True)

    personas = query.order_by(Persona.is_default.desc(), Persona.created_at.desc()).offset(skip).limit(limit).all()

    logger.info(f"📋 Listando {len(personas)} personas para usuário {current_user.id}")

    return personas

@router.get("/{persona_id}", response_model=PersonaResponse, summary="Obter persona específica")
async def get_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém uma persona específica do usuário
    """
    persona = get_persona_by_id(db, persona_id, current_user.id)
    validate_persona_ownership(persona, current_user)

    return persona

@router.put("/{persona_id}", response_model=PersonaResponse, summary="Atualizar persona")
async def update_persona(
    persona_id: int,
    persona_update: PersonaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma persona existente
    """
    try:
        # Buscar persona
        persona = get_persona_by_id(db, persona_id, current_user.id)
        validate_persona_ownership(persona, current_user)

        # Verificar se está tentando definir como padrão
        if persona_update.is_default == True and not persona.is_default:
            # Remover status padrão de outras personas
            existing_default = db.query(Persona).filter(
                Persona.owner_id == current_user.id,
                Persona.is_default == True,
                Persona.id != persona_id
            ).first()

            if existing_default:
                existing_default.is_default = False

        # Atualizar campos
        update_data = persona_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            if field in ['brand_voice', 'target_audience', 'visual_guidelines',
                        'content_guidelines', 'instagram_settings']:
                # Converter objetos Pydantic para dict
                if value is not None:
                    value = value.dict() if hasattr(value, 'dict') else value

            setattr(persona, field, value)

        db.commit()
        db.refresh(persona)

        logger.info(f"✅ Persona atualizada: {persona.name} (ID: {persona.id})")

        return persona

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar persona {persona_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar persona"
        )

@router.delete("/{persona_id}", summary="Deletar persona")
async def delete_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta uma persona e todos os dados relacionados
    """
    try:
        # Buscar persona
        persona = get_persona_by_id(db, persona_id, current_user.id)
        validate_persona_ownership(persona, current_user)

        # Verificar se não é a única persona do usuário
        total_personas = db.query(Persona).filter(
            Persona.owner_id == current_user.id,
            Persona.is_active == True
        ).count()

        if total_personas <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível deletar a única persona ativa"
            )

        # Limpar dados do banco vetorial
        try:
            from ...services.vector_store import vector_store
            await vector_store.clear_persona_collection(persona_id)
            logger.info(f"🧹 Dados vetoriais da persona {persona_id} removidos")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao limpar dados vetoriais: {e}")

        # Deletar persona (cascata deleta knowledge_bases relacionadas)
        db.delete(persona)
        db.commit()

        logger.info(f"🗑️ Persona deletada: {persona.name} (ID: {persona_id})")

        return {"message": "Persona deletada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar persona {persona_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar persona"
        )

# =============================================================================
# ROTAS ESPECIAIS
# =============================================================================

@router.get("/{persona_id}/summary", summary="Resumo da persona")
async def get_persona_summary(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna um resumo consolidado da persona para uso rápido
    """
    persona = get_persona_by_id(db, persona_id, current_user.id)
    validate_persona_ownership(persona, current_user)

    # Contar base de conhecimento
    knowledge_count = len(persona.knowledge_bases) if persona.knowledge_bases else 0

    # Resumo das configurações
    summary = {
        "id": persona.id,
        "name": persona.name,
        "description": persona.description,
        "is_default": persona.is_default,
        "knowledge_base_count": knowledge_count,
        "brand_voice_summary": persona.brand_voice_summary,
        "target_audience_summary": persona.target_audience_summary,
        "created_at": persona.created_at,
        "last_updated": persona.updated_at,
        "configuration_completeness": {
            "brand_voice": bool(persona.brand_voice),
            "target_audience": bool(persona.target_audience),
            "visual_guidelines": bool(persona.visual_guidelines),
            "content_guidelines": bool(persona.content_guidelines),
            "instagram_settings": bool(persona.instagram_settings)
        }
    }

    # Calcular score de completude
    config_scores = list(summary["configuration_completeness"].values())
    completeness_score = (sum(config_scores) / len(config_scores)) * 100
    summary["completeness_score"] = round(completeness_score, 1)

    return summary

@router.post("/{persona_id}/set-default", summary="Definir como persona padrão")
async def set_default_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Define uma persona como padrão para o usuário
    """
    try:
        # Buscar persona
        persona = get_persona_by_id(db, persona_id, current_user.id)
        validate_persona_ownership(persona, current_user)

        # Remover status padrão de outras personas
        db.query(Persona).filter(
            Persona.owner_id == current_user.id,
            Persona.is_default == True
        ).update({"is_default": False})

        # Definir esta como padrão
        persona.is_default = True

        db.commit()

        logger.info(f"⭐ Persona {persona.name} definida como padrão")

        return {"message": f"Persona '{persona.name}' definida como padrão"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao definir persona padrão: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao definir persona padrão"
        )

@router.post("/{persona_id}/duplicate", response_model=PersonaResponse, summary="Duplicar persona")
async def duplicate_persona(
    persona_id: int,
    new_name: str = Query(..., description="Nome para a nova persona"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma cópia de uma persona existente
    """
    try:
        # Buscar persona original
        original_persona = get_persona_by_id(db, persona_id, current_user.id)
        validate_persona_ownership(original_persona, current_user)

        # Criar cópia
        duplicated_persona = Persona(
            name=new_name,
            description=f"Cópia de: {original_persona.description}" if original_persona.description else None,
            owner_id=current_user.id,
            brand_voice=original_persona.brand_voice,
            target_audience=original_persona.target_audience,
            visual_guidelines=original_persona.visual_guidelines,
            content_guidelines=original_persona.content_guidelines,
            instagram_settings=original_persona.instagram_settings,
            is_default=False  # Cópia nunca é padrão
        )

        db.add(duplicated_persona)
        db.commit()
        db.refresh(duplicated_persona)

        logger.info(f"📋 Persona duplicada: {original_persona.name} -> {new_name}")

        return duplicated_persona

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao duplicar persona: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao duplicar persona"
        )