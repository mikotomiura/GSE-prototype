# gse-stage1-adr-prereg —— 次の検証の段 1 の ADR と事前登録の草案、空回しの次の版

## 背景

- 次の検証の段 1 の形は `.steering/20261103-gse-next-study-design/decisions.md` 判断 2〜13 で研究者が決めた。判断 9 で、これを新しい ADR 1 本に書き、ADR-031・ADR-032 の対象を O1 から次の検証へ移すと決め、起票は別タスクにした。
- ADR-042（Accepted）が MhD の単位を分けた。Migration 6 は、段 1 の事前登録に ADR-042 の決めずに残したもの（停滞の定義の選択・再標本化の手順と申告の最小の間隔・D5 の値と独立な陽性の数え方・H4b の検査と後退先・日の境界とエピソードの所属）を足すとしている。
- 配管の空回し（`experiments/20261103-mhd-pipeline-dryrun/`）の notes §5 が、事前登録に持っていく候補（模擬に見分ける力を入れる・日のブロックだけの巡回する再標本化で被覆を確かめ直す・収束と分離を出力に出す ほか）を挙げた。
- 引き継ぎ: `.steering/_handoff/next-session-gse-after-mhd-unit-adr.md` の候補 3（研究者が選んだ・2026-11-03）。

## ゴール

1. ADR-043（Accepted）: 次の検証の段 1 の形（判断 2〜8・10・12・13）を書き、ADR-031・ADR-032 の対象を O1 から段 1 に移す。両 ADR の Accepted の条件を段 1 の同意文書の承認に読み替える。ADR-031 M9 の束ねを段 1 では解く。
2. `docs/preregistration-stage1.md`（草案・凍結しない）: 段 1 の事前登録に書く項目（next-study-design の項目 1〜17・ADR-042 Migration 6・MhD 判断 8〜10・空回しの notes §5）を、項目・形・値を決める手順として書く。値は空欄にする。
3. 空回しの次の版（`experiments/` の新しいディレクトリ）:
   - (a) 1 人の中の日を単位にした合成の模擬。見分ける力・基準率・回答率・日の揺れを入れ、巡回する日のブロックの再標本化で、較正の傾き・切片の区間の被覆と幅を日数ごとに出す。事前登録の件数の見積もりの部品。
   - (b) CoAuthor の版の直し（巡回するブロック・Newton 法の収束と分離の記録・陽性対照の書き出し・範囲を四分位に・切片の計算への変異）。
   - どちらも条件を計算の前にコミットし、陽性対照を通す。

## スコープ

### 含むもの
- ADR-043 の起票と `docs/adr/README.md` の一覧への追加・ADR-031・032 の行への注記（本文は書き換えない）。
- 事前登録の草案。
- 空回しの次の版 (a)(b) の条件・コード・陽性対照・結果・notes。
- 完了時の /cross-review（Claude と Codex）。

### 含まないもの
- 事前登録の値の決定と凍結（本人の段 1 の探索の後）。attack-me は凍結の前の版で Codex を加えて回す（判断 5）。
- 保留 1（動機づけと同期・共生の感覚の問い方）。
- `docs/research-positioning.md`・`docs/wbs-verification-halfyear.md` の改訂（ADR-041 Migration 4 の別タスク）。
- 段 1 の同意文書・プローブの発火の配線（ADR-031 M5）などの実装。
- `~/gse-public-data/landscape/holdout.json` を開くこと。O1 の記録を使うこと。
- 結果を詰まりの推定や MhD が学習できた根拠にすること。

## 受け入れ条件

- [ ] ADR-043 が判断 2〜13 の決定を落とさず書き、ADR-031・032 の本文を書き換えていない（一覧と注記だけ）。
- [ ] 事前登録の草案に next-study-design の項目 1〜17 と ADR-042 Migration 6 の 5 つ・MhD 判断 8〜10・notes §5 の 1〜5 が、それぞれどこで扱うかの対応つきで入っている。値を決めていない。
- [ ] (a)(b) の条件が計算の前のコミットにあり、陽性対照が results に書き出され、変異で赤になる。
- [ ] (a) が日数 × 見分ける力 × 基準率の格子で、傾きと切片の区間の幅と被覆を出す。
- [ ] /cross-review を通し、指摘の対応を decisions.md に書く。

## 関連ドキュメント

- `.steering/20261103-gse-next-study-design/decisions.md`
- `docs/adr/ADR-042-effect-unit-and-mhd-sample-unit.md`・`.steering/20261103-gse-mhd-unit-adr/decisions.md` 判断 8〜10
- `experiments/20261103-mhd-pipeline-dryrun/`（conditions・notes）
- `docs/adr/ADR-031-*.md`・`docs/adr/ADR-032-*.md`

## 運用メモ
- /reimagine 適用: No
- 理由: ADR-043 は既に決まった判断の書き下ろしで、新しく決めるのは M9 だけ。模擬は条件を計算の前にコミットし陽性対照で確かめる（研究者が推奨どおり選んだ・2026-11-03）。
