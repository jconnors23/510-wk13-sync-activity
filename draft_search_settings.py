# Settings used by both scripts/build-draft-index.py (writes the database)
# and app.py (reads it). After you change a value here, run the build script
# again. If the build and the app use different values, the app either
# cannot find the collection or returns distances that mean nothing.

from pathlib import Path

# Project root, so the app finds chromadb/ from any working directory.
ROOT = Path(__file__).resolve().parent

# Embedding model from Hugging Face. It turns each sentence into a list of
# 384 numbers. It is downloaded on first use (needs internet), then reused.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# The build writes this folder. The app only reads it.
DB_DIR = ROOT / "chromadb"
# The build deletes this name and writes it again. The app loads the same name.
COLLECTION_NAME = "draft_2025"
# How many nearest picks one search returns.
N_RESULTS = 5

# The season to index. It is passed to nflreadpy's load_draft_picks().
# Passing True instead of a year loads every season since 1980. If you
# change this, also change COLLECTION_NAME, and note that ROUND_WORDS in the
# build script only covers rounds 1 to 7 (older drafts had more rounds).
# Data source: https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.parquet
DRAFT_SEASON = 2025
