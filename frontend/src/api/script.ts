import { fetchApi } from './client';
import type { Script } from '../types';

export async function getScript(projectId: string): Promise<Script | null> {
  try {
    return await fetchApi<Script>(`/projects/${projectId}/script`);
  } catch (err) {
    if (err instanceof Error && err.message.includes('404')) return null;
    throw err;
  }
}

export function createScript(projectId: string, content: string): Promise<Script> {
  return fetchApi<Script>(`/projects/${projectId}/script`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export function updateScript(projectId: string, content: string): Promise<Script> {
  return fetchApi<Script>(`/projects/${projectId}/script`, {
    method: 'PUT',
    body: JSON.stringify({ content }),
  });
}
