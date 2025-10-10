import os
import time
import shutil


class CleanupService:
    def __init__(self, runs_root: str, hours: int | None = 48, days: int | None = None):
        self.runs_root = runs_root
        self.hours = hours
        self.days = days

    def cleanup(
        self,
        dry_run: bool = True,
        *,
        force: bool = False,
        max_age_hours: int | None = None,
        max_age_days: int | None = None,
        session_id: str | None = None,
    ):
        now = time.time()
        if force:
            cutoff = float("inf")  # Her şeyi hedefle
        else:
            if max_age_days is not None:
                cutoff = now - max_age_days * 86400
            elif max_age_hours is not None:
                cutoff = now - max_age_hours * 3600
            elif self.days is not None:
                cutoff = now - self.days * 86400
            else:
                hours = self.hours if self.hours is not None else 48
                cutoff = now - hours * 3600
        deleted_runs = 0
        deleted_sessions = 0
        errors: list[dict] = []
        if not os.path.isdir(self.runs_root):
            return {"deleted_runs": 0, "deleted_sessions": 0, "dry_run": dry_run, "errors": []}
        for name in os.listdir(self.runs_root):
            dir_path = os.path.join(self.runs_root, name)
            try:
                if not os.path.isdir(dir_path):
                    continue
                if session_id and name != session_id:
                    continue
                if force or os.path.getmtime(dir_path) < cutoff:
                    if not dry_run:
                        try:
                            shutil.rmtree(dir_path)
                        except Exception as e:
                            errors.append({"path": dir_path, "error": str(e)})
                            continue
                    deleted_runs += 1
            except Exception:
                continue
        return {
            "deleted_runs": deleted_runs,
            "deleted_sessions": deleted_sessions,
            "dry_run": dry_run,
            "errors": errors,
        }
