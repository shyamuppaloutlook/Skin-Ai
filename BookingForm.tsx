import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

interface BookingFormData {
  patient_id: string;
  doctor_id: string;
  appointment_date: string;
  duration: string;
  notes: string;
}

const doctors = [
  { id: 1, name: 'Dr. John Smith', specialization: 'Cardiology' },
  { id: 2, name: 'Dr. Sarah Johnson', specialization: 'Neurology' },
  { id: 3, name: 'Dr. Michael Brown', specialization: 'Orthopedics' },
  { id: 4, name: 'Dr. Emily Davis', specialization: 'Pediatrics' },
  { id: 5, name: 'Dr. Robert Wilson', specialization: 'Internal Medicine' },
];

const BookingForm: React.FC = () => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<BookingFormData>({
    patient_id: '',
    doctor_id: '',
    appointment_date: '',
    duration: '30',
    notes: ''
  });

  const { data: patients, isLoading: patientsLoading } = useQuery<Patient[]>(
    'patients',
    () => fetch(`${API_BASE_URL}/patients`).then(res => res.json()).then(data => data.patients || [])
  );

  const bookingMutation = useMutation(
    (bookingData: BookingFormData) => 
      fetch(`${API_BASE_URL}/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...bookingData,
          patient_id: parseInt(bookingData.patient_id),
          doctor_id: parseInt(bookingData.doctor_id),
          duration: parseInt(bookingData.duration)
        })
      }).then(res => res.json()),
    {
      onSuccess: () => {
        toast.success('Appointment booked successfully!');
        setFormData({
          patient_id: '',
          doctor_id: '',
          appointment_date: '',
          duration: '30',
          notes: ''
        });
        queryClient.invalidateQueries('dashboard');
      },
      onError: (error: any) => {
        toast.error(error.message || 'Failed to book appointment');
      }
    }
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.patient_id || !formData.doctor_id || !formData.appointment_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    bookingMutation.mutate(formData);
  };

  // Get minimum date (today) for appointment booking
  const minDate = new Date().toISOString().slice(0, 16);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow-sm rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Book New Appointment</h2>
          <p className="mt-1 text-sm text-gray-600">
            Schedule an appointment with our healthcare providers
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
          {/* Patient Selection */}
          <div>
            <label htmlFor="patient_id" className="block text-sm font-medium text-gray-700 mb-2">
              Patient *
            </label>
            <select
              id="patient_id"
              name="patient_id"
              value={formData.patient_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select a patient</option>
              {patients?.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.first_name} {patient.last_name} - {patient.email}
                </option>
              ))}
            </select>
            {patientsLoading && (
              <p className="mt-1 text-sm text-gray-500">Loading patients...</p>
            )}
          </div>

          {/* Doctor Selection */}
          <div>
            <label htmlFor="doctor_id" className="block text-sm font-medium text-gray-700 mb-2">
              Doctor *
            </label>
            <select
              id="doctor_id"
              name="doctor_id"
              value={formData.doctor_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select a doctor</option>
              {doctors.map((doctor) => (
                <option key={doctor.id} value={doctor.id}>
                  {doctor.name} - {doctor.specialization}
                </option>
              ))}
            </select>
          </div>

          {/* Appointment Date and Time */}
          <div>
            <label htmlFor="appointment_date" className="block text-sm font-medium text-gray-700 mb-2">
              Appointment Date & Time *
            </label>
            <input
              type="datetime-local"
              id="appointment_date"
              name="appointment_date"
              value={formData.appointment_date}
              onChange={handleInputChange}
              min={minDate}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Duration */}
          <div>
            <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
              Duration (minutes)
            </label>
            <select
              id="duration"
              name="duration"
              value={formData.duration}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="45">45 minutes</option>
              <option value="60">60 minutes</option>
              <option value="90">90 minutes</option>
            </select>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Any special requirements or notes for the appointment..."
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setFormData({
                patient_id: '',
                doctor_id: '',
                appointment_date: '',
                duration: '30',
                notes: ''
              })}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Clear Form
            </button>
            <button
              type="submit"
              disabled={bookingMutation.isLoading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {bookingMutation.isLoading ? 'Booking...' : 'Book Appointment'}
            </button>
          </div>
        </form>
      </div>

      {/* Booking Tips */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-blue-400">💡</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Booking Tips</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li>Book appointments at least 24 hours in advance</li>
                <li>Arrive 15 minutes early for paperwork</li>
                <li>Bring your insurance card and ID</li>
                <li>Cancel 24 hours in advance to avoid fees</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingForm;
