-- CoachMe v43: rezervace osobních tréninků
-- Trenér vypisuje volné termíny (client_id null). Klient si termín zabere / uvolní jen přes RPC book_slot / cancel_slot.
create table if not exists public.slots (
  id text primary key,
  trainer_id text not null,
  client_id text,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
create index if not exists slots_trainer_idx on public.slots(trainer_id);
create index if not exists slots_client_idx on public.slots(client_id);
alter table public.slots enable row level security;
-- trenér spravuje své termíny
create policy slots_trainer on public.slots for all to authenticated
  using (trainer_id = (select auth.uid()::text))
  with check (trainer_id = (select auth.uid()::text));
-- klient vidí termíny svého trenéra (volné i obsazené)
create policy slots_client_sel on public.slots for select to authenticated
  using (trainer_id = (select public.my_trainer()));
alter publication supabase_realtime add table public.slots;

create or replace function public.book_slot(p_id text)
returns boolean language plpgsql security definer set search_path to '' as $$
begin
  update public.slots set client_id = auth.uid()::text, updated_at = now()
   where id = p_id and client_id is null
     and trainer_id = (select c.trainer_id from public.clients c where c.id = auth.uid()::text)
     and (data->>'at')::timestamptz > now();
  return found;
end $$;

create or replace function public.cancel_slot(p_id text)
returns boolean language plpgsql security definer set search_path to '' as $$
begin
  update public.slots set client_id = null, updated_at = now()
   where id = p_id and client_id = auth.uid()::text
     and (data->>'at')::timestamptz > now() + interval '12 hours';
  return found;
end $$;
revoke all on function public.book_slot(text) from public, anon;
revoke all on function public.cancel_slot(text) from public, anon;
grant execute on function public.book_slot(text) to authenticated;
grant execute on function public.cancel_slot(text) to authenticated;

-- klient, který odejde od trenéra, uvolní své budoucí rezervace u něj
create or replace function public.client_slots_free()
returns trigger language plpgsql security definer set search_path to '' as $$
begin
  update public.slots set client_id = null, updated_at = now()
   where client_id = new.id and trainer_id = old.trainer_id and (data->>'at')::timestamptz > now();
  return new;
end $$;
revoke all on function public.client_slots_free() from public, anon, authenticated;
create trigger clients_slots_free after update of trainer_id on public.clients
  for each row when (old.trainer_id is distinct from new.trainer_id)
  execute function public.client_slots_free();
