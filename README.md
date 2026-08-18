# 🐙 MTA keep-alive

Ping automático cada 5 minutos (24/7, gratis) al server MTA para mantenerlo
"tocado" en hosts que miden tráfico de red.

- `keepalive.py` — el script (consulta ASE por UDP, puerto del juego + 123)
- `.github/workflows/keepalive.yml` — GitHub Actions que lo corre cada 5 min

## Server configurado (por defecto)

- IP: `51.68.107.75` — Puerto: `12599` (ASE = `12722`)

Para cambiarlo: **Settings → Secrets and variables → Actions → Variables** →
`MTA_IP` y `MTA_PORT` (sobreescriben los valores por defecto).

## Aviso por Discord (opcional)

1. **Settings → Secrets and variables → Actions**
2. Pestaña **Secrets** → **New repository secret**
3. Nombre: `DISCORD_WEBHOOK` → Valor: la URL del webhook de Discord

Te avisará en ese canal cuando el server no responda.

> ⚠️ No evita que el host apague por **monedas o falta de jugadores** — eso
> es política del hosting. Y GitHub a veces bloquea UDP: si las corridas
> siempre fallan, usa tu PC con `python3 keepalive.py 51.68.107.75 12599`.
