"""Explicit migration entry point. Never imports config or reads dotenv."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.history import HistoryStore

if __name__ == '__main__':
    dsn = os.environ.get('HISTORY_DATABASE_URL')
    if not dsn:
        raise SystemExit('HISTORY_DATABASE_URL must identify the intended database')
    HistoryStore.from_dsn(dsn).migrate()
    print('History migrations 001–002 complete')
