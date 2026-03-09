import asyncio
import json
import os
import threading
from collections import deque
from datetime import datetime, timezone

import dash
import plotly.graph_objects as go
import websockets
from dash import Dash, Input, Output, dcc, html

BACKEND_WS_URL = os.getenv("BACKEND_WS_URL", "ws://127.0.0.1:8000/ws")
MAX_POINTS = 30

points = deque(maxlen=MAX_POINTS)
status = {"connected": False, "last_error": ""}
state_lock = threading.Lock()


async def consume_backend_ws() -> None:
    while True:
        try:
            async with websockets.connect(BACKEND_WS_URL) as ws:
                with state_lock:
                    status["connected"] = True
                    status["last_error"] = ""
                while True:
                    payload = await ws.recv()
                    data = json.loads(payload)
                    with state_lock:
                        points.append(
                            {
                                "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                                "value": data.get("value", 0),
                            }
                        )
        except Exception as e:
            with state_lock:
                status["connected"] = False
                status["last_error"] = str(e)
            await asyncio.sleep(2)


def run_ws_consumer() -> None:
    asyncio.run(consume_backend_ws())


threading.Thread(target=run_ws_consumer, daemon=True).start()

app: Dash = dash.Dash(__name__)
app.title = "Dash Realtime Dashboard"

app.layout = html.Div(
    [
        html.H1("Realtime Dashboard"),
        html.Div("Status: connecting...", id="status-label", style={"marginBottom": "12px"}),
        dcc.Graph(id="live-chart"),
        dcc.Interval(id="refresh", interval=1000, n_intervals=0),
    ],
    style={"maxWidth": "1000px", "margin": "24px auto", "padding": "0 12px"},
)


@app.callback(
    Output("status-label", "children"),
    Output("live-chart", "figure"),
    Input("refresh", "n_intervals"),
)
def refresh(_n: int):
    with state_lock:
        state = "connected" if status["connected"] else "reconnecting"
        suffix = "" if not status["last_error"] else f" | {status['last_error']}"
        current_points = list(points)

    x_data = [p["timestamp"][-8:] for p in current_points]
    y_data = [p["value"] for p in current_points]

    figure = go.Figure(
        data=[
            go.Scatter(
                x=x_data,
                y=y_data,
                mode="lines",
                name="value",
                line={"shape": "spline"},
            )
        ]
    )
    figure.update_layout(
        title="CSV data stream",
        xaxis_title="time",
        yaxis_title="value",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )

    return f"Status: {state}{suffix}", figure


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
