import { useAppContext } from '../App';
import Sidebar from './Sidebar';
import Tabs from './Tabs';
import Chat from './Chat';
import Editor from './Editor';
import ProjectDetail from './ProjectDetail';
import '../styles/Layout.css';

export default function Layout() {
  const { activeTab, selectedProjectId } = useAppContext();

  function renderTabContent() {
    if (!selectedProjectId) {
      return (
        <div className="empty-state">
          <p>Select a project from the sidebar to get started.</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'project':
        return <ProjectDetail projectId={selectedProjectId} />;
      case 'chat':
        return <Chat projectId={selectedProjectId} />;
      case 'script':
        return <Editor mode="script" projectId={selectedProjectId} />;
      case 'social':
        return <Editor mode="social" projectId={selectedProjectId} />;
    }
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-panel">
        <Tabs />
        <div className="tab-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}
