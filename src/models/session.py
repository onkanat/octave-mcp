from datetime import datetime
from typing import Optional

class Session:
    def __init__(self, session_id: str, persistent: bool, work_dir: str):
        self.session_id = session_id
        self.persistent = persistent
        self.start_time = datetime.now()
        self.last_active = datetime.now()
        self.work_dir = work_dir
