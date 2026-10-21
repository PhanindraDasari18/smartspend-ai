from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import httpx
from app.core.config import settings
from app.schemas import AnalyzeRequest, AskRequest, CategorizeRequest
from app.services.finance import summarize, category_totals, anomalies, answer
from app.ml.categorizer import predict_category

app = FastAPI(title="SmartSpend AI API", version="1.0.0", description="Authenticated deterministic finance analysis API")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.allowed_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

async def authenticated_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="A valid Supabase access token is required")
    api_key = settings.supabase_publishable_key or settings.supabase_anon_key
    if not settings.supabase_url or not api_key:
        raise HTTPException(status_code=503, detail="Authentication service is not configured")
    token = authorization.split(" ", 1)[1].strip()
    if not token or len(token) > 8192:
        raise HTTPException(status_code=401, detail="Invalid access token")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.supabase_url.rstrip('/')}/auth/v1/user", headers={"apikey": api_key, "Authorization": f"Bearer {token}"})
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable")
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return response.json()

@app.get("/health")
async def health(): return {"status": "ok"}

@app.post("/api/v1/categorize")
async def categorize(body: CategorizeRequest, _: dict = Depends(authenticated_user)):
    prediction = predict_category(body.description, body.merchant)
    return prediction.model_dump()

@app.post("/api/v1/analyze")
async def analyze(body: AnalyzeRequest, _: dict = Depends(authenticated_user)):
    return {"summary": summarize(body.transactions), "categories": category_totals(body.transactions), "anomalies": anomalies(body.transactions), "period": {"start": min((t.date for t in body.transactions), default=None), "end": max((t.date for t in body.transactions), default=None)}}

@app.post("/api/v1/assistant/ask")
async def ask(body: AskRequest, _: dict = Depends(authenticated_user)):
    start = min((t.date for t in body.transactions), default=None)
    end = max((t.date for t in body.transactions), default=None)
    period = f"{start.isoformat()} to {end.isoformat()}" if start and end else "an empty supplied period"
    return {"answer": f"For {period}: {answer(body.question, body.transactions)}", "mode": "deterministic", "evidence_count": len(body.transactions), "period": {"start": start, "end": end}}
