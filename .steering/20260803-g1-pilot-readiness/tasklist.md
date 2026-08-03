# タスクリスト — G1 パイロット P-1 の実施可能化

## T-1 B-1 = プローブ無効化（案 C・実装するだけ）

- [x] `analysis/probe_scheduler.rs` に純ロジック `probes_disabled_by_env` を追加
- [x] 単体テストを追加（既定は無効化しない／`"1"` のときだけ無効化する）
- [x] `lib.rs` のプローブスレッドを env で **spawn しない**ようにする
- [x] `cargo test --workspace` / `cargo clippy` が緑
- [x] `run.sh [5]` の意図を「kill switch が入っていること ＋ 無関係な未コミット変更が無いこと」に変更
- [x] 解析経路に影響しないことを事前登録第 5 版に書く

## T-1b B-5 = 入力先（ローカル HTML 入力パッド）

- [x] `materials/writing-pad.html` を作る（補完 off・live 文字数・保存なし）
- [x] 文字数の数え方を 1 つに固定し、`preregistration.md §3.5` の産出量報告と整合させる
- [x] `protocol.md` に「どこに入力するか」と当日の手順（拡張なしで開く等）を書く
- [x] `participant-guide.md` / `consent.md` の「本文は保存しない」との整合を確認する

## T-3 フォーム

- [x] `Form_G1/GSE_G1_Form_Builder.gs`（同意 / 強制比較 / 終了後アンケートの 3 本）
- [x] `Form_G1/README.md`（配備手順・固定 ID の埋め方・紙のバックアップ）
- [x] `forms_to_blocks.py`（CSV → `manipulation_check_answers`）＋ `--selftest`

## T-4 終了後アンケート

- [x] `preregistration.md` **第 5 版 §2.10** に「取るが判定には使わない」を明記
- [x] `config.json` に同期
- [x] フォーム側に実装（G1-S）

## T-5 転記工程の信頼性

- [x] `validate_blocks.py`（構成 / 割付一致 / NDJSON 名 / 操作チェック対応 / probe 行 0）
- [x] `--selftest` を書き、`run.sh [4]` に組み込む
- [x] `blocks/README.md` を更新

## T-6 実施環境の確定

- [x] `protocol.md` に `HMM_VERSION` の刻印手順（誰がいつ何を書くか）
- [x] `env.md` に実施 OS の記録欄（`§5.1-4` の報告義務）
- [x] `data.md` の匿名化・送付フローを P-1 で通しで確認する段取り
- [x] `--verify-blocks` が P-1 で**初回実行**であることを明記

## 事前登録 第 5 版

- [x] 改訂履歴（**判定を緩めていないことの論証**つき）
- [x] `§2.10` 終了後アンケート（判定に使わない）
- [x] `§2.11` 入力先の固定
- [x] `§5-3` の訂正（コード変更ゼロ → kill switch を要求する）
- [x] `config.json` を同期
- [x] ★ **改訂した規則を実行するスクリプトが同じ版か**を確かめる（E-6 / E-7 の教訓）

## 仕上げ

- [x] `bash run.sh` GREEN
- [x] `python3 validate_materials.py --strict` / `analyze.py --selftest` / `validate_blocks.py --selftest` 緑
- [x] `notes.md` に本ラウンドの節を追記
- [x] `decisions.md` に判断を記録
- [x] `/cross-review`（★ 渡すのは git diff のみ。NDJSON・被験者データを渡さない）
- [x] コミット（PII・セッション日時を出さない）

## T-7 `/cross-review`（★ 実施済み・指摘 6 件をすべて反映）

- [x] 安全ゲート通過（proprietary/機密なし・予算 PASS・codex あり・`secrets-filter.sh` マッチ 0 件）
- [x] ⚠️ 差分 2703 行 ＞ 手動承認閾値 2000 行 → **研究者判断でコード部分（1520 行）に絞った**
- [x] 両者一致 HIGH 1 件 / MEDIUM 2 件、Codex のみ 2 件、Claude のみ 1 件 → **全件採用**（`b0286fc`）
- [x] ⚠️ **Codex が独自に 1 件見つけた**（`forms_to_blocks.py` の二択判定が部分一致の先勝ち）

## ★ 残タスク（研究者が行う）

- [ ] `Form_G1` の 3 フォームを Google Forms に配備し、固定 ID を `.gs` に埋める
- [ ] CI で Windows / macOS の本番バイナリをビルドし、実施端末に入れる
- [ ] `GSE_DISABLE_PROBES=1` を起動手段（ショートカット / launcher）に固定する
- [ ] ★ **パイロット P-1 を実施する**（`--verify-blocks` / `validate_blocks.py --dataset` の初回実行）
- [ ] P-1 の後に確証標本の n を凍結する（`§2.4-1`）
