# Build the Search Index

`scripts/build-draft-index.py` turns the 2025 draft table into a Chroma database that the search page reads. This page explains each step and the data at each stage. For the commands and the expected output, see [How to Run and Publish](./how-to-run.md).

The script adds the project root to Python's import path so that `import draft_search_settings` works from the `scripts/` folder. You do not need to do anything for this.

## Settings Used by the Build

| Setting | Value | What it controls |
| --- | --- | --- |
| `DRAFT_SEASON` | `2025` | The season passed to `load_draft_picks`. Passing `True` instead would load every season since 1980 |
| `MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | The embedding model |
| `DB_DIR` | `chromadb/` under the project root | Where the database is saved |
| `COLLECTION_NAME` | `draft_2025` | The name of the collection inside the database |

## Step 1: Turn Each Pick Into One Sentence

A *chunk* is the piece of text that Chroma stores and returns for one result. Here, one draft pick is one chunk, so each of the **257** rows becomes one sentence and no text is split further.

| Change made to the row | Why |
| --- | --- |
| Position code written as words (`QB` becomes `quarterback`) | The model reads ordinary words better than codes |
| Position placed first and repeated | After the position, the wording is the same for every pick |
| Round number written as a word (`1` becomes `first`) | Lets "first round" match |
| Missing values replaced by `Unknown player`, `unknown college`, `an unknown team`, or `unknown position` | Keeps every sentence complete. No 2025 sentence needed a fallback |
| Id built as season and pick (`2025-1`) | Chroma needs a unique text id for each sentence |

Example sentence for pick 1:

> quarterback. Cam Ward is a quarterback from Miami (FL). TEN drafted him in the first round of the 2025 NFL draft, pick 1.

Note: the sentence template has two wording faults that the saved data still contains. It always writes "is a", so 41 sentences read "is a offensive …" or "is a outside …". College names that end in a period, such as `Ohio St.`, give a double period (47 sentences). Fixing either one needs a code change and a rebuild.

## Step 2: Turn Each Sentence Into Numbers

An embedding model turns text into a list of numbers so that sentences with similar meaning get similar lists. MiniLM gives **384** numbers per sentence. The script scales each list to length 1 (`normalize_embeddings=True`). The search page uses the same model, and the same scaling setting, so questions and sentences are handled alike.

The first run downloads the model from Hugging Face. Later runs reuse the local copy.

## Step 3: Save Everything in Chroma

`chromadb.PersistentClient` saves the database to `DB_DIR`, so it is still there after the script exits. `Settings(anonymized_telemetry=False)` turns off Chroma's anonymous usage reporting.

The script deletes the `draft_2025` collection if it already exists, then creates it again with `metadata={"hnsw:space": "cosine"}`. Deleting first matters because adding the same ids a second time would keep the old text. The metadata setting makes Chroma score matches by cosine distance instead of its default, squared L2 distance.

`collection.add` saves the sentences, their embeddings, and their ids together. Because the script supplies the embeddings, Chroma does not run its own embedding model.

## Files Chroma Creates

| Path | What it is |
| --- | --- |
| `chroma.sqlite3` | The collection settings, the sentences, and their ids |
| `8bfd8890-557b-457d-afa2-29b9a03312cc/` | The folder for the collection's search index. Chroma creates the name at random, so a fresh build gets a different name |
| `data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin` | The files Chroma uses to find the closest embeddings quickly |

Do not rename or move files inside `chromadb/`. Chroma looks them up by these names.

## Data Files and Column Reference

The build script reads the draft table straight from nflverse and does not write either CSV file. The notebook writes `data/processed/indexed-draft-sentences-2025.csv`. No script in the project writes `data/raw/draft-picks-2025.csv`. To recreate it, run `nflreadpy.load_draft_picks(2025)` and save the result with `write_csv`. The app does not read either file. It reads only the Chroma database.

### Processed Sentences

`data/processed/indexed-draft-sentences-2025.csv`, 257 rows.

| Column | Type | How it's built | Empty? | What it means |
| --- | --- | --- | --- | --- |
| `id` | text | `season-pick`, such as `2025-1` | Never | Unique id for one sentence in Chroma |
| `document` | text | Sentence built from position, name, college, team, round, season, and pick (Step 1) | Never | The text Chroma stores and returns |

### Raw Draft Table

`data/raw/draft-picks-2025.csv`, 257 rows and 36 columns, as returned by `load_draft_picks(2025)`. The meanings come from the nflverse draft picks data dictionary (https://nflreadr.nflverse.com/articles/dictionary_draft_picks.html). "Used in sentence" marks the 7 columns the build script reads. The other 29 cannot be searched.

| Column | Type | Used in sentence | Empty rows | What it means | Example |
| --- | --- | --- | --- | --- | --- |
| `season` | integer | Yes | 0 | Draft year | `2025` |
| `round` | integer | Yes | 0 | Draft round, 1 to 7 | `1` |
| `pick` | integer | Yes | 0 | Overall pick number | `1` |
| `team` | text | Yes | 0 | Drafting team code | `TEN` |
| `gsis_id` | text | No | 1 | Id for joining with other nflverse data | `00-0040676` |
| `pfr_player_id` | text | No | 0 | Pro Football Reference id | `WardCa00` |
| `cfb_player_id` | text | No | 8 | College Football Reference id | `cameron-ward-1` |
| `pfr_player_name` | text | Yes | 0 | Player name as recorded by Pro Football Reference | `Cam Ward` |
| `hof` | true/false | No | 0 | Selected to the Hall of Fame | `False` |
| `position` | text | Yes | 0 | Position code as recorded by Pro Football Reference (20 codes in 2025) | `QB` |
| `category` | text | No | 0 | Broader position group | `QB` |
| `side` | text | No | 1 | `O` offense, `D` defense, `S` special teams | `O` |
| `college` | text | Yes | 0 | College attended in final year | `Miami (FL)` |
| `age` | integer | No | 2 | Age at the draft | `23` |
| `to` | integer | No | 20 | Final NFL season played | `2026` |
| `allpro` | integer | No | 0 | AP First Team All-Pro selections | `0` |
| `probowls` | integer | No | 0 | Pro Bowl selections | `0` |
| `seasons_started` | integer | No | 0 | Seasons as primary starter | `1` |
| `w_av` | integer | No | 20 | Weighted Approximate Value (a Pro Football Reference career score) | `7` |
| `car_av` | number | No | 257 | Career Approximate Value. Empty for every 2025 pick | none |
| `dr_av` | integer | No | 25 | Approximate Value earned for the drafting team | `7` |
| `games` | integer | No | 20 | Career NFL games | `26` |
| `pass_completions` | integer | No | 20 | Career pass completions | `506` |
| `pass_attempts` | integer | No | 20 | Career pass attempts | `827` |
| `pass_yards` | integer | No | 20 | Career passing yards | `4883` |
| `pass_tds` | integer | No | 20 | Career passing touchdowns | `23` |
| `pass_ints` | integer | No | 20 | Career interceptions thrown | `13` |
| `rush_atts` | integer | No | 20 | Career rushing attempts | `68` |
| `rush_yards` | integer | No | 20 | Career rushing yards | `310` |
| `rush_tds` | integer | No | 20 | Career rushing touchdowns | `4` |
| `receptions` | integer | No | 20 | Career receptions | `0` |
| `rec_yards` | integer | No | 20 | Career receiving yards | `0` |
| `rec_tds` | integer | No | 20 | Career receiving touchdowns | `0` |
| `def_solo_tackles` | integer | No | 124 | Career solo tackles | `35` |
| `def_ints` | integer | No | 226 | Career interceptions made | `3` |
| `def_sacks` | number | No | 196 | Career sacks | `6.0` |

The examples are from pick 1 (Cam Ward) where that row has a value, and from the first non-empty row otherwise. The career columns are totals as of the download date, so they change each time the data is downloaded again.

## Running the Same Steps in the Notebook

`notebooks/draft-search-walkthrough.ipynb` runs the same steps one cell at a time. It reads `data/raw/draft-picks-2025.csv` instead of downloading. Running its Chroma cell deletes and re-creates the `draft_2025` collection, so stop `app.py` first. A running app may keep reading the old collection or fail.
