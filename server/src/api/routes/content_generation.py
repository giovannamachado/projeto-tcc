"""
Rotas para geração de conteúdo usando IA.
Endpoints principais para criar legendas, hashtags e ideias de posts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ...core.database import get_db
from ...models.user import User
from ...models.persona import Persona
from ...services.ai_service import ai_service
from ...services.image_service import image_service
from ...services.vector_store import vector_store
from ..routes.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_user_persona(db: Session, persona_id: int, user_id: int) -> Persona:
    """Obtém persona do usuário com validação"""
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.owner_id == user_id,
        Persona.is_active == True
    ).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona não encontrada ou inativa"
        )

    return persona

def prepare_persona_data_for_ai(persona: Persona) -> Dict[str, Any]:
    """Prepara dados da persona para envio ao serviço de IA"""
    return {
        'id': persona.id,
        'name': persona.name,
        'description': persona.description,
        'brand_voice': persona.brand_voice or {},
        'target_audience': persona.target_audience or {},
        'visual_guidelines': persona.visual_guidelines or {},
        'content_guidelines': persona.content_guidelines or {},
        'instagram_settings': persona.instagram_settings or {}
    }

# =============================================================================
# ROTAS DE GERAÇÃO DE CONTEÚDO
# =============================================================================

@router.post("/generate-caption", summary="Gerar legenda para Instagram")
async def generate_instagram_caption(
    generation_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera legenda personalizada para post do Instagram baseada na persona

    Body esperado:
    {
        "persona_id": 1,
        "topic": "lançamento de produto",
        "style": "engajamento", // "engajamento", "informativo", "storytelling"
        "include_hashtags": true,
        "additional_context": "produto é um app mobile para fitness"
    }
    """
    try:
        # Validar dados de entrada
        persona_id = generation_request.get('persona_id')
        topic = generation_request.get('topic')

        if not persona_id or not topic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="persona_id e topic são obrigatórios"
            )

        # Buscar persona
        persona = get_user_persona(db, persona_id, current_user.id)

        # Preparar dados para IA
        persona_data = prepare_persona_data_for_ai(persona)

        # Parâmetros opcionais
        style = generation_request.get('style', 'engajamento')
        include_hashtags = generation_request.get('include_hashtags', True)
        additional_context = generation_request.get('additional_context', '')

        # Enriquecer tópico com contexto adicional
        enriched_topic = topic
        if additional_context:
            enriched_topic = f"{topic}. Contexto adicional: {additional_context}"

        # Gerar legenda
        logger.info(f"🤖 Gerando legenda para persona {persona.name}: {topic}")

        result = await ai_service.generate_instagram_caption(
            persona_data=persona_data,
            topic=enriched_topic,
            style=style,
            include_hashtags=include_hashtags
        )

        # Adicionar informações da solicitação
        result['request_info'] = {
            'persona_id': persona_id,
            'persona_name': persona.name,
            'original_topic': topic,
            'style': style,
            'include_hashtags': include_hashtags,
            'user_id': current_user.id
        }

        logger.info(f"✅ Legenda gerada com sucesso para {persona.name}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar legenda: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na geração de conteúdo"
        )

