import { GoogleGenAI } from "@google/genai";
import { GEMINI_MODEL, SYSTEM_PROMPT } from "../constants";
import { Prescription } from "../types";

const ai = new GoogleGenAI({ apiKey: import.meta.env.VITE_GEMINI_API_KEY });

export const analyzePrescription = async (base64Image: string): Promise<Partial<Prescription>> => {
  try {
    // Strip the data URL prefix if present (e.g., "data:image/jpeg;base64,")
    const base64Data = base64Image.split(',')[1] || base64Image;

    const response = await ai.models.generateContent({
      model: GEMINI_MODEL,
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: 'image/jpeg',
              data: base64Data
            }
          },
          {
            text: "Analyze this prescription and extract medicine details."
          }
        ]
      },
      config: {
        systemInstruction: SYSTEM_PROMPT,
        responseMimeType: "application/json"
      }
    });

    const text = response.text;
    if (!text) {
      throw new Error("No response text received from Gemini.");
    }

    const data = JSON.parse(text);

    return {
      doctorName: data.doctor_name,
      patientName: data.patient_name,
      medicines: data.medicines,
      createdAt: new Date().toISOString()
    };

  } catch (error) {
    console.error("Gemini Analysis Error:", error);
    throw error;
  }
};
