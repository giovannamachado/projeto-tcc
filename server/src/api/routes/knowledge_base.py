"""
Rotas para gerenciamento da base de conhecimento.
Upload, processamento e gerenciamento de documentos para contextualização RAG.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid
from pathlib import Path
import aiofiles
import os

from ...core.database import get_db
from ...core.config import settings
from ...models.user import User
from ...models.persona import Persona
from ...models.knowledge_base import KnowledgeBase, ProcessingStatus
from ...services.document_processor import document_processor
from ...services.vector_store import vector_store
from ..routes.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_knowledge_base_by_id(db: Session, kb_id: int, user_id: int) -> Optional[KnowledgeBase]:
    """Busca documento da base de conhecimento por ID"""
    return db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.owner_id == user_id
    ).first()

def validate_knowledge_base_ownership(kb: KnowledgeBase, user: User):
    """Valida se o documento pertence ao usuário"""
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )

    if kb.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este documento"
        )

def get_user_persona(db: Session, persona_id: int, user_id: int) -> Persona:
    """Obtém persona do usuário"""
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.owner_id == user_id
    ).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona não encontrada"
        )

    return persona

async def save_uploaded_file(file: UploadFile) -> Path:
    """Salva arquivo enviado no sistema de arquivos"""
    # Gerar nome único para o arquivo
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = settings.upload_path / unique_filename

    # Salvar arquivo
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    return file_path

async def process_document_async(kb_id: int, file_path: Path, db: Session):
    """Processa documento de forma assíncrona"""
    try:
        # Buscar registro do banco
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb:
            logger.error(f"❌ Knowledge base {kb_id} não encontrada para processamento")
            return

        # Atualizar status para processando
        kb.processing_status = ProcessingStatus.PROCESSING.value
        db.commit()

        # Processar documento
        logger.info(f"🔄 Iniciando processamento do documento {kb.title}")

        result = await document_processor.process_document(
            file_path,
            metadata={
                'title': kb.title,
                'description': kb.description,
                'persona_id': kb.persona_id,
                'kb_id': kb.id
            }
        )

        if not result['success']:
            # Erro no processamento
            kb.processing_status = ProcessingStatus.FAILED.value
            kb.processing_error = result.get('error', 'Erro desconhecido')
            db.commit()
            logger.error(f"❌ Falha no processamento do documento {kb.title}: {result.get('error')}")
            return

        # Atualizar metadados do documento
        kb.word_count = result['metadata'].get('word_count', 0)
        kb.chunk_count = result['metadata'].get('chunk_count', 0)

        # Adicionar ao banco vetorial
        vector_store_id = f"kb_{kb.id}_{uuid.uuid4().hex[:8]}"

        success = await vector_store.add_document(
            persona_id=kb.persona_id,
            document_id=vector_store_id,
            text_chunks=result['chunks'],
            metadata={
                **result['metadata'],
                'title': kb.title,
                'description': kb.description,
                'kb_id': kb.id
            }
        )

        if success:
            # Sucesso completo
            kb.processing_status = ProcessingStatus.COMPLETED.value
            kb.vector_store_id = vector_store_id
            kb.processing_error = None

            from datetime import datetime
            kb.processed_at = datetime.utcnow()

            logger.info(f"✅ Documento {kb.title} processado com sucesso")
        else:
            # Erro na vetorização
            kb.processing_status = ProcessingStatus.FAILED.value
            kb.processing_error = "Erro ao adicionar documento ao banco vetorial"
            logger.error(f"❌ Erro na vetorização do documento {kb.title}")

        db.commit()

    except Exception as e:
        logger.error(f"❌ Erro no processamento assíncrono: {e}")
        # Atualizar status de erro
        try:
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
            if kb:
                kb.processing_status = ProcessingStatus.FAILED.value
                kb.processing_error = str(e)
                db.commit()
        except:
            pass

# =============================================================================
# ROTAS DE UPLOAD E PROCESSAMENTO
# =============================================================================

@router.post("/upload", summary="Upload de documento para base de conhecimento")
async def upload_document(
    persona_id: int = Form(..., description="ID da persona"),
    title: str = Form(..., description="Título do documento"),
    description: Optional[str] = Form(None, description="Descrição do documento"),
    file: UploadFile = File(..., description="Arquivo a ser processado"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Faz upload de um documento para a base de conhecimento
    """
    try:
        # Validar persona
        persona = get_user_persona(db, persona_id, current_user.id)

        # Validar arquivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo é obrigatório"
            )

        # Verificar extensão
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado. Extensões permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Verificar tamanho
        file_size = 0
        content = await file.read()
        file_size = len(content)

        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo muito grande. Tamanho máximo: {settings.MAX_FILE_SIZE_MB}MB"
            )

        # Recriar o arquivo para salvar
        await file.seek(0)

        # Salvar arquivo
        file_path = await save_uploaded_file(file)

        # Criar registro na base de dados
        kb = KnowledgeBase(
            title=title,
            description=description,
            persona_id=persona_id,
            owner_id=current_user.id,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_extension,
            processing_status=ProcessingStatus.PENDING.value
        )

        db.add(kb)
        db.commit()
        db.refresh(kb)

        # Iniciar processamento em background
        import asyncio
        asyncio.create_task(process_document_async(kb.id, file_path, db))

        logger.info(f"📁 Upload realizado: {file.filename} -> {title} (ID: {kb.id})")

        return {
            "id": kb.id,
            "title": kb.title,
            "file_name": kb.file_name,
            "file_size_mb": kb.file_size_mb,
            "status": kb.processing_status,
            "message": "Upload realizado com sucesso. Processamento iniciado."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no upload do arquivo"
        )

