# SmartSpend AI

A responsive personal finance analyzer for Indian users. Track income, expenses and refunds, review budgets, import CSVs, and explore deterministic financial insights. Authentication and persistence are powered by Supabase; the FastAPI service supplies categorization and analysis without requiring a paid AI key.

## Features

- Supabase signup/login, session restoration and protected app pages.
- RLS-owned transactions, budgets and category feedback.
- Transaction CRUD, search, filters, pagination and CSV export.
- CSV preview, row validation and duplicate review before import.
- Real transaction-based summaries and Recharts charts, budget tracking and demo data behind an explicit action.
- Rule-first categorization with optional scikit-learn classifier, anomaly detection and deterministic assistant.
- Responsive dashboard, insights, assistant, budgets and settings.

## Stack and layout

React, TypeScript, Vite, Recharts, Lucide, Supabase JS; FastAPI, Pydantic, Pandas and scikit-learn; Supabase PostgreSQL with RLS.

```text
frontend/        React application
backend/         FastAPI API and tests
database/        Supabase SQL migrations
docs/            architecture and deployment notes
sample-data/     non-personal CSV example
```

## Local setup

### Quick demo (Windows)

Double-click `run.bat`. It installs frontend dependencies on first run and opens the app. Choose **Explore with demo data**. This demo does not save to an account and does not require Supabase, Python, or API keys.

### Full setup

1. Create a Supabase project and run `database/migrations/001_initial_schema.sql` in its SQL editor.
2. Copy `frontend/.env.example` to `frontend/.env.local`, setting the project URL, anon/publishable key and API base URL.
3. Copy `backend/.env.example` to `backend/.env`, set the same Supabase URL and anon key, and set `ALLOWED_ORIGINS=http://localhost:5173`.
4. Install and run the frontend with `cd frontend; npm install; npm run dev`.
5. Use Python 3.11 (pinned in `backend/.python-version`). Run the API with `cd backend; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload`.

The frontend can render the public landing page without Supabase credentials, but signup and data features require a configured project. The API health check works without credentials; protected endpoints require a valid Supabase access token.

## Tests and build

```powershell
cd backend
pip install -r requirements.txt
pytest
python -m compileall app

cd ..\frontend
npm install
npm test
npm run build
```

## Data and ML

The synthetic examples in `backend/app/ml/training_data.py` are demonstration-only and do not represent customer spending. Merchant rules are applied first; a TF-IDF/logistic regression model handles less obvious descriptions. `evaluate_synthetic_model()` reports a stratified held-out precision, recall, macro F1 and confusion matrix for those synthetic examples only. This score is not a claim about customer data. Add representative labeled examples and evaluate before production use. User category corrections are stored only when explicitly saved and never trigger automatic retraining.

CSV columns supported directly: `date,description,amount,type,category,payment_method` (category and payment method are optional). Dates must be ISO `YYYY-MM-DD`; amount is a positive decimal; type is income, expense or refund. Common aliases such as transaction_date, details, value, debit/credit are recognized. Upload is capped at 5 MB and 5,000 rows. Duplicate matching is a warning only; records are never silently overwritten.

## Security

Ordinary CRUD uses the browser Supabase client under RLS. The backend accepts a bearer access token and validates it against Supabase Auth; it does not have a service role or database password. Never place privileged keys or an LLM key in frontend variables. CSV export escapes spreadsheet formulas. Configure Auth redirect URLs and production CORS origins narrowly.

## Deployment

See [docs/deployment.md](docs/deployment.md). Typical hosting: Vercel for `frontend`, Render for `backend`, Supabase for Auth/Postgres. No deployment is performed by this repository.

## Screenshots

Run the app with a configured Supabase project, then capture the dashboard and mobile layout and add images here. No screenshots are included because none have been captured from a running instance.

## Limitations and next steps

The assistant is deterministic and supports common spending questions; optional generative responses are not enabled in this MVP. CSV column mapping is based on aliases rather than an arbitrary interactive mapper. Account deletion is exposed as a guided confirmation and requires deleting the account through Supabase Auth administration or a separately reviewed Edge Function; no privileged deletion key is shipped. Add production monitoring, backups and a reviewed deletion workflow before handling real customer data.
