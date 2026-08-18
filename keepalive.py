#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
keepalive.py — mantén "tocado" tu server MTA por UDP (ASE)
===========================================================
Envía una consulta ASE al server cada N minutos para que, en hosts que
miden tráfico de red (y no jugadores), el server no se duerma.

⚠️ IMPORTANTE:
  - No sirve si el host apaga por FALTA DE JUGADORES o MONEDAS (política
    del host: reclama la recompensa diaria en su panel).
  - Un navegador/página web NO puede mandar UDP: esto corre en una máquina
    siempre encendida (tu PC, un VPS, GitHub Actions, etc.).

Uso:
    python3 keepalive.py 1.2.3.4 22003            # ping cada 4 min
    python3 keepalive.py 1.2.3.4 22003 --once     # un solo ping (CI/cron)
    python3 keepalive.py 1.2.3.4 22003 -i 60      # ping cada 60 s
"""

import argparse
import socket
import sys
import time

# Evita que la terminal de Windows (cp1252) truene con emojis/acentos
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_INTERVAL = 20  # segundos (20s — maximo agresivo)


def query_ase(ip: str, port: int, timeout: float = 3.0) -> dict | None:
    """Consulta ASE completa: devuelve info del server o None si no responde."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(b"s", (ip, port + 123))
        data, _ = s.recvfrom(8192)
    except (socket.timeout, OSError):
        return None
    finally:
        s.close()

    if data[:4] != b"EYE1":
        return None

    i = 4
    length = data[i]; i += 1
    i += length - 1

    info = []
    for _ in range(8):
        slen = data[i]; i += 1
        s_str = data[i:i + slen - 1].decode("utf-8", "replace"); i += slen - 1
        info.append(s_str)

    def to_int(s):
        try:
            return int(s or 0)
        except ValueError:
            return 0

    return {
        "name": info[1] if len(info) > 1 else "?",
        "gamemode": info[2] if len(info) > 2 else "?",
        "map": info[3] if len(info) > 3 else "?",
        "players": to_int(info[6]) if len(info) > 6 else 0,
        "max_players": to_int(info[7]) if len(info) > 7 else 0,
        "version": info[4] if len(info) > 4 else "?",
    }


def ping(ip: str, port: int, timeout: float = 3.0) -> bool:
    """Manda el byte 's' (consulta ASE) y espera respuesta corta."""
    result = query_ase(ip, port, timeout)
    return result is not None


def parse_args(argv):
    p = argparse.ArgumentParser(description="Ping ASE a un server MTA")
    p.add_argument("ip", help="IP del server MTA")
    p.add_argument("port", nargs="?", type=int, default=22003,
                   help="puerto del juego (ASE = juego + 123)")
    p.add_argument("--once", action="store_true",
                   help="un solo ping y salir (exit 0 = ok, 1 = sin respuesta)")
    p.add_argument("-i", "--interval", type=int, default=DEFAULT_INTERVAL,
                   help=f"segundos entre pings (default {DEFAULT_INTERVAL})")
    return p.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    ase_port = args.port + 123
    print(f"keepalive → {args.ip}:{ase_port} (ASE)", flush=True)

    if args.once:
        result = query_ase(args.ip, args.port)
        if result:
            print(f"ping OK | Players: {result['players']}/{result['max_players']} | Server: {result['name']} | GM: {result['gamemode']} | Map: {result['map']}", flush=True)
            return 0
        else:
            print("ping FAIL | sin respuesta", flush=True)
            return 1

    ok = fail = 0
    while True:
        if ping(args.ip, args.port):
            ok += 1
            print(f"[{time.strftime('%H:%M:%S')}] ping OK  (ok={ok} fallos={fail})", flush=True)
        else:
            fail += 1
            print(f"[{time.strftime('%H:%M:%S')}] ⚠ sin respuesta (ok={ok} fallos={fail})", flush=True)
        time.sleep(max(10, args.interval))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nkeepalive detenido.")
