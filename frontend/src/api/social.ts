import { fetchApi } from './client';
import type { SocialMedia } from '../types';

export type SocialMediaData = Omit<SocialMedia, 'id' | 'project_id' | 'created_at' | 'updated_at'>;

export async function getSocialMedia(projectId: string): Promise<SocialMedia | null> {
  try {
    return await fetchApi<SocialMedia>(`/projects/${projectId}/social-media`);
  } catch (err) {
    if (err instanceof Error && err.message.includes('404')) return null;
    throw err;
  }
}

export function createSocialMedia(projectId: string, data: Partial<SocialMediaData>): Promise<SocialMedia> {
  return fetchApi<SocialMedia>(`/projects/${projectId}/social-media`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function updateSocialMedia(projectId: string, data: Partial<SocialMediaData>): Promise<SocialMedia> {
  return fetchApi<SocialMedia>(`/projects/${projectId}/social-media`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