# =============================================================================
# ROTAS DE LISTAGEM E CONSULTA
# =============================================================================

@router.get("/", summary="Listar documentos da base de conhecimento")
async def list_knowledge_base(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    persona_id: Optional[int] = Query(None, description="Filtrar por persona"),
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Lista documentos da base de conhecimento do usuário
    """
    query = db.query(KnowledgeBase).filter(KnowledgeBase.owner_id == current_user.id)

    if persona_id:
        # Validar se persona pertence ao usuário
        persona = get_user_persona(db, persona_id, current_user.id)
        query = query.filter(KnowledgeBase.persona_id == persona_id)

    if status_filter:
        query = query.filter(KnowledgeBase.processing_status == status_filter)

    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(KnowledgeBase.created_at.desc())

    total = query.count()
    documents = query.offset(skip).limit(limit).all()

    # Preparar resposta com informações adicionais
    documents_data = []
    for doc in documents:
        doc_data = {
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "file_name": doc.file_name,
            "file_size_mb": doc.file_size_mb,
            "file_type": doc.file_type,
            "processing_status": doc.processing_status,
            "processing_error": doc.processing_error,
            "word_count": doc.word_count,
            "chunk_count": doc.chunk_count,
            "usage_count": doc.usage_count,
            "relevance_score": doc.relevance_score,
            "persona_id": doc.persona_id,
            "persona_name": doc.persona.name if doc.persona else None,
            "created_at": doc.created_at,
            "processed_at": doc.processed_at,
            "is_processed": doc.is_processed,
            "is_processing": doc.is_processing,
            "has_error": doc.has_error
        }
        documents_data.append(doc_data)

    return {
        "documents": documents_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{kb_id}", summary="Obter documento específico")
async def get_knowledge_base_document(
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém informações detalhadas de um documento
    """
    kb = get_knowledge_base_by_id(db, kb_id, current_user.id)
    validate_knowledge_base_ownership(kb, current_user)

    # Obter estatísticas do banco vetorial se processado
    vector_stats = None
    if kb.is_processed and kb.vector_store_id:
        try:
            vector_stats = await vector_store.get_collection_stats(kb.persona_id)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter estatísticas vetoriais: {e}")

    return {
        "id": kb.id,
        "title": kb.title,
        "description": kb.description,
        "file_name": kb.file_name,
        "file_size_mb": kb.file_size_mb,
        "file_type": kb.file_type,
        "processing_status": kb.processing_status,
        "processing_error": kb.processing_error,
        "word_count": kb.word_count,
        "chunk_count": kb.chunk_count,
        "usage_count": kb.usage_count,
        "relevance_score": kb.relevance_score,
        "embedding_model": kb.embedding_model,
        "vector_store_id": kb.vector_store_id,
        "persona_id": kb.persona_id,
        "persona_name": kb.persona.name if kb.persona else None,
        "created_at": kb.created_at,
        "updated_at": kb.updated_at,
        "processed_at": kb.processed_at,
        "is_processed": kb.is_processed,
        "is_processing": kb.is_processing,
        "has_error": kb.has_error,
        "vector_stats": vector_stats
    }

# =============================================================================
# ROTAS DE GERENCIAMENTO
# =============================================================================

@router.put("/{kb_id}", summary="Atualizar informações do documento")
async def update_knowledge_base_document(
    kb_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza título e descrição de um documento
    """
    kb = get_knowledge_base_by_id(db, kb_id, current_user.id)
    validate_knowledge_base_ownership(kb, current_user)

    # Campos permitidos para atualização
    allowed_fields = {'title', 'description', 'is_active'}

    for field, value in update_data.items():
        if field in allowed_fields and value is not None:
            setattr(kb, field, value)

    db.commit()
    db.refresh(kb)

    logger.info(f"✅ Documento atualizado: {kb.title} (ID: {kb.id})")

    return {"message": "Documento atualizado com sucesso"}

@router.delete("/{kb_id}", summary="Deletar documento")
async def delete_knowledge_base_document(
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta um documento da base de conhecimento
    """
    try:
        kb = get_knowledge_base_by_id(db, kb_id, current_user.id)
        validate_knowledge_base_ownership(kb, current_user)

        # Remover do banco vetorial
        if kb.vector_store_id:
            try:
                await vector_store.delete_document(kb.persona_id, kb.vector_store_id)
                logger.info(f"🧹 Dados vetoriais removidos para documento {kb.title}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao remover dados vetoriais: {e}")

        # Remover arquivo físico
        if kb.file_path and os.path.exists(kb.file_path):
            try:
                os.remove(kb.file_path)
                logger.info(f"🗑️ Arquivo físico removido: {kb.file_path}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao remover arquivo físico: {e}")

        # Remover registro do banco
        db.delete(kb)
        db.commit()

        logger.info(f"🗑️ Documento deletado: {kb.title} (ID: {kb_id})")

        return {"message": "Documento deletado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar documento: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar documento"
        )

# =============================================================================
# ROTAS DE BUSCA E ANÁLISE
# =============================================================================

@router.post("/{kb_id}/search", summary="Buscar conteúdo no documento")
async def search_in_document(
    kb_id: int,
    search_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca conteúdo específico dentro de um documento
    """
    kb = get_knowledge_base_by_id(db, kb_id, current_user.id)
    validate_knowledge_base_ownership(kb, current_user)

    if not kb.is_processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Documento ainda não foi processado"
        )

    query = search_data.get('query', '')
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query de busca é obrigatória"
        )

    # Buscar no banco vetorial
    try:
        results = await vector_store.search_similar_content(
            persona_id=kb.persona_id,
            query=query,
            n_results=search_data.get('limit', 5),
            filter_metadata={'kb_id': kb.id}
        )

        # Incrementar contador de uso
        kb.increment_usage()
        db.commit()

        return {
            "query": query,
            "document_title": kb.title,
            "results_count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"❌ Erro na busca: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na busca"
        )

@router.get("/stats/overview", summary="Estatísticas gerais da base de conhecimento")
async def get_knowledge_base_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais da base de conhecimento do usuário
    """
    # Estatísticas básicas
    total_docs = db.query(KnowledgeBase).filter(KnowledgeBase.owner_id == current_user.id).count()

    processed_docs = db.query(KnowledgeBase).filter(
        KnowledgeBase.owner_id == current_user.id,
        KnowledgeBase.processing_status == ProcessingStatus.COMPLETED.value
    ).count()

    processing_docs = db.query(KnowledgeBase).filter(
        KnowledgeBase.owner_id == current_user.id,
        KnowledgeBase.processing_status == ProcessingStatus.PROCESSING.value
    ).count()

    failed_docs = db.query(KnowledgeBase).filter(
        KnowledgeBase.owner_id == current_user.id,
        KnowledgeBase.processing_status == ProcessingStatus.FAILED.value
    ).count()

    # Estatísticas por persona
    personas_stats = []
    personas = db.query(Persona).filter(Persona.owner_id == current_user.id).all()

    for persona in personas:
        persona_docs = db.query(KnowledgeBase).filter(
            KnowledgeBase.persona_id == persona.id
        ).count()

        personas_stats.append({
            "persona_id": persona.id,
            "persona_name": persona.name,
            "documents_count": persona_docs
        })

    # Estatísticas de uso
    total_usage = db.query(KnowledgeBase).filter(
        KnowledgeBase.owner_id == current_user.id
    ).with_entities(
        db.func.sum(KnowledgeBase.usage_count)
    ).scalar() or 0

    total_words = db.query(KnowledgeBase).filter(
        KnowledgeBase.owner_id == current_user.id
    ).with_entities(
        db.func.sum(KnowledgeBase.word_count)
    ).scalar() or 0

    return {
        "summary": {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "processing_documents": processing_docs,
            "failed_documents": failed_docs,
            "processing_rate": round((processed_docs / total_docs * 100) if total_docs > 0 else 0, 1)
        },
        "usage": {
            "total_searches": total_usage,
            "total_words": total_words,
            "average_usage_per_doc": round(total_usage / processed_docs if processed_docs > 0 else 0, 1)
        },
        "by_persona": personas_stats,
        "file_types": [
            {"type": ext, "supported": True}
            for ext in settings.ALLOWED_EXTENSIONS
        ]
    }