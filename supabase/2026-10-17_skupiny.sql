-- CoachMe v45: skupiny klientů (vidí je jen trenér, klienti ne)
create table if not exists public.client_groups (
  id text primary key,
  trainer_id text not null,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
create index if not exists client_groups_trainer_idx on public.client_groups(trainer_id);
alter table public.client_groups enable row level security;
create policy client_groups_trainer on public.client_groups for all to authenticated
  using (trainer_id = (select auth.uid()::text))
  with check (trainer_id = (select auth.uid()::text));
alter publication supabase_realtime add table public.client_groups;
