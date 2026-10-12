# 打鍵のリズムで動く背景のステージ —— 合成の列での机上の検査

## 背景

研究者の提案「打鍵のリズムで滑らかに動く背景（ステージ）」は、親タスク `.steering/20261012-portrait-rhythm-motion/` で調査 1 ラウンド（S-RM）と議論を経て、EH3 の後に回す EH4 などの候補になった（同 decisions 判断 1）。最初の段は、合成の打鍵の列で、リアルタイムの写像（打鍵 → 毎フレームの描画のパラメータ）が停滞・打鍵の有無・速さをどれだけ写すかを測る机上の検査である（同 判断 4）。試作は作らない。

引き継ぎ: `.steering/_handoff/next-session-rhythm-stage-desk-check.md`。

## ゴール

1. 机上の検査の設計（`design.md`）を、合否の基準を含めて研究者と決め、どの結果よりも前にコミットして固定する。
2. 計器を `experiments/<YYYYMMDD>-rhythm-stage-desk-check/` に作り、本番を回して記録する（固定の後の段）。
3. 新規性を確かめる検索を `/literature-review` で 1 ラウンド回す（引き継ぎ §3.5）。

このセッションの範囲は、1 の設計の起こしと研究者の決定まで（2・3 の着手は決定しだい）。

## スコープ

### 含むもの
- 合成の打鍵の列（EH1 の生成器 world v2 を基に）だけを使う机上の検査の設計と計器。
- 写像の候補の比較（生の追従・強い平滑化・順序だけ・揺らぎ）と、止まっている間の振る舞い（据え置き・減衰・地へ戻る）。
- 時間の解像度: 秒ごとの集計と秒未満の両方（研究者・判断 3）。
- 新規性の検索 1 ラウンド（反証側を厚く）。

### 含まないもの
- 背景の変化での招待（研究者・判断 2。候補には残る・親タスク判断 5）。
- 試作（自分の PC で動かす）・`src-tauri/` の描画やデスクトップの層の窓の実装。
- 実在の人の打鍵・gse-dataset のログ。キーストロークの内容・NDJSON の生ログを外部の LLM（Codex を含む）に送ること。
- 作業中に注意を奪うか（`E-14`）・人が状態計として読むか・ゲーム化。机上では測れない。
- 肖6・親タスクの判断 5（壁紙の規則）の変更。`PS-Q8` を閉じること。
- EH3 のファイル（`wallpaper.rs`・EH3 の事前登録）に触れること。

## 受け入れ条件

- [ ] `design.md` に、写像の候補・入力・攻撃者の特徴・基準のモデル・合否の基準（項目 1 だけ）・記述の項目（2〜6）・自己検査が書かれ、研究者の決定が `decisions.md` にある
- [ ] `design.md` が、計器のどの結果（下見を含む）よりも前にコミットされている
- [ ] 本番の結果が `experiments/.../results/` と `notes.md` にあり、読み方が「検査した範囲で見つからなかった／見つかった」までに限られている
- [ ] 新規性の検索の結果が記録され、出典が `docs/references.md` に append-only で登録されている

## 関連ドキュメント

- `.steering/20261012-portrait-rhythm-motion/`（requirement・decisions 判断 1〜10・survey-results・idea-section12）
- `.steering/20261005-portrait-invitation-constraints/`（decisions 判断 5・8・12〜15・constraints-ledger T1・T2・肖6・肖14）
- `experiments/20261010-portrait-eh1-round5/` と `.steering/20261010-portrait-eh1-round2`〜`round5/design.md`（EH1 の型）
- `.steering/20261012-eh3-windows-device-rest/decisions.md` 判断 3（特徴量が据え置かれる間）
- `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 実装の設計ではなく検査の設計で、候補の比較は検査の中で行う（親タスク判断 2 と同じ扱い）。研究者が求めれば適用する。
