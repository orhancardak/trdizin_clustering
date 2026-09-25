import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMBEDDINGS_DIR = os.getenv(
    "EMBEDDINGS_DIR",
    os.path.join(PROJECT_ROOT, "embeddings"),
)

EMBEDDING_FILE = os.path.join(
    EMBEDDINGS_DIR,
    "mpnet_multilingual_embeddings.npy"
)

INDEX_FILE = os.path.join(
    EMBEDDINGS_DIR,
    "article_embedding_index.csv"
)

UMAP_FILE = os.path.join(
    EMBEDDINGS_DIR,
    "umap_2d_coordinates.csv"
)
