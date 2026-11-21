# Example Searches

These are real results from the saved database (257 sentences, cosine distance), using the project's model and settings. They show what correct output looks like and where the search works poorly. Distances are rounded to three decimals, as the app prints them.

## What the Searches Returned

| Search | Best distance | What came back |
| --- | --- | --- |
| `quarterback` | 0.365 | Five quarterbacks |
| `kicker` | 0.445 | Both 2025 kickers, then a punter, then two unrelated positions |
| `first round wide receiver` | 0.356 | Five wide receivers, none drafted in the first round |
| `Ohio State` | 0.650 | No Ohio State players. The data spells the school `Ohio St.` |
| `passing yards leader` | 0.538 | Unrelated players. Statistics are not in the sentences |

## Search That Works: "quarterback"

```text
0.365 — quarterback. Cam Ward is a quarterback from Miami (FL). TEN drafted him in the first round of the 2025 NFL draft, pick 1.
0.388 — quarterback. Tyler Shough is a quarterback from Louisville. NOR drafted him in the second round of the 2025 NFL draft, pick 40.
0.415 — quarterback. Jalen Milroe is a quarterback from Alabama. SEA drafted him in the third round of the 2025 NFL draft, pick 92.
0.422 — quarterback. Graham Mertz is a quarterback from Florida. HOU drafted him in the sixth round of the 2025 NFL draft, pick 197.
0.434 — quarterback. Jaxson Dart is a quarterback from Mississippi. NYG drafted him in the first round of the 2025 NFL draft, pick 25.
```

All five results are quarterbacks. The 2025 draft has 14 quarterbacks, and the app shows only the closest five.

## Search That Runs Out of Matches: "kicker"

```text
0.445 — kicker. Andres Borregales is a kicker from Miami (FL). NWE drafted him in the sixth round of the 2025 NFL draft, pick 182.
0.478 — kicker. Tyler Loop is a kicker from Arizona. BAL drafted him in the sixth round of the 2025 NFL draft, pick 186.
0.555 — punter. Jeremy Crawshaw is a punter from Florida. DEN drafted him in the sixth round of the 2025 NFL draft, pick 216.
0.604 — defensive end. Jack Sawyer is a defensive end from Ohio St.. PIT drafted him in the fourth round of the 2025 NFL draft, pick 123.
0.649 — offensive lineman. Josh Conerly is a offensive lineman from Oregon. WAS drafted him in the first round of the 2025 NFL draft, pick 29.
```

The 2025 draft has two kickers, so results 3 to 5 are the next closest sentences. The punter is a reasonable third result. The last two are not. The jump in distance, from 0.478 to 0.604 and above, is the sign that the matches have run out.

## Search That Ignores a Detail: "first round wide receiver"

```text
0.356 — wide receiver. Jack Bech is a wide receiver from TCU. LVR drafted him in the second round of the 2025 NFL draft, pick 58.
0.398 — wide receiver. Jimmy Horn is a wide receiver from Colorado. CAR drafted him in the sixth round of the 2025 NFL draft, pick 208.
0.400 — wide receiver. LaJohntay Wester is a wide receiver from Colorado. BAL drafted him in the sixth round of the 2025 NFL draft, pick 203.
0.407 — wide receiver. Kyle Williams is a wide receiver from Washington St.. NWE drafted him in the third round of the 2025 NFL draft, pick 69.
0.412 — wide receiver. Junior Bergen is a wide receiver from Montana. SFO drafted him in the seventh round of the 2025 NFL draft, pick 252.
```

Every result is a wide receiver, but none was drafted in the first round. The position appears twice in each sentence and the round once, so the position has more effect on the ranking. Semantic search ranks by overall similarity and does not filter on an exact value.

## Searches That Fail: "Ohio State" and "passing yards leader"

`Ohio State` returns players from Louisville, Notre Dame, USC, and Texas (best distance 0.650). The data writes the school as `Ohio St.`, and the model does not connect the two forms strongly enough to rank those players first.

`passing yards leader` returns Mike Green and Fadil Diggs (defensive ends), Carson Vinson (offensive tackle), Emery Jones (offensive lineman), and Cam Ward (best distance 0.538). The sentences contain no statistics, so the search has nothing to match on. Passing yards are in the raw table but are not used. See the column reference in [Build the Search Index](./build-the-index.md#raw-draft-table).