@router.post("/generate-ideas", summary="Gerar ideias de conteúdo")
async def generate_content_ideas(
    generation_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera múltiplas ideias de conteúdo baseadas na persona

    Body esperado:
    {
        "persona_id": 1,
        "content_type": "posts", // "posts", "stories", "reels"
        "count": 5,
        "focus_area": "educacional" // opcional
    }
    """
    try:
        # Validar dados de entrada
        persona_id = generation_request.get('persona_id')

        if not persona_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="persona_id é obrigatório"
            )

        # Buscar persona
        persona = get_user_persona(db, persona_id, current_user.id)

        # Preparar dados para IA
        persona_data = prepare_persona_data_for_ai(persona)

        # Parâmetros
        content_type = generation_request.get('content_type', 'posts')
        count = min(generation_request.get('count', 5), 10)  # Máximo 10 ideias
        focus_area = generation_request.get('focus_area', '')

        # Validar tipo de conteúdo
        valid_types = ['posts', 'stories', 'reels', 'igtv', 'carrossel']
        if content_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de conteúdo inválido. Tipos válidos: {', '.join(valid_types)}"
            )

        # Gerar ideias
        logger.info(f"💡 Gerando {count} ideias de {content_type} para {persona.name}")

        ideas = await ai_service.generate_content_ideas(
            persona_data=persona_data,
            content_type=content_type,
            count=count
        )

        # Filtrar por área de foco se especificada
        if focus_area and ideas:
            filtered_ideas = []
            focus_lower = focus_area.lower()

            for idea in ideas:
                title_lower = idea.get('title', '').lower()
                description_lower = idea.get('description', '').lower()

                if focus_lower in title_lower or focus_lower in description_lower:
                    filtered_ideas.append(idea)

            # Se encontrou ideias filtradas, use elas
            if filtered_ideas:
                ideas = filtered_ideas

        result = {
            'ideas': ideas,
            'request_info': {
                'persona_id': persona_id,
                'persona_name': persona.name,
                'content_type': content_type,
                'requested_count': count,
                'generated_count': len(ideas),
                'focus_area': focus_area,
                'user_id': current_user.id
            },
            'generated_at': datetime.now().isoformat()
        }

        logger.info(f"✅ {len(ideas)} ideias geradas para {persona.name}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar ideias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na geração de ideias"
        )

@router.post("/generate-hashtags", summary="Gerar hashtags personalizadas")
async def generate_hashtags(
    generation_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera hashtags personalizadas baseadas no tópico e persona

    Body esperado:
    {
        "persona_id": 1,
        "topic": "alimentação saudável",
        "count": 15,
        "mix_strategy": "balanced" // "popular", "niche", "balanced"
    }
    """
    try:
        # Validar dados de entrada
        persona_id = generation_request.get('persona_id')
        topic = generation_request.get('topic')

        if not persona_id or not topic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="persona_id e topic são obrigatórios"
            )

        # Buscar persona
        persona = get_user_persona(db, persona_id, current_user.id)

        # Por enquanto, gerar hashtags usando a função de legenda
        # Em uma versão futura, criar função específica para hashtags
        persona_data = prepare_persona_data_for_ai(persona)

        result = await ai_service.generate_instagram_caption(
            persona_data=persona_data,
            topic=f"gerar apenas hashtags sobre: {topic}",
            style="hashtags",
            include_hashtags=True
        )

        # Extrair apenas as hashtags
        hashtags = result.get('hashtags', [])

        count = generation_request.get('count', 15)
        if len(hashtags) > count:
            hashtags = hashtags[:count]

        response = {
            'hashtags': hashtags,
            'topic': topic,
            'strategy': generation_request.get('mix_strategy', 'balanced'),
            'persona_name': persona.name,
            'generated_at': datetime.now().isoformat()
        }

        logger.info(f"🏷️ {len(hashtags)} hashtags geradas para {persona.name}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar hashtags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na geração de hashtags"
        )

# =============================================================================
# ROTAS DE BUSCA E CONTEXTO
# =============================================================================

