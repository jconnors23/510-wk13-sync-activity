# How to Run and Publish

This page covers what you need, what each command does, and what you should see. The bare commands are also listed in the project `README.md`.

## Requirements

| Need | Detail |
| --- | --- |
| Python | 3.13. The project was built and tested on 3.13 |
| Packages | Pinned in `requirements.txt` |
| Internet | Needed for the first build (draft table and model download) and the first app start (model download) |
| Notebook only | A Jupyter kernel, such as `pip install ipykernel`. It is not in `requirements.txt`, so the Space does not install it |
| Publishing only | A Hugging Face account and an access token with write permission |

Run every command from the project root. On some systems `python` is called `python3`.

## Step 1: Install the Packages

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## Step 2: Build the Database (Optional)

The repository already contains a built database in `chromadb/`, so you can skip this step. Run it if `chromadb/` is missing, or if you change the model name, database folder, collection name, or draft year in `draft_search_settings.py`. Changing `N_RESULTS` does not need a rebuild. The app reads that number when it searches.

```bash
python scripts/build-draft-index.py
```

When it finishes it prints the number of saved picks and the folder, then the first sentence:

```text
Saved 257 picks to /path/to/project/chromadb
quarterback. Cam Ward is a quarterback from Miami (FL). TEN drafted him in the first round of the 2025 NFL draft, pick 1.
```

The build replaces the saved database, so stop the app before you run it. For what each step of the build does, see [Build the Search Index](./build-the-index.md).

## Step 3: Start the Search Page

```bash
python app.py
```

Open http://127.0.0.1:7860 and click one of the example questions. Each result line starts with a distance. A smaller distance is a closer match. [Example Searches](./example-searches.md) shows what correct output looks like.

