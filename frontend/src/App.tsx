import { createContext, useContext, useState } from 'react';
import Layout from './components/Layout';
import type { ActiveTab } from './types';

interface AppContextValue {
  selectedProjectId: string | null;
  activeTab: ActiveTab;
  setSelectedProjectId: (id: string | null) => void;
  setActiveTab: (tab: ActiveTab) => void;
}

export const AppContext = createContext<AppContextValue | null>(null);

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContext must be used inside AppContext.Provider');
  return ctx;
}

export default function App() {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('project');

  return (
    <AppContext.Provider value={{ selectedProjectId, activeTab, setSelectedProjectId, setActiveTab }}>
      <Layout />
    </AppContext.Provider>
  );
}
