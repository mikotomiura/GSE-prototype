# ESM 監査 criterion のゲート解除（起票 11 の ⓪〜④）

> ★ 一次資料: `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md` **起票 11** /
> `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md`（551 行） /
> `docs/adr/ADR-013` / `ADR-014` / `ADR-029` / `.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md` /
> `src-tauri/src/{schema_dto,logger,capabilities,recording,redaction,lib,o1}.rs`。
> ⚠️ 引き継ぎ `.steering/_handoff/next-session-after-literature-grounding.md` は**三次資料**（当たりを付けるのみ）。

## 背景

⚠️★★★ **`.idea/…survey.md:140` が逐語で「**監査 criterion**: 層化 ESM で
「熟考・詰まり・外部資料・会話・離席・回答不能」を少数取得する」と要求している**のに、
★ 現行の計器は `q1_friction` / `q2_progress` の 1..5 Likert 2 つしか持たない。

★ **2026-09-13 に研究者判断 = 「(a) 6 択フルを O1 で取る」が出ている**（⚠️ 本タスクで再決定しない）。
⚠️ しかし `security-checker` が「取るなら先に閉じること」を 4 点出しており、
★ 順序は **⓪ 提出猶予/第三者 → ① 規約 → ② 同意 → ③ `capabilities` 粒度 → ④ コード**である。
⚠️★★★ **④ から始めてはならない。**

⚠️★★★ **締切の性質**: 「O1 配布前」ではなく **「O1 の収集が本格化する前」**。
★ **打鍵ログは後から再解析できるが、その場の自己申告は後から生成できない**
＋ ★ **出したら消せない**（`.age` は `delete_time_range` の対象外）。

### ⚠️★★★ 本タスクの調査で新たに実測した 4 件（★ 起票 11 に無い）

| # | ⚠️ 事実 | ★ 一次資料（実測） |
|---|---|---|
| **1** | ⚠️★★★ **O1 同意文書の中核の約束が破れる。** 逐語「★ この記録では**画面に何も出しません**（⚠️ 出すと、ふだんの作業が変わってしまうためです）」 | `consent-draft-o1.md` §3 注 C。★ 引き継ぎが名指しした `participant-setup-guide.md:105` / `:185-186` **だけではない** |
| **2** | ⚠️★★★ **プローブは O1 で構造的に発火しない。** → ★ ④ は「フィールド追加」では済まず**発火配線**を伴う | `lib.rs:4696` プローブスレッドは `SESSION_START_MS != 0` を要求 ／ `SESSION_START_MS.store` は `lib.rs:3009`（`start_session` 内）だけ ／ `App.tsx:336` 逐語「★ `start_session` も `record_session_meta` も **呼ばない**」 |
| **3** | ⚠️★★★ **区間指定削除が自己申告行を 1 行も消していない。** ★ `line_timestamp` は `"t"` を読むが、`realtime_label` / `vignette_response` / `session_meta` は `"ts"`、`probe_assignment` は `"scheduled_ts"` を書く | `redaction.rs:81-89` ＋ `logger.rs:537/555/602/631`。⚠️ 削除 UI は **O1 以外でも出る**（`RecordingControls.tsx:508` の else 枝）→ ★ **通常運用（v0.3 較正）で既に live な欠陥** |
| **4** | ⚠️ **起票 11 #3 の根拠が失効している。** 「ADR-029 D3 の層 (a)」は **第 3 版で枠組みごと差し替え**られ存在しない（★ ADR-029 禁止 **#17** 逐語「`left_observation` の内訳が 4 層に割れた」は**誤り**） | `ADR-029:240-246` / `:512`。→ ★ **結論（`capabilities` 粒度が要る）は ADR-013 D1 単独で立つ**ので変わらない |

## ゴール

1. ★ **⓪〜③ を 1 本の新 ADR（ADR-031）で裁く。**
2. ★ **① を `data-privacy` ルール 7 に条文として落とす。**
3. ★ **② の同意文書改訂を *案* として出す**（⚠️ **承認は研究者**。被験者向け文書は契約）。
4. ★ **④ を additive に実装し、検査を同じコミットで置く**（`verify-before-claiming` ルール 6）。
5. ★ **実測 3（区間削除の穴）を塞ぐ。**

