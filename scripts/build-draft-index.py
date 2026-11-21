# Build the search database in four steps: download the 2025 draft picks,
# write one sentence per pick, turn each sentence into a list of numbers,
# and save sentences and numbers in chromadb/.
# Needs internet on the first run (draft data and embedding model).
# Run from the project root, before app.py:
#   python scripts/build-draft-index.py
# This script does not write the CSV files in data/. The notebook writes
# data/processed/, and nothing in the project writes data/raw/.

import sys
from pathlib import Path

# Python looks for imports next to the file being run, which is scripts/.
# Add the project root so "import draft_search_settings" works below.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import chromadb
import nflreadpy as nfl
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import draft_search_settings as settings

model = SentenceTransformer(settings.MODEL_NAME)
# Download the draft table and keep only the season in DRAFT_SEASON.
# The result has one row per drafted player.
draft = nfl.load_draft_picks(settings.DRAFT_SEASON)

# Spell out position codes. The model works on ordinary words, so a search
# for "quarterback" matches the word "quarterback" better than the code "QB".
# A code missing from this table is used as written.
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

# Round numbers as words, so a search for "first round" can match.
# A round above 7 becomes "unknown". The 2025 draft has rounds 1 to 7 only.
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

    # Put the position first and repeat it. After the position, every sentence
    # uses the same wording, so repeating it makes position a larger part of
    # what the model sees. Example output:
    #   quarterback. Cam Ward is a quarterback from Miami (FL). TEN drafted him
    #   in the first round of the 2025 NFL draft, pick 1.
    sentence = (
        f"{position}. {name} is a {position} from {college}. "
        f"{team} drafted him in the {round_word} round of the "
        f"{row['season']} NFL draft, pick {row['pick']}."
    )
    texts.append(sentence)
    # Chroma needs a unique text id for each sentence. The id is season-pick,
    # so 2025-1 is the first overall pick of 2025.
    ids.append(f"{row['season']}-{row['pick']}")

# Turn each sentence into 384 numbers, scaled to length 1. app.py applies
# the same setting to the typed question.
embeddings = model.encode(texts, normalize_embeddings=True)

# Save to disk, so the database is still there after this script exits.
client = chromadb.PersistentClient(
    path=str(settings.DB_DIR),
    settings=Settings(anonymized_telemetry=False),
)

# Remove the old collection so a re-run replaces it. Adding the same ids
# again would keep the old text. On the first run no collection exists, so
# the error is expected and ignored. Note: this also ignores any other error
# from delete_collection.
try:
    client.delete_collection(settings.COLLECTION_NAME)
except Exception:
    pass

# Score matches by cosine distance (Chroma's default is squared L2 distance).
# Smaller means the question and the pick are closer in meaning.
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
