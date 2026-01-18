from fastapi import WebSocket
from typing import Dict, Set


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept connection and register for job updates."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove connection from job updates."""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast_to_job(self, job_id: str, message: dict):
        """Send message to all connections watching a job."""
        if job_id not in self.active_connections:
            return

        dead_connections = set()
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)

        self.active_connections[job_id] -= dead_connections
        if not self.active_connections[job_id]:
            del self.active_connections[job_id]


manager = ConnectionManager()
