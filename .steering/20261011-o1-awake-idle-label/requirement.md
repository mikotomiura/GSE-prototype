# o1-awake-idle-label — 起きたまま入力の無い区間の feat 行を P1 の観測区間から外す

## 背景

O1 のアプリは宣言したタスクのラベルを自分では外さない（`src-tauri/src/lib.rs` の `O1Declaration::KeepCurrent`）。PC が起きていれば、席を外していても宣言ラベル付きの `feat` 行が 1 秒ごとに続く。

既存の前処理 idle trim（事前宣言 v1.2 §6・issue #330・`.steering/20261008-p1-sleep-trim/`）が落とすのは、`feat` 行の 60 秒以上の穴の直前とファイルの最後だけで、行が途切れない「起きたままの放置」は拾わない。

研究者の実走（Surface・v0.1.40・2026-10-09 14:20 JST から）の閉じた 2 ファイルを数えた（集計値だけ・`verification.md`）:

- 24 時間のファイルで `feat` 行の穴（60 秒以上）は 0 個。PC は一度も寝ていない。既存の idle trim はファイルの末尾以外を落とさない。
- 入力（`key` 行と `pointer_bin` 行）が 30 分以上途切れた区間が、`feat` 行のある時間の 69%（24 時間ファイル）を占める。夜の 9.5 時間の無入力も、宣言ラベル付きの観測区間として残る。

## ゴール

起きたまま入力の無い区間の扱いを、研究者のメモ（作業していなかった時間）と実走データを突き合わせて研究者が決め、`gse-replay --features` の前処理（idle trim と同じ場所）に足す。

研究者が決めること（handoff の 1〜3。Claude は決めない）:

1. 「作業していない」とみなす無入力の長さの閾値（と、無入力の最初をどれだけ残すか）
2. 区間を落とすのか、ラベルだけ無効にするのか
3. 事前宣言 p1-episode（v1.2・凍結）の改訂か逸脱の記録か。前処理なしと並べて報告するか

## スコープ

### 含むもの

- 実走データ（閉じたファイル）での無入力区間の分布と、研究者のメモとの突き合わせ（repo の外で集計し、集計値だけを `verification.md` に書く）
- 閾値の候補ごとの「落とす量」と「メモとの一致（取りこぼし・削りすぎ）」の表
- 研究者の裁定の後: 前処理の純関数とテスト・`gse-replay --features` への配線・凍結 JSON・事前宣言の改訂（または逸脱の記録）・ADR-030 の補訂・用語集

### 含まないもの

- アプリ側の直し（ラベルを自動で外す・電源の知らせの行）。O1 は v0.1.40 のまま
- O1 の送信の知らせ（被験者に出ない）と、`keyboard hook may be dead` の繰り返し（handoff の「別件」。扱いは研究者が決める）
- HMM・`features.rs`・`engine.rs`（`HMM_VERSION` は bump しない）

## 受け入れ条件

- [ ] 閉じた実走ファイルの名前と SHA-256、無入力の分布、候補ごとの表が `verification.md` にある（NDJSON は repo に入れない・外部 LLM に渡さない）
- [ ] 研究者の裁定 1〜3 が `decisions.md` にある
- [ ] （裁定の後）前処理のテストが緑・`cargo test --manifest-path src-tauri/Cargo.toml --workspace` 緑・`check_prereg_parity.py` と `--self-test` 緑・P1 の Python テスト緑
- [ ] （裁定の後）実走ファイルで、前処理後の観測区間がメモの「離席」区間を外し、「入力なしだが作業中」の区間をどれだけ残すかを表で示す
- [ ] code-reviewer ∥ security-checker と /cross-review

## 関連ドキュメント

- `.steering/20261011-o1-awake-idle-label/handoff.md`
- `.steering/20261008-p1-sleep-trim/`（requirement / design / decisions / verification）
- `docs/preregistration-p1-episode.md` §6
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` 補訂 4
- `docs/glossary.md`「無入力の末尾の前処理」

## 運用メモ

- /reimagine 適用: No
- 理由: 規則の形（閾値・丸ごと落とす・入力の定義・事前宣言の改訂）は研究者が裁定した（判断 3〜6）。実装は v1.2 の idle trim と同じ場所・同じ仕組み（凍結 JSON・`--set`・封筒）に載せるだけで、比べる構造案の余地が小さい。
