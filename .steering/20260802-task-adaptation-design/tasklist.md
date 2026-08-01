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
- [x] `research-positioning.md §5` 未変更 / `docs/references.md` 未変更
- [x] PII・セッション日時・raw NDJSON なし
- [ ] `/cross-review`（**skip**・理由は `decisions.md` 判断 12）
- [ ] 研究者判断待ち: G1 相乗り / `phase` 暫定案 / 正例の 2 種類目
