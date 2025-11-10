/**
 * Página Principal (Home)
 */

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            IA Generativa para
            <span className="text-blue-600"> Instagram</span>
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Crie conteúdo personalizado e autêntico para seu Instagram usando
            Inteligência Artificial. Defina sua persona, adicione sua base de
            conhecimento e gere legendas, hashtags e ideias incríveis.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              href="/register"
              className="rounded-md bg-blue-600 px-8 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Começar Agora
            </Link>
            <Link
              href="/login"
              className="text-base font-semibold leading-7 text-gray-900"
            >
              Fazer Login <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            <div className="flex flex-col">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
                  <span className="text-white">👤</span>
                </div>
                Defina Sua Persona
              </dt>
              <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                <p className="flex-auto">
                  Configure o tom de voz, público-alvo e identidade visual da sua
                  marca para gerar conteúdo 100% alinhado.
                </p>
              </dd>
            </div>

            <div className="flex flex-col">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
                  <span className="text-white">📚</span>
                </div>
                Base de Conhecimento
              </dt>
              <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                <p className="flex-auto">
                  Faça upload de documentos, guias de estilo e posts antigos.
                  Nossa IA usa RAG para contextualizar cada geração.
                </p>
              </dd>
            </div>

            <div className="flex flex-col">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
                  <span className="text-white">🤖</span>
                </div>
                Conteúdo Personalizado
              </dt>
              <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                <p className="flex-auto">
                  Gere legendas, hashtags e ideias de posts em segundos,
                  mantendo a voz única da sua marca.
                </p>
              </dd>
            </div>
          </dl>
        </div>

        {/* CTA Section */}
        <div className="mx-auto mt-16 max-w-2xl text-center sm:mt-20">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Pronto para criar conteúdo autêntico?
          </h2>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Crie sua conta gratuitamente e comece a gerar conteúdo agora mesmo.
          </p>
          <div className="mt-10">
            <Link
              href="/register"
              className="rounded-md bg-blue-600 px-8 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-500"
            >
              Criar Conta Grátis
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
