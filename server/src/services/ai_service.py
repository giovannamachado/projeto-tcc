"""
Serviço de IA para geração de texto.
Suporta múltiplos providers: Google Gemini, OpenRouter (modelos free) e Ollama (local).
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import httpx

from ..core.config import settings
from .vector_store import vector_store

logger = logging.getLogger(__name__)


class AIService:
    """
    Serviço de IA para geração de conteúdo com suporte a múltiplos providers

    Providers suportados:
    - google: Google Gemini via AI Studio (grátis, requer GOOGLE_API_KEY)
    - openrouter: OpenRouter com modelos gratuitos (requer OPENROUTER_API_KEY)
    - ollama: Modelos locais via Ollama (100% grátis, sem API key)
    """

    def __init__(self):
        self.provider = settings.AI_TEXT_PROVIDER.lower()
        self.model = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Inicializa o provider configurado"""
        try:
            if self.provider == "google":
                self._initialize_gemini()
            elif self.provider == "openrouter":
                self._initialize_openrouter()
            elif self.provider == "ollama":
                self._initialize_ollama()
            else:
                logger.warning(
                    f"Provider desconhecido '{self.provider}', usando google como fallback")
                self.provider = "google"
                self._initialize_gemini()
        except Exception as e:
            logger.error(
                f"❌ Erro ao inicializar provider {self.provider}: {e}")
            raise

    def _initialize_gemini(self):
        """Inicializa Google Gemini"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY não configurada!\n"
                "Obtenha GRÁTIS em: https://aistudio.google.com/app/apikey"
            )

        genai.configure(api_key=settings.GOOGLE_API_KEY)

        generation_config = {
            "temperature": settings.TEMPERATURE,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": settings.MAX_TOKENS,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        self.model = genai.GenerativeModel(
            model_name=settings.DEFAULT_MODEL,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        logger.info(f"✅ Google Gemini inicializado: {settings.DEFAULT_MODEL}")

    def _initialize_openrouter(self):
        """Inicializa OpenRouter"""
        if not settings.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY não configurada!\n"
                "Crie conta GRÁTIS em: https://openrouter.ai/\n"
                "Modelos gratuitos disponíveis!"
            )

        self.model = {
            "api_key": settings.OPENROUTER_API_KEY,
            "model": settings.OPENROUTER_MODEL,
            "base_url": "https://openrouter.ai/api/v1"
        }

        logger.info(f"✅ OpenRouter inicializado: {settings.OPENROUTER_MODEL}")

    def _initialize_ollama(self):
        """Inicializa Ollama (local)"""
        self.model = {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL
        }

        logger.info(
            f"✅ Ollama inicializado: {settings.OLLAMA_MODEL} @ {settings.OLLAMA_BASE_URL}")

    async def _generate_text(self, prompt: str) -> str:
        """Gera texto usando o provider configurado"""
        if self.provider == "google":
            response = self.model.generate_content(prompt)
            return response.text

        elif self.provider == "openrouter":
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.model['base_url']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.model['api_key']}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model['model'],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": settings.TEMPERATURE,
                        "max_tokens": settings.MAX_TOKENS,
                    }
                )

                if response.status_code != 200:
                    logger.error(f"OpenRouter error: {response.text}")
                    raise ValueError("Erro ao gerar texto via OpenRouter")

                data = response.json()
                return data["choices"][0]["message"]["content"]

        elif self.provider == "ollama":
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.model['base_url']}/api/generate",
                    json={
                        "model": self.model['model'],
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": settings.TEMPERATURE,
                            "num_predict": settings.MAX_TOKENS,
                        }
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Ollama error: {response.text}")
                    raise ValueError(
                        "Erro ao conectar ao Ollama.\n"
                        "Certifique-se de que está rodando: ollama serve"
                    )

                data = response.json()
                return data["response"]

        raise ValueError(f"Provider não suportado: {self.provider}")

    def _build_persona_context(self, persona_data: Dict[str, Any]) -> str:
        """Constrói contexto detalhado da persona para o prompt"""
        context_parts = []

        # Informações básicas
        context_parts.append(
            f"PERSONA: {persona_data.get('name', 'Sem nome')}")

        if persona_data.get('description'):
            context_parts.append(f"DESCRIÇÃO: {persona_data['description']}")

        # Tom de voz
        brand_voice = persona_data.get('brand_voice', {})
        if brand_voice:
            voice_parts = []
            if brand_voice.get('traits'):
                voice_parts.append(
                    f"Características: {', '.join(brand_voice['traits'])}")
            if brand_voice.get('tone'):
                voice_parts.append(f"Tom: {brand_voice['tone']}")
            if brand_voice.get('personality'):
                voice_parts.append(
                    f"Personalidade: {brand_voice['personality']}")
            if brand_voice.get('emojis_usage'):
                voice_parts.append(
                    f"Uso de emojis: {brand_voice['emojis_usage']}")

            if voice_parts:
                context_parts.append(f"TOM DE VOZ: {' | '.join(voice_parts)}")

        # Público-alvo
        target_audience = persona_data.get('target_audience', {})
        if target_audience:
            audience_parts = []
            if target_audience.get('age_range'):
                audience_parts.append(f"Idade: {target_audience['age_range']}")
            if target_audience.get('interests'):
                audience_parts.append(
                    f"Interesses: {', '.join(target_audience['interests'][:5])}")
            if target_audience.get('location'):
                audience_parts.append(
                    f"Localização: {target_audience['location']}")

            if audience_parts:
                context_parts.append(
                    f"PÚBLICO-ALVO: {' | '.join(audience_parts)}")

        # Diretrizes de conteúdo
        content_guidelines = persona_data.get('content_guidelines', {})
        if content_guidelines:
            content_parts = []
            if content_guidelines.get('topics'):
                content_parts.append(
                    f"Temas: {', '.join(content_guidelines['topics'][:5])}")
            if content_guidelines.get('hashtags'):
                content_parts.append(
                    f"Hashtags: {', '.join(content_guidelines['hashtags'][:10])}")
            if content_guidelines.get('call_to_actions'):
                content_parts.append(
                    f"CTAs: {', '.join(content_guidelines['call_to_actions'][:3])}")

            if content_parts:
                context_parts.append(
                    f"DIRETRIZES: {' | '.join(content_parts)}")

        return "\\n".join(context_parts)

    async def _get_relevant_context(self, persona_id: int, query: str) -> str:
        """Recupera contexto relevante do banco vetorial (RAG)"""
        try:
            # Buscar documentos similares
            similar_docs = await vector_store.search_similar_content(
                persona_id=persona_id,
                query=query,
                n_results=settings.TOP_K_RETRIEVAL
            )

            if not similar_docs:
                return ""

            # Construir contexto
            context_parts = ["CONTEXTO DA BASE DE CONHECIMENTO:"]

            # Limitar a 3 documentos
            for i, doc in enumerate(similar_docs[:3], 1):
                content = doc['content'][:500]  # Limitar tamanho
                metadata = doc.get('metadata', {})

                doc_info = f"Documento {i}"
                if metadata.get('title'):
                    doc_info += f" - {metadata['title']}"

                context_parts.append(f"{doc_info}:")
                context_parts.append(content)
                context_parts.append("---")

            return "\\n".join(context_parts)

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar contexto RAG: {e}")
            return ""

    async def generate_instagram_caption(
        self,
        persona_data: Dict[str, Any],
        topic: str,
        style: str = "engajamento",
        include_hashtags: bool = True
    ) -> Dict[str, Any]:
        """
        Gera legenda para post do Instagram

        Args:
            persona_data: Dados da persona
            topic: Tópico/tema do post
            style: Estilo da legenda (engajamento, informativo, storytelling)
            include_hashtags: Se deve incluir hashtags

        Returns:
            Dict com legenda, hashtags e metadados
        """
        try:
            # Construir contexto da persona
            persona_context = self._build_persona_context(persona_data)

            # Recuperar contexto RAG
            rag_context = await self._get_relevant_context(
                persona_data.get('id'),
                topic
            )

        # Construir prompt
            prompt = f"""
