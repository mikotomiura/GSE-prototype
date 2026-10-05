# paper-suggest — 投稿する論文の案と投稿計画（2026-09-27 時点）

> ⚠️ **これは提案であって確定ではない。** 確定した判断は `decisions.md`（判断 1–16）、評価設計の下書きは `design.md`。
> 具体的な議論は次セッションへ送る（`.steering/_handoff/next-session-ime-paper-discussion.md`）。
> ⚠️ 本文中の数値はすべて 2026-09-27 に一次で確かめた値だが、**論文に引く前に測り直す**。

---

## 1. なぜこの 1 本か（論文化可能性調査の結論）

| 候補 | 判定 | 理由（一次） |
|---|---|---|
| ★ **IME 変換状態の content-free 観測** | **書く** | 人を対象としない評価で成立する。先行との差分に文献の裏付けがある（`docs/research-positioning.md:805-821`） |
| [P321] 公開データの再解析 | ★ **並行で書く**（2026-09-28 判断 16・判断 9 を改めた） | ★ 新しい公開データ [P434]（CC BY 4.0）で同じ定義を当てはめられると分かった。⚠️ R₀ 自体は原著が既報（補集合 21% / 正式版 33%）なので、芯は「成果を要求しない指標のずれ（分子の効果）」と交絡・版の揺れ。暫定の投稿先 = EASE 2027 Short Papers（2027-03-01） |
| 事前登録どおりの否定的結果（Phase1） | 保留 | n=5・課題 1 種・**倫理審査を経ていない**（`.steering/20260804-g1-pilot-execution/decisions.md` D-3） |
| headline（Stuck × 介入機会の前向き検証） | 書けない | 未検証。Phase1 GATE3 = `DataInsufficient`（`experiments/20260731-phase1-calibration-analysis/notes.md:99-105`） |
| AI エージェントを使った研究開発の経験報告 | 保留 | 材料は多いが、失敗の体系的な分類・集計が無い |
| 理論（生成的返権論） | 書けない | `EH0`。系統的レビューで C1〜C6 は既出 |

---

## 2. タイトル案

### BRM 向け（本命）

| # | 案 | ねらい |
|---|---|---|
| T1 | **Observing Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a synthetic-input validation** | 3 つの貢献をそのまま並べる。BRM の手法論文らしい |
| T2 | **Content-free logging of input method editor (IME) conversion for writing-process research** | 打鍵ログ研究（Inputlog 系）の読者に届く語で書く |
| T3 | **Beyond text-level keystroke logging: Capturing IME conversion dynamics in Japanese writing without capturing the text** | [P270] のようなテキスト水準ロガーとの差を題に出す |
| T4 | **What can a keystroke logger know about IME composition without seeing the text?** | 問いの形。E2（本文復元）の結果が強ければ合う |

★ 推し: **T1**（主張と評価の対応が題から読める）。E2 の結果次第で T4 も有力。
★ **2026-09-28 に T1 で決定**（decisions.md 判断 15）。E2 の結果が強ければ T4 へ変えてよい。

### ~~CHI 2027 Posters 向け（任意）~~ ⚠️ 2026-09-28 に取り下げ（判断 13 の追記）

- **Seeing Conversion, Not Content: Privacy-Preserving Observation of Japanese IME Use**
- **Content-Free IME Logging: How Much Conversion Behavior Can Be Observed Without the Text?**

---

## 3. 要旨の骨子（結果は空欄）

> Keystroke logging is an established method in writing research, but for languages typed through an input method editor (IME), such as Japanese, text-level loggers bypass the conversion process and content-level loggers must read the text. We (1) analyze what IME state is observable from outside the target application on Windows and macOS, showing that Windows TSF composition of other processes cannot be observed by design and that macOS exposes no public API; (2) present a cross-platform logger that records one row per conversion (duration, navigation, abandonment) without recording any text, and makes the platform asymmetry explicit in the log; and (3) validate it against ground truth captured inside a reference input field, using synthetic input across [N] scenarios, [IMEs] and both platforms. Detection F1 was [__], duration error [__], and abandonment agreement κ = [__]. A reconstruction analysis shows that [__]. Runtime overhead was [__] CPU and [__] MB memory. Code, scenarios and data are openly available.

---

## 4. 貢献と「書かないこと」

| # | 貢献 | 状態 |
|---|---|---|
| C1 | 観測可能性の分析（TSF はアーキテクチャ上観測不可・UIPI が理由ではない・macOS は公開 API なし・WinEvent なら content-free が構造的に保証される） | 調査は済（`survey-input-channels.md` §7）。⚠️ 論文用に MS / Apple の一次文書へ引き直して `[Pn]` で接地する |
| C2 | 両 OS のロガー（1 変換 = 1 行・OS の非対称をログ上で宣言する `capabilities`） | 実装は済（`ime_compose.rs` / `schema_dto.rs` `ImeShadow`） |
| C3 | 精度評価（参照入力欄を正解・合成入力・シナリオ × OS × IME） | **未着手**（本論文の律速） |
| C4 | 本文をどこまで復元できるか（開集合の復元・閉集合の同定） | **未着手** |
| C5 | 実行コスト | ⚠️ **2026-09-28**: 既存の CPU 0.98% は**無効**（旧計器の過小報告）。既存の有効値は GSE アプリ全体の値（macOS 2.19% / Windows 2.06%）。→ ★ **公開する観測部だけを両 OS で再計測**（判断 12）。バッテリーは測らない |

