/**
 * Página de Geração de Conteúdo
 */

'use client';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import Navbar from '@/components/common/Navbar';
import ContentGenerator from '@/components/content/ContentGenerator';
import { useAuth } from '@/contexts/AuthContext';
import personaService, { Persona } from '@/lib/services/personaService';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function GeneratePage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
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
        setPersonas(data.filter((p) => p.is_active));
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
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gerar Conteúdo</h1>
          <p className="mt-2 text-sm text-gray-600">
            Crie legendas, hashtags e ideias personalizadas para o Instagram
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : personas.length === 0 ? (
          <div className="rounded-lg bg-yellow-50 p-8 text-center">
            <span className="text-4xl">⚠️</span>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Você precisa criar uma persona primeiro
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              As personas definem a identidade de marca para gerar conteúdo personalizado
            </p>
            <button
              onClick={() => router.push('/personas/new')}
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Criar Persona
            </button>
          </div>
        ) : (
          <ContentGenerator personas={personas} />
        )}
      </div>
    </>
  );
}
