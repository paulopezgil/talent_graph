import { useEffect, useState } from 'react';
import { getScript, createScript, updateScript } from '../api/script';
import { getSocialMedia, createSocialMedia, updateSocialMedia } from '../api/social';
import type { SocialMedia } from '../types';
import '../styles/Editor.css';

interface Props {
  mode: 'script' | 'social';
  projectId: string;
}

const SOCIAL_FIELDS: { key: keyof Omit<SocialMedia, 'id' | 'project_id' | 'created_at' | 'updated_at'>; label: string; rows: number }[] = [
  { key: 'youtube_title', label: 'YouTube Title', rows: 2 },
  { key: 'youtube_description', label: 'YouTube Description', rows: 5 },
  { key: 'instagram_description', label: 'Instagram', rows: 4 },
  { key: 'tiktok_description', label: 'TikTok', rows: 3 },
  { key: 'twitter_post', label: 'Twitter / X', rows: 3 },
  { key: 'linkedin_post', label: 'LinkedIn', rows: 4 },
];

export default function Editor({ mode, projectId }: Props) {
  const [scriptContent, setScriptContent] = useState('');
  const [socialData, setSocialData] = useState<Record<string, string>>({});
  const [exists, setExists] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState('');

  useEffect(() => {
    setExists(false);
    setSavedMsg('');
    if (mode === 'script') {
      getScript(projectId).then(s => {
        setScriptContent(s?.content ?? '');
        setExists(s !== null);
      }).catch(console.error);
    } else {
      getSocialMedia(projectId).then(s => {
        if (s) {
          const data: Record<string, string> = {};
          SOCIAL_FIELDS.forEach(f => { data[f.key] = s[f.key] ?? ''; });
          setSocialData(data);
          setExists(true);
        } else {
          const empty: Record<string, string> = {};
          SOCIAL_FIELDS.forEach(f => { empty[f.key] = ''; });
          setSocialData(empty);
        }
      }).catch(console.error);
    }
  }, [mode, projectId]);

  async function handleSave() {
    setIsSaving(true);
    setSavedMsg('');
    try {
      if (mode === 'script') {
        if (exists) {
          await updateScript(projectId, scriptContent);
        } else {
          await createScript(projectId, scriptContent);
          setExists(true);
        }
      } else {
        if (exists) {
          await updateSocialMedia(projectId, socialData);
        } else {
          await createSocialMedia(projectId, socialData);
          setExists(true);
        }
      }
      setSavedMsg('Saved');
      setTimeout(() => setSavedMsg(''), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="editor-panel">
      {mode === 'script' ? (
        <div className="editor-field">
          <label className="editor-label">Script</label>
          <textarea
            className="editor-textarea editor-textarea--tall"
            value={scriptContent}
            onChange={e => setScriptContent(e.target.value)}
            placeholder="Write your video script here…"
          />
        </div>
      ) : (
        SOCIAL_FIELDS.map(field => (
          <div key={field.key} className="editor-field">
            <label className="editor-label">{field.label}</label>
            <textarea
              className="editor-textarea"
              rows={field.rows}
              value={socialData[field.key] ?? ''}
              onChange={e => setSocialData(prev => ({ ...prev, [field.key]: e.target.value }))}
              placeholder={`Write your ${field.label} content…`}
            />
          </div>
        ))
      )}
      <div className="editor-actions">
        <button className="save-btn" onClick={handleSave} disabled={isSaving}>
          {isSaving ? 'Saving…' : 'Save'}
        </button>
        {savedMsg && <span className="saved-msg">{savedMsg}</span>}
      </div>
    </div>
  );
}
