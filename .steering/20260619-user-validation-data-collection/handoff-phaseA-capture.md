> ⚠️ **SUPERSEDED (2026-06-23)**: 本 handoff の **A3 (成果物スナップショット機構) は廃案**。
> WBS v2 / codex-review v0.4 §4.2 が (b)=「diff量÷総打鍵数」を廃止し、`manual_contribution_ratio`
> 等 (キーストローク由来カウンタ、成果物不要) に置換したため。A2 は `dismiss_reason` 4択を中核に存続。
> 後継タスク: `.steering/20260623-capture-schema-freeze/`。詳細は同 `decisions.md` の SUPERSEDE 注記。

# 次セッション開始プロンプト — Phase A: 捕捉完全性 (capture completeness)

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> 親ロードマップ: `.steering/20260619-user-validation-data-collection/roadmap-xy.md` (X/Y 二軸・Phase A-F)。
> 決定根拠: 同 `decisions.md` (D4 中身禁止 / D5 ストリーム / D7 (b) diff量=案A)。
> **新規 `/start-task` で着手。ブランチは下記「前提」に従い main 基点で別 PR。**

## なぜ Phase A が次か (支配原則=捕捉の不可逆性)

パイロットで録り損ねた信号は永久に失われる。(a)(b) アウトカム算出 (#5) は「捕捉が済んでいる」
前提に立てない。現状の捕捉ギャップ (roadmap §1):
- **A2 介入応答が未ログ**: Wall 提示 / ⏸押下 / early-unlock / Zen 完了 / 順守 が NDJSON に残らない疑い
  (grep で記録箇所なし)。⏸押下数は設計書で「GSE 思想の実証データ＝独立指標」と明記。
- **A3 成果物スナップショットが存在しない**: (b) diff量 は案A=成果物由来だが、成果物を session 単位で
  保存する機構が無い。**これが無いと (b) はパイロットで永久に失われる**。

→ #5 より前に A2・A3 を入れる。これが Phase A。

## 直前までの状態 (2026-06-20)

- #1 参加者 ID 設定可能化: 完了 (main)。
- #2 ペースト捕捉 (A1): **PR #16** (`feature/clipboard-paste-count`) で実装・push 済。CI(win+mac) で
  build/test 検証中。残: 実機 Ctrl+V/Cmd+V 挙動の手動確認。**未マージ**。
- ⚠️ `main` は PR #14 (Part 2) 止まり。Part 3 (`68b5871`) 未マージ。

## スコープ

### 含むもの
- **A2 介入応答イベントの NDJSON 記録**: Wall 提示 / ⏸(pause/Zen 入り) / early-unlock / Zen 完了 /
  順守(complied) / dismissed 等を固定カテゴリ＋時刻で記録 (本文・内容なし)。`intervention_decision`
  (判定側) とは別に「ユーザー応答側」を残す。新 `LogEntryDto` variant or 既存拡張。
- **A3 成果物スナップショット機構 (案A 前提)**: session start/end で作業対象を保存し diff量 を後で
  算出可能にする。**成果物の中身は raw NDJSON 同様に暗号化ローカルのみ**、共有物 (metrics.json) には
  数値 diff量 しか出さない。NDJSON には中身非由来の参照 (snapshot id 等) のみ残す案を検討。

### 含まないもの
- (a)(b) の**指標算出** (#5 = Phase B、`handoff-ab-metrics.md`)。本タスクは「捕捉」まで。
- #3 anonymize / #4 package / #6 DuckDB / Phase D (X 強化: context_beacon/波形cue) / Phase E (散歩)。
- features/HMM への組み込み。

## 要承認の設計判断 (次セッションで会話承認 — 研究設計フォーク)

1. **A3 成果物取得法 (roadmap フォーク#3・必須)**: track 別に何をどう保存するか。
   - coding (vibe-coding) = 作業ディレクトリの git snapshot / `git diff --stat` の数値、
   - 文章 (argumentative/correspondence/creative) = 完成テキストの文字数/変化量。
   - session との紐付け、被験者端末での保存・暗号化フロー、アプリ内 vs スクリプトの責務分界。
   - **設計判断が重く複数案ありうる → プラン段階で `/reimagine` 起動を推奨**。
2. **A2 イベント設計**: どの応答を記録するか / 単一 variant に集約 vs 複数 / フィールド (固定カテゴリのみ)。
3. **総打鍵数・diff量 の整合** (Phase B の前提固め): A3 の diff量 定義が (b) の分子に直結する点を確認。
   - 注: roadmap フォーク#1(同一/分離セッション)・#2(前後比較設計) は Phase E/F の判断。A3 はそれらと
     独立に捕捉機構として設計できるが、session 紐付け方式が #1/#2 に影響され得る点だけ意識する。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. `/start-task` で `.steering/[今日]-capture-completeness/` 作成 → (A3 で `/reimagine` 検討) → `/add-feature`。
2. **docs 先読み**: roadmap-xy.md / decisions.md (D4/D5/D7) / development-guidelines §3(Replay-as-Truth)・
   §10(data repo) / functional-design (介入・⏸の位置づけ)。
3. **Skill 参照 (必須)**: `data-privacy` (最重要=中身を残さない・成果物中身を共有物に出さない) /
   `intervention-design` (A2: Wall/Zen/early-unlock の意味論) / `architecture-rules` (LogEntry 変換は
   analysis 外・OS 依存は input/) / `rust-standards` / 成果物に hook が絡むなら `hook-constraints`。
4. **サブエージェント委譲**: `file-finder`/`impact-analyzer` で wall_server/lib.rs の介入フロー・
   logger 書き出し・session 境界 (`meta`)・既存 schema 同期パスを調査。
5. **実装後 `code-reviewer` + `security-checker` を並列** (焦点 = **成果物の中身・キーストローク内容が
   NDJSON/metrics/共有物に一切漏れない**・固定カテゴリと数値のみ)。
6. **`/cross-review`**: jq 不在なら Codex skip → Claude 単独へ縮退・skip 理由明記 (`project_codex_review_needs_jq`)。

## 前提 (ブランチ / schema 衝突回避 — 重要)

- A2 はほぼ確実に **NDJSON schema 変更** (新 variant) を伴う。#2(paste) も schema を足しているため、
  **先に PR #16 を main へマージし、更新後の main から Phase A ブランチを切る** (schema variant の
  二重管理・parity 二重ドリフトを避ける)。
- PR #16 マージ前に着手せざるを得ない場合は **`feature/clipboard-paste-count` を基点**にする
  (paste variant を含んだ状態で積む)。どちらにせよ「main 直コミット」はしない。

## スキーマ変更の必須手順 (#2 と同じ — 取りこぼし注意)

- `cargo run --bin emit_schema > src-tauri/schema/current.json` で再生成 → diff 確認。
- **gse-dataset 側 `schema/current.json` にコピー同期** → `python scripts/check_schema_parity.py
  --dataset C:/gse-dataset` が exit 0。
- gse-replay が新 variant で panic しないこと (fixture に 1 行足して確認、`timestamp()` 方針を決める)。
- ゴールデン: A2/A3 を features/HMM に使わないなら `FeatSnapshot` 不変 → `gse-replay --snapshot` byte-equal。

## 検証ゲート

- `cargo test --workspace` 緑 (A2 の read-back・新 variant parse テスト追加)。
- `gse-replay --snapshot` byte-equal / schema parity 緑 (schema 変更時)。
- **CI(win+mac)**: ブランチ push で `check` ジョブ (build/test/snapshot/schema drift) が両 OS で走る。
- 手動 (実機): 介入応答 (⏸/early-unlock 等) が NDJSON に出る・成果物が保存され**中身は共有物に出ない**こと。
- code-reviewer / security-checker CRITICAL/HIGH なし。

## 制約

- `tracing`/`anyhow`/`any` 禁止/`winapi` 禁止・`analysis/` は OS 非依存・LogEntry 変換は analysis 外。
- **中身 (キーストローク内容・成果物テキスト・クリップボード) を NDJSON/metrics/共有物に一切入れない**
  (data-privacy 最優先・固定カテゴリ＋数値のみ)。成果物の中身は暗号化ローカルのみ。
- `.steering/` 記録を省略しない。`/finish-task` まで完遂。**別 PR・main 基点 (上記前提)**。

## 受け入れ条件

- A2: 介入応答 (Wall提示/⏸/early-unlock/Zen完了/順守/dismiss) が固定カテゴリ＋時刻で NDJSON に残る。
- A3: session 単位で成果物が保存され、後で diff量 (数値) を算出できる。**中身は共有物に出ない**。
- schema 変更 → emit_schema 再生成 → gse-dataset 同期 → parity 緑。
- `cargo test --workspace` green / `gse-replay --snapshot` byte-equal / CI(win+mac) 緑。
- code-reviewer / security-checker CRITICAL/HIGH なし (特に中身非漏洩)。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-phaseA-capture.md に従い、
Phase A (capture completeness) を実装してください。パイロット前に「録り損ねたら永久に失う」
捕捉ギャップ A2・A3 を埋めるタスクです。

着手前に: /start-task で .steering/[今日]-capture-completeness/ を作成 → (A3 は設計重いので
/reimagine 検討) → /add-feature。roadmap-xy.md と decisions.md(D4/D5/D7)、
data-privacy / intervention-design / architecture-rules / rust-standards Skill を読む。

スコープ:
A2 = 介入応答イベントの NDJSON 記録 (Wall提示/⏸押下/early-unlock/Zen完了/順守/dismiss を
固定カテゴリ+時刻で。intervention_decision の「判定側」とは別に「ユーザー応答側」を残す)。
A3 = 成果物スナップショット機構 (案A=diff量の供給源)。session start/end で作業対象を保存し
後で数値 diff量 を算出可能に。成果物の中身は暗号化ローカルのみ、共有物には数値だけ。
スコープ外: (a)(b)指標算出(#5)・anonymize/package(#3#4)・DuckDB(#6)・context_beacon/波形cue(Phase D)・
散歩(Phase E)・features/HMM 組み込み。

要承認の設計 (会話で承認): ①A3 成果物取得法 (coding=git diff数値 / 文章=文字数、session紐付け、
被験者端末の保存・暗号化、アプリ内 vs スクリプト責務) ②A2 のイベント設計 (variant 構成・固定カテゴリ)
③diff量定義と (b) 分子の整合。①は複数案ありうるので /reimagine 推奨。

CLAUDE.md 準拠で: /start-task → (/reimagine) → /add-feature → 上記 Skill 参照 →
file-finder/impact-analyzer で wall_server/lib.rs 介入フロー・logger 書き出し・session境界・schema同期
パスを調査 → 実装 → code-reviewer + security-checker 並列 (焦点=成果物/キーストローク内容が
NDJSON/metrics/共有物に一切漏れない・固定カテゴリと数値のみ) → /cross-review (jq不在なら Claude単独・
skip理由明記) → finish-task。

前提(重要): A2 は schema 変更を伴う。先に PR #16 (paste) を main へマージし更新後 main から切る
(schema variant 二重管理回避)。未マージで着手なら feature/clipboard-paste-count を基点に。main 直コミット不可。
schema変更時: emit_schema 再生成→src-tauri/schema/current.json→gse-dataset コピー→check_schema_parity.py緑。
features/HMM 未利用なら gse-replay --snapshot は byte-equal。ブランチ push で CI(win+mac) が回る。

制約: tracing/anyhow/any禁止/winapi禁止・analysis は OS非依存・LogEntry変換は analysis外・
中身(キーストローク/成果物テキスト/クリップボード)を NDJSON/metrics/共有物に一切入れない(数値+固定カテゴリのみ)・
成果物中身は暗号化ローカルのみ・.steering 記録必須・別PR。
```
