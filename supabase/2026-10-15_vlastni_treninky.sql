-- CoachMe: clients create their own templates and exercises.
-- A client-made row has client_id = the client and trainer_id = the client's current trainer (null without one).
-- Only that client and their trainer see it; other clients of the trainer do not.

alter table public.templates add column if not exists client_id text references public.clients(id) on delete cascade;
alter table public.exercises add column if not exists client_id text references public.clients(id) on delete cascade;
alter table public.templates alter column trainer_id drop not null;
alter table public.exercises alter column trainer_id drop not null;
create index if not exists templates_client_idx on public.templates(client_id);
create index if not exists exercises_client_idx on public.exercises(client_id);

-- clients read the trainer's shared rows plus their own, never another client's
drop policy if exists tp_sel on public.templates;
create policy tp_sel on public.templates for select using (
  trainer_id = (select auth.uid()::text)
  or (client_id is null and trainer_id = (select public.my_trainer()))
  or client_id = (select auth.uid()::text));
drop policy if exists ex_sel on public.exercises;
create policy ex_sel on public.exercises for select using (
  trainer_id = (select auth.uid()::text)
  or (client_id is null and trainer_id = (select public.my_trainer()))
  or client_id = (select auth.uid()::text));

-- clients write only their own rows, tied to their current trainer
drop policy if exists tp_client on public.templates;
create policy tp_client on public.templates for all
  using (client_id = (select auth.uid()::text))
  with check (client_id = (select auth.uid()::text) and (trainer_id is null or trainer_id = (select public.my_trainer())));
drop policy if exists ex_client on public.exercises;
create policy ex_client on public.exercises for all
  using (client_id = (select auth.uid()::text))
  with check (client_id = (select auth.uid()::text) and (trainer_id is null or trainer_id = (select public.my_trainer())));

-- unlinking a client hides their own templates/exercises from the old trainer
create or replace function public.detach_client(p_client text)
returns void language plpgsql security definer set search_path to '' as $$
begin
  delete from public.assignments where client_id = p_client;
  delete from public.messages where client_id = p_client;
  delete from public.notes where client_id = p_client;
  update public.templates set trainer_id = null where client_id = p_client;
  update public.exercises set trainer_id = null where client_id = p_client;
  perform set_config('app.trainer_change', '1', true);
  update public.clients set trainer_id = null where id = p_client;
  perform set_config('app.trainer_change', '', true);
end $$;
revoke all on function public.detach_client(text) from public, anon, authenticated;

-- a new trainer sees the client's own templates/exercises
create or replace function public.change_trainer(p_code text)
returns json language plpgsql security definer set search_path to '' as $$
declare t public.trainers;
begin
  select * into t from public.trainers x where x.code = upper(regexp_replace(coalesce(p_code,''), '\s', '', 'g'));
  if t.id is null then raise exception 'bad code'; end if;
  perform set_config('app.trainer_change', '1', true);
  update public.clients set trainer_id = t.id where id = auth.uid()::text;
  if not found then raise exception 'not a client'; end if;
  perform set_config('app.trainer_change', '', true);
  update public.templates set trainer_id = t.id where client_id = auth.uid()::text;
  update public.exercises set trainer_id = t.id where client_id = auth.uid()::text;
  return json_build_object('id', t.id, 'name', t.data->>'name');
end $$;
