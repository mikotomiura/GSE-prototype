# How the AI screener is called

This file belongs to attachment 6, with `instructions.md`. It fixes the wording that wraps a batch of records for one call, and the settings of the call (GSRR-33). Round 3 of the check on the 34 exploratory records used this wording; rounds 1 and 2 used an earlier wording that allowed web access when no abstract had been retrieved (GSRR-37).

## Settings

- Model: Claude Opus 5.5 (model identifier `claude-opus-5-5`, Anthropic).
- How it is run: as a subagent of Claude Code (subagent type `general-purpose`, model `opus`), one subagent per batch. No other settings (such as temperature) are set; the defaults of Claude Code apply.
- The subagent has file and web tools available; the wording below forbids web access and any file other than the batch's inputs. This is a rule given to the model, not a technical block (GSRR-65).
- Inputs are files in a working directory outside the repository:
  - `instructions.md` (attachment 6);
  - `in/<ID>.stage1.txt` (ID, title, DOI, URL and the abstract as retrieved, or "Abstract (not retrieved):");
  - `ft/<ID>.txt` (the free full text, with its source URL on the first line).
- Outputs are written to `out1/`, `out2/` and `out3/`, one JSON object per record and stage. The format is checked by a script before anyone reads the content.

## Wording for stage 1 (title and abstract)

```
You are the AI screener for a literature database. Work only as described here.

Base directory: <working directory>

1. Read `instructions.md` in the base directory in full and follow it exactly. This is Stage 1 (title and abstract).
2. Your records: <up to nine record IDs, in the screening order>. For each, read `in/<ID>.stage1.txt`. Judge each record on its own.
3. If the abstract says "not retrieved", judge from the title alone and set `read` to "title only". Do not open any web page.
4. Write one JSON object per record to `out1/<ID>.json` (schema in instructions section 5, stage 1, Q7 empty, centre empty).

Forbidden: reading any file other than `instructions.md` and your `in/<ID>.stage1.txt` files (do not open other files in `in/` or `ft/`, anything outside the base directory, any git repository, or the Downloads folder); any web access (WebFetch, WebSearch, curl, a browser). Do not edit any file other than your own outputs.

Deadline: 15 minutes. Return a short table: ID, decision, code, read.
```

## Wording for stages 2 and 3 (full text and centre)

```
You are the AI screener for a literature database. Work only as described here.

Base directory: <working directory>

1. Read `instructions.md` in full and follow it exactly. This is Stage 2 (full text) and, for records you include at Stage 2, Stage 3 (centre).
2. Records with a full text: <IDs>. For each, read the full text `ft/<ID>.txt` (first line = source URL; texts are long, read in parts until you have covered Methods, Measures and Results).
3. Records with no free full text found: <IDs>. For these, the input is only `in/<ID>.stage1.txt` and the fact that no free full text was found; apply the Stage 2 rule for records without a free full text.
4. Judge each record on its own.
5. Write the Stage 2 object to `out2/<ID>.json` (stage 2, centre empty). If the decision is `include`, also write the Stage 3 object to `out3/<ID>.json` (stage 3, centre filled).
6. Quotes: at most 25 words each; never copy questionnaire items in full.

Forbidden: reading any file other than `instructions.md` and the input files named above (no git repository, no Downloads or Documents folder); any web access (WebFetch, WebSearch, curl, a browser). Do not edit any file other than your own outputs.

Deadline: 20 minutes. Return a short table: ID, stage-2 decision, code, centre.
```

Items 2 and 3 are left out when a batch has no record of that kind.
