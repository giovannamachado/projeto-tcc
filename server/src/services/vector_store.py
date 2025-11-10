"""
Serviço de banco vetorial usando ChromaDB.
Implementa a funcionalidade RAG (Retrieval-Augmented Generation) para contextualizar
a geração de conteúdo com base na base de conhecimento do usuário.
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import uuid
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

from ..core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Serviço para gerenciar o banco vetorial ChromaDB

    Responsável por:
    - Armazenar embeddings de documentos
    - Buscar conteúdo relevante por similaridade
    - Gerenciar coleções por persona
    - Otimizar recuperação de contexto para RAG
    """

    def __init__(self):
        self.client = None
        self.collections = {}
        self.embedding_function = None

    async def initialize(self):
        """Inicializa o cliente ChromaDB"""
        try:
            # Configurar ChromaDB
            chroma_settings = Settings(
                persist_directory=str(settings.chroma_path),
                anonymized_telemetry=False
            )

            # Criar cliente persistente
            self.client = chromadb.PersistentClient(
                path=str(settings.chroma_path),
                settings=chroma_settings
            )

            # Configurar função de embedding (Sentence Transformers local)
            # Usa um modelo leve e gratuito por padrão, evitando custos por requisição
            # Modelos possíveis: 'all-MiniLM-L6-v2' (rápido) ou 'multi-qa-MiniLM-L6-cos-v1'
            self.embedding_function = SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )

            logger.info(f"✅ ChromaDB inicializado em: {settings.chroma_path}")

        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
            raise

    def get_collection_name(self, persona_id: int) -> str:
        """Gera nome da coleção para uma persona específica"""
        return f"persona_{persona_id}_knowledge"

    async def get_or_create_collection(self, persona_id: int):
        """Obtém ou cria uma coleção para uma persona"""
        collection_name = self.get_collection_name(persona_id)

        if collection_name not in self.collections:
            try:
                # Tentar obter/criar coleção garantindo função de embedding configurada
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"persona_id": persona_id}
                )
                logger.info(f"📚 Coleção pronta: {collection_name}")
            except Exception as e:
                logger.error(f"❌ Erro ao obter/criar coleção {collection_name}: {e}")
                raise

            self.collections[collection_name] = collection

        return self.collections[collection_name]

    async def add_document(
        self,
        persona_id: int,
        document_id: str,
        text_chunks: List[str],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Adiciona um documento ao banco vetorial

        Args:
            persona_id: ID da persona
            document_id: ID único do documento
            text_chunks: Lista de chunks de texto
            metadata: Metadados do documento

        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            collection = await self.get_or_create_collection(persona_id)

            # Preparar dados para inserção
            documents = text_chunks
            metadatas = []
            ids = []

            for i, chunk in enumerate(text_chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "document_id": document_id,
                    "chunk_id": chunk_id
                }

                ids.append(chunk_id)
                metadatas.append(chunk_metadata)

            # Adicionar ao ChromaDB
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"✅ Documento {document_id} adicionado com {len(text_chunks)} chunks")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao adicionar documento {document_id}: {e}")
            return False

    async def search_similar_content(
        self,
        persona_id: int,
        query: str,
        n_results: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca conteúdo similar no banco vetorial

        Args:
            persona_id: ID da persona
            query: Texto de busca
            n_results: Número de resultados (padrão: configuração)
            filter_metadata: Filtros de metadados

        Returns:
            List[Dict]: Lista de documentos similares com metadados
        """
        try:
            collection = await self.get_or_create_collection(persona_id)

            if n_results is None:
                n_results = settings.TOP_K_RETRIEVAL

            # Executar busca por similaridade
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )

            # Formatar resultados
            similar_docs = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_docs.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0,
                        'id': results['ids'][0][i] if results['ids'] else None
                    })

            logger.info(f"🔍 Encontrados {len(similar_docs)} documentos similares para persona {persona_id}")
            return similar_docs

        except Exception as e:
            logger.error(f"❌ Erro na busca de similaridade: {e}")
            return []

    async def delete_document(self, persona_id: int, document_id: str) -> bool:
        """
        Remove um documento do banco vetorial

        Args:
            persona_id: ID da persona
            document_id: ID do documento

        Returns:
            bool: True se removido com sucesso
        """
        try:
            collection = await self.get_or_create_collection(persona_id)

            # Buscar todos os chunks do documento
            results = collection.get(
                where={"document_id": document_id}
            )

            if results['ids']:
                # Deletar todos os chunks
                collection.delete(ids=results['ids'])
                logger.info(f"🗑️ Documento {document_id} removido ({len(results['ids'])} chunks)")
                return True
            else:
                logger.warning(f"⚠️ Documento {document_id} não encontrado")
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao deletar documento {document_id}: {e}")
            return False

    async def get_collection_stats(self, persona_id: int) -> Dict[str, Any]:
        """
        Obtém estatísticas da coleção de uma persona

        Returns:
            Dict: Estatísticas da coleção
        """
        try:
            collection = await self.get_or_create_collection(persona_id)

            # Obter contagem de documentos
            count_result = collection.count()

            # Obter alguns metadados para análise
            sample_results = collection.get(limit=10)

            # Calcular estatísticas
            unique_documents = set()
            if sample_results.get('metadatas'):
                for metadata in sample_results['metadatas']:
                    if 'document_id' in metadata:
                        unique_documents.add(metadata['document_id'])

            stats = {
                'total_chunks': count_result,
                'estimated_documents': len(unique_documents),
                'collection_name': self.get_collection_name(persona_id),
                'persona_id': persona_id
            }

            return stats

        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {'error': str(e)}

    async def clear_persona_collection(self, persona_id: int) -> bool:
        """
        Limpa todos os documentos de uma persona

        Args:
            persona_id: ID da persona

        Returns:
            bool: True se limpo com sucesso
        """
        try:
            collection_name = self.get_collection_name(persona_id)

            # Deletar coleção
            self.client.delete_collection(collection_name)

            # Remover do cache
            if collection_name in self.collections:
                del self.collections[collection_name]

            logger.info(f"🧹 Coleção da persona {persona_id} limpa")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao limpar coleção: {e}")
            return False

# Instância global
vector_store = VectorStoreService()

async def init_vector_store():
    """Inicializa o serviço de banco vetorial"""
    await vector_store.initialize()