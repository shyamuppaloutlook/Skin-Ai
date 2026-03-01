import React from 'react';
import { useQuery } from 'react-query';
import { format } from 'date-fns';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

interface DashboardData {
  total_patients: number;
  total_appointments: number;
  active_appointments: number;
  average_appointment_duration: number;
  recent_appointments: Array<{
    id: number;
    patient_name: string;
    appointment_date: string;
    status: string;
  }>;
}

const Dashboard: React.FC = () => {
  const { data: dashboardData, isLoading, error } = useQuery<DashboardData>(
    'dashboard',
    () => fetch(`${API_BASE_URL}/analytics/dashboard`).then(res => res.json()),
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const stats = [
    {
      name: 'Total Patients',
      value: dashboardData?.total_patients || 0,
      change: '+12%',
      changeType: 'positive',
      icon: '👥'
    },
    {
      name: 'Total Appointments',
      value: dashboardData?.total_appointments || 0,
      change: '+8%',
      changeType: 'positive',
      icon: '📅'
    },
    {
      name: 'Active Appointments',
      value: dashboardData?.active_appointments || 0,
      change: '+5%',
      changeType: 'positive',
      icon: '⏰'
    },
    {
      name: 'Avg Duration (min)',
      value: Math.round(dashboardData?.average_appointment_duration || 0),
      change: '-2%',
      changeType: 'negative',
      icon: '⏱️'
    }
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm skeleton h-32"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-red-400">⚠️</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
            <div className="mt-2 text-sm text-red-700">
              Unable to fetch dashboard data. Please try again later.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="mt-1 text-sm text-gray-600">
          Real-time overview of your healthcare management system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <div className="flex items-center mt-2">
                  <span
                    className={`text-sm font-medium ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {stat.change}
                  </span>
                  <span className="text-sm text-gray-500 ml-2">from last month</span>
                </div>
              </div>
              <div className="text-3xl">{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Appointments */}
      <div className="bg-white shadow-sm rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Appointments</h3>
        </div>
        <div className="overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {dashboardData?.recent_appointments?.map((appointment) => (
              <li key={appointment.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">
                        {appointment.patient_name}
                      </p>
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          appointment.status === 'scheduled'
                            ? 'bg-blue-100 text-blue-800'
                            : appointment.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {appointment.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {format(new Date(appointment.appointment_date), 'PPP p')}
                    </p>
                  </div>
                </div>
              </li>
            ))}
            {(!dashboardData?.recent_appointments || dashboardData.recent_appointments.length === 0) && (
              <li className="px-6 py-4">
                <p className="text-sm text-gray-500 text-center">No recent appointments</p>
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📝</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">New Patient</h3>
              <p className="text-sm text-gray-500">Register a new patient</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Generate Report</h3>
              <p className="text-sm text-gray-500">Create analytics report</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">⚙️</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Settings</h3>
              <p className="text-sm text-gray-500">System configuration</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
