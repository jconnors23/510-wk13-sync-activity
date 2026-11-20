# Shared by the build script and app.py. Both must use these same values.

from pathlib import Path

# Project root, so the app finds chromadb/ from any working directory.
ROOT = Path(__file__).resolve().parent

# 384-d MiniLM. Both sides normalize vectors for cosine distance.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DB_DIR = ROOT / "chromadb"
COLLECTION_NAME = "draft_2025"
N_RESULTS = 5

# Year passed to load_draft_picks. True loads every draft since 1980.
# https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.parquet
DRAFT_SEASON = 2025
