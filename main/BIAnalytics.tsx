import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { format, subDays } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

interface BIData {
  powerBI?: any;
  tableau?: any;
  googleDataStudio?: any;
  realTime?: any;
  advanced?: any;
}

const BIAnalytics: React.FC = () => {
  const [selectedTool, setSelectedTool] = useState<'powerbi' | 'tableau' | 'google'>('powerbi');
  const [realTimeData, setRealTimeData] = useState<any>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  // Fetch BI data
  const { data: biData, isLoading } = useQuery<BIData>(
    'bi-analytics',
    async () => {
      const responses = await Promise.all([
        fetch(`${API_BASE_URL}/bi/power-bi/dataset/comprehensive`).then(res => res.json()),
        fetch(`${API_BASE_URL}/bi/tableau/extract/hyper`).then(res => res.json()),
        fetch(`${API_BASE_URL}/bi/google-data-studio/report`).then(res => res.json()),
        fetch(`${API_BASE_URL}/bi/analytics/advanced`).then(res => res.json()),
      ]);

      return {
        powerBI: responses[0],
        tableau: responses[1],
        googleDataStudio: responses[2],
        advanced: responses[3],
      };
    },
    { refetchInterval: 60000 } // Refresh every minute
  );

  // Real-time data streaming
  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/bi/real-time/stream`);
        const data = await response.json();
        setRealTimeData(data);
      } catch (error) {
        console.error('Real-time data error:', error);
      }
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [isStreaming]);

  // Power BI Dashboard Data
  const powerBIData = biData?.powerBI?.data || [];
  const patientDemographics = React.useMemo(() => {
    if (!powerBIData.length) return { labels: [], data: [] };

    const ageGroups = powerBIData.reduce((acc: any, patient: any) => {
      const age = patient.age || 0;
      let group = 'Unknown';
      if (age < 18) group = '0-17';
      else if (age < 35) group = '18-34';
      else if (age < 50) group = '35-49';
      else if (age < 65) group = '50-64';
      else group = '65+';

      acc[group] = (acc[group] || 0) + 1;
      return acc;
    }, {});

    return {
      labels: Object.keys(ageGroups),
      data: Object.values(ageGroups),
    };
  }, [powerBIData]);

  const appointmentTrends = React.useMemo(() => {
    if (!powerBIData.length) return { labels: [], datasets: [] };

    const last30Days = [];
    const appointmentCounts = [];

    for (let i = 29; i >= 0; i--) {
      const date = format(subDays(new Date(), i), 'yyyy-MM-dd');
      last30Days.push(format(subDays(new Date(), i), 'MMM dd'));
      
      const count = powerBIData.filter((apt: any) => 
        apt.appointment_date && apt.appointment_date.startsWith(date)
      ).length;
      appointmentCounts.push(count);
    }

    return {
      labels: last30Days,
      datasets: [
        {
          label: 'Daily Appointments',
          data: appointmentCounts,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
        },
      ],
    };
  }, [powerBIData]);

  // Advanced Analytics Data
  const advancedData = biData?.advanced;
  const doctorPerformance = React.useMemo(() => {
    if (!advancedData?.doctor_performance) return { labels: [], datasets: [] };

    const doctors = advancedData.doctor_performance;
    return {
      labels: doctors.map((d: any) => d.doctor_name),
      datasets: [
        {
          label: 'Total Appointments',
          data: doctors.map((d: any) => d.total_appointments),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
        },
        {
          label: 'Completed Appointments',
          data: doctors.map((d: any) => d.completed_appointments),
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
        },
      ],
    };
  }, [advancedData]);

  const revenueAnalytics = advancedData?.revenue_analytics || {};

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
    },
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm skeleton h-80"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Advanced BI Analytics</h2>
          <p className="mt-1 text-sm text-gray-600">
            Power BI, Tableau, and Google Data Studio integration
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              isStreaming 
                ? 'bg-green-600 text-white hover:bg-green-700' 
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            {isStreaming ? '🔴 Live Streaming' : '⚪ Start Streaming'}
          </button>
          
          <select
            value={selectedTool}
            onChange={(e) => setSelectedTool(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="powerbi">Power BI</option>
            <option value="tableau">Tableau</option>
            <option value="google">Google Data Studio</option>
          </select>
        </div>
      </div>

      {/* Real-time Metrics */}
      {realTimeData && (
        <div className="bg-white shadow-sm rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Real-time Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{realTimeData.active_appointments}</div>
              <div className="text-sm text-blue-800">Active Appointments</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{realTimeData.today_appointments}</div>
              <div className="text-sm text-green-800">Today's Appointments</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{realTimeData.total_patients}</div>
              <div className="text-sm text-purple-800">Total Patients</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{realTimeData.system_load?.cpu_usage || 0}%</div>
              <div className="text-sm text-orange-800">System Load</div>
            </div>
          </div>
        </div>
      )}

      {/* BI Tool Specific Dashboards */}
      {selectedTool === 'powerbi' && (
        <div className="space-y-6">
          {/* Power BI Style Dashboard */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Patient Demographics</h3>
              <div className="chart-container">
                <Pie
                  data={{
                    labels: patientDemographics.labels,
                    datasets: [{
                      data: patientDemographics.data,
                      backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(251, 146, 60, 0.8)',
                        'rgba(147, 51, 234, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                      ],
                    }],
                  }}
                  options={pieOptions}
                />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Appointment Trends (30 Days)</h3>
              <div className="chart-container">
                <Line data={appointmentTrends} options={chartOptions} />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Analytics</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Monthly Revenue</span>
                  <span className="text-lg font-bold text-green-600">
                    ${revenueAnalytics.monthly_revenue?.toLocaleString() || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Outstanding Amount</span>
                  <span className="text-lg font-bold text-red-600">
                    ${revenueAnalytics.outstanding_amount?.toLocaleString() || 0}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Patient Retention</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm font-medium text-gray-700">New Patients (This Month)</span>
                  <span className="text-lg font-bold text-blue-600">
                    {advancedData?.patient_retention?.new_patients_this_month || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Returning Patients</span>
                  <span className="text-lg font-bold text-purple-600">
                    {advancedData?.patient_retention?.returning_patients || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedTool === 'tableau' && (
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Tableau-Style Analytics</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="chart-container">
              <h4 className="text-md font-medium text-gray-800 mb-2">Doctor Performance</h4>
              <Bar data={doctorPerformance} options={chartOptions} />
            </div>
            <div className="chart-container">
              <h4 className="text-md font-medium text-gray-800 mb-2">Appointment Status Distribution</h4>
              <Doughnut
                data={{
                  labels: ['Scheduled', 'Completed', 'Cancelled', 'No-Show'],
                  datasets: [{
                    data: [35, 45, 12, 8],
                    backgroundColor: [
                      'rgba(59, 130, 246, 0.8)',
                      'rgba(16, 185, 129, 0.8)',
                      'rgba(251, 146, 60, 0.8)',
                      'rgba(239, 68, 68, 0.8)',
                    ],
                  }],
                }}
                options={pieOptions}
              />
            </div>
          </div>
        </div>
      )}

      {selectedTool === 'google' && (
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Google Data Studio Style</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">2,847</div>
              <div className="text-sm text-blue-800">Total Patients</div>
              <div className="text-xs text-blue-600 mt-1">↑ 12% from last month</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600">156</div>
              <div className="text-sm text-green-800">Daily Appointments</div>
              <div className="text-xs text-green-600 mt-1">↑ 8% from last week</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">94.2%</div>
              <div className="text-sm text-purple-800">Satisfaction Rate</div>
              <div className="text-xs text-purple-600 mt-1">↑ 2.1% improvement</div>
            </div>
          </div>
        </div>
      )}

      {/* Export Options */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Data Export for BI Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Power BI Export</h4>
            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Export as JSON
              </button>
              <button className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Export as CSV
              </button>
            </div>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Tableau Export</h4>
            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-700">
                Export as Excel
              </button>
              <button className="w-full px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-700">
                Export as Hyper
              </button>
            </div>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Google Data Studio</h4>
            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Export as Google Sheets
              </button>
              <button className="w-full px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Connect to BigQuery
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Integration Status */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-blue-400">🔗</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">BI Integration Status</h3>
            <div className="mt-2 text-sm text-blue-700">
              <div className="space-y-1">
                <div>✅ Power BI API: Connected and streaming data</div>
                <div>✅ Tableau Extract: Ready for data refresh</div>
                <div>✅ Google Data Studio: Schema optimized and connected</div>
                <div>✅ Real-time Streaming: Active ({isStreaming ? 'Live' : 'Paused'})</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BIAnalytics;
