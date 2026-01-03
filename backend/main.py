from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload_prescription, medicines, reminders, auth, verify_medicine
import uvicorn
import os

app = FastAPI(title="Medi-Scribe Backend")

# 1. Logging Middleware (Helps debug requests on Render)
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# 2. CORS Configuration (CRITICAL for Deployment)
# We use ["*"] to allow ALL origins. This is the safest way to ensure 
# Vercel can talk to Render without "Network Error" issues.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Register Routes
app.include_router(auth.router)
app.include_router(upload_prescription.router)
app.include_router(medicines.router)
app.include_router(reminders.router)
app.include_router(verify_medicine.router)

@app.get("/")
def read_root():
    return {"message": "Medi-Scribe API is running"}

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    # reload=False for production stability
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)