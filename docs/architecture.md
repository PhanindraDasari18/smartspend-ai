# Architecture

React/Vite owns presentation and ordinary CRUD through Supabase JS. Supabase Auth provides user sessions; PostgreSQL RLS constrains each transaction, budget and feedback row to `auth.uid() = user_id`. The frontend passes its short lived bearer access token plus a minimal transaction slice to FastAPI only for categorization or analysis. FastAPI validates that token by calling Supabase Auth `/auth/v1/user` with the anon key, then computes answers from the request data. It has no privileged database credentials.

The finance calculation service uses `Decimal`; chart display converts to numbers only after database values are fetched. Merchant categorization uses documented exact substring rules and otherwise flags the prediction for review. Statistical outliers require at least five observations per category and use median/MAD safeguards. A future evaluated sklearn model can be added behind the same prediction API.
