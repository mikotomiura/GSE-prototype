# 単位 a: ADR-030 補訂 1（項目 1〜5・7・8）

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **a**。

## 背景

- タスク 2（`20260914-mhd-feature-offline-tiers`）の issue 008 で `stall onset` の検出器を実装した。そのとき ADR-030 が書き切っていなかった規則（観測区間・`feat` 行 0 本の扱い）を実装が一意に決めた。
- 研究者判断 25（2026-09-18）が、修飾キー規則・IME 抑制・`hole_gap_ms`・ポインタ極を裁き、「理論レビューの中で補訂案にし、人の採否を経て反映する」とした（#15）。
- 前段（`20260918-theory-critical-review`）が補訂案（`adr-030-amendment-draft.md`）を作り、研究者判断 1 #5（再開・再停止は条件 A の辺）と S7 / S8 のサーヴェイの結果を足した。

## ゴール

- ADR-030 の末尾に「補訂 1」節を足し、補訂案の項目 1〜5・7・8 を規範として書く。
- S7 の注記（`T1c` の証拠列「中〜強」は位置なし版に移らない）と、S8 の注記（条件 A による再開・再停止は今回の範囲で先例 0 件の新しい操作化）を入れる。
- 項目 6（E1 の実装形）は入れない。D7 の表の事実誤り（「次の `t0` は起きえない」）は、項目 6 を保留していることと一緒に明示する。

## スコープ

### 含むもの
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` の末尾に補訂 1 節を追加
- `docs/adr/README.md` の ADR-030 行のステータス欄に補訂 1 を 1 文で足す
- 本文の D7 表と D3 修飾キー規則・抑制表・D10 Tier 表の該当行に「補訂 1 項目 n を見よ」の参照だけを足すかの判断（→ `decisions.md`）

### 含まないもの
- ⚠️ 項目 6（E1 の実装形）—— issue 006 V1 の裁定の後
- ⚠️ ADR-030 本文の書き換え
- ⚠️ 値（`W` / `q` / `B` / `hole_gap_ms` ほか）—— P1 前の事前宣言文書
- ⚠️ 実装（`stall_onset.rs`・`redaction.rs`・`RecordingControls.tsx`）—— 項目 5 のテスト固定は実装タスクへ渡す

## 受け入れ条件

- [ ] 補訂 1 の規範文が `stall_onset.rs` の module doc・テスト名（`no_lookahead_in_net` ほか）と一致する（項目 1 / 2）
- [ ] 項目 3 が ADR-032 D9（`key.mod`）と macOS の事実（修飾キー行が届かない）に矛盾しない
- [ ] 項目 5 の前提（削除 UI は分単位・`delete_time_range` は任意の ms を受ける）を一次で確かめている
- [ ] 項目 6 の内容（E1 を検出列へ入れる書き方）を入れていない
- [ ] 引用はすべて `docs/references.md` に登録済みの ID
- [ ] `/cross-review` 2 巡を通し、指摘の採否を `decisions.md` に記録している

## 関連ドキュメント

- `.steering/20260918-theory-critical-review/adr-030-amendment-draft.md`・`definitions-restop-t1d-t1c.md` §3
- `.steering/20260914-mhd-feature-offline-tiers/decisions.md` 判断 25 / 26・`blockers.md` 起票 11〜15
- `docs/literature/20260919-content-free-revision-measures.md`（S7）・`docs/literature/20260919-resumption-restop-and-bout-segmentation.md`（S8）
- `docs/adr/ADR-032-instrument-change-arbitration.md` D9

## 運用メモ

- /reimagine 適用: **No**
- 理由: 補訂の中身は研究者判断 25 と前段の判断 1 で決まっている。ここでは既決を ADR へ書き写す
