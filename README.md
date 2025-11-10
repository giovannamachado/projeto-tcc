# 🚀 IA Generativa para Conteúdo de Instagram# 🚀 IA Generativa para Conteúdo de Mídia Social - TCC



Sistema web de **Inteligência Artificial Generativa** com arquitetura **RAG (Retrieval-Augmented Generation)** para criação personalizada de conteúdo para Instagram.> **Aplicação de Inteligência Artificial Generativa para Criação Personalizada de Conteúdo em Redes Sociais: Um Estudo Focado no Instagram**



[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)

[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)

[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)

[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://typescriptlang.org)[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://typescriptlang.org)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📝 Sobre

## 📝 Sobre o Projeto

Aplicação que permite criar conteúdo personalizado para Instagram usando IA. O sistema aprende com documentos da marca (manual de identidade, posts anteriores, etc.) e gera legendas, hashtags e ideias de posts mantendo a voz única da marca.

Sistema web que utiliza **Inteligência Artificial Generativa** com arquitetura **RAG (Retrieval-Augmented Generation)** para criação personalizada e autêntica de conteúdo para Instagram. Permite que criadores de conteúdo e marcas gerem posts alinhados com sua identidade visual e tom de voz únicos.

**Principais funcionalidades:**

- 👤 Gestão de personas de marca### � Problema Resolvido

- 📚 Base de conhecimento com documentos- **Dificuldade de manter consistência** na criação de conteúdo

- 🤖 Geração de legendas e hashtags- **Tempo excessivo** gasto na criação de legendas e hashtags

- 🔐 Sistema de autenticação seguro- **Falta de personalização** em ferramentas genéricas de IA

- **Necessidade de contextualizar** a IA com a identidade da marca

## 🛠️ Tecnologias

### 💡 Solução Proposta

**Backend:** Python, FastAPI, ChromaDB, SQLAlchemy  - **Personas Personalizáveis** para definir identidade da marca

**Frontend:** Next.js 14, TypeScript, Tailwind CSS  - **Base de Conhecimento** com documentos da empresa

**IA:** Google Gemini Pro  - **Sistema RAG** para contextualização inteligente

- **Geração Multimodal** de textos e hashtags

## 🚀 Como executar

## 🏗️ Arquitetura Técnica

### Pré-requisitos

- Node.js 18+```mermaid

- Python 3.11+graph TB

- Google AI API Key ([obter aqui](https://makersuite.google.com/app/apikey))    A[👤 Usuário] --> B[🌐 Frontend Next.js]

    B --> C[🔌 API FastAPI]

### Instalação    C --> D[🧠 Google Gemini Pro]

    C --> E[📊 ChromaDB Vetorial]

1. **Clone o repositório**    C --> F[🗄️ SQLite/PostgreSQL]

```bash

git clone <seu-repositorio>    subgraph "🤖 Sistema RAG"

cd projeto-tcc        E --> G[📄 Documentos]

```        G --> H[🔍 Busca Semântica]

        H --> I[📝 Contexto]

2. **Configure as variáveis de ambiente**        I --> D

```bash    end

# Backend

cp server/.env.example server/.env    subgraph "🛡️ Segurança"

# Edite server/.env e adicione sua GOOGLE_API_KEY        J[🔑 JWT Tokens]

        K[🔐 API Keys Env]

# Frontend        L[✅ Validação Pydantic]

cp client/.env.example client/.env.local    end

``````



3. **Inicie o backend**## 🌟 Funcionalidades Implementadas

```bash

cd server### ✅ Core Features

python -m venv venv- **👤 Gestão de Personas** - Definição completa de identidade de marca

source venv/bin/activate  # Windows: venv\Scripts\activate- **📚 Base de Conhecimento** - Upload e processamento de documentos (PDF, DOCX, TXT, MD)

pip install -r requirements.txt- **🤖 Geração de Conteúdo** - Legendas, hashtags e ideias personalizadas

uvicorn main:app --reload- **🔍 Sistema RAG** - Contextualização baseada na base de conhecimento

```- **🔐 Autenticação JWT** - Sistema seguro de login e autorização

- **📊 API RESTful** - Documentação automática com Swagger/OpenAPI

4. **Inicie o frontend** (em outro terminal)

```bash### 🛡️ Segurança Implementada

cd client- **Chaves API** gerenciadas via variáveis de ambiente

npm install- **Headers de segurança** configurados (CORS, XSS, etc.)

npm run dev- **Validação rigorosa** de dados com Pydantic

```- **Autenticação JWT** com tokens seguros

- **Rate limiting** e proteção contra ataques

5. **Acesse a aplicação**

- Frontend: http://localhost:3000## 🛠️ Stack Tecnológica

- API: http://localhost:8000

- Docs: http://localhost:8000/docs| Componente | Tecnologia | Justificativa |

|------------|------------|---------------|

## 📂 Estrutura| **Frontend** | Next.js 14 + TypeScript | Framework React moderno, SSR/SSG, excelente DX |

| **Backend** | Python + FastAPI | Performance excepcional, ideal para IA/ML |

```| **Banco Vetorial** | ChromaDB | Open-source, fácil setup, perfeito para RAG |

projeto-tcc/| **IA Generativa** | Google Gemini Pro | API robusta, custo acessível, ótima para texto |

├── server/              # Backend FastAPI| **Database** | SQLite → PostgreSQL | Desenvolvimento rápido → Produção escalável |

│   ├── src/| **Estilização** | Tailwind CSS + Shadcn/ui | Design system moderno e consistente |

│   │   ├── api/        # Rotas da API| **Deploy** | Vercel + Railway | Platforms gratuitas com CI/CD automático |

│   │   ├── core/       # Configurações

│   │   ├── models/     # Modelos do banco## 🚀 Quick Start

│   │   ├── schemas/    # Validação

│   │   └── services/   # Lógica de negócio### 📋 Pré-requisitos

│   └── main.py```bash

│# Ferramentas necessárias

└── client/             # Frontend Next.jsNode.js 18+     # https://nodejs.org/

    └── src/Python 3.11+    # https://python.org/

        ├── app/        # PáginasGit             # https://git-scm.com/

        ├── components/ # Componentes React

        └── lib/        # Utilitários# Chave de API necessária

```Google AI API Key  # https://makersuite.google.com/app/apikey

```

## 📄 Licença

### ⚡ Setup Rápido

MIT License

```bash

---# 1. Clone o repositório

git clone <seu-repositorio>

**Trabalho de Conclusão de Curso**  cd projeto-tcc

Sistemas de Informação | 2024

# 2. Configure ambiente
cp .env.example .env
cp client/.env.example client/.env.local
# Edite os arquivos .env com sua chave do Gemini Pro

# 3. Backend (Terminal 1)
cd server
python -m venv venv
venv\Scripts\activate  # Windows | source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Frontend (Terminal 2)
cd client
npm install
npm run dev
```

### 🌐 Acessar Aplicação
- **Frontend:** http://localhost:3000
- **API Backend:** http://localhost:8000
- **Documentação:** http://localhost:8000/docs

## 📂 Estrutura do Projeto

```
projeto-tcc/
├── 📁 server/                    # 🐍 Backend Python FastAPI
│   ├── 📁 src/
│   │   ├── 📁 api/routes/       # 🛣️ Endpoints da API
│   │   ├── 📁 core/             # ⚙️ Configurações centrais
│   │   ├── 📁 models/           # 🗃️ Modelos SQLAlchemy
│   │   ├── 📁 schemas/          # ✅ Validação Pydantic
│   │   └── 📁 services/         # 🧠 Lógica de negócio
│   ├── 📄 main.py              # 🚀 Ponto de entrada
│   └── 📄 requirements.txt     # 📦 Dependências Python
│
├── 📁 client/                   # ⚛️ Frontend Next.js
│   ├── 📁 src/
│   │   ├── 📁 app/             # 📱 App Router Next.js 13+
│   │   ├── 📁 components/      # 🧩 Componentes React
│   │   ├── 📁 lib/             # 🔧 Utilitários
│   │   ├── 📁 hooks/           # 🪝 Custom Hooks
│   │   ├── 📁 services/        # 🌐 Chamadas API
│   │   └── 📁 store/           # 🏪 Estado Global
│   └── 📄 package.json        # 📦 Dependências Node.js
│
├── 📄 README.md               # 📚 Este arquivo
├── 📄 DEPLOY.md              # 🚀 Guia de deploy
├── 📄 DEVELOPMENT.md         # 🛠️ Guia de desenvolvimento
├── 📄 RESUMO_EXECUTIVO.md    # 📊 Resumo técnico
└── 📄 .gitignore             # 🚫 Arquivos ignorados
```

## 🔧 Principais Comandos

### Backend
```bash
# Desenvolvimento
uvicorn main:app --reload

# Testes
pytest

# Formatação
black src/

# Type checking
mypy src/
```

### Frontend
```bash
# Desenvolvimento
npm run dev

# Build produção
npm run build

# Linting
npm run lint

# Testes
npm test
```

## 📊 Demonstração de Uso

### 1. Criação de Persona
```json
{
  "name": "Marca Fitness",
  "brand_voice": {
    "traits": ["motivacional", "amigável", "técnico"],
    "tone": "inspirador"
  },
  "target_audience": {
    "age_range": "25-40",
    "interests": ["fitness", "saúde", "bem-estar"]
  }
}
```

### 2. Upload de Base de Conhecimento
- 📄 Manual de marca (PDF)
- 📋 Posts anteriores (DOCX)
- 📝 Diretrizes de conteúdo (TXT)

### 3. Geração de Conteúdo
```json
{
  "persona_id": 1,
  "topic": "novo treino funcional",
  "style": "motivacional"
}
```

**Resultado:**
```
💪 Que tal revolucionar seu treino hoje?

Nosso novo programa de treino funcional vai te desafiar
de uma forma completamente nova! 🔥

Exercícios que trabalham músculos que você nem sabia
que existiam. Prepare-se para suar e se superar!

👇 Conta pra gente: qual é o seu maior desafio no treino?

#TreinoFuncional #Fitness #Motivacao #VemTreinar
#AcademiaVida #SemLimites #FocoNaForma
```

## 🎯 Diferencial Técnico

### 🧠 Sistema RAG Avançado
- **Contextualização Inteligente:** IA considera documentos da marca
- **Busca Semântica:** ChromaDB encontra conteúdo relevante
- **Personalização Profunda:** Cada geração é única da marca

### �️ Segurança Robusta
- **API Keys Protegidas:** Jamais expostas no frontend
- **Autenticação JWT:** Tokens seguros com expiração
- **Validação Rigorosa:** Pydantic + TypeScript

### 📈 Arquitetura Escalável
- **Microserviços:** Frontend e backend independentes
- **Cache Inteligente:** Respostas otimizadas
- **Deploy Automatizado:** CI/CD com Vercel e Railway

## 💰 Análise de Custos

### 🆓 Protótipo Acadêmico
- **Frontend (Vercel):** Gratuito
- **Backend (Railway):** $5/mês
- **Gemini Pro API:** Gratuito (60 req/min)
- **ChromaDB:** Gratuito (self-hosted)
- **Total:** $0-5/mês ✅

### 💼 Viabilidade Comercial
- **MVP:** $50-200/mês
- **Scale-up:** $200-1000/mês
- **Enterprise:** $1000+/mês

## � Resultado Acadêmico

### 📚 Contribuições Técnicas
1. **Implementação prática de RAG** em ambiente de produção
2. **Integração de múltiplas APIs de IA** em sistema coeso
3. **Arquitetura moderna full-stack** com boas práticas
4. **Estudo de caso real** de IA aplicada ao marketing digital

### 🎓 Objetivos de Aprendizado Atingidos
- ✅ **Desenvolvimento Full-Stack** com tecnologias modernas
- ✅ **Integração de IA** em aplicações reais
- ✅ **Arquitetura de Software** escalável e mantível
- ✅ **DevOps e Deploy** automatizado
- ✅ **Segurança de Aplicações** web

## 🚀 Deploy em Produção

### 📖 Guias Completos Disponíveis
- **[DEPLOY.md](DEPLOY.md)** - Guia completo de deploy
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup de desenvolvimento
- **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)** - Análise técnica detalhada

