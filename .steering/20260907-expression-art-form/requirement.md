# expression-art-form — 層 A の「数値を添えるか」を裁定し、ADR-023 M9 を遂行する

## 背景

★ **ADR-023 §Migration M9 が別タスクへ割った作業が本タスクである。**

M9 の逐語:

> ★ `docs/architecture/expression-channel.md` §7.1 / §8 を更新する。
> §7.1 の位置づけ（合否 → 操作チェック）と、⚠️ **新しい未決を 2 件立てる**:
> **(a)「層 A に数値を添えるか」**（→ **D3-d**）／
> ⚠️★★★ **(b)「期間中の *関与* を、受動的・content-free に、かつ ADR-017 D3 の inbound 禁止に
> 触れずに測れるか」**（→ **D3-c** 要件 2。★ 現時点で計器は存在しない）

★ **一次で確認した現状**（2026-09-07）:

| # | 事実 | 一次 |
|---|---|---|
| 1 | ★ `expression-channel.md` §8 に **(a) も (b) も立っていない** | ★ 実測（§8 の表に該当行なし） |
| 2 | ★ §7.1 は「**最小プロトコル（ADR-021 D8）**」のままで、位置づけが「合否」寄りに読める | ★ 実測 |
| 3 | ⚠️ **ADR-023 M6**（`experiments/20260902-expression-layerA-visual/notes.md` の位置づけ更新）も未着手 | ★ 実測 |

### ★ 本タスクが (a) を「未決として立てる」で終わらない理由

⚠️★★★ **ADR-023 D3-d は文献の側から (a) を閉じられなかった** ——
逐語「純アンビエントで行動が動く」は **`PLAUSIBLE BUT UNPROVEN`**。

★ **しかし GSE には文献の外に決め手がありうる** ——
⚠️ **ADR-021 D4 の境界契約は `level`(3 値) / `invitation`(2 値) / `seq` / `emitted_at` / `epoch` しか運ばず、
受け入れ観点 A2 が逐語で「連続値・本文・位置・端末名が無い」ことを要求している。**
→ ★★★ **「層 A に数値を添える」は境界契約そのものの改訂を要求する。**
★ したがって (a) は **内部契約と曝露予算の側から裁定できる可能性がある**（★ 研究者判断・2026-09-07）。

## ゴール

1. ★ **ADR-025 を起票し、(a)「層 A に数値を添えるか」を Accepted で閉じる。**
2. ★ `docs/architecture/expression-channel.md` **§7.1 の位置づけを「合否」→「事前の操作チェック」へ改める。**
3. ★ 同 **§8 に未決 2 件を立てる** —— **(a) は「ADR-025 で閉じた」ことを記録**し、**(b) は未決のまま残す**
   （★ **「何が埋まれば閉じるか」を第 2 列に書く**）。
4. ★ **ADR-023 M6 を同梱する** —— `experiments/20260902-expression-layerA-visual/notes.md` の
   位置づけを「合否」→「*事前の* 操作チェック」に改める。
   ⚠️★★★ **設計もハーネスも一切変えない**（★ ADR-023 M6 の逐語）。

## スコープ

### 含むもの
- `docs/adr/ADR-025-*.md`（新規）＋ `docs/adr/README.md` への登録
- `docs/architecture/expression-channel.md` §7.1 / §8（＋ 波及する §3.5 / §7.5 の受け入れ観点）
- `experiments/20260902-expression-layerA-visual/notes.md` の**位置づけの文言のみ**
- `docs/glossary.md` への用語追記（★ `操作チェック`）
- `.steering/20260907-expression-art-form/`

### 含まないもの（★ ハンドオフ §C ＋ 本タスクの追加）
- ⚠️ **ADR-024 の再検討**（★ 完了済み）
- ⚠️ **既存 ADR（017/018/020/021/022/023/024）の本文を書き換えない**
  → ★ **ADR-024 と同じ「番号の大きい ADR が上書きする」作法を採る**
