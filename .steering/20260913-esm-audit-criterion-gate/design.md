# 設計 — ESM 監査 criterion のゲート解除

## 実装アプローチ

★ **⓪①③ ＋ 本タスクで実測した欠陥 1 件を、1 本の新 ADR（ADR-031）で裁く。**
⚠️ 3 本に割らない —— ★ どれも「6 択 ESM を O1 の計器に入れる」という**同じ 1 つの判断の構成要素**であり、
分けると**どれが前提でどれが帰結か**が読めなくなる（★ ADR-029 が D1〜D6 を 1 本に束ねたのと同じ作法）。

⚠️★★★ **既存 ADR の本文は 1 文字も書き換えない。**★ 改訂は番号の大きい ADR が上書きする。

## 裁定（★ ADR-031 の Decision になるもの）

### D1. 配信経路 —— ★ **O1 本体のプローブとして出す。反応性は「避ける」のではなく「測る」**

- ⚠️★★★ **現状: プローブは O1 で構造的に発火しない**（実測 2）。→ ★ **④ は配線を伴う**。
- ⚠️★★★ **O1 同意 §3 注 C 逐語「★ この記録では画面に何も出しません」が破れる。**→ ★ ② で改訂する。
- ★ **根拠**: `.idea/…survey.md:439` 逐語「**measurement reactivity を測る**。ESM、可視化、
  作品提示そのものが行動を変えるため、**probe density と表示有無を共変量化する**」
  ＋ `:463`「**ESM の回答負担、反応性、MNAR**、計測停止・区間削除の発生率」＝ ★ **O1 が測るべき対象に既に入っている**。
- ★ **却下**: 本体外（フォーム等）で取る案 → ⚠️ **event-stratified が原理的に成立しない**
  （`:239` 逐語「ランダム ESM だけでは希少 episode が不足するため、ランダム枠を残しつつ
  **event-stratified probe を併用する**」）。
- ★ **研究者確認済み**（2026-09-13）。

### D2. 層化 —— ★ **観測事象で層化する。推定器の出力では層化しない**

- ★ 層化の駆動は `.idea:235` 逐語「**低操作終了後・復帰後に層化した one-tap ESM**」＝ **観測事象**。
- ⚠️★★★ **`p_stuck` / HMM 状態 / `feat` 行で層化してはならない** —— ★ 監査 criterion が
  主 criterion と**循環する**（`:137` 逐語「行動だけで criterion を作ると循環する」／
  [V22] の扱い「opportune moment 予測を**較正に流用すると独立性汚染**」）。
- ⚠️ **限界として明記する**: 低操作の閾値も打鍵ストリーム由来なので**完全な独立ではない**。
  ★ 主張は「推定器の *事後確率* から切り離す」までであり、「独立である」とは書かない。
- ★ ADR-014 **D4b**「記録のみ。推論には 1 バイトも流さない」と両立する（★ 層化は**記録側の事象**で駆動）。

### D3. ① 規約 —— ★ **`data-privacy` ルール 7 に「自己申告による行動カテゴリ」を足す**

- ⚠️ 現行ルール 7 の禁止「役割カテゴリ（`editor`/`terminal`/`browser`）を入れない」は
  **計器由来（アプリ識別子 → カテゴリ写像）**についてしか書いていない。
- ★ 6 択の「**外部資料**」「**会話**」は**意味的に等価**。→ ★ **自己申告経路を明文の射程に入れる。**
- ★ **許す形（4 条件）**: (i) 固定 6 択のみ / (ii) **自由記述欄を置かない** /
  (iii) **相手・アプリ・URL・ファイル名を 1 バイトも持たない** / (iv) **理由や説明を求めない**。
- ★ (iv) の根拠は [V117] 逐語「**procedures that entail describing or explaining thoughts and actions
  are significantly reactive**」（★ think-aloud 自体は `r = −.03` で非反応的）。
- ⚠️ **ADR-014 D4 の禁止表は書き換えない** —— ★ 本 ADR は「D4 の禁止表は *計器由来* を禁じたもので、
  自己申告経路は射程外だった」ことを**明示**し、**新たに条件付きで許可する**。

