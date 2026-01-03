from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload_prescription, medicines, reminders, auth, verify_medicine

app = FastAPI(title="Medi-Scribe Backend")

# Temporary logging for debugging
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# CORS Config
# In backend/main.py

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://medi-scribe-khaki.vercel.app/", # <--- Add your future Vercel URL here later
    "*" # OR just use this star temporarily to allow ALL domains (easiest for now)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this to ["*"] for easiest deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(upload_prescription.router)
app.include_router(medicines.router)
app.include_router(reminders.router)
app.include_router(verify_medicine.router)

@app.get("/")
def read_root():
    return {"message": "Medi-Scribe API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
