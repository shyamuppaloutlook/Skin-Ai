import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import BookingForm from './components/BookingForm';
import PatientList from './components/PatientList';
import Analytics from './components/Analytics';
import BIAnalytics from './components/BIAnalytics';
import Header from './components/Header';
import { useQuery } from 'react-query';

type TabType = 'dashboard' | 'booking' | 'patients' | 'analytics' | 'bi-analytics';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  const { data: healthData } = useQuery(
    'health',
    () => fetch(`${API_BASE_URL}/health`).then(res => res.json()),
    { refetchInterval: 30000 } // Check health every 30 seconds
  );

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'booking', name: 'Book Appointment', icon: '📅' },
    { id: 'patients', name: 'Patients', icon: '👥' },
    { id: 'analytics', name: 'Analytics', icon: '📈' },
    { id: 'bi-analytics', name: 'BI Analytics', icon: '🔬' },
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
        tabs={tabs}
        systemStatus={healthData?.status}
      />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-slide-in">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'booking' && <BookingForm />}
          {activeTab === 'patients' && <PatientList />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'bi-analytics' && <BIAnalytics />}
        </div>
      </main>
    </div>
  );
};

export default App;