## スコープ

### 含むもの
- `docs/adr/ADR-031-*.md`（⓪①③ ＋ 実測 3 の裁定）
- `.claude/skills/data-privacy/SKILL.md` ルール 7 の改訂
- `consent-draft-o1.md` / `docs/participant-setup-guide.md` の改訂**案**
- `schema_dto.rs` / `logger.rs` / `capabilities.rs` / `recording.rs` への additive 追加 ＋ `emit_schema` parity
- `redaction.rs` の時刻フィールド取りこぼし修正 ＋ 回帰テスト
- ★ 順序 B（未踏 `.docx` 再生成）/ 順序 C（文献残件）は**本タスクの後段**

### 含まないもの
- ⚠️★★★ **起票 11 の研究者判断 (a) の再決定**
- ⚠️★★★ **ADR 本文（ADR-001〜030）の *決定* の書き換え**（★ 改訂は番号の大きい新 ADR へ）
- ⚠️ **O1 でプローブを発火させる配線そのもの**（`lib.rs` / `App.tsx` / launcher の `GSE_DISABLE_PROBES=1`）
  → ★ **別タスクへ起票**（⚠️ 反応性・UI・同意承認が揃ってから）
- ⚠️ `docs/preregistration-v0.3.md` の書き換え / `HMM_VERSION` の bump / `.idea` 本文の書き換え
- ⚠️ **Form_O1 の GAS 実配備**（★ 研究者が手で行う）

## 受け入れ条件

- [ ] AC1 ADR-031 が ⓪①③ ＋ 実測 3 を裁いており、**引用（`[Pn]`/`[Vn]`）が付いている**（`citation-ssot` ルール 1・⚠️ ADR も対象）
- [ ] AC2 `data-privacy` ルール 7 に「自己申告による行動カテゴリ」の行がある
- [ ] AC3 同意文書の改訂案が「破れる逐語」を**名指しで**直しており、⚠️ **研究者承認待ちと明記**されている
- [ ] AC4 `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が緑
- [ ] AC5 `cargo run --bin emit_schema` の出力が `src-tauri/schema/current.json` と byte-equal
- [ ] AC6 `gse-replay --snapshot` の回帰が緑（★ byte-equal）
- [ ] AC7 区間指定削除が **自己申告行を消す**回帰テストがある（⚠️ `session_meta` は消えないことも対で固定）
- [ ] AC8 `PYTHONUTF8=1 python scripts/check_citations.py` が「違反なし」（⚠️ **1 回で全件出ない** → 繰り返す）
- [ ] AC9 `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0
- [ ] AC10 `code-reviewer` ＋ `security-checker` を並列で通し、HIGH を消化した
- [ ] AC11 `/cross-review`（⚠️ **パス限定**・`docs/mitou_submission/**` を送らない・`P0\d\d` を目視）

## 関連ドキュメント

- `docs/adr/ADR-013-collection-self-description.md` D1 / D2（`capabilities` の意味）
- `docs/adr/ADR-014-continuous-natural-work-collection.md` D4 / D4b / D7 / D8（禁止表・同意 3 点・48h 猶予）
- `docs/adr/ADR-029-outcome-role-arbitration.md` D3（⚠️ **第 3 版**・禁止 #17）
- `docs/o1-deletion-ledger.md` §1 / §2（削除経路）
- `.claude/skills/data-privacy/SKILL.md` ルール 3 / 6 / 7

## 運用メモ
- /reimagine 適用: **No**
- 理由: ★ 選択肢と制約が一次資料側で既に狭く決まっており（研究者判断 (a) ／ ADR-013 D1 ／ ADR-014 D4 禁止表 ／
  `.idea` の逐語要求）、⚠️ **ゼロから再生成しても同じ枠に戻る**。★ 代わりに **⓪ の 3 択を ADR 内で明示的に比較**する。
