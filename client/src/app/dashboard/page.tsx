/**
 * Página do Dashboard
 */

'use client';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import Navbar from '@/components/common/Navbar';
import { useAuth } from '@/contexts/AuthContext';
import personaService, { Persona } from '@/lib/services/personaService';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);

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
      } catch (error) {
        console.error('Erro ao carregar personas:', error);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchPersonas();
    }
  }, [isAuthenticated]);

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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Bem-vindo, {user?.full_name}!
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Gerencie suas personas e crie conteúdo incrível para o Instagram
          </p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Link
            href="/personas/new"
            className="flex items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-6 hover:border-blue-500 hover:bg-blue-50"
          >
            <div className="text-center">
              <span className="text-4xl">➕</span>
              <p className="mt-2 font-medium text-gray-900">Nova Persona</p>
              <p className="text-sm text-gray-500">Criar identidade de marca</p>
            </div>
          </Link>

          <Link
            href="/generate"
            className="flex items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-6 hover:border-blue-500 hover:bg-blue-50"
          >
            <div className="text-center">
              <span className="text-4xl">🤖</span>
              <p className="mt-2 font-medium text-gray-900">Gerar Conteúdo</p>
              <p className="text-sm text-gray-500">Legendas, hashtags e ideias</p>
            </div>
          </Link>

          <Link
            href="/personas"
            className="flex items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-6 hover:border-blue-500 hover:bg-blue-50"
          >
            <div className="text-center">
              <span className="text-4xl">👥</span>
              <p className="mt-2 font-medium text-gray-900">Minhas Personas</p>
              <p className="text-sm text-gray-500">Ver todas as personas</p>
            </div>
          </Link>
        </div>

        {/* Personas List */}
        <div>
          <h2 className="mb-4 text-xl font-semibold text-gray-900">
            Personas Recentes
          </h2>

          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : personas.length === 0 ? (
            <div className="rounded-lg bg-gray-50 p-12 text-center">
              <p className="text-gray-500">
                Você ainda não criou nenhuma persona.
              </p>
              <Link
                href="/personas/new"
                className="mt-4 inline-block rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Criar Primeira Persona
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {personas.slice(0, 6).map((persona) => (
                <Link
                  key={persona.id}
                  href={`/personas/${persona.id}`}
                  className="block rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md"
                >
                  <h3 className="text-lg font-semibold text-gray-900">
                    {persona.name}
                  </h3>
                  <p className="mt-2 line-clamp-2 text-sm text-gray-600">
                    {persona.description || 'Sem descrição'}
                  </p>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(persona.created_at).toLocaleDateString('pt-BR')}
                    </span>
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
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
