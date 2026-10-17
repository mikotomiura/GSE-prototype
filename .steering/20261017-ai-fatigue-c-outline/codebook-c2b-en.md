# Codebook for C2b: what each scale item asks about, and toward what

Attachment to the registration. **Version 2 (2026-10-17).** The English text is the authoritative version.

Changes from version 1 (fixed 2026-10-15 in Japanese and used only for exploration):
- `OTH` is split into `FAT` (tiredness or depletion) and `OTH`.
- `OTHER` is added as a target.
- The coder values are changed.

Any later change will be versioned and logged as an amendment, with the reason and the affected rows.

## Principles

- Code the **item wording only**. The scale authors' factor name is copied into `author_factor` and is not used for coding. When the wording-based code and the factor name disagree, this is counted in `mismatch`.
- Instructions or stems (for example, "After video conferencing ...") are copied into `context`. They show the situation the item refers to. They are not used to decide the type.
- Give each item one primary type. If an item falls between two types, set `boundary` = 1 and record the other type in `secondary_type`. Give the reason in one sentence in `rationale`.
- Reverse-keyed items take the type of the dimension they ask about, from either pole. For example, "I feel full of energy" is `FAT`, and "I am interested in ..." is `MOT`.

## Step 1: content type (`type`)

| Code | Name | Rule | Anchors (examples) | Boundary examples |
|---|---|---|---|---|
| `MOT` | Reduced motivation, interest or willingness | The item directly asks about having no, or less, willingness, interest or initiative to do something | The motivational items of the Zoom Exhaustion & Fatigue Scale derived from the MFI reduced-motivation subscale: "I don't feel like doing anything", "I dread having to do things". Also "I've lost interest in ...", "I have become less proactive in ..." | Tiredness given as the reason ("too tired to do other things"): primary `FAT`, secondary `MOT`, `boundary` = 1 |
| `AVO` | Avoidance, restriction or withdrawal behaviour | The item asks about avoiding the target, using it less, ignoring it, or choosing another means, as behaviour or as a behavioural tendency | "I avoid using AI even when it could help me.", "I avoid social situations" | Wanting to be alone ("want to be alone"): `AVO`, `boundary` = 1, `secondary_type` = `MOT`. Needing time alone ("need time by yourself"): `AVO`, `boundary` = 1, `secondary_type` = `OTH` |
| `FUT` | Futility or helplessness | The item asks whether one's effort or interest feels meaningless or ineffective | "... is pointless", "I doubt whether my efforts ... have any real impact" | — |
| `IRR` | Irritation or other negative affect | The item asks about irritation, frustration, low mood or other negative feelings that are not depletion | "frustrated", "irritated", "irritable", "moody" | "discouraged": `IRR`, `boundary` = 1, `secondary_type` = `MOT` |
| `FAT` | Tiredness or depletion | The item asks about feeling tired, exhausted, drained or depleted, including emotional exhaustion | "I feel exhausted", "emotionally drained" | "tired of constantly evaluating ..." (being fed up): `FAT`, `boundary` = 1, `secondary_type` = `MOT`. "too tired to do other things": `FAT`, `boundary` = 1, `secondary_type` = `MOT` |
| `OTH` | Other | Cognitive load, difficulty understanding, bodily and sensory symptoms other than tiredness, sleep | "My eyes can feel strained ..." | — |

Note: emotional exhaustion ("emotionally drained") is depletion and is coded `FAT`, not `IRR`.

## Step 2: target (`target`)

Assign a target when `type` or `secondary_type` is `MOT`, `AVO` or `FUT`. Otherwise leave it empty.

| Code | Name | Examples |
|---|---|---|
| `TASK` | Tasks or activities in general (no specific target named) | "doing anything", "having to do things", "other things" |
| `AI_USE` | Using AI | "using AI", "new AI features" |
| `AI_VERIFY` | Judging the truth or reliability of AI output or information | "assessing the reliability of AI-generated content" |
| `AI_PRIV` | Managing privacy with AI | "protecting personal data", "privacy settings in AI tools" |
| `SOCIAL` | Contact with other people | "social situations", "be alone" |
| `OTHER` | A named target not listed above | for example, a specific medium or setting other than AI |

## Columns

`scale_id, item_no, item_text, context, author_factor, type, secondary_type, boundary, target, mismatch, rationale, source_page, coder`

- `item_text`: verbatim, in the final questionnaire form. It is kept in the working file only and is not released (see registration [GSRR-50]).
- `mismatch`: kept from version 1 for the exploration records only. It is not used in the registered synthesis.
- `coder`: `coder1` or `coder2`. AI-drafted values are not allowed for C2b.
- Anchors quote short phrases from published items, with their sources. Full items are kept in the working file only.

## Counting

- Primary count: each item counts once, for its primary `type`. The denominator is the instrument's item count.
- Lenient count (sensitivity analysis): each boundary item also counts once for its `secondary_type`. The denominator stays the instrument's item count.

## Limitation

Item wording does not show what scores contain. An item that does not ask about motivation directly may still contribute to scores that reflect reduced motivation. Testing that requires correlational or factor-analytic data.
