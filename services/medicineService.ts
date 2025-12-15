
const API_URL = import.meta.env.VITE_API_URL;

export interface VerificationResult {
    status: "prescribed" | "replacement" | "not_prescribed" | "error";
    identified_medicine_name: string;
    purpose: string;
    explanation: string;
    replacement_for?: string;
}

export const medicineService = {
    async verifyMedicine(imageFile: File, prescriptionId: string, token: string): Promise<VerificationResult> {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('prescription_id', prescriptionId);

        const response = await fetch(`${API_URL}/medicine/verify`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
            throw new Error(error.detail || 'Verification request failed');
        }

        return response.json();
    }
};
