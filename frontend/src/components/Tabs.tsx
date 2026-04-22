import { useAppContext } from '../App';
import type { ActiveTab } from '../types';
import '../styles/Tabs.css';

const TABS: { id: ActiveTab; label: string }[] = [
  { id: 'project', label: 'Project' },
  { id: 'chat', label: 'Chat' },
  { id: 'script', label: 'Script' },
  { id: 'social', label: 'Social' },
];

export default function Tabs() {
  const { activeTab, setActiveTab, selectedProjectId } = useAppContext();

  return (
    <nav className="tabs">
      {TABS.map(tab => (
        <button
          key={tab.id}
          className={`tab-btn${activeTab === tab.id ? ' active' : ''}`}
          onClick={() => setActiveTab(tab.id)}
          disabled={!selectedProjectId}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
