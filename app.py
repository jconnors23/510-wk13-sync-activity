# Search app for the saved draft index.
# Start it with:
#   python app.py
# The build script must be run first so chromadb/chroma.sqlite3 exists.

import chromadb
import gradio as gr
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import draft_search_settings as settings

# Load the model named in draft_search_settings.py.
# The question is embedded with this same model, then compared to the stored vectors.
model = SentenceTransformer(settings.MODEL_NAME)

# Open the database the build script wrote. Do not rebuild it here.
# Telemetry is off so opening the database does not send a usage ping.
client = chromadb.PersistentClient(
    path=str(settings.DB_DIR),
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection(settings.COLLECTION_NAME)


def semantic_search(query):
    # Embed the question, then ask Chroma for the nearest sentences.
    query = (query or "").strip()
    if not query:
        return "Type a search, such as: quarterback."

    # One vector for the user's sentence.
    # Same normalize flag as the build script, so the two vectors can be compared.
    query_embedding = model.encode([query], normalize_embeddings=True)

    # How many hits to return is set in draft_search_settings.py.
    # Smaller distance means a closer pick.
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=settings.N_RESULTS,
    )

    # Pair each returned sentence with its distance so the score is visible.
    lines = []
    documents = results["documents"][0]
    distances = results["distances"][0]
    for document, distance in zip(documents, distances):
        lines.append(f"{distance:.3f} — {document}")

    # Gradio shows this string in the output box.
    return "\n\n".join(lines)


# One text box in, one text box out.
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
