import { fetchApi } from './client';
import type { ChatMessage } from '../types';

export function sendMessage(
  projectId: string,
  content: string,
  history: ChatMessage[]
): Promise<ChatMessage> {
  return fetchApi<ChatMessage>(`/projects/${projectId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ content, history }),
  });
}
