# p1-sleep-trim — スリープ直後の入力の無い feat 行を P1 の観測区間から外す

## 背景

issue #330。Windows のモダンスタンバイ（S0）で O1（v0.1.40）を寝かせると、電源につないだ試験では、寝てから 16 分間 `feat` 行が約 1 Hz で書かれ続けた（`.steering/20261008-windows-sleep-test/result.md`）。バッテリーでは 4 秒以内に止まった。macOS（2026-09-10・蓋閉じ）では 1 秒後に止まった。

P1 の観測区間は `feat` 行の有無だけで切られる（ADR-030 D8 (b-2)・補訂 1 項目 1）。そのため、この 16 分は「観測していて、手が止まっている」区間になり、寝ている間に stall onset が立ちうる（`warmup_count=10` にした実行で、12:41:26 に立つことを確かめた）。

v0.1.40 は 2 名に配布済みで、O1 は 2026-10-08 に始まった。配布済みの分に効くのは解析の前処理だけである。P1 の実データはまだ 1 件も見ていない。

## ゴール

`gse-replay --features` が観測区間を作る前に、次の規則で `feat` 行を落とす。規則と値は、P1 の実データを見る前に、事前登録の改訂（v1.2）として宣言する。

- 規則（研究者裁定 2026-10-08）: `feat` 行の間隔が 60 秒以上空いた穴の直前、またはファイルの最後の `feat` 行で、その時刻 `h` より前で最後の `key` 行または `pointer_bin` 行の時刻を `L` とする。時刻が `max(L, h − 30 分)` より後で `h` 以下の `feat` 行を落とす。
  - 2026-10-09 追記（判断 6・研究者確認）: `L` の代わりに「`L` 以上で最初の `feat` 行（最後の入力を含む秒の行）」を使う。最後の入力が観測区間の内側に入るようにするため。
- 入力に数えるのは `key` と `pointer_bin` の行だけ（`ime_state` や `focus_transition` はシステムが出しうる。実記録でも、寝た 11 秒後に `ime_state` が 1 行出ていた）。
- 前処理なしの実行（上限 0）も並べて報告する。2 本は誤差の向きが逆なので、補正ではなく挟む関係として読む。

## スコープ

### 含むもの

- 前処理の純関数と単体テスト（`analysis/feat_offline/`）
- `gse-replay --features` への配線（`feat_ts` を作った直後に 1 回だけ掛ける）と、封筒への記録（値と、落とした行・時間の量）
- 凍結 JSON に 2 キーを足し、version を 1.1.0 にする
- `docs/preregistration-p1-episode.md` の v1.2 改訂宣言
- ADR-030 補訂 4（観測区間の規則と先読みの範囲を上書きする）
- 依存する検査・スクリプト・テストを揃える（`check_prereg_parity.py`・`p1_run_grid.py`・`run-features-all-poles.sh`・`p1_restart_default_config.rs`・replay.rs のテストほか）
- 実記録（試験用 ID の P998・G-GEAR の手元・repo 外）で、前処理後の観測区間が 12:38 付近で切れることを確かめる
- O1 事前登録の草案（`.steering/20261007-o1-preregistration-draft/`）に、この前処理への参照を足す（PR #329 の merge 後）

### 含まないもの

- アプリ側の直し（復帰時の生存の監視・「記録されていない」の表示・電源の知らせの行）。別 issue にする（研究者裁定 2026-10-08）。O1 は v0.1.40 のまま走らせる。
- Windows のバッテリーでの長いスリープ・蓋閉じ・複数回、macOS の複数回の追加の確かめ
- HMM・`features.rs`・`engine.rs` の変更（`HMM_VERSION` は bump しない）

## 受け入れ条件

- [ ] 前処理の純関数のテストが緑（穴の長さの境界・上限・入力の種類・ファイルの最後・短い穴をまたぐ無入力・入力が無い区間）
- [ ] `gse-replay --features` の封筒 `config` に 2 キーの値が出て、`--set` で上限を 0 にすると前処理なしの実行と同じ観測区間になる
- [ ] `python scripts/check_prereg_parity.py` と `--self-test` が緑
- [ ] `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が緑
- [ ] P1 の Python 側のテスト（`scripts/tests/`）が緑
- [ ] 実記録で、前処理後の 1 本目の観測区間の右端が 12:38:09 付近（最後の打鍵）になり、`warmup_count=10` の実行で寝ている間の onset が消える
- [ ] code-reviewer ∥ security-checker と /cross-review を通す

## 関連ドキュメント

- issue #330
- `.steering/20261008-windows-sleep-test/result.md`（PR #329）
- `docs/preregistration-p1-episode.md`・`src-tauri/prereg/p1-episode.json`
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` D8 (b-2)・補訂 1 項目 1・5

## 運用メモ

- /reimagine 適用: No
- 理由: 規則の形・入れる場所・主と感度の位置づけは研究者が裁定済み（`decisions.md` 判断 1〜5）。実装の形は既存の `--set` と凍結 JSON の仕組みに載せるだけで、複数の構造案を比べる余地が小さい。
