import { Prescription } from "../types";

const STORAGE_KEY = 'mediscribe_prescriptions';

export const savePrescription = (prescription: Prescription): void => {
  const existing = getPrescriptions();
  const updated = [prescription, ...existing];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
};

export const getPrescriptions = (): Prescription[] => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
};

export const getPrescriptionById = (id: string): Prescription | undefined => {
  const list = getPrescriptions();
  return list.find(p => p.id === id);
};

export const deletePrescription = async (id: string, token: string): Promise<void> => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/prescriptions/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to delete prescription');
  }
};
