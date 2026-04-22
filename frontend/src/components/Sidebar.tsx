import { useEffect, useState } from 'react';
import { useAppContext } from '../App';
import { getProjects, createProject } from '../api/projects';
import type { ProjectListItem } from '../types';
import '../styles/Sidebar.css';

export default function Sidebar() {
  const { selectedProjectId, setSelectedProjectId, setActiveTab } = useAppContext();
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    getProjects().then(setProjects).catch(console.error);
  }, []);

  async function handleCreate() {
    setIsCreating(true);
    try {
      const project = await createProject();
      setProjects(prev => [project, ...prev]);
      setSelectedProjectId(project.id);
      setActiveTab('project');
    } catch (err) {
      console.error(err);
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">TalentStream AI</h1>
      </div>
      <ul className="project-list">
        {projects.map(project => (
          <li
            key={project.id}
            className={`project-item${selectedProjectId === project.id ? ' selected' : ''}`}
            onClick={() => {
              setSelectedProjectId(project.id);
              setActiveTab('project');
            }}
          >
            {project.title}
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">
        <button className="create-btn" onClick={handleCreate} disabled={isCreating}>
          {isCreating ? 'Creating…' : '+ New Project'}
        </button>
      </div>
    </aside>
  );
}
