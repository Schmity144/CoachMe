-- CoachMe v49: každou registraci trenéra schvaluje majitel.
-- POZOR: spustit až spolu s vydáním frontendu (po "zveřejni to"), jinak by noví trenéři v aktuální verzi aplikace uvízli bez vysvětlení.
-- Stávající trenéři zůstávají schválení (výchozí true při přidání sloupce), noví mají false.
alter table public.trainers add column if not exists approved boolean not null default true;
alter table public.trainers alter column approved set default false;

-- trenér si schválení nemůže nastavit sám; mění ho jen approve_trainer (majitel)
create or replace function public.trainers_guard()
returns trigger language plpgsql set search_path to '' as $function$ begin
  if coalesce(auth.jwt()->>'role','') = 'authenticated' then
    if tg_op = 'INSERT' then new.is_owner := false; new.id := auth.uid()::text; new.approved := false;
      if coalesce(current_setting('app.code_change', true),'') <> '1' then new.code := public.gen_trainer_code(); end if;
    else new.is_owner := old.is_owner; new.id := old.id;
      if coalesce(current_setting('app.approve', true),'') <> '1' then new.approved := old.approved; end if;
      if coalesce(current_setting('app.code_change', true),'') <> '1' then new.code := old.code; end if;
    end if;
  end if;
  if new.code is null then new.code := public.gen_trainer_code(); end if;
  new.updated_at := now(); return new; end $function$;

create or replace function public.approve_trainer(p_id text)
returns boolean language plpgsql security definer set search_path to '' as $function$
declare n int;
begin
  if not public.is_owner() then raise exception 'owner only'; end if;
  perform set_config('app.approve', '1', true);
  update public.trainers set approved = true where id = p_id;
  get diagnostics n = row_count;
  perform set_config('app.approve', '', true);
  return n > 0;
end $function$;
revoke all on function public.approve_trainer(text) from public, anon;
grant execute on function public.approve_trainer(text) to authenticated;

-- kód neschváleného trenéra nefunguje
create or replace function public.trainer_by_code(p_code text)
returns json language sql stable security definer set search_path to '' as $function$
  select json_build_object('id', t.id, 'name', t.data->>'name', 'spec', t.data->>'spec')
  from public.trainers t where t.approved and t.code = upper(regexp_replace(coalesce(p_code,''), '\s', '', 'g')) $function$;

create or replace function public.register_client(p_code text, p_name text, p_goal text)
returns json language plpgsql security definer set search_path to '' as $function$
declare t public.trainers;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if exists(select 1 from public.removed_accounts r where r.id = auth.uid()::text) then raise exception 'account removed'; end if;
  if exists(select 1 from public.trainers x where x.id = auth.uid()::text) then raise exception 'already a trainer'; end if;
  select * into t from public.trainers x where x.approved and x.code = upper(regexp_replace(coalesce(p_code,''), '\s', '', 'g'));
  if t.id is null then raise exception 'bad code'; end if;
  perform set_config('app.trainer_change', '1', true);
  insert into public.clients(id, trainer_id, data) values (auth.uid()::text, t.id,
    jsonb_build_object('name', coalesce(nullif(p_name,''),'Klient'), 'goal', coalesce(nullif(p_goal,''),'Zatím nevyplněno'), 'email', auth.jwt()->>'email', 'joined', now(), 'target', 3, 'photo', null, 'status', 'active'))
  on conflict (id) do nothing;
  perform set_config('app.trainer_change', '', true);
  return json_build_object('id', t.id, 'name', t.data->>'name');
end $function$;

create or replace function public.change_trainer(p_code text)
returns json language plpgsql security definer set search_path to '' as $function$
declare t public.trainers;
begin
  select * into t from public.trainers x where x.approved and x.code = upper(regexp_replace(coalesce(p_code,''), '\s', '', 'g'));
  if t.id is null then raise exception 'bad code'; end if;
  perform set_config('app.trainer_change', '1', true);
  update public.clients set trainer_id = t.id where id = auth.uid()::text;
  if not found then raise exception 'not a client'; end if;
  perform set_config('app.trainer_change', '', true);
  update public.templates set trainer_id = t.id where client_id = auth.uid()::text;
  update public.exercises set trainer_id = t.id where client_id = auth.uid()::text;
  return json_build_object('id', t.id, 'name', t.data->>'name');
end $function$;
