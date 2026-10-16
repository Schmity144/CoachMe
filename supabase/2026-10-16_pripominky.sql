-- CoachMe v42: připomínka tréninku (web push)
-- Klíče (VAPID + tajný klíč pro cron) se vkládají zvlášť do push.config, NEJSOU v tomto souboru.
create extension if not exists pg_cron;
create extension if not exists pg_net;

create schema if not exists push;
revoke all on schema push from public, anon, authenticated;
create table if not exists push.config (k text primary key, v text not null);
revoke all on push.config from public, anon, authenticated;

create table if not exists public.push_subs (
  id text primary key,
  client_id text not null default (auth.uid())::text,
  sub jsonb not null,
  hour int not null default 8 check (hour between 0 and 23),
  tz text not null default 'Europe/Prague',
  "on" boolean not null default true,
  last_sent date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists push_subs_client on public.push_subs(client_id);
alter table public.push_subs enable row level security;
create policy push_subs_own on public.push_subs for all to authenticated
  using (client_id = (select auth.uid())::text)
  with check (client_id = (select auth.uid())::text);

-- Kdo má dnes v místním čase naplánovaný trénink, je hodina připomínky a dnes ještě necvičil
create or replace function public.push_due()
returns table(id text, sub jsonb, tpl_name text)
language sql security definer set search_path = public as $$
  with s as (
    select p.*, (now() at time zone p.tz) as loc from push_subs p
    where p."on" and extract(hour from (now() at time zone p.tz))::int = p.hour
      and (p.last_sent is null or p.last_sent < (now() at time zone p.tz)::date)
  ), la as (
    select distinct on (a.client_id, a.data->>'templateId') a.client_id, a.data
    from assignments a order by a.client_id, a.data->>'templateId', a.data->>'date' desc
  )
  select s.id, s.sub, (select t.data->>'name' from la join templates t on t.id = la.data->>'templateId'
      where la.client_id = s.client_id and coalesce(la.data->'days','[]'::jsonb) @> to_jsonb(extract(isodow from s.loc)::int - 1)
      limit 1)
  from s
  where exists (select 1 from la join templates t on t.id = la.data->>'templateId'
      where la.client_id = s.client_id and coalesce(la.data->'days','[]'::jsonb) @> to_jsonb(extract(isodow from s.loc)::int - 1))
    and not exists (select 1 from sessions x where x.client_id = s.client_id
      and ((x.data->>'date')::timestamptz at time zone s.tz)::date = s.loc::date);
$$;

create or replace function public.push_mark(ids text[])
returns void language sql security definer set search_path = public as $$
  update push_subs set last_sent = (now() at time zone tz)::date where id = any(ids);
$$;

create or replace function public.push_off(p_id text)
returns void language sql security definer set search_path = public as $$
  update push_subs set "on" = false, updated_at = now() where id = p_id;
$$;

create or replace function public.push_cfg(p_k text)
returns text language sql security definer set search_path = public as $$
  select v from push.config where k = p_k;
$$;

revoke all on function public.push_due() from public, anon, authenticated;
revoke all on function public.push_mark(text[]) from public, anon, authenticated;
revoke all on function public.push_off(text) from public, anon, authenticated;
revoke all on function public.push_cfg(text) from public, anon, authenticated;
grant execute on function public.push_due() to service_role;
grant execute on function public.push_mark(text[]) to service_role;
grant execute on function public.push_off(text) to service_role;
grant execute on function public.push_cfg(text) to service_role;