### D4. ③ `capabilities` 粒度 —— ★ **新しい行種 `activity_label` にする**

| 案 | ⚠️ 問題 |
|---|---|
| 既存 `realtime_label` に nullable フィールドを足す | ⚠️★★★ **`capabilities` に現れない** → ★ 「計器が無い（古いビルド）」と「被験者が答えなかった」が**分離できない**（ADR-013 D1） |
| ★ **新行種にする**（採用） | ★ `KNOWN_LINE_TYPES` ＋ `config_gated()` に載り、**行種粒度の判定表がそのまま効く** |

- ★ `config_gated`（**0 行は判定不能**）へ入れる。⚠️ `unconditional` へは入れない
  （★ プローブが止まれば丸ごと出ない。`probe_assignment` / `realtime_label` と同じ理由）。
- ★ **fail-safe が効く**: `recording.rs:64-66` `is_writable_while_paused` は
  `recording_pause` / `meta` のみ true ＝ **新行種は既定で一時停止に遮断される**。
- ⚠️★★★ **3 点セットを忘れない**: `LogEntry::line_type()` / `KNOWN_LINE_TYPES` /
  `paused_blocks_every_data_line_type` の**ハードコード列挙**（★ 後者は自動検査されない）。
- ⚠️ **訂正**: 起票 11 #3 が挙げた根拠「ADR-029 D3 の層 (a)」は **D3 第 3 版で枠組みごと差し替えられ存在しない**
  （★ ADR-029 禁止 **#17**）。→ ★ **結論は ADR-013 D1 単独で立つ**ので変わらない。

### D5. ⓪ 提出猶予と第三者 —— ★ **(c) を採る。ただし「何もしない」ではなく構造的保証 3 点を課す**

| 案 | 判定 | 理由 |
|---|---|---|
| (a) ESM 行に 48h より長い猶予 | ⚠️ **却下** | ★ 猶予は **ファイル単位**（`o1.rs:62` `SUBMIT_GRACE_MS` ＋ `reconcile` の「閉じたファイル」述語）。行種ごとに分けると**提出モデルを割る**。⚠️ かつ**第三者には何も与えない**（猶予は本人の削除窓） |
| (b) 第三者言及を含む回答を自動提出の対象外 | ⚠️★★★ **却下** | ★ 6 択のうち「会話」だけ**構造的欠測**にすると、⚠️ **監査 criterion の目的（`left_observation` の混合を割る）そのものを壊す**。★ しかも `.idea:463` は **MNAR を O1 で *測れ*** と言っている —— ⚠️ **設計で MNAR を作るのは逆** |
| ★ **(c) ＋ 構造的保証 3 点** | ★ **採用** | 下記 |

★ **構造的保証**:
1. ★ **第三者を識別可能にしない**（D3 の 4 条件）→ 残るのは「**その時刻に会話していた**」という
   **被験者自身の行動申告**であって、第三者の個人データではない。
2. ★ **被験者は第三者の求めに応じて区間指定削除を使える**（`o1-deletion-ledger.md §2` の既存経路・
   時間帯指定・⚠️ **理由を尋ねない**）→ ★ 第三者は**被験者を通じた間接経路**を持つ。
   ⚠️★★★ **ただしこれは現状成立しない** → **D6**。
3. ★ **同意文書に書く**: 「会話」を選ぶと**その時刻に会話していたことが残る** ／
   ⚠️ **提出後は端末操作では消えない**。

### D6. ⚠️★★★ **区間指定削除が自己申告行を 1 行も消していない**（★ 実測。本 ADR の発見）

- ★ `redaction.rs:81-89` `line_timestamp` は `obj.get("t")` を読む。
- ⚠️ ところが `logger.rs` は **`realtime_label` / `vignette_response` / `session_meta` に `"ts"`**、
  **`probe_assignment` に `"scheduled_ts"`** を書く（★ `logger.rs:537/555/602/631`）。
  → ★ `line_timestamp` が `None` を返し、`retain_outside_range` が **残す**。
