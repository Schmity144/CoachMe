# CoachMe – ostrá verze

- Web: https://coachme-trenink.netlify.app (Netlify projekt `coachme-trenink`, tým schmity144)
- Databáze: Supabase projekt `coachme` (ref `iqrtiypkczsarqimbnqj`, eu-central-1). Schéma je v migracích projektu (coachme_schema, regen_code, regen_code_flag, reset_trainer_change_flag).
- `site/` = to, co se nasazuje (index.html + supabase.js + ikona + manifest). `coachme-web.zip` = totéž zabalené pro ruční nahrání do Netlify.
- `source/` = zdroj: `src.html` je demo, `prod.py` z něj vyrobí ostrou verzi (`bash buildprod.sh`).
- `test/` = testy v Playwrightu s náhradou Supabase (`mock-supabase.js`).

Data: každá tabulka má sloupec `data` (jsonb) s objektem aplikace a sloupce pro oprávnění (trainer_id / client_id). Klienti vidí jen svoje data a šablony svého trenéra, trenér jen své klienty, poznámky trenéra nevidí nikdo jiný, majitel vidí trenéry, klienty, tréninky a nahlášené problémy, ale ne zprávy.
Majitele nastavíš jen v databázi: `update trainers set is_owner = true where data->>'email' = '...'`.
