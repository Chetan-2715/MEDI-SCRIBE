
export interface Medicine {
  medicine_name: string;
  medicine_type: 'tablet' | 'syrup' | 'ointment' | 'injection' | 'other';
  dosage_pattern: string; // e.g., "1-0-1"
  instructions: string; // e.g., "After food"
  total_tablets?: number;
  duration_days: number;
  description: string; // Medical explanation
  purpose: string; // e.g., "Pain relief"
}

export interface Prescription {
  id: string;
  imageUrl: string;
  createdAt: string;
  medicines: Medicine[];
  doctorName?: string;
  patientName?: string;
}

export interface ProcessingState {
  status: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
  message?: string;
}

export enum CalendarType {
  GOOGLE = 'GOOGLE',
  ICAL = 'ICAL'
}

export interface User {
  id: string;
  name: string;
  email: string;
  token?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}
