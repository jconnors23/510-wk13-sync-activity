# Conclusions

## What the Search Does Well

Searching by position works. A search for `quarterback` returns five quarterbacks, and the distances stay close together (0.365 to 0.434). This works because each sentence starts with the spelled-out position and repeats it.

## What the Search Does Not Do

- **No exact filters.** A search for `first round wide receiver` returns wide receivers from rounds 2, 3, 6, and 7. Round, team, and pick number have less effect on the ranking than position, and nothing filters on them.
- **No spelling variants for schools.** The data writes `Ohio St.`, and a search for `Ohio State` does not find those players.
- **No statistics.** Only 7 of the 36 raw columns go into the sentences. Career numbers such as passing yards cannot be searched.
- **Always five results.** When fewer than five picks match, as with the two kickers, the rest of the list is filled with the next closest sentences. A jump in distance is the sign of this.

[Example Searches](./example-searches.md) shows the full output behind each point.

## How to Use or Extend It

Use the page to find picks by position or by a description close to the sentence wording. To change what can be searched, change the sentence in `scripts/build-draft-index.py` (for example, add the position group or a career statistic), then rebuild the database. To index another season, change `DRAFT_SEASON` and `COLLECTION_NAME` in `draft_search_settings.py`, then rebuild. Note that `ROUND_WORDS` covers rounds 1 to 7 only.

Cursor wrote the code and configuration, and Kiro wrote the code comments and these pages. The full breakdown is in the "How This Project Was Built" section of the project `README.md`.