- ⚠️★★★ **削除 UI は O1 以外でも出る**（`RecordingControls.tsx:508` の else 枝）
  → ★ **通常運用（v0.3 較正）で live な欠陥**である（★ 「消しました（N 件）」と出るのに自己申告行は残る）。
- ★ **決定 1**: **新行種 `activity_label` は `"t"` を使う。**
- ★ **決定 2**: **既存 3 行種（`realtime_label` / `probe_assignment` / `vignette_response`）も消せるようにする。**
  ⚠️ **`session_meta` は `meta` と同じく常に残す**（★ `gse-replay` が 1 本を要求し、
  消すと**ファイルが永久に提出されない**／`meta` の先例 = 研究者判断 R-12）。
- ★ **決定 3**: **検査を同じコミットで置く**（`verify-before-claiming` ルール 6）。

## 変更対象

### 新規作成
- `docs/adr/ADR-031-self-reported-activity-audit-criterion.md`
- `.steering/20260913-esm-audit-criterion-gate/{requirement,design,tasklist,decisions}.md`

### 修正
- `.claude/skills/data-privacy/SKILL.md` — ルール 7 に自己申告行 ＋ チェックリスト 1 行
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md` — §3 表 ／ 注 C ／ §4（**案**）
- `docs/participant-setup-guide.md:105` / `:185-186` — 「だけ」節（**案**）
- `src-tauri/src/schema_dto.rs` — `ActivityLabel` variant ＋ `ActivityCategoryDto` ＋ `probe_assignment` の `stratum`
- `src-tauri/src/logger.rs` — 書式文字列 ＋ `LogEntry::line_type()` ＋ コンストラクタ
- `src-tauri/src/capabilities.rs` — `KNOWN_LINE_TYPES` ＋ `config_gated()`
- `src-tauri/src/recording.rs` — `paused_blocks_every_data_line_type` の列挙
- `src-tauri/src/redaction.rs` — `line_timestamp` の時刻キー ＋ テスト
- `src-tauri/schema/current.json` — `emit_schema` で再生成
- `docs/adr/README.md` — ADR-031 の行
- `docs/glossary.md` — `activity_label` / 監査 criterion（★ 必要なら）
- `docs/references.md` — ⚠️ **既存 [Vn] を使う。新規登録は必要な場合のみ**

## 影響範囲

| 影響先 | ⚠️ 対処 |
|---|---|
| `gse-dataset`（NDJSON Schema） | ★ `emit_schema` の drift check が CI で拾う。⚠️ **additive（ADR-005）** なので既存ログは読める |
| `gse-replay`（回帰） | ★ 新行種は既存 fixture に出ないので `--snapshot` は **byte-equal のまま**（⚠️ 走らせて確認する） |
| `build_analysis_db.py` | ⚠️ `OutcomeMetrics` を触らないので**対象外**（★ memory の外部契約は `metrics.json` 側） |
| 配布ビルド | ⚠️ **本タスクでは配布しない**（★ ADR-014 判断 4 の境界は「配布」） |

## 既存パターンとの整合性

- ★ **ADR-005 additive versioning**（フィールドは足すだけ・既存を改名しない）
- ★ **ADR-013 D1 / D2**（`capabilities` は **送出元があるか**で導出する・`#[cfg]` を反映する）
- ★ `logger.rs` は **`format!` の直書き**で NDJSON を出す（⚠️ `serde::Serialize` 経由にしない・モジュール doc）

## テスト戦略

- 単体: `line_timestamp` が 4 行種すべてで正しい時刻を返す／`session_meta` は `None`
- 単体: `is_writable_while_paused("activity_label") == false`
- 単体: `capabilities_covers_every_line_type` が新行種で緑（★ 足し忘れれば赤になることを**実際に外して確認**）
- 単体: `LogEntry::line_type()` の網羅
- 統合: `emit_schema` の byte-equal
- 回帰: `gse-replay --snapshot tests/snapshots/minimal.json`
- ⚠️★★★ **ルール 5b**: 検査自体を **正常 / 不在 / 壊れている** の 3 状態で試す
