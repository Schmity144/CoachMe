// CoachMe – odběr kalendáře klienta (webcal). Tajný token je v clients.data.cal.tok.
import { createClient } from "npm:@supabase/supabase-js@2";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const BYDAY = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];
const esc = (s: string) => String(s || "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\r?\n/g, "\\n");
const fold = (l: string) => { const out: string[] = []; let s = l; while (new TextEncoder().encode(s).length > 74) { let n = 70; while (new TextEncoder().encode(s.slice(0, n)).length > 74) n--; const c = s.charCodeAt(n - 1); if (c >= 0xd800 && c < 0xdc00) n--; out.push(s.slice(0, n)); s = " " + s.slice(n); } out.push(s); return out.join("\r\n"); };
const ymd = (d: Date) => d.toISOString().slice(0, 10).replace(/-/g, "");
const utc = (d: Date) => d.toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
const TZ = ["BEGIN:VTIMEZONE", "TZID:Europe/Prague", "BEGIN:DAYLIGHT", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "TZNAME:CEST", "DTSTART:19700329T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT", "BEGIN:STANDARD", "TZOFFSETFROM:+0200", "TZOFFSETTO:+0100", "TZNAME:CET", "DTSTART:19701025T030000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD", "END:VTIMEZONE"];

Deno.serve(async (req) => {
  const t = new URL(req.url).searchParams.get("t") || "";
  if (!/^[A-Za-z0-9]{20,64}$/.test(t)) return new Response("not found", { status: 404 });
  const { data: cl } = await sb.from("clients").select("id,trainer_id,data").filter("data->cal->>tok", "eq", t).maybeSingle();
  if (!cl || !cl.trainer_id) return new Response("not found", { status: 404 });
  const cal = cl.data.cal || {};
  const [{ data: as }, { data: tr }, { data: sl }] = await Promise.all([
    sb.from("assignments").select("id,data").eq("client_id", cl.id),
    sb.from("trainers").select("data").eq("id", cl.trainer_id).maybeSingle(),
    sb.from("slots").select("id,data").eq("client_id", cl.id),
  ]);
  // nejnovější přiřazení každé šablony (stejně jako latestAssign v aplikaci)
  const seen: Record<string, 1> = {};
  const latest = (as || []).map((a) => ({ id: a.id, ...a.data })).sort((a, b) => String(b.date).localeCompare(String(a.date))).filter((a) => seen[a.templateId] ? false : (seen[a.templateId] = 1));
  const withDays = latest.filter((a) => (a.days || []).length);
  const tids = withDays.map((a) => a.templateId);
  const { data: tp } = tids.length ? await sb.from("templates").select("id,data").in("id", tids) : { data: [] };
  const tmap = new Map((tp || []).map((x) => [x.id, x.data]));
  const trName = (tr && tr.data && tr.data.name) || "CoachMe";
  const now = new Date(), L: string[] = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CoachMe//CZ", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:CoachMe – tréninky", "X-WR-TIMEZONE:Europe/Prague", "REFRESH-INTERVAL;VALUE=DURATION:PT1H", "X-PUBLISHED-TTL:PT1H", ...(cal.t ? TZ : [])];
  // pondělí tohoto týdne (Praha je UTC+1/+2, stačí datum)
  const mon = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())); mon.setUTCDate(mon.getUTCDate() - ((mon.getUTCDay() + 6) % 7));
  withDays.forEach((a) => {
    const t = tmap.get(a.templateId); if (!t) return;
    const desc = (t.ex || []).map((e: { name: string; sets?: unknown[] }) => "• " + e.name + (e.sets ? " – " + e.sets.length + "×" : "")).join("\n") + (a.note ? "\n\nVzkaz od trenéra: " + a.note : "");
    (a.days as number[]).forEach((d) => {
      const day = new Date(mon); day.setUTCDate(mon.getUTCDate() + d);
      L.push("BEGIN:VEVENT", "UID:" + a.id + "-" + d + "@coachme", "DTSTAMP:" + utc(now));
      if (cal.t) { const [h, m] = String(cal.t).split(":"); const end = new Date(day); end.setUTCHours(+h, +m + (cal.dur || 60)); L.push("DTSTART;TZID=Europe/Prague:" + ymd(day) + "T" + h.padStart(2, "0") + m.padStart(2, "0") + "00", "DTEND;TZID=Europe/Prague:" + ymd(end) + "T" + String(end.getUTCHours()).padStart(2, "0") + String(end.getUTCMinutes()).padStart(2, "0") + "00"); }
      else { const nx = new Date(day); nx.setUTCDate(day.getUTCDate() + 1); L.push("DTSTART;VALUE=DATE:" + ymd(day), "DTEND;VALUE=DATE:" + ymd(nx), "TRANSP:TRANSPARENT"); }
      L.push("RRULE:FREQ=WEEKLY;BYDAY=" + BYDAY[d], fold("SUMMARY:" + esc("🏋️ " + t.name)), fold("DESCRIPTION:" + esc(desc)), "URL:https://coachme-trenink.netlify.app/?go=workout", "END:VEVENT");
    });
  });
  (sl || []).forEach((s) => {
    const at = new Date(s.data.at); if (isNaN(+at) || at.getTime() < now.getTime() - 60 * 864e5) return;
    const end = new Date(at.getTime() + (s.data.dur || 60) * 60000);
    L.push("BEGIN:VEVENT", "UID:" + s.id + "@coachme", "DTSTAMP:" + utc(now), "DTSTART:" + utc(at), "DTEND:" + utc(end), fold("SUMMARY:" + esc("Osobní trénink – " + trName)), ...(s.data.place ? [fold("LOCATION:" + esc(s.data.place))] : []), "END:VEVENT");
  });
  L.push("END:VCALENDAR");
  return new Response(L.join("\r\n") + "\r\n", { headers: { "content-type": "text/calendar; charset=utf-8", "cache-control": "max-age=900", "content-disposition": "inline; filename=coachme.ics" } });
});
