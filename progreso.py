"""Progreso en vivo del pipeline de agentes.

La app corre en un solo proceso y atiende un pipeline a la vez, así que basta un
estado global (no hace falta un id de trabajo por petición). Cada agente marca su
paso al empezar y el frontend lo sondea con GET /api/progress para pintar la tira
de pasos en tiempo real. Todos los agentes viven en el mismo proceso (main.py monta
sus routers juntos), por eso este módulo compartido les vale a todos.
"""
import threading
import time

_lock = threading.Lock()
_estado = {"paso": None, "activo": False, "ts": 0.0}

# Orden canónico de los pasos; el frontend mapea cada id a su etiqueta.
PASOS = ("cinefilo", "escritor", "agrupador", "bbdd", "obsi")


def iniciar():
    """Arranca una vuelta nueva (borra el paso de la anterior)."""
    with _lock:
        _estado.update(paso=None, activo=True, ts=time.time())


def set_paso(paso):
    """Marca el agente que está trabajando ahora mismo."""
    with _lock:
        _estado.update(paso=paso, activo=True, ts=time.time())


def terminar():
    with _lock:
        _estado["activo"] = False


def get():
    with _lock:
        return dict(_estado)
