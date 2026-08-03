# タスクリスト — G1 パイロット P-1 の実施可能化

## T-1 B-1 = プローブ無効化（案 C・実装するだけ）

- [ ] `analysis/probe_scheduler.rs` に純ロジック `probes_disabled_by_env` を追加
- [ ] 単体テストを追加（既定は無効化しない／`"1"` のときだけ無効化する）
- [ ] `lib.rs` のプローブスレッドを env で **spawn しない**ようにする
- [ ] `cargo test --workspace` / `cargo clippy` が緑
- [ ] `run.sh [5]` の意図を「kill switch が入っていること ＋ 無関係な未コミット変更が無いこと」に変更
- [ ] 解析経路に影響しないことを事前登録第 5 版に書く

## T-1b B-5 = 入力先（ローカル HTML 入力パッド）

- [ ] `materials/writing-pad.html` を作る（補完 off・live 文字数・保存なし）
- [ ] 文字数の数え方を 1 つに固定し、`preregistration.md §3.5` の産出量報告と整合させる
- [ ] `protocol.md` に「どこに入力するか」と当日の手順（拡張なしで開く等）を書く
- [ ] `participant-guide.md` / `consent.md` の「本文は保存しない」との整合を確認する

## T-3 フォーム

- [ ] `Form_G1/GSE_G1_Form_Builder.gs`（同意 / 強制比較 / 終了後アンケートの 3 本）
- [ ] `Form_G1/README.md`（配備手順・固定 ID の埋め方・紙のバックアップ）
- [ ] `forms_to_blocks.py`（CSV → `manipulation_check_answers`）＋ `--selftest`

## T-4 終了後アンケート

- [ ] `preregistration.md` **第 5 版 §2.10** に「取るが判定には使わない」を明記
- [ ] `config.json` に同期
- [ ] フォーム側に実装（G1-S）

## T-5 転記工程の信頼性

- [ ] `validate_blocks.py`（構成 / 割付一致 / NDJSON 名 / 操作チェック対応 / probe 行 0）
- [ ] `--selftest` を書き、`run.sh [4]` に組み込む
- [ ] `blocks/README.md` を更新

## T-6 実施環境の確定

- [ ] `protocol.md` に `HMM_VERSION` の刻印手順（誰がいつ何を書くか）
- [ ] `env.md` に実施 OS の記録欄（`§5.1-4` の報告義務）
- [ ] `data.md` の匿名化・送付フローを P-1 で通しで確認する段取り
- [ ] `--verify-blocks` が P-1 で**初回実行**であることを明記

## 事前登録 第 5 版

- [ ] 改訂履歴（**判定を緩めていないことの論証**つき）
- [ ] `§2.10` 終了後アンケート（判定に使わない）
- [ ] `§2.11` 入力先の固定
- [ ] `§5-3` の訂正（コード変更ゼロ → kill switch を要求する）
- [ ] `config.json` を同期
- [ ] ★ **改訂した規則を実行するスクリプトが同じ版か**を確かめる（E-6 / E-7 の教訓）

## 仕上げ

- [ ] `bash run.sh` GREEN
- [ ] `python3 validate_materials.py --strict` / `analyze.py --selftest` / `validate_blocks.py --selftest` 緑
- [ ] `notes.md` に本ラウンドの節を追記
- [ ] `decisions.md` に判断を記録
- [ ] `/cross-review`（★ 渡すのは git diff のみ。NDJSON・被験者データを渡さない）
- [ ] コミット（PII・セッション日時を出さない）
