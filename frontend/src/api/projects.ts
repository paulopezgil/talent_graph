import { fetchApi } from './client';
import type { Project, ProjectListItem } from '../types';

export function getProjects(): Promise<ProjectListItem[]> {
  return fetchApi<ProjectListItem[]>('/projects');
}

export function createProject(): Promise<Project> {
  return fetchApi<Project>('/projects', { method: 'POST' });
}

export function getProject(id: string): Promise<Project> {
  return fetchApi<Project>(`/projects/${id}`);
}

export function updateProject(
  id: string,
  data: { title?: string; description?: string; summary?: string; key_topics?: string[] }
): Promise<Project> {
  return fetchApi<Project>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
