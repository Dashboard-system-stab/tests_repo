import asyncio
import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Realtime CSV Backend")
DATA_FILE = Path(__file__).parent / "data.csv"


def load_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "timestamp": row["timestamp"],
                    "value": float(row["value"]),
                }
            )
    return rows


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def stream_csv(websocket: WebSocket) -> None:
    await websocket.accept()
    rows = load_rows()

    try:
        while True:
            for row in rows:
                payload = {
                    "timestamp": row["timestamp"],
                    "value": row["value"],
                    "server_time": datetime.utcnow().isoformat() + "Z",
                }
                await websocket.send_json(payload)
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