@router.post("/search-knowledge", summary="Buscar na base de conhecimento")
async def search_knowledge_base(
    search_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca informações relevantes na base de conhecimento da persona

    Body esperado:
    {
        "persona_id": 1,
        "query": "estratégias de marketing digital",
        "limit": 5
    }
    """
    try:
        # Validar dados de entrada
        persona_id = search_request.get('persona_id')
        query = search_request.get('query')

        if not persona_id or not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="persona_id e query são obrigatórios"
            )

        # Buscar persona
        persona = get_user_persona(db, persona_id, current_user.id)

        # Parâmetros de busca
        limit = min(search_request.get('limit', 5), 20)  # Máximo 20 resultados

        # Buscar no banco vetorial
        logger.info(f"🔍 Buscando '{query}' na base de conhecimento de {persona.name}")

        results = await vector_store.search_similar_content(
            persona_id=persona_id,
            query=query,
            n_results=limit
        )

        # Preparar resposta
        response = {
            'query': query,
            'persona_name': persona.name,
            'results_count': len(results),
            'results': results,
            'searched_at': datetime.now().isoformat()
        }

        logger.info(f"✅ {len(results)} resultados encontrados")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na busca: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na busca"
        )

# =============================================================================
# ROTAS DE ANÁLISE E MELHORIAS
# =============================================================================

@router.post("/analyze-content", summary="Analisar conteúdo gerado")
async def analyze_content(
    analysis_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analisa um conteúdo gerado e sugere melhorias

    Body esperado:
    {
        "persona_id": 1,
        "content": "texto da legenda aqui...",
        "content_type": "caption",
        "target_metrics": ["engagement", "reach"]
    }
    """
    try:
        # Validar dados de entrada
        persona_id = analysis_request.get('persona_id')
        content = analysis_request.get('content')

        if not persona_id or not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="persona_id e content são obrigatórios"
            )

        # Buscar persona
        persona = get_user_persona(db, persona_id, current_user.id)

        # Por enquanto, retornar análise básica
        # Em versão futura, implementar análise com IA

        analysis = {
            'content_analysis': {
                'character_count': len(content),
                'word_count': len(content.split()),
                'emoji_count': sum(1 for char in content if ord(char) > 127),
                'hashtag_count': content.count('#'),
                'mention_count': content.count('@')
            },
            'persona_alignment': {
                'score': 0.85,  # Score simulado
                'feedback': 'Conteúdo bem alinhado com a persona'
            },
            'suggestions': [
                'Considere adicionar mais hashtags específicas do nicho',
                'O tom está adequado para o público-alvo',
                'Inclua uma call-to-action mais clara'
            ],
            'optimizations': {
                'engagement_potential': 'Alto',
                'readability_score': 'Bom',
                'brand_consistency': 'Excelente'
            },
            'analyzed_at': datetime.now().isoformat()
        }

        logger.info(f"📊 Conteúdo analisado para {persona.name}")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na análise"
        )

# =============================================================================
# ROTAS DE ESTATÍSTICAS
# =============================================================================

@router.get("/stats/usage", summary="Estatísticas de uso da geração de conteúdo")
async def get_content_generation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    persona_id: Optional[int] = Query(None, description="Filtrar por persona específica")
):
    """
    Retorna estatísticas de uso das funcionalidades de geração de conteúdo
    """
    # Por enquanto, retornar estatísticas simuladas
    # Em produção, seria implementado tracking de uso real

    stats = {
        'user_id': current_user.id,
        'generation_summary': {
            'total_captions_generated': 45,
            'total_ideas_generated': 23,
            'total_hashtag_sets_generated': 12,
            'total_searches_performed': 67
        },
        'most_used_personas': [
            {'persona_id': 1, 'name': 'Marca Principal', 'usage_count': 34},
            {'persona_id': 2, 'name': 'Produto X', 'usage_count': 23}
        ],
        'popular_content_types': [
            {'type': 'posts', 'count': 28},
            {'type': 'stories', 'count': 15},
            {'type': 'reels', 'count': 12}
        ],
        'generation_trends': {
            'this_week': 12,
            'this_month': 45,
            'average_per_week': 8.5
        },
        'generated_at': datetime.now().isoformat()
    }

    # Se persona específica foi solicitada, filtrar dados
    if persona_id:
        persona = get_user_persona(db, persona_id, current_user.id)
        stats['filtered_by_persona'] = {
            'persona_id': persona_id,
            'persona_name': persona.name
        }

    return stats

# =============================================================================
# ROTA DE GERAÇÃO DE IMAGENS
# =============================================================================

@router.post("/generate-image", summary="Gerar imagem alinhada à persona")
async def generate_image(
    generation_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera uma imagem via Stability AI considerando diretrizes visuais da persona.

    Body esperado:
    {
        "persona_id": 1,
        "prompt": "foto de produto em cena minimalista",
        "ratio": "square"  // square | portrait | landscape (opcional)
    }
    """
    try:
        persona_id = generation_request.get('persona_id')
        prompt = generation_request.get('prompt')
        ratio = generation_request.get('ratio', 'square')

        if not persona_id or not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="persona_id e prompt são obrigatórios"
            )

        persona = get_user_persona(db, persona_id, current_user.id)
        persona_data = prepare_persona_data_for_ai(persona)

        result = await image_service.generate_image(
            persona_data=persona_data,
            prompt=prompt,
            ratio=ratio,
        )

        return {
            "image": result,
            "persona": {"id": persona.id, "name": persona.name},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar imagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )