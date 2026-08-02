# タスクリスト — G1 実施直前準備

## T-0 先読み

- [x] `.steering/20260802-g1-implementation/decisions.md`（D-1〜D-6・**D-5 が主題**）
- [x] `preregistration.md`（改訂履歴 ＋ §2.4 §2.5 §2.7〜§2.9 §3.7 §5.1 §5.2）
- [x] `protocol.md` / `materials/README.md` / `materials/topic01_{lo,hi}.md` / `config.json` /
      `validate_materials.py` / `notes.md`

## T-1 D-5 の決着（★ 最優先・研究者判断）

- [x] (a)(b)(c) を研究者に提示した
- [x] **(b) を採用**（`decisions.md` E-1）
- [x] `preregistration.md` を**第 3 版**に改訂（冒頭「改訂履歴 — 第 3 版」に ★訂正 として記録）
- [x] ★ **判定を緩めていないことを論証**した（4 点：経路 0 本増 / ラベル非依存 / §3.4 不変 / n=1 で救済無しも不変）
- [x] `§2.5` の解釈規約の表を `✗ かつ true` / `✗ かつ false` に分けた
- [x] `config.json` の `positive_control.decision_rule` を同期した

## T-2 主判定の検出力についての研究者確認

- [x] 「帰無 95%点が AUC≈0.94 ＝ 実質 AUC≈1.0 が要る」ことを提示した
- [x] **補強する**判断を得た（`decisions.md` E-2）
- [x] `§3.7` に「`✗` の証拠力の前提条件」を追加した（**`✗` の射程を狭める方向のみ**）
- [x] `config.json` の `asymmetry_of_conclusions.negative_result_precondition_v3` を同期した

## T-3 本番用の課題文 8 題材 × 2 版

- [x] P-1 を先に回すかを研究者に確認 → **先に作る**（`decisions.md` E-3）
- [x] `topic02` 商店街の駐輪場 / `topic03` 小学校の屋外プール / `topic04` 燃やすごみの収集
- [x] `topic05` 公民館の部屋の予約 / `topic06` コミュニティバス / `topic07` 公園でのボール遊び
- [x] `topic08` 学校から家庭への連絡
- [x] 各題材で **LO 1 本 / HI 3 本**、**HI の 3 本は同じ問いに食い違う答え**
- [x] 資料総文字数を題材内 **±5% 以内**に調整（最大 3.8%）＋ 題材間も 451〜490 字に揃えた
- [x] ★ `python3 validate_materials.py --strict` = **緑**
- [x] `materials/README.md` の状態表を更新（P-1 後の修正が許容されることも明記）

## T-4 n の扱いと実施順序

- [x] n の凍結時期を研究者に確認 → **P-1 の後に凍結**（`decisions.md` E-5）
- [x] `config.json` の `n_subjects` は `TO_BE_FROZEN_AFTER_PILOT` のまま（数値を書かない）
- [x] ★ **凍結の手続き**（何をして・何を `notes.md` に書くか）を書き下した
- [x] ★ **n=1 の既知の限界**を研究者に提示し `notes.md` に記録した
- [x] 実施順序を確認 → **Phase1 の凍結解除後**（`decisions.md` E-4）
- [x] ★ ADR との食い違いが**生じない**ことを確認（順序を変更していないので `docs/adr/` への追記は不要）

## T-5 レビュー

- [x] 自分で全文を読み直し、`preregistration.md` ↔ `config.json` ↔ `notes.md` ↔
      `materials/README.md` の齟齬が無いことを確認した
- [x] ★ `/cross-review`（Claude ＋ Codex の独立レビュー）**実施済み**（ユーザー承認を得て起動）
      - 安全ゲート: proprietary/機密なし・予算内（残 96k > 30k）・diff 986 行（手動承認閾値 2000 未満）
      - 渡したのは **git diff のみ**（NDJSON 生ログ・被験者データは渡していない）
- [x] ★★ **指摘 1（HIGH・実バグ）を一次確認して修正**: `analyze.py` が `test_can_reject_at_all` を
      見ずに無条件で `"G1 IS VOID"` を出していた → `interpretability()` に切り出して §2.5 第 3 版を実装
      ＋ **回帰テストを selftest に固定**（`decisions.md` E-6）
- [x] 指摘 4（`§3.7` の `test_can_reject_at_all` が主判定側か positive control 側か曖昧）→ 限定語を追加
- [x] 指摘 5（結果に事前登録の版が刻まれない）→ `preregistration_revision: 3` と `decision_status` を出力に追加
- [x] 指摘 2（`§3.4` の字面が §2.5 の分岐と食い違う）→ ★ **§3.4 は変更禁止節なので触っていない。**
      `notes.md` に**残存論点**として記録した（抜け穴は生じないことも併記）
- [x] Codex の指摘のうち「`config.json` の構造変更が既存スクリプトを壊す」は
      **false positive**（`revision.*` を読むスクリプトは repo 内に存在しない）と判定

## 検証

- [x] `python3 validate_materials.py --strict` = 緑
- [x] `python3 -c "import json; json.load(open('config.json'))"` = OK
- [x] `bash run.sh` = **GREEN**
- [x] `src-tauri/` / `src/` に変更が無い（`run.sh` [5] が確認）
- [x] ★ **実験は実施していない**（`results/` は空・`blocks/` に割付ファイル無し）
