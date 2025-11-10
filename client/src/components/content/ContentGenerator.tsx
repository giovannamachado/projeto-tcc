/**
 * Componente de Gerador de Conteúdo
 */

'use client';

import contentService, {
    GenerateCaptionResponse
} from '@/lib/services/contentService';
import { Persona } from '@/lib/services/personaService';
import { useState } from 'react';
import LoadingSpinner from '../common/LoadingSpinner';

interface ContentGeneratorProps {
  personas: Persona[];
}

export default function ContentGenerator({ personas }: ContentGeneratorProps) {
  const [selectedPersona, setSelectedPersona] = useState<number | null>(null);
  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState<'engajamento' | 'informativo' | 'storytelling'>(
    'engajamento'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateCaptionResponse | null>(null);
  const [error, setError] = useState('');

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedPersona || !topic) {
      setError('Selecione uma persona e insira um tópico');
      return;
    }

    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response = await contentService.generateCaption({
        persona_id: selectedPersona,
        topic,
        style,
        include_hashtags: true,
      });

      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Erro ao gerar conteúdo');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copiado para a área de transferência!');
  };

  return (
    <div className="space-y-6">
      {/* Form */}
      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Selecione a Persona
          </label>
          <select
            value={selectedPersona || ''}
            onChange={(e) => setSelectedPersona(Number(e.target.value))}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            required
          >
            <option value="">Escolha uma persona...</option>
            {personas.map((persona) => (
              <option key={persona.id} value={persona.id}>
                {persona.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Tópico / Assunto
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            placeholder="Ex: lançamento de novo produto"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Estilo da Legenda
          </label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value as typeof style)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="engajamento">Engajamento</option>
            <option value="informativo">Informativo</option>
            <option value="storytelling">Storytelling</option>
          </select>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <LoadingSpinner size="sm" />
              <span className="ml-2">Gerando...</span>
            </div>
          ) : (
            'Gerar Legenda'
          )}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Resultado</h3>
            <button
              onClick={() => copyToClipboard(result.caption)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              📋 Copiar Legenda
            </button>
          </div>

          <div className="rounded-md bg-gray-50 p-4">
            <p className="whitespace-pre-wrap text-gray-700">{result.caption}</p>
          </div>

          {result.hashtags && result.hashtags.length > 0 && (
            <div>
              <h4 className="mb-2 text-sm font-medium text-gray-700">Hashtags</h4>
              <div className="flex flex-wrap gap-2">
                {result.hashtags.map((tag, index) => (
                  <span
                    key={index}
                    className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <button
                onClick={() => copyToClipboard(result.hashtags.join(' '))}
                className="mt-2 text-sm text-blue-600 hover:text-blue-700"
              >
                📋 Copiar Hashtags
              </button>
            </div>
          )}

          {result.call_to_action && (
            <div>
              <h4 className="mb-2 text-sm font-medium text-gray-700">
                Call to Action
              </h4>
              <p className="text-sm text-gray-600">{result.call_to_action}</p>
            </div>
          )}

          <div className="border-t pt-4 text-xs text-gray-500">
            <p>Gerado por: {result.model_used}</p>
            <p>Persona: {result.request_info.persona_name}</p>
          </div>
        </div>
      )}
    </div>
  );
}
