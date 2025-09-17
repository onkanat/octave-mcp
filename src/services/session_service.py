from src.models.session import Session
from typing import Dict
from datetime import datetime

class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def get_or_create_session(self, session_id: str, persistent: bool, work_dir: str) -> Session:
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_active = datetime.now()
            return session
        session = Session(session_id, persistent, work_dir)
        self.sessions[session_id] = session
        return session
