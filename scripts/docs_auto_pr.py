"""
Docs Auto-PR Script

Bu script, docs/ klasöründeki değişiklikleri tespit eder, özetler ve
otomatik olarak bir pull request (PR) açar.
Kullanım: python scripts/docs_auto_pr.py
"""

import os
import subprocess
import sys
from datetime import datetime

docs_dir = os.path.abspath("docs")
branch_name = f"docs-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def get_changed_docs():
    result = subprocess.run(
        ["git", "status", "--porcelain", docs_dir], capture_output=True, text=True
    )
    changed = []
    for line in result.stdout.splitlines():
        if line and line[0] in ("M", "A", "D"):
            changed.append(line[3:])
    return changed


def create_branch(branch):
    subprocess.run(["git", "checkout", "-b", branch])


def commit_and_push(changed_files, branch):
    subprocess.run(["git", "add"] + changed_files)
    subprocess.run(["git", "commit", "-m", f"docs: otomatik güncelleme ({datetime.now()})"])
    subprocess.run(["git", "push", "origin", branch])


def open_pr(branch):
    pr_title = f"docs: otomatik güncelleme ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    pr_body = "Bu PR docs/ klasöründeki otomatik değişiklikleri içerir."
    subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--base",
            "master",
            "--head",
            branch,
        ]
    )


def main():
    changed = get_changed_docs()
    if not changed:
        print("docs/ klasöründe değişiklik yok.")
        sys.exit(0)
    print(f"Değişen dosyalar: {changed}")
    create_branch(branch_name)
    commit_and_push(changed, branch_name)
    open_pr(branch_name)
    print("Otomatik PR açıldı.")


if __name__ == "__main__":
    main()
