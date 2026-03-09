# Realtime Dashboard (FastAPI + NiceGUI/Dash)

## Структура
- `backend/` - FastAPI сервер, читает `data.csv` и стримит точки по WebSocket `/ws`
- `frontend/` - NiceGUI dashboard, получает точки с backend по WebSocket и рисует live-график
- `frontend-dash/` - Dash dashboard с тем же источником данных и тем же портом

## Запуск

1. Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Сервер: `http://127.0.0.1:8000`, websocket: `ws://127.0.0.1:8000/ws`

2. Frontend (в отдельном терминале):
```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Dashboard: `http://127.0.0.1:8080`

## Запуск в Docker (backend + выбранный frontend)

```bash
docker compose --profile nicegui up --build
```

или

```bash
docker compose --profile dash up --build
```

- Backend: `http://127.0.0.1:8000`
- Frontend Dashboard: `http://127.0.0.1:8080`

Профили:
- `nicegui` -> сервис `frontend-nicegui`
- `dash` -> сервис `frontend-dash`

Важно: одновременно включать оба frontend-профиля нельзя, т.к. оба используют `8080:8080`.

Остановка:
```bash
docker compose down
```

## Формат данных
`backend/data.csv`:
```csv
timestamp,value
2026-03-09T10:00:00,12
```

Backend циклически отправляет строки CSV каждые 1 секунду.
