-- CoachMe: trainer removes a client, owner removes a trainer with all their clients.
-- Apply to the live project only on release ("zveřejni to").

alter table public.clients alter column trainer_id drop not null;

-- accounts the owner removed can't register again as a trainer
create table if not exists public.removed_accounts (id text primary key, removed_at timestamptz not null default now());
alter table public.removed_accounts enable row level security;

-- unlink one client: trainer-side data about the client goes, the client's own history stays
create or replace function public.detach_client(p_client text)
returns void language plpgsql security definer set search_path to '' as $$
begin
  delete from public.assignments where client_id = p_client;
  delete from public.messages where client_id = p_client;
  delete from public.notes where client_id = p_client;
  perform set_config('app.trainer_change', '1', true);
  update public.clients set trainer_id = null where id = p_client;
  perform set_config('app.trainer_change', '', true);
end $$;
revoke all on function public.detach_client(text) from public, anon, authenticated;

create or replace function public.remove_client(p_client text)
returns void language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if not exists(select 1 from public.clients c where c.id = p_client and c.trainer_id = auth.uid()::text) then
    raise exception 'not your client';
  end if;
  perform public.detach_client(p_client);
end $$;

create or replace function public.remove_trainer(p_trainer text)
returns json language plpgsql security definer set search_path to '' as $$
declare n int := 0; c record;
begin
  if not public.is_owner() then raise exception 'owner only'; end if;
  if p_trainer = auth.uid()::text then raise exception 'cannot remove yourself'; end if;
  if exists(select 1 from public.trainers t where t.id = p_trainer and t.is_owner) then raise exception 'cannot remove owner'; end if;
  for c in select id from public.clients where trainer_id = p_trainer loop
    perform public.detach_client(c.id); n := n + 1;
  end loop;
  delete from public.notes where trainer_id = p_trainer;
  delete from public.templates where trainer_id = p_trainer;
  delete from public.exercises where trainer_id = p_trainer;
  delete from public.trainers where id = p_trainer;
  insert into public.removed_accounts(id) values (p_trainer) on conflict do nothing;
  return json_build_object('clients', n);
end $$;

revoke all on function public.remove_client(text) from public, anon;
revoke all on function public.remove_trainer(text) from public, anon;
grant execute on function public.remove_client(text) to authenticated;
grant execute on function public.remove_trainer(text) to authenticated;

-- block re-registration of a removed trainer account
create or replace function public.register_trainer(p_name text, p_spec text)
returns void language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if exists(select 1 from public.removed_accounts r where r.id = auth.uid()::text) then raise exception 'account removed'; end if;
  if exists(select 1 from public.clients c where c.id = auth.uid()::text) then raise exception 'already a client'; end if;
  insert into public.trainers(id, code, data) values (auth.uid()::text, public.gen_trainer_code(),
    jsonb_build_object('name', coalesce(nullif(p_name,''),'Trenér'), 'email', auth.jwt()->>'email', 'spec', coalesce(p_spec,''), 'bio', '', 'photo', null, 'joined', now()))
  on conflict (id) do nothing;
end $$;

create or replace function public.register_client(p_code text, p_name text, p_goal text)
returns json language plpgsql security definer set search_path to '' as $$
declare t public.trainers;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if exists(select 1 from public.removed_accounts r where r.id = auth.uid()::text) then raise exception 'account removed'; end if;
  if exists(select 1 from public.trainers x where x.id = auth.uid()::text) then raise exception 'already a trainer'; end if;
  select * into t from public.trainers x where x.code = upper(regexp_replace(coalesce(p_code,''), '\s', '', 'g'));
  if t.id is null then raise exception 'bad code'; end if;
  perform set_config('app.trainer_change', '1', true);
  insert into public.clients(id, trainer_id, data) values (auth.uid()::text, t.id,
    jsonb_build_object('name', coalesce(nullif(p_name,''),'Klient'), 'goal', coalesce(nullif(p_goal,''),'Zatím nevyplněno'), 'email', auth.jwt()->>'email', 'joined', now(), 'target', 3, 'photo', null, 'status', 'active'))
  on conflict (id) do nothing;
  perform set_config('app.trainer_change', '', true);
  return json_build_object('id', t.id, 'name', t.data->>'name');
end $$;
