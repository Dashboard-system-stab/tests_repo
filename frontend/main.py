import asyncio
import json
import os
from collections import deque
from datetime import datetime, timezone

import websockets
from nicegui import app, ui

BACKEND_WS_URL = os.getenv("BACKEND_WS_URL", "ws://127.0.0.1:8000/ws")
MAX_POINTS = 30

points = deque(maxlen=MAX_POINTS)
status = {"connected": False, "last_error": ""}


async def consume_backend_ws() -> None:
    while True:
        try:
            async with websockets.connect(BACKEND_WS_URL) as ws:
                status["connected"] = True
                status["last_error"] = ""
                while True:
                    payload = await ws.recv()
                    data = json.loads(payload)
                    points.append(
                        {
                            "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                            "value": data.get("value", 0),
                        }
                    )
        except Exception as e:
            status["connected"] = False
            status["last_error"] = str(e)
            await asyncio.sleep(2)


@ui.page("/")
def dashboard() -> None:
    ui.label("Realtime Dashboard").classes("text-2xl font-bold")
    status_label = ui.label("Status: connecting...")

    chart = ui.echart(
        {
            "title": {"text": "CSV data stream"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": []},
            "yAxis": {"type": "value"},
            "series": [{"name": "value", "type": "line", "smooth": True, "data": []}],
        }
    ).classes("w-full h-96")

    def refresh() -> None:
        state = "connected" if status["connected"] else "reconnecting"
        suffix = "" if not status["last_error"] else f" | {status['last_error']}"
        status_label.set_text(f"Status: {state}{suffix}")

        x_data = [p["timestamp"][-8:] for p in points]
        y_data = [p["value"] for p in points]
        chart.options["xAxis"]["data"] = x_data
        chart.options["series"][0]["data"] = y_data
        chart.update()

    ui.timer(1.0, refresh)


async def on_startup() -> None:
    asyncio.create_task(consume_backend_ws())


app.on_startup(on_startup)
ui.run(title="NiceGUI Realtime Dashboard", host="0.0.0.0", port=8080, reload=False)
