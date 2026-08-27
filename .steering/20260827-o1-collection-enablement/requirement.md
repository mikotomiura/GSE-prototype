# 要件 — O1 の計器を「収集できる形」にする

- **日付**: 2026-08-27
- **種別**: feature (実装)
- **入口**: `.steering/_handoff/next-session-prompt-o1-implementation.md`
- **ブランチ**: `feature/o1-collection-enablement`

## 背景

O1 (R3-a・自然作業の常時収集) は **研究者判断が全件確定済み**である
(`.steering/20260825-o1-researcher-decisions/decisions.md` 判断 O1-1〜O1-7 /
`docs/adr/ADR-016` 判断 4・4b-0〜4b-3 / `docs/adr/ADR-014` D6・D8)。
⚠️ **実装が追いついていないため、いま収集を始めると 3 つが同時に壊れる**:

| # | 実装しないと | 出所 |
|---|---|---|
| 1 | 自然作業が `task_kind:"argumentative"` / `head_id:"writing"` として**積極的に誤ラベル**される | `src/App.tsx:15-21,223` |
| 2 | 「開始する」を押し忘れた区間で**打鍵だけが欠け、ポインタ / フォーカスは残る** → **計器の欠損が「非打鍵区間」に化ける** | `lib.rs:2713` / `lib.rs:3147-3196` |
| 3 | 同意文書 §2 / §4 / §5 が**実装を前提に書かれている**ので、**文書が嘘になる** | `consent-draft-o1.md` |

## ゴール (受け入れ条件)

- **A**: O1/R3 モードのマーカーが存在し、**G1 と同時に立たない**ことがテストで固定されている。
- **B**: O1 モードでは `session_active` の門を通さず**常時収集**する。
  稼働中インジケータ (トレイ / `RecordingControls`) が **「記録しているのに記録していません」と言わない**。
  `liveness` の `starved_ms` が O1 でも進む (フック死を検出できる)。
- **C**: O1 モードでのみ宣言 UI の lock が外れ、**既存 4 値**を
  「論述 / 通信文 / デザイン・映像・制作作業 / vibe coding」として出す。
  **未宣言のあいだ `session_meta` を書かない**。宣言変更 1 回 =
  **`session_meta` 出力 → ローテート → `engine.reset()`** が 1 アクションで揃う。
- **D**: **日次ローテート**でファイルが閉じ、**48 時間の猶予**の後にだけ提出候補になる。
  猶予中は `delete_time_range` で**端末上から消える**ことがテストで固定されている。

### 不変条件 (⚠️ 1 バイトも変えない)

- 段 1 の観測チャネル (`workspace-behavior-observation.md §2.1`) / ADR-009 D2 の 4 択
- `HMM_VERSION` (`0.5.0`・`analysis/engine.rs:58`) — **特徴量経路に触れない**
- ゴールデンの byte-equal / `src-tauri/schema/current.json`
- **G1 / Phase1 の実行時挙動** — 分岐はすべて O1 モードの中に閉じる
- G1 の配布ビルド (収集途中の G1 に新ビルドを配らない)

## スコープ外

- 推論への配線 (段 3) — ADR-011 D4「読む実装は G1 判定後」は不変
- `task_kind` の schema 変更 — 判断 4b-3 が schema を変えない形を選んでいる
- 段 1 へのチャネル追加 (凍結済み・mac の `buttons` 恒常 0 は D-5 で受容済み)
- `replay.rs` の flaky test (`.steering/20260825-replay-flaky-test/`)
- ADR-016 D8 の「計測器のゲートを 2 本に割る」(`is_observed_key` / `is_feature_key`) — 本セッションの §1 に無い

## 運用メモ

- /reimagine 適用: **No**
- 理由: 設計は研究者判断 (O1-1〜O1-7 / ADR-016 判断 4・4b) で確定済みであり、
  代替案の再生成は §0-2「研究者判断を作り直さない」に反する。
