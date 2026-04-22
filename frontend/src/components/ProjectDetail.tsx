import { useEffect, useState } from 'react';
import { getProject, updateProject } from '../api/projects';
import type { Project } from '../types';
import '../styles/Editor.css';

interface Props {
  projectId: string;
}

export default function ProjectDetail({ projectId }: Props) {
  const [project, setProject] = useState<Project | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState('');

  useEffect(() => {
    setProject(null);
    getProject(projectId).then(p => {
      setProject(p);
      setTitle(p.title);
      setDescription(p.description ?? '');
    }).catch(console.error);
  }, [projectId]);

  async function handleSave() {
    if (!project) return;
    setIsSaving(true);
    setSavedMsg('');
    try {
      const updated = await updateProject(projectId, { title, description });
      setProject(updated);
      setSavedMsg('Saved');
      setTimeout(() => setSavedMsg(''), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  }

  if (!project) return <div className="loading">Loading…</div>;

  return (
    <div className="editor-panel">
      <div className="editor-field">
        <label className="editor-label">Title</label>
        <input
          className="editor-input"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />
      </div>
      <div className="editor-field">
        <label className="editor-label">Description</label>
        <textarea
          className="editor-textarea"
          rows={4}
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
      </div>
      {project.summary && (
        <div className="editor-field">
          <label className="editor-label">Summary (AI generated)</label>
          <p className="editor-readonly">{project.summary}</p>
        </div>
      )}
      {project.key_topics && project.key_topics.length > 0 && (
        <div className="editor-field">
          <label className="editor-label">Key Topics</label>
          <p className="editor-readonly">{project.key_topics.join(', ')}</p>
        </div>
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
