# Video explainers: working notes

The two explainer videos linked from the root README were made by hand with a
hosted video generation model. **No code in this repository generates video**,
and the raw files are not committed. These are the notes from four attempts.

The brief was a minute or so of vertical, TikTok-shaped footage introducing a
neighbourhood, shot in a Shoreditch / Brick Lane setting.

## Constraints the tool imposed

- 8 seconds per generation, so anything longer has to be stitched.
- Roughly 5 minutes of wall-clock time per 8-second segment.
- About three lines of on-screen text per segment before it becomes unreadable.

## What each pass changed

**V1 — one segment.** Confirmed the tool could produce a usable 8 seconds and
established the generation time. Nothing longer was attempted.

**V2 — stitching.** Concatenating independently generated segments broke
character continuity: the same person looked like a different person in each
clip. Fix attempted: feed the final frame of one segment in as the reference
image for the next. It helped, and did not fully solve it.

**V3 — styling.** Style parameters aimed at a younger audience. The output did
not land; the look was recalibrated for V4. No audience testing was done, then
or since — "did not land" is the author's judgement, not a measurement.

**V4 — the version that shipped.** Frame referencing plus the revised style,
compiled past a minute with the character holding together across cuts. This is
the version linked from the README.

## Known defect

Text overlays render unreliably — some captions come out garbled or drop
characters. It is visible in the published videos. The cause was not
investigated.

## If this were picked up again

The obvious next step is a text overlay pass done outside the generation model,
composited afterwards, rather than asking the model to render captions.

---

*Notes by MasteraSnackin, February 2026, during the hackathon build.*
