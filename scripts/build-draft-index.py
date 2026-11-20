# Download the 2025 draft, embed one sentence per pick, and save chromadb/.
# Run before app.py: python scripts/build-draft-index.py

import sys
from pathlib import Path

# This file is in scripts/. Import settings from the project root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import chromadb
import nflreadpy as nfl
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import draft_search_settings as settings

model = SentenceTransformer(settings.MODEL_NAME)
draft = nfl.load_draft_picks(settings.DRAFT_SEASON)

# MiniLM does not treat QB as quarterback, so the sentence uses the full word.
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

ROUND_WORDS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
}

texts = []
ids = []
for row in draft.iter_rows(named=True):
    name = row["pfr_player_name"] or "Unknown player"
    code = row["position"] or ""
    college = row["college"] or "unknown college"
    team = row["team"] or "an unknown team"
    position = POSITION_WORDS.get(code, code or "unknown position")
    round_word = ROUND_WORDS.get(row["round"], "unknown")

    # Position comes first so it is not lost in the shared sentence.
    sentence = (
        f"{position}. {name} is a {position} from {college}. "
        f"{team} drafted him in the {round_word} round of the "
        f"{row['season']} NFL draft, pick {row['pick']}."
    )
    texts.append(sentence)
    ids.append(f"{row['season']}-{row['pick']}")

embeddings = model.encode(texts, normalize_embeddings=True)

client = chromadb.PersistentClient(
    path=str(settings.DB_DIR),
    settings=Settings(anonymized_telemetry=False),
)

# Re-adding the same ids would skip the new text, so delete first.
try:
    client.delete_collection(settings.COLLECTION_NAME)
except Exception:
    pass

collection = client.create_collection(
    settings.COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)
collection.add(
    documents=texts,
    embeddings=embeddings.tolist(),
    ids=ids,
)

print(f"Saved {collection.count()} picks to {settings.DB_DIR}")
print(texts[0])
