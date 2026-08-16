# タスクリスト — Step 5c（速度軸と AB-D10 の根治）

## Phase 1: 実装（A′）

- [x] `abxBlindStart`: 開始状態を 1 回だけ定義・`carrySeed` 削除
- [x] `abxBlindNext`: 準備区間を 1 相にし、状態を変える呼び出しを prep / i1 から全て外す
- [x] `abxBlindNext`: `i2` の状態を `bl.state` と `kind` から決め、`bl.state` を更新
- [x] `abxPrepSeconds`: 式は据え置き・comment を A′ の理由へ書き換え
- [x] `abxBlindFinish`: `protocol` を `3phase-noreset-v2` へ・`timing` に `from` / `to`
- [x] `step4.config.json` の `_prep_seconds_why` を A′ の経緯へ更新

## Phase 2: 検査

- [x] 既存 3 検査（AB-D2 / AB-D7 × 2）を A′ 用に置換・強化
- [x] 新規: `abxBlindNext` に状態リテラルと `abxSetInstant` が無い
- [x] 新規: `bl.state` が更新され、**条件分岐の中に無い**
- [x] 新規: 上下の均衡（★ 実装の式を取り出して 4 通り評価 ＋ 全通り列挙・両方の開始状態）
- [x] 新規: `protocol` が新しい値で、旧文字列が残っていない
- [x] meta 変異を追加し、**壊して赤くなることを実測**
- [x] `bash run.sh check` が exit 0（★ 静的 127 / meta 174 / 平滑器 51 / Step 3 30 / 混入 0）

## Phase 3: レビュー

- [x] `code-reviewer` + `security-checker` を並列起動
- [x] HIGH 2 件を反映（S5C-D3 画面の漏れ / S5C-D5 均衡検査が実装を見ていない）
- [x] MEDIUM 7 件を反映（S5C-D4 ほか・混入検査の走査範囲）
- [x] 再度 `run.sh check` が exit 0

## Phase 4: ブラウザ実地

- [x] キャッシュを疑う（`abxBlindNext.toString()` に新コードがあることを実測）
- [x] ★ AC-2 / AC-3 / AC-4 と AC-1 の構造面 → **node harness で実コードのまま 400 通り検証**
- [x] BL-1 の関門（★ 研究者の操作で解除）／着弾プローブで `btn-play` への着弾を実測
- [x] AC-1 の**音の側**: 準備区間で粒子率が定数（★ 737 サンプルで実測・8/8 トライアルで min=max）
- [x] `abx-now` が盲検中に伏せられていることの実地確認（★ 737 サンプル全部が伏せ字）

## Phase 5: 研究者の耳（★ ここからは私は測れない）

- [x] 条件をその場で実測して研究者に渡す（⚠️ **1 巡目は `c_texture` のまま走り無駄になった** → S5C-D6 で実装で塞いだ）
- [x] 遷移 0 秒 × 8 回 → **7/8**（ヒット 3/4・誤警報 0/4）
- [x] 遷移 5 秒 × 8 回 → **8/8**（4/4・0/4）
- [x] 遷移 20 秒 × 8 回 → **8/8**（4/4・0/4）
- [x] ★★★ 遷移 60 秒 × 8 回 → **7/8**（3/4・0/4）＝ **製品の速度で読める**
- [ ] ⚠️★★★ **B1: 層 0 = 1.0 で 10 分（★ 2026-08-14 も未実施＝研究者が音を聞ける環境に無いため・S5C-D9）**
      ★ 手順は組み立て済み（`P011` の smoothed CSV で離席を詰めて 18.4 分再生可能）

## Phase 6: 記録と完了

- [x] `notes.md` に【Step 5c】節（S5C-1〜S5C-5）
- [x] `decisions.md` に S5C-D1〜D5
- [x] 測定結果を `notes.md` へ（S5C-6 / S5C-7 / S5C-8 / S5C-9）
- [x] ★ `/cross-review`（2026-08-14 実施・Codex 正常完了 / skip なし。⚠️ **HIGH 1 件＝実セッション名の外部送信**・S5C-D8）
- [x] ★ HIGH の修正と実測（静的 129 / meta 178 / フィルタ試験 22・**旧フィルタが素通りしていたことも実測**）
- [ ] ⚠️ 残った MEDIUM/LOW 4 件（`window.__step4` / `abx-texture-ack` / `direction_balance` 突合 / `abx-now` 静的検査）
- [ ] ⚠️ `/finish-task`（**未実施**）
- [x] 次セッション用の引き継ぎ `.steering/_handoff/next-session-prompt-expression-theory-survey.md`
