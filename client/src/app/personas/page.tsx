/**
 * Página de Listagem de Personas
 */

'use client';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import Navbar from '@/components/common/Navbar';
import { useAuth } from '@/contexts/AuthContext';
import personaService, { Persona } from '@/lib/services/personaService';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function PersonasPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const data = await personaService.list();
        setPersonas(data);
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar personas');
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchPersonas();
    }
  }, [isAuthenticated]);

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja deletar esta persona?')) {
      return;
    }

    try {
      await personaService.delete(id);
      setPersonas(personas.filter((p) => p.id !== id));
    } catch (err: any) {
      alert(err.message || 'Erro ao deletar persona');
    }
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Minhas Personas</h1>
            <p className="mt-2 text-sm text-gray-600">
              Gerencie as identidades de marca para geração de conteúdo
            </p>
          </div>
          <Link
            href="/personas/new"
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Nova Persona
          </Link>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        ) : personas.length === 0 ? (
          <div className="rounded-lg bg-gray-50 p-12 text-center">
            <span className="text-6xl">👤</span>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Nenhuma persona criada
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Comece criando sua primeira persona para gerar conteúdo personalizado
            </p>
            <Link
              href="/personas/new"
              className="mt-4 inline-block rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Criar Primeira Persona
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {personas.map((persona) => (
              <div
                key={persona.id}
                className="relative rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {persona.name}
                  </h3>
                  <span
                    className={`rounded-full px-2 py-1 text-xs ${
                      persona.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {persona.is_active ? 'Ativa' : 'Inativa'}
                  </span>
                </div>

                <p className="mt-2 line-clamp-3 text-sm text-gray-600">
                  {persona.description || 'Sem descrição'}
                </p>

                {/* Info */}
                <div className="mt-4 space-y-2">
                  {persona.brand_voice?.tone && (
                    <div className="flex items-center text-xs text-gray-500">
                      <span className="mr-2">🎭</span>
                      Tom: {persona.brand_voice.tone}
                    </div>
                  )}
                  {persona.target_audience?.age_range && (
                    <div className="flex items-center text-xs text-gray-500">
                      <span className="mr-2">🎯</span>
                      Público: {persona.target_audience.age_range}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="mt-6 flex gap-2">
                  <Link
                    href={`/personas/${persona.id}`}
                    className="flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-center text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Ver Detalhes
                  </Link>
                  <button
                    onClick={() => handleDelete(persona.id)}
                    className="rounded-md border border-red-300 bg-white px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50"
                  >
                    Deletar
                  </button>
                </div>

                <div className="mt-2 text-xs text-gray-400">
                  Criada em {new Date(persona.created_at).toLocaleDateString('pt-BR')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