**書かないこと**:
- 「世界初」「先行が存在しない」（`docs/glossary.md` 禁止用語）。差分は**設計上の排他性**で書く（[P270] は IME を迂回、[V5] は本文の読み取りに依存）。
- 自然な打鍵での精度（合成入力だけなので主張できない → 限界に書く）。
- 認知状態の推定・介入・GSE 全体の有効性（この論文の範囲外）。
- 「content-free だから安全」という断定（E2 の結果で限定して書く）。

---

## 5. 想定される査読の突っ込みと備え

| 突っ込み | 備え |
|---|---|
| 合成入力だけで実用の精度が分かるのか | 端のケースを網羅したシナリオで**失敗の型**を示すことを主目的にする。打鍵タイミングを 2 条件にして感度を出す。自然打鍵は限界と今後の課題 |
| 参照入力欄は 1 アプリにすぎない | 限界として明記。可能なら第 2 の参照入力欄（別フレームワーク）を足す |
| macOS の打鍵推論は IME の版に依存するのでは | 評価時の OS / IME の版を固定・記録。版依存は限界に書く |
| なぜ 0x8030 を使わないのか | 実装済みの経路だけを評価したと明記し、0x8030 は今後の課題（survey §7.4/§7.7） |
| 本文を本当に復元できないのか | E2 で定量化。同定がある程度できるならそう書く |
| コードは使えるのか | 評価一式を公開 repo で配布（decisions.md 判断 5） |

---

## 6. 投稿計画（大まか）

> ★ **2026-10-04 改訂（判断 145）**: 現行の日程は判断 145 の表（**BRM へ 10 月末に投稿**・原稿は計測と並行で書く）。下の表は当初の計画。

| 時期 | マイルストーン |
|---|---|
| 〜2026-10 中旬 | 評価プロトコルの確定（`/reimagine` → 凍結）、macOS の参照入力欄・シナリオ実行器・照合器 |
| 〜2026-11 上旬 | macOS 実測。Windows の参照入力欄（まず MS-IME から自窓へ IMM 互換メッセージが届くかを確かめる） |
| 〜2026-11 下旬 | Windows 実測（研究者の Windows 機・収集のみ依頼）、E2、バッテリー再計測 |
| 2026-12 | 執筆、評価一式の公開、BRM の規程確認、**BRM 投稿** |
| ~~〜2027-01-21~~ | ~~（任意）**CHI 2027 Posters**（4 ページ・非アーカイブ）~~ ⚠️ 取り下げ |
| 2027 前半 | BRM 査読対応。未踏採択後に GSE 本体を OSS 化し JOSS へ |

**遅れたときの縮退順**（★ 2026-09-28 判断 14 で更新）: 実アプリへの転移確認 → Google 日本語入力 → 現代文コーパス → マウス確定（S9）を「評価できなかった」とする → E2 の開集合の復元。

### ★ 2 本目（[P321] 再解析・判断 16）の並行計画

| 時期 | マイルストーン |
|---|---|
| 〜2026-10 | 正式版 [P433] の replication package をブラウザで取得し v1 と突き合わせる／[P434] の表を入力にした解析を `experiments/` に置く（seed 不要・入力の SHA-256 固定） |
| 〜2026-11 | 層別（起点）・区間推定・2 データの並置を確定。先行（help-seeking・debugging の観察研究）の位置づけ |
| 2027-01〜02 | 執筆（6 頁）。★ IME 論文の BRM 投稿（12 月）・CHI Posters（01-21）の後に集中する |
| 2027-02-22 / 03-01 | ★ **EASE 2027 Short Papers** abstract / paper（AoE）。⚠️ 投稿先は研究者の最終確認待ち（次点 ICPC 2027 RENE 12-18） |
**見送りの条件**: 参照入力欄で正解が取れない IME が必須側（macOS 標準 / MS-IME）にあると判明した場合は、設計を戻して再検討する。

---

## 7. 次セッションで議論すること

★ 2026-09-28 の状況（decisions.md 判断 10–16）:

1. ✅ `design.md` 初版の承認（訂正 4 点入り・判断 10）→ ✅ `/reimagine` 1 回目 → ハイブリッドを採用（判断 14）
2. ✅ タイトル = T1（判断 15）
3. ✅ ライセンス = コード Apache-2.0 / データ・文書 CC BY 4.0（判断 15）
4. ✅ BRM の規程確認（Open Practices Statement・Declarations・TOP Level 2 の信頼できるリポジトリ・Type 4 のデータ方針）。非アーカイブ発表は規程に記述が無い → 投稿時の書簡で開示（判断 13）
5. ✅ CPU 0.98% は無効な値だった → E3 は観測部だけ再計測（判断 12）
6. ⬜ 後続 issue への分解（`design.md` §8 に案）
7. ✅ [P321] 再解析 → 新しい公開データ [P434] が見つかり、2 本目を並行で進める（判断 16）