- ⚠️ **凍結済み `docs/preregistration-v0.3.md` を書き換えない**
- ⚠️★★★ **コード変更ゼロ** —— `src-tauri/` / `src/` / `scripts/` を触らない
- ⚠️★★★ **試視を回さない** —— PS-Q5 / E-7 / M-3 の実測は本タスクの外（★ 被験者の手配が前提）
- ⚠️ **(b) の計器を *決めない***（★ §8 に未決として立てるまで）
- ⚠️ **層 B の仕様を決めない**（★ 裁定の射程は**層 A**。層 B は却下案の説明に留める）
- ⚠️ **フォーカス遷移アームを既存データで回さない**（★ `capabilities_gate.py` が `INSTRUMENT_ABSENT`）
- ⚠️ **「慣れているか（習慣化）」を扱わない**（★ ADR-020 / M7）
- ⚠️ **`scripts/secrets-filter.sh` に `email=` を足さない**（★ M10・fail-closed で over-block）
- ⚠️ **`receipt` の実装を広げない**（★ `data-privacy` ルール 7）
- ⚠️ **B-2（M1 Step 2b 本解析）/ B-3（`capabilities_gate.py` の `file_id`）は別タスク**
- ⚠️ **未コミットの未踏スライド作業を触らない**（★ `.pptx` / `figures/` / `scripts/md2pptx.py` 他）

## 受け入れ条件（★ Done を観測可能な条件で言う）

- [ ] **D-1** `docs/adr/ADR-025-*.md` が存在し、**ステータスが `Accepted`** で、(a) の裁定が書かれている
- [ ] **D-2** `docs/adr/README.md` に ADR-025 の行があり、**表題が本文の H1 と一致する**
- [ ] **D-3** `expression-channel.md` §7.1 に **「操作チェック」の位置づけ**が明記されている（grep）
- [ ] **D-4** `expression-channel.md` §8 に **(a) の決着**と **(b) の未決**の行が存在する（grep）
- [ ] **D-5** `experiments/20260902-expression-layerA-visual/notes.md` の位置づけが更新され、
      **`spec.md` / ハーネスのコードと機械検査に差分が無い**（`git diff --stat` で `notes.md` のみ）
- [ ] **D-6** `PYTHONUTF8=1 python scripts/check_citations.py` が **「違反なし」**（exit 0）
- [ ] **D-7** `docs/glossary.md` の**禁止用語**が新規文書に混入していない（grep）
- [ ] **D-8** ⚠️ **コード変更ゼロの確認** —— `git diff --stat` に `src-tauri/` / `src/` / `scripts/` が現れない
- [ ] **D-9** `code-reviewer` ＋ `security-checker` 並列 → `/cross-review`（★ コミット後・パス限定）

## Stop 条件（★ 進めてはいけない合図）

- ⚠️ (a) の裁定が **ADR-021 D4 の境界契約を改訂する向き**に倒れ、かつ **改訂の影響が層 A の外へ及ぶ**とき
  → ★ **研究者に戻す**（★ 本タスクの射程は層 A）
- ⚠️ `check_citations.py` が是正を繰り返しても「違反なし」に到達しないとき
  （★ **重複検出は 1 回で全件出ない** —— memory: check_citations は違反を隠す）

## 関連ドキュメント

- `docs/adr/ADR-023-coupling-as-primary-outcome.md` **D3 / D3-c / D3-d / §Migration M6 / M9**
- `docs/adr/ADR-021-expression-channel-open-items.md` **D1 / D2 / D3 / D4 / D8 / D9 / D10**
- `docs/adr/ADR-022-layer-a-medium-implementation-constraints.md` **D1 / D2 / D4 / D5 / D7**
- `docs/adr/ADR-017-expression-channel-boundary.md` **D3 / D4 / D6 / D8 / D10**
- `docs/adr/ADR-018-physical-anchor-without-completion.md` **D1 / D2 / D3**
- `docs/architecture/expression-channel.md` **§3 / §3.5 / §7.1 / §7.5 / §8**
- `docs/references.md`（★ [P324] / [P325] / [P326] / [P327] / [P328] / [P147] / [P337] / [P315] / [V140]）

## 運用メモ

- **/reimagine 適用: Yes**
- 理由: ★ **(a) は設計判断そのもの**であり、初回案（「内部契約から *添えない* を導く」）に
  引きずられると **却下案の検討が形骸化する**。★ `CLAUDE.md` セッション行動規範 5 に従い、
  **設計承認前に `/reimagine` で案を破棄・再生成して比較する。**
