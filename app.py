# Search page for the 2025 NFL draft. It takes a typed question, finds the
# five draft picks whose sentences are closest in meaning, and shows them.
# This file only reads the database. Create it first with:
#   python scripts/build-draft-index.py

import chromadb
import gradio as gr
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import draft_search_settings as settings

# Load the same embedding model the build script used. Numbers from two
# different models cannot be compared, so the distances would be wrong.
model = SentenceTransformer(settings.MODEL_NAME)

# Open the database folder made by the build script. If the folder or the
# collection is missing, get_collection fails. This file never creates it.
client = chromadb.PersistentClient(
    path=str(settings.DB_DIR),
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection(settings.COLLECTION_NAME)


def semantic_search(query):
    query = (query or "").strip()
    if not query:
        return "Type a search, such as: quarterback."

    # Scale the question's embedding to length 1, the same way the build
    # script scaled the sentence embeddings. Keep this setting identical in both files.
    query_embedding = model.encode([query], normalize_embeddings=True)
    # Ask Chroma for the N_RESULTS closest sentences (set in
    # draft_search_settings.py). Distance is 0 for the same meaning and grows
    # as the meaning differs, so a smaller number is a better match.
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=settings.N_RESULTS,
    )

    lines = []
    documents = results["documents"][0]
    distances = results["distances"][0]
    for document, distance in zip(documents, distances):
        lines.append(f"{distance:.3f} — {document}")
    return "\n\n".join(lines)


# Build the page: one input box, one output box, and four example questions
# a visitor can click. The "if __name__" check at the bottom starts the web
# server only when you run `python app.py`, not when another file imports this one.
demo = gr.Interface(
    fn=semantic_search,
    inputs=gr.Textbox(label="Enter your search query"),
    outputs=gr.Textbox(label="Top Matches"),
    title="Semantic Search Engine",
    description=(
        "Search the 2025 NFL draft. "
        "Source: https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.parquet. "
        "A smaller distance is a closer match."
    ),
    examples=[
        "quarterback",
        "wide receiver",
        "kicker",
        "defensive end",
    ],
)

if __name__ == "__main__":
    demo.launch()