Você é um especialista em criação de conteúdo para Instagram. Sua tarefa é gerar uma legenda autêntica e envolvente baseada na persona e contexto fornecidos.

{persona_context}

{rag_context}

TAREFA: Criar legenda para Instagram sobre "{topic}"
ESTILO: {style}
INCLUIR HASHTAGS: {"Sim" if include_hashtags else "Não"}

INSTRUÇÕES:
1. Mantenha o tom de voz da persona
2. Considere o público-alvo específico
3. Use o contexto da base de conhecimento quando relevante
4. A legenda deve ser natural e autêntica
5. Se incluir hashtags, misture hashtags populares e de nicho
6. Use emojis conforme as preferências da persona
7. Inclua uma call-to-action apropriada

FORMATO DE RESPOSTA (JSON):
{{
    "caption": "Legenda principal aqui...",
    "hashtags": ["#hashtag1", "#hashtag2", "..."],
    "call_to_action": "Call to action específica",
    "emoji_suggestions": ["😊", "🚀", "..."],
    "tone_analysis": "análise do tom usado"
}}

Gere apenas o JSON, sem texto adicional.
"""

            # Gerar resposta usando provider configurado
            response_text = await self._generate_text(prompt)

            # Tentar parsear JSON
            try:
                result = json.loads(response_text)

                # Adicionar metadados
                result['generated_at'] = datetime.now().isoformat()
                result[
                    'model_used'] = f"{self.provider}:{settings.DEFAULT_MODEL if self.provider == 'google' else self.model.get('model', 'unknown')}"
                result['persona_id'] = persona_data.get('id')
                result['topic'] = topic
                result['style'] = style

                logger.info(
                    f"✅ Legenda gerada para persona {persona_data.get('id')}")
                return result

            except json.JSONDecodeError:
                # Fallback se não conseguir parsear JSON
                return {
                    "caption": response_text,
                    "hashtags": [],
                    "call_to_action": "",
                    "emoji_suggestions": [],
                    "tone_analysis": "Geração em texto livre",
                    "generated_at": datetime.now().isoformat(),
                    "model_used": f"{self.provider}",
                    "persona_id": persona_data.get('id'),
                    "topic": topic,
                    "style": style
                }

        except Exception as e:
            logger.error(f"❌ Erro ao gerar legenda: {e}")
            raise

    async def generate_content_ideas(
        self,
        persona_data: Dict[str, Any],
        content_type: str = "posts",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Gera ideias de conteúdo baseadas na persona

        Args:
            persona_data: Dados da persona
            content_type: Tipo de conteúdo (posts, stories, reels)
            count: Número de ideias a gerar

        Returns:
            List[Dict]: Lista de ideias de conteúdo
        """
        try:
            # Construir contexto da persona
            persona_context = self._build_persona_context(persona_data)

            # Recuperar contexto geral da base de conhecimento
            rag_context = await self._get_relevant_context(
                persona_data.get('id'),
                "conteúdo marca estratégia"
            )

            # Construir prompt
            prompt = f"""
Você é um estrategista de conteúdo para Instagram. Gere {count} ideias criativas de {content_type} baseadas na persona.

{persona_context}

{rag_context}

INSTRUÇÕES:
1. Ideias devem estar alinhadas com a persona
2. Considere tendências atuais do Instagram
3. Foque no público-alvo especificado
4. Varie entre diferentes tipos de engajamento
5. Use insights da base de conhecimento quando possível

FORMATO DE RESPOSTA (JSON):
{{
    "ideas": [
        {{
            "title": "Título da ideia",
            "description": "Descrição detalhada",
            "content_type": "tipo específico",
            "engagement_goal": "objetivo de engajamento",
            "key_elements": ["elemento1", "elemento2"],
            "trending_potential": "alto/médio/baixo"
        }}
    ]
}}

Gere apenas o JSON, sem texto adicional.
"""

            # Gerar resposta
            response_text = await self._generate_text(prompt)

            # Parsear resposta
            try:
                result = json.loads(response_text)

                # Adicionar metadados a cada ideia
                for idea in result.get('ideas', []):
                    idea['generated_at'] = datetime.now().isoformat()
                    idea['persona_id'] = persona_data.get('id')

                logger.info(f"✅ {len(result.get('ideas', []))} ideias geradas")
                return result.get('ideas', [])

            except json.JSONDecodeError:
                logger.error("❌ Erro ao parsear JSON das ideias")
                return []

        except Exception as e:
            logger.error(f"❌ Erro ao gerar ideias de conteúdo: {e}")
            raise

    async def analyze_content_performance(
        self,
        content_data: Dict[str, Any],
        persona_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa a performance de um conteúdo e sugere melhorias
        """
        # Implementação futura para análise de performance
        # Por enquanto, retorna estrutura básica
        return {
            "analysis": "Análise não implementada ainda",
            "suggestions": [],
            "score": 0.0
        }


# Instância global
ai_service = AIService()
