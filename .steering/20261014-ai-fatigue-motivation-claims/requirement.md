# AI 疲労と動機の主張（`.idea` の核 1・2）を別の研究として扱えるかの議論とサーヴェイ

## 背景

- `.idea/20261005-motivation-fatigue-reentry-surface.md`（版管理外）の核のうち、次の 2 つを GSE の外の別の研究として扱う方向にした（研究者・2026-10-14）。
  1. 構成: AI 疲労と呼ばれているものの中身の少なからぬ部分は、動機（投資を続ける意思）の低下である。
  2. 人: AI 疲労とデジタル疲労が両方高い人がいる（画面越しの作業に共通する 1 つの疲労の 2 つの呼び名かもしれない）。
- 確かめる道具は文献の項目の分析と質問紙で、打鍵の観測は要らない。GSE の中で質問紙を足すと ADR・`data-privacy`・O1 の同意文書の変更になり、実行中の O1 には入れられない。
- S-MR（2026-10-05・`docs/literature/20261005-motivation-fatigue-reentry-surface.md`）は網が粗かった（各 angle 2.5〜3.6 分）。
- 引き継ぎ: `.steering/_handoff/next-session-ai-fatigue-motivation-claims.md`（ブランチ `docs/handoff-tangibility-ai-fatigue`）。

## ゴール

1・2 の主張と研究のコンセプトについて、(a) 空白か、(b) 研究としての価値があるか、(c) 論文として出せるか、を議論とサーヴェイ（`/literature-review` 1 ラウンド）で確かめ、表にまとめる。研究にするか・論文にできるかは研究者が決める（決定は `decisions.md`）。

## スコープ

### 含むもの
- 下位の問い SQ1（動機の成分）・SQ2（弁別）・SQ3（出せる形: 公開データ・尺度の使用許諾・投稿先と倫理審査の要件）のサーヴェイ（6 angle）
- カード・`docs/references.md` への append-only 登録・`_index.md` の 1 行
- 「空白か・価値・出せる形と投稿先・倫理・GSE との関係・C との重なり」の表

### 含まないもの
- 研究にするか・論文にするかの決定（研究者が決める）
- C（AI 疲労 DB の測定論の論文・DB の研究者と共同で進めると決まっている）との分け方の決定（DB の研究者とユーザーが決める。本タスクは重なる所を記録するだけ）
- DB の判定・34 件の写し・追加候補の表を材料に使うこと。結果を DB に渡す 3 点に混ぜること
- AI 疲労を GSE が検出・診断する、HMM の状態や打鍵からの推定の対象に足すこと
- 尺度の短縮・改変・質問紙の実施・コード変更

## 受け入れ条件

- [x] カード `docs/literature/20261014-*.md` があり、下位の問いごとに温度（確定 / PLAUSIBLE BUT UNPROVEN / 判定不能）が付いている
- [x] 反証 angle を含め、否決リストがある
- [x] `python3 scripts/check_citations.py` が `=== 違反なし ===`
- [x] まとめの表（空白か・価値・出せる形・投稿先・倫理・GSE との関係・C との重なり）が `summary.md` にある
- [x] 研究者の決定（または「決定待ち」）が `decisions.md` にある

## 関連ドキュメント

- 引き継ぎ §6 の一次資料一覧
- `docs/literature/20261005-motivation-fatigue-reentry-surface.md`（S-MR）

## 運用メモ
- /reimagine 適用: No
- 理由: 実装・設計判断ではなくサーヴェイと議論のタスク
