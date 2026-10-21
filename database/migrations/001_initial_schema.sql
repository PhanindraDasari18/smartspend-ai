create extension if not exists "pgcrypto";

create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  occurred_on date not null,
  description text not null check (char_length(description) between 1 and 300),
  merchant text,
  amount numeric(12,2) not null check (amount > 0),
  transaction_type text not null check (transaction_type in ('income','expense','refund')),
  category text not null default 'Other',
  payment_method text,
  source text not null default 'manual' check (source in ('manual','import','demo')),
  import_fingerprint text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists transactions_user_date_idx on public.transactions(user_id, occurred_on desc);
create index if not exists transactions_user_category_idx on public.transactions(user_id, category);
create index if not exists transactions_import_fingerprint_idx on public.transactions(user_id, import_fingerprint) where import_fingerprint is not null;

create table if not exists public.budgets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  month_start date not null check (extract(day from month_start) = 1),
  category text not null,
  limit_amount numeric(12,2) not null check (limit_amount > 0),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique(user_id, month_start, category)
);
create table if not exists public.category_feedback (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  transaction_id uuid not null references public.transactions(id) on delete cascade,
  predicted_category text not null, correct_category text not null,
  created_at timestamptz not null default now(),
  unique(user_id, transaction_id)
);

alter table public.transactions enable row level security;
alter table public.budgets enable row level security;
alter table public.category_feedback enable row level security;
drop policy if exists "transactions own rows" on public.transactions;
drop policy if exists "budgets own rows" on public.budgets;
drop policy if exists "feedback own rows" on public.category_feedback;
create policy "transactions own rows" on public.transactions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "budgets own rows" on public.budgets for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "feedback own rows" on public.category_feedback for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create or replace function public.set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end; $$;
drop trigger if exists transactions_set_updated_at on public.transactions;
create trigger transactions_set_updated_at before update on public.transactions for each row execute function public.set_updated_at();
drop trigger if exists budgets_set_updated_at on public.budgets;
create trigger budgets_set_updated_at before update on public.budgets for each row execute function public.set_updated_at();
