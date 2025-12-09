# Medi-Scribe 🏥💊

**Medi-Scribe** is an intelligent healthcare assistant that simplifies prescription management. By leveraging **OCR** , it digitizes handwritten medical prescriptions, extracts medicine details, and organizes them into a user-friendly dashboard.

## 🚀 Features


*   **📄 Smart Digitization**: Upload prescription images to automatically extract patient names, medicines, dosages, and instructions.
*   **🧠 AI-Powered**: Uses **Google Gemini 1.5 Flash** to interpret complex handwriting and medical context.

*   **🔔 Medication Management**: View and manage your prescriptions and medicines in one place.

## 🛠️ Tech Stack

### Frontend
-   **Framework**: React (Vite)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS
-   **Icons**: Lucide React

### Backend
-   **Framework**: FastAPI (Python)
-   **AI Model**: Google Gemini 1.5 Flash
-   **OCR**: Tesseract / Gemini Vision
-   **Server**: Uvicorn


---

## 📦 Installation & Setup

### Prerequisites
-   Node.js & npm
-   Python 3.8+
-   Supabase Account
-   Google Gemini API Key

### 1. Clone the Repository
```bash
git clone https://github.com/Chetan-2715/MEDI-SCRIBE.git
cd MEDI-SCRIBE
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment.

```bash
cd backend
# Install Dependencies
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### 3. Frontend Setup
Open a new terminal and navigate to the root directory.

```bash
# Install Dependencies
npm install
npm run dev
```

---

## 🤝 Contributing
Contributions are welcome! <br>Please feel free to submit a Pull Request.
