# Deployment guide

1. Create Supabase, Vercel and Render accounts and a GitHub repository.
2. Create a Supabase project. Execute `database/migrations/001_initial_schema.sql` in SQL Editor. Keep email confirmation enabled as appropriate for your audience and add local/production redirect URLs under Authentication URL Configuration.
3. Copy environment examples. Frontend: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_BASE_URL`. Backend: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `ALLOWED_ORIGINS`. The anon key is intentionally public; never set a service role key in either app. Optional LLM settings are currently reserved and unused.
4. Run locally using commands in the root README. Confirm the API `/health`, signup/login, create a transaction, verify a different account cannot read it, and test CSV import/export.
5. Push the repository. Configure Vercel project root as `frontend`; build command `npm run build`, output `dist`. Add `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, and `VITE_API_BASE_URL`.
6. Configure Render as a Python web service rooted at `backend`; `backend/.python-version` pins Python 3.11. Build with `pip install -r requirements.txt`; start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` (or legacy `SUPABASE_ANON_KEY`), and exact frontend origin in `ALLOWED_ORIGINS`.
7. Update frontend API URL to the Render HTTPS endpoint and Supabase Auth redirect URLs to the deployed frontend. Redeploy and smoke test health, login, CRUD, RLS, assistant and CSV export.

Use host secret managers for backend environment variables. Enforce HTTPS, narrow CORS, configure backups and monitor provider logs without transaction descriptions or access tokens. No deployment is included in this repo.
