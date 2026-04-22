export interface ProjectListItem {
  id: string;
  title: string;
  updated_at: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  summary: string | null;
  key_topics: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface Script {
  id: string;
  project_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface SocialMedia {
  id: string;
  project_id: string;
  youtube_title: string | null;
  youtube_description: string | null;
  instagram_description: string | null;
  tiktok_description: string | null;
  twitter_post: string | null;
  linkedin_post: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export type ActiveTab = 'project' | 'chat' | 'script' | 'social';
