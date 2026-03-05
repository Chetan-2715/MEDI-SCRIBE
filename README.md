# 🏥 Medi-Scribe

**Medi-Scribe** is an AI-powered healthcare companion that transforms handwritten prescriptions into digital, actionable insights.

> *Decipher doctor's handwriting, verify your meds, and never miss a dose.* 🚀

---

## 🔥 Key Features

### 📄 **Smart Prescription Digitization**
* **Advanced OCR**: To read even the messiest handwritten prescriptions.
* **Structured Extraction**: Automatically pulls out Medicine Names, Dosages (e.g., `1-0-1`), Quantities, and Instructions.
* **Handwriting Intelligence**: Understands circled numbers as quantities, fractions (½) as half-tablets, and medical abbreviations.

### 💊 **Medicine Verification**
* **Visual Analysis**: Upload a photo of a loose tablet or medicine strip.
* **RAG-Powered Check**: The AI compares the image against your **specific prescription context** to tell you:
    * ✅ **Prescribed**: Matches your doctor's order exactly.
    * ⚠️ **Replacement**: It's a safe generic alternative (same salt composition).
    * ❌ **Not Prescribed**: Dangerous mismatch warning.

### 🧠 **Deep Medical Insights**
* **Explanation vs. Tags**: Instead of just saying "Antibiotic", Medi-Scribe explains: *"Amoxicillin is used to treat bacterial infections like pneumonia and bronchitis."*
* **Clinical Accuracy**: Maps complex brand names to understandable medical purposes.

### 🔔 **Smart Reminders**
* **One-Click Calendar**: Instantly adds dosage schedules to your **Google Calendar**.
* **Intelligent Timing**: Automatically calculates specific time slots (Morning/Afternoon/Night) based on dosage patterns.

### 🔐 **Seamless Authentication**
* **Google One-Tap**: Instant sign-in without remembering passwords.
* **Auto-Onboarding**: Frictionless account creation flow.

---

## 🛠️ Tech Stack

### **Frontend**
* ⚛️ **React (Vite)** - Blazing fast, responsive UI.
* 🎨 **Tailwind CSS** - Modern styling with Dark Mode support.
* ✨ **Framer Motion** - Smooth, engaging animations.
* 📦 **Lucide React** - Clean, professional iconography.

### **Backend**
* 🐍 **FastAPI** - High-performance Python REST API.
* 🧠 **Google Gemini AI** - The intelligence behind OCR and Vision analysis.
* 🗄️ **Neon** - Serverless PostgreSQL Database.
* 🔒 **JWT & OAuth2** - Enterprise-grade security handling.

---

## 🚀 Installation & Setup

### Prerequisites
* Node.js & npm
* Python 3.10+
* Neon Serverless Postgres Account
* Google Cloud Console Project (for OAuth)

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/Chetan-2715/MEDI-SCRIBE.git](https://github.com/Chetan-2715/MEDI-SCRIBE.git)
cd MEDI-SCRIBE
````

### 2️⃣ Backend Setup

Navigate to the backend directory and set up the Python environment.

```bash
cd backend
# Create Virtual Environment (Optional but recommended)
python -m venv venv
# Activate: .\venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)

# Install Dependencies
pip install -r requirements.txt

# Run the Server
uvicorn main:app --reload
```

*Server runs at `http://127.0.0.1:8000`*

### 3️⃣ Frontend Setup

Open a new terminal in the root directory.

```bash
# Install Dependencies
npm install

# Run the App
npm run dev
```

*App runs at `http://localhost:3000`*

-----

## 🔑 Environment Variables

Create a `.env` file in **Frontend** and **Backend** directories.

**Frontend (`.env`)**

```env
VITE_API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

**Backend (`backend/.env`)**

```env
DATABASE_URL=postgresql://user:password@endpoint.neon.tech/neondb?sslmode=require
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id_here
SECRET_KEY=your_jwt_secret
```

-----

## 🤝 Contributing

Contributions are welcome\! <br>
Please feel free to submit a Pull Request.

**Built with ❤️ by Chetan Shabadi**