from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload_prescription, medicines, reminders, auth

app = FastAPI(title="Medi-Scribe Backend")

# CORS Setup
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
    "*" # Allow all for dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(upload_prescription.router)
app.include_router(medicines.router)
app.include_router(reminders.router)

@app.get("/")
def read_root():
    return {"message": "Medi-Scribe API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
