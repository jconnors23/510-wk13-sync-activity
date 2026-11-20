# Build the Chroma database once.
# Run this before app.py:
#   python scripts/build-draft-index.py
# It downloads the 2025 draft, turns each pick into one sentence,
# embeds those sentences, and saves them under chromadb/.

import sys
from pathlib import Path

# This file lives in scripts/. Add the project root so the settings module imports.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import chromadb
import nflreadpy as nfl
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import draft_search_settings as settings

# Load the model named in draft_search_settings.py.
# The first run downloads it. Later runs reuse the local copy.
model = SentenceTransformer(settings.MODEL_NAME)

# Pull one draft season from nflverse.
# The parquet URL and the year both live in draft_search_settings.py.
# Each row is one player selected in that draft.
draft = nfl.load_draft_picks(settings.DRAFT_SEASON)

# The draft table stores short codes like QB and WR.
# The search model does not treat QB as the word quarterback,
# so the sentence uses the full word.
POSITION_WORDS = {
    "QB": "quarterback",
    "RB": "running back",
    "WR": "wide receiver",
    "TE": "tight end",
    "OL": "offensive lineman",
    "OT": "offensive tackle",
    "OG": "offensive guard",
    "G": "offensive guard",
    "C": "center",
    "DL": "defensive lineman",
    "DE": "defensive end",
    "DT": "defensive tackle",
    "LB": "linebacker",
    "OLB": "outside linebacker",
    "DB": "defensive back",
    "CB": "cornerback",
    "S": "safety",
    "SAF": "safety",
    "FS": "free safety",
    "K": "kicker",
    "P": "punter",
    "LS": "long snapper",
}

# Round numbers are written as words so "first round" can match.
ROUND_WORDS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
}

# Turn each row into one sentence. That sentence is the chunk.
# A draft row is already a single fact, so we do not split it.
texts = []
ids = []
for row in draft.iter_rows(named=True):
    # Missing text would crash the sentence, so fill a plain fallback.
    name = row["pfr_player_name"] or "Unknown player"
    code = row["position"] or ""
    college = row["college"] or "unknown college"
    team = row["team"] or "an unknown team"
    position = POSITION_WORDS.get(code, code or "unknown position")
    round_word = ROUND_WORDS.get(row["round"], "unknown")

    # One pick, one document. This is the text Chroma stores and returns.
    # The position word comes first. The rest of the sentence looks the same
    # for every player, so the model needs the job title where it is easy to see.
    sentence = (
        f"{position}. {name} is a {position} from {college}. "
        f"{team} drafted him in the {round_word} round of the "
        f"{row['season']} NFL draft, pick {row['pick']}."
    )
    texts.append(sentence)

    # Stable id: year plus overall pick number. Chroma requires strings.
    ids.append(f"{row['season']}-{row['pick']}")

# Embed every sentence with MiniLM.
# normalize_embeddings makes each vector length 1, which cosine distance expects.
embeddings = model.encode(texts, normalize_embeddings=True)

# Open a database on disk.
# An in-memory client would disappear when this script exits.
# PersistentClient keeps chroma.sqlite3 so the app can load it later.
# Telemetry is off so the build does not send a usage ping.
client = chromadb.PersistentClient(
    path=str(settings.DB_DIR),
    settings=Settings(anonymized_telemetry=False),
)

# Drop the old collection if we are rebuilding, then start clean.
# Adding the same ids twice would skip the new text instead of replacing it.
try:
    client.delete_collection(settings.COLLECTION_NAME)
except Exception:
    pass

# Cosine distance: 0 is the same meaning, larger means less alike.
# This only matches the app if both sides used the same model and normalized vectors.
collection = client.create_collection(
    settings.COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)

# Store the sentences and the vectors together, same call as the starter.
collection.add(
    documents=texts,
    embeddings=embeddings.tolist(),
    ids=ids,
)

print(f"Saved {collection.count()} picks to {settings.DB_DIR}")
print(texts[0])