### 🌐 Plataformas Recomendadas
- **Frontend:** Vercel (gratuito)
- **Backend:** Railway ($5/mês)
- **Database:** PostgreSQL (Railway incluso)
- **Monitoring:** Gratuito com Railway

## 🔮 Roadmap Futuro

### 🎯 Próximas Funcionalidades
- [ ] **Geração de Imagens** (Stable Diffusion/DALL-E)
- [ ] **Analytics de Performance**
- [ ] **A/B Testing** de conteúdo
- [ ] **Agendamento** de posts
- [ ] **Multi-plataforma** (TikTok, LinkedIn)

### 🛠️ Melhorias Técnicas
- [ ] **Cache Redis** para performance
- [ ] **Monitoring completo** (Sentry, DataDog)
- [ ] **Testes automatizados** (>80% coverage)
- [ ] **CI/CD avançado** (GitHub Actions)

## 📞 Suporte e Contato

### 🐛 Issues e Bugs
Abra uma issue no repositório com:
- Descrição do problema
- Steps para reproduzir
- Screenshots se relevante

### 💬 Dúvidas Acadêmicas
- **Orientador:** [Nome do Professor]
- **Instituição:** [Sua Universidade]
- **Curso:** Sistemas de Informação

### 🤝 Contribuições
Contributions são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines.

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

**🎓 Desenvolvido como Trabalho de Conclusão de Curso**

**Sistemas de Informação | 2024**

[![GitHub](https://img.shields.io/badge/GitHub-Perfil-black?logo=github)](https://github.com/seu-usuario)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-blue?logo=linkedin)](https://linkedin.com/in/seu-perfil)

</div>