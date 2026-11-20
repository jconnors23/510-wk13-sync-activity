# Gradio search over the saved Chroma index. Run the build script first.

import chromadb
import gradio as gr
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import draft_search_settings as settings

# Same model the build script used.
model = SentenceTransformer(settings.MODEL_NAME)

# Read the saved index. Do not rebuild it here.
client = chromadb.PersistentClient(
    path=str(settings.DB_DIR),
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection(settings.COLLECTION_NAME)


def semantic_search(query):
    query = (query or "").strip()
    if not query:
        return "Type a search, such as: quarterback."

    # Same normalize flag as the build, so the vectors can be compared.
    query_embedding = model.encode([query], normalize_embeddings=True)
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
