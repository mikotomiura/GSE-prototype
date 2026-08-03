# タスクリスト

## 事前調査
- [x] `ADR-006`（Decision / 下位決定 #2/#3 / Migration）を読む
- [x] `personalization-and-online-learning.md` §11-11 / §4.4 / §5.2 / §3.1-3.4 / §8.2 / §9 / §11 を読む
- [x] `experiments/20260802-within-person-scope-detector/notes.md` §2/§4/§5 を読む
- [x] `domain-adapter-boundary.md`（未較正 head の原則・Adapter A/B/C）を読む
- [x] コード側の事実確認（`self_marker` の Stuck 固定 / `f3` / `App.tsx` の argumentative ロック / `TaskKindDto`）

## T-C 較正プロトコル（先行）
- [x] Phase1 の失敗の構造を言語化（宣言が観測でなく設定）
- [x] セッション内 block 設計（within-person のレバレッジ問題を解く根拠つき）
- [x] out-of-scope 正例の作り方と**その限界**（demand characteristics・上界としか読まない）
- [x] ラベルの 3 供給層（S 構造化 / N 自然 / R 自己申告）と各層の可否
- [x] `self_marker` 再利用禁止（コード根拠つき）
- [x] 除外基準にタスク内容を含める（block 単位・研究者判断・検出器出力は使わない）
- [x] 各 head の baseline 獲得計画（未決 3 を閉じる: Writing のみ較正）
- [x] G1 との統合方針（相乗り推奨・要因を掛け合わせない）

## T-A 統合設計
- [x] out-of-scope = フラグ（head にしない）＋ 却下案の根拠
- [x] head 相対の定義（routing 誤りへの fallback になる）
- [x] 宣言 vs 観測の衝突規則（re-route しない）＋ 昇格ゲート
- [x] 時間解像度（streaming 推定 / Decision Episode 読み出し / 検証は block）
- [x] 「新機構を作らない」制約を allow-list ＋ 禁止リストで固定
- [x] `phase` の暫定決定（§11-1 未解決 1）

## T-B 検出器の構造
- [x] 構造式（3 項 ＋ floor ＋ 縮約）と凍結する 5 つのコミットメント
- [x] 既知 4 例の当てはめ（★ retrodiction であることを明記）
- [x] 到達不能性（`unreachable`）の出力と報告要件
- [x] `scope_fit` → `evidence_quality` の写像（hard mute 禁止・ヒステリシス）
- [x] 定数の推定手続き（in-scope 側だけ ／ 禁止事項 ／ 報告要件）
- [x] オフライン消費（recovery model の感度解析）

## 文書化・整合
- [x] `docs/architecture/task-adaptation-and-scope-gating.md` 作成
- [x] `docs/adr/ADR-010-task-scope-gating.md` 作成
- [x] `docs/adr/README.md` に ADR-010 を追加
- [x] `ADR-006` に「拡張であって改訂ではない」注記（Decision 本文は無改変）
- [x] `§11-11` / `§11-1` にポインタと暫定案
- [x] `domain-adapter-boundary.md` Layer 3-4 に scope 経路の注記
- [x] `.steering/` 記録（requirement / design / decisions / tasklist）

## 検証
- [x] コード変更ゼロ（`git status` で `src/` `src-tauri/` に差分なし）
- [x] 凍結対象に触れていない
- [x] `research-positioning.md §5` 未変更
- [x] ~~`docs/references.md` 未変更~~ → ★ **追加ラウンド（下記）で [P36]–[P42] / [V66]–[V74] を append-only 登録した**
      （設計フェーズ単体では未変更だった。renumber・削除はしていない）
- [x] PII・セッション日時・raw NDJSON なし
- [ ] `/cross-review`（**skip**・理由は `decisions.md` 判断 12）
- [ ] 研究者判断待ち: G1 相乗り / `phase` 暫定案 / 正例の 2 種類目

## 追加ラウンド: 文献接地（`/literature-review`・2026-08-02）
- [x] RQ 分解（RQ1 較正 3 下位 / RQ2 検出 4 下位・反証 angle 2 本を含む）
- [x] 多角探索 16 ソース取得
- [x] claim 抽出 12 → 敵対的 3 票検証（confirmed 11 / 否決 4・うち 2-1 が 1）
- [x] カード生成 `docs/literature/20260802-scope-detection-and-conformal-calibration.md`（10 カード）
- [x] `docs/references.md` へ append-only 登録（[P36]–[P42] / [V66]–[V74]・renumber なし）
- [x] `docs/literature/_index.md` に 1 行追記
- [x] 設計本体 §0/§2.4/§3.1/§4.1/§4.2/§4.5/§5 と ADR-010 D1/D5 へ inline 還元
- [x] `research-positioning §3`（ランドスケープ 3 項追加）/ `§4`（★ 新規性の縮小）へ還元・**§5 は未変更**
- [x] 全 inline [n] が references.md に実在することを機械確認
- [ ] 次ラウンド: 一次全文確認（[V66] の α 下限・[V68] の適用範囲）/ Chow 原論文 / [P39][P40] 本文 / SE の IDE テレメトリ系
