# gse-m5-probe-wiring-plan —— プローブの配線（ADR-031 M5）の実装の計画（R2）

## 背景

- 段 1 の配布までの道筋（`docs/architecture/gse-design-map.md` §3）で、研究者本人の段 1 の試し（R5・探索・ADR-043 D3）は R2（M5 の実装）と R3（gse-dataset の schema の同期）を待ち、R2 は R1（招待の配線の枝 `feature/nudge-default-off` を main へ）を待つ。
- R1 は 2026-11-05 時点で実機の確かめが未実施（研究者の回答）。枝は origin/main より 188 コミット遅れ、origin に push されていない。
- R1 を待つ間に進められるものとして、M5 の実装の計画を先に立てる（design-map §3.2）。
- 設計の一次: design-map §4（決めたこと 4.1・既にあるもの 4.2・提案 4.3）、ADR-043 D5・D6・D8・D9、ADR-031（Proposed）、ADR-047、ADR-048 D3、事前登録の草案 `docs/preregistration-stage1.md`（S1-A1〜A7・S1-F5〜F10。S1-A6・A7・F5〜F10 は未 push の枝 `docs/gse-stage1-prereg-revision` にある）。

## ゴール

- M5 の実装を、別のセッションで着手できる形の計画にする: 変更するファイル・新しい行種と schema の差・純粋な関数とその検査・画面・`capabilities` の宣言・R1 との衝突点・R3 の同期・検証の手順。
- 頻度と閾値は探索用の仮の定数で作る前提にする（確定は R6 の後の R6′）。
- `/reimagine` で作り直した案と比べ、研究者が採る案を選ぶ。

## スコープ

### 含むもの

- C4 のプローブ（無作為の枠が主・層化は補い・毎回 Q1・Q2・6 択の 3 問・申告の幅 30 秒）の配線。新しいモード（O1 の提出・自動起動・インストール ID・削除を共有・Nudge と招待を出さない）。
- 日の終わりの問い（ADR-048 D3・S1-F5〜F8・F10）: 契機（夕方の打鍵の途切れ・補助にトレイの終了と一時停止）・翌日の拾い直し（遅れた回答の印）・回答の記録（時刻・回答の後の打鍵の量・回答にかかった時間）。項目の文は S-DQ の候補の表から仮の文（判断 1）。
- 申告を求めない区間（S1-A6）: 無作為の置き方の仕組みと記録を仮の定数で作り、既定は無効（判断 2）。
- 抑制の記録 `probe_suppressed`（design-map §4.1 判断 9）。

### 含まないもの

- コードの変更（このタスクは計画だけ。実装は R1 が main に入ってから別のタスクで）。
- 事前登録の値の確定（R6）・同意文書（R4）・倫理審査（R8）・配布（R9）・手跡（R10）。
- 日の終わりの問いの項目の文の確定（S1-F7）と、同期と速さの区別の対照（S1-F9）。

## 受け入れ条件

- [ ] design.md に、変更するファイルと関数・新しい行種と schema の差・検査の名前・画面の確かめの手順・R1 との衝突点・R3 の手順が書いてある
- [ ] `/reimagine` の v1 と v2 を比べ、研究者が選んだ案が decisions.md に記録されている
- [ ] tasklist.md が、別のセッションが requirement・design・tasklist だけで実装に着手できる粒度になっている
- [ ] 研究者に決めてもらったことが decisions.md に記録されている

## 関連ドキュメント

- `docs/architecture/gse-design-map.md` §3・§4
- `docs/adr/ADR-031-self-reported-activity-audit-criterion.md`・`ADR-043-next-study-stage1-c4-collection.md`・ADR-047・`ADR-048-handmark-as-counterpart-of-abstention.md`
- `docs/preregistration-stage1.md`（改訂は枝 `docs/gse-stage1-prereg-revision`）
- `docs/literature/20261105-daily-end-of-day-items.md`（S-DQ・枝 `docs/gse-daily-item-scale-literature`）

## 運用メモ

- /reimagine 適用: Yes
- 理由: 新しいモードの切り方、無作為と層化と日の終わりの問いの調停、問わない区間の置き方と、複数の案がありうる設計の判断が重なる。計画だけなので作り直しの費用は文書の分だけ（研究者の回答・2026-11-05）。
