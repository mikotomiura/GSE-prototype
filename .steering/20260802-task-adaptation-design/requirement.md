# Phase2 以降のタスク適応（head 選択 × out-of-scope）の設計

## 背景

`ADR-006` は `task_kind` → **どの head を走らせるか**を決めたが、
**「どの head も当てはまらない」状態を定義していない**（`personalization-and-online-learning.md §11-11` の起票）。
現行コードの切替は `ime_open` の 2 値のみで、対象外の作業は**誤った head で黙って処理される**。
`progress_proxy` は対象外作業（写経・タイピング練習）で**最大化する**ため、
「Need が高い」のではなく「**Need の計算そのものが無意味**」な区間が正常値として扱われる。

直前ラウンド（`experiments/20260802-within-person-scope-detector/`）で
**個人基準単独の検出器は動かない**ことが実測され、処方箋が **連言**（個人内逸脱 AND 絶対ゲート）に変わった。
その帰結を ADR-006 のタスク適応設計へ統合するのが本タスクである。

## ゴール

**構造のレベルで閉じる**（コード変更ゼロ・設計文書のみ）:

- **T-A**: out-of-scope を含むタスク適応の統合設計（head なのかフラグなのか／宣言と観測の衝突／時間解像度）
- **T-B**: 検出器の**構造**の凍結（**定数は凍結しない**——「どう推定するか」の手続きを書く）
- **T-C**: Phase2 較正プロトコル（**正解ラベルの供給源**）＋ 各 head の baseline 獲得計画

推奨順序 **T-C → T-A → T-B**（検出器を先に詰めると「検証できる観測が設計されていない」穴に落ちる）。

## スコープ

### 含むもの
- 設計文書 1 本（`docs/architecture/task-adaptation-and-scope-gating.md`）と ADR 1 本（ADR-010）
- 既存文書からのポインタ更新（ADR README / ADR-006 の「拡張」注記 / §11-11 / §11-1 / adapter-boundary）
- `phase` の定義（`§11-1` 未解決 1）の**暫定案**（研究者判断待ち）

### 含まないもの
- **コード変更**（凍結対象を含め一切触れない）
- 定数の値（floor 倍率・絶対ゲート閾値・縮約強度・最小 n）
- 実験の実行・再解析（別トラック: `_handoff/next-session-prompt-task-scope-ground-truth.md`）
- 文献の新規引用（`docs/references.md` に追記なし。マスキング等は**出典未確認**のまま）

## 受け入れ条件

- [x] ADR-006 を**改訂ではなく拡張**として扱い、その関係を明記した
- [x] out-of-scope が head かフラグかを決め、**「新機構を作らない」性質を壊していない**
- [x] 宣言（②）と観測（③）が食い違ったときの規則を決めた
- [x] 判定の時間解像度を決め、`§3.1` Decision Episode と整合させた
- [x] 検出器の構造を凍結し、**定数は値を書かず推定手続きだけを書いた**
- [x] Phase2 較正プロトコル（正例の作り方・除外基準・各 head の baseline 獲得）を書いた
- [x] Phase1 の失敗（宣言が観測でなく設定だった）を繰り返さない設計になっている
- [x] 過大主張していない（「フラグされないこと ≠ 対象作業だったこと」を維持）
- [x] PII・セッション日時を出力していない／raw NDJSON を扱っていない

## 関連ドキュメント

- `docs/adr/ADR-006-task-kind-beta-wiring.md`（Decision ＋ 下位決定 #2/#3 ＋ Migration）
- `docs/architecture/personalization-and-online-learning.md` §11-11 / §4.4 / §5.2 / §8.2
- `docs/architecture/domain-adapter-boundary.md`（未較正 head では強介入を出さない）
- `experiments/20260802-task-scope-detector/` / `experiments/20260802-within-person-scope-detector/`
