# Shared settings for the draft search.
# scripts/build-draft-index.py and app.py both import this file.
# Change a value here once. Do not copy these values into the other files.
# The build script and the app must agree on the model, the folder, and the
# collection name. If they do not, search distances are meaningless or the
# app cannot open the database.

from pathlib import Path

# Folder that contains this file. Paths below start here, so
# `python app.py` still finds the database from any working directory.
ROOT = Path(__file__).resolve().parent

# Embedding model. Indexing and search must use this exact name.
# Indexing and search must use this exact model.
# It returns 384 numbers per sentence. Both scripts normalize those
# vectors to length 1, which is what cosine distance in Chroma expects.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# On-disk Chroma database. A finished build writes chroma.sqlite3 here.
# The app only reads this folder. It does not download the draft.
DB_DIR = ROOT / "chromadb"

# Collection name inside DB_DIR.
# The build script deletes this name and writes it again.
# The app loads this same name. A mismatch raises a missing-collection error.
COLLECTION_NAME = "draft_2025"

# How many nearest picks one search returns.
N_RESULTS = 5

# Season passed to nflreadpy.load_draft_picks.
# Source file, all drafts since 1980:
# https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.parquet
# This year keeps the 2025 rows only. True, or no year, loads every season.
DRAFT_SEASON = 2025
