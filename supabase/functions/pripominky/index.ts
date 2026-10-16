// CoachMe – ranní připomínka tréninku (web push). Volá ji pg_cron každých 15 minut.
import webpush from "npm:web-push@3.6.7";
import { createClient } from "npm:@supabase/supabase-js@2";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const cfg = async (k: string) => (await sb.rpc("push_cfg", { p_k: k })).data as string | null;

Deno.serve(async (req) => {
  const secret = await cfg("cron_secret");
  if (!secret || req.headers.get("x-cron-secret") !== secret) return new Response("forbidden", { status: 403 });
  const [pub, priv] = await Promise.all([cfg("vapid_public"), cfg("vapid_private")]);
  if (!pub || !priv) return new Response("no keys", { status: 500 });
  webpush.setVapidDetails("mailto:schmidt.misak@seznam.cz", pub, priv);

  const { data: due, error } = await sb.rpc("push_due");
  if (error) return new Response(error.message, { status: 500 });
  const sent: string[] = [];
  let off = 0;
  for (const r of due ?? []) {
    const payload = JSON.stringify({
      title: "Dnes máš trénink 💪",
      body: (r.tpl_name ? r.tpl_name + " · " : "") + "klepni a začni",
      url: "/?go=workout",
    });
    try {
      await webpush.sendNotification(r.sub, payload, { TTL: 4 * 3600, urgency: "normal" });
      sent.push(r.id);
    } catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) { await sb.rpc("push_off", { p_id: r.id }); off++; }
    }
  }
  if (sent.length) await sb.rpc("push_mark", { ids: sent });
  return Response.json({ due: due?.length ?? 0, sent: sent.length, off });
});
