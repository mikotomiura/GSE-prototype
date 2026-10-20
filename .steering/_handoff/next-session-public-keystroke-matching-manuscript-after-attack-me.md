# 次のセッション（Mac）: 照合の論文 —— attack-me round 1 の後、結果を待つ間と結果が出た後

作成 2026-10-21（判断 66〜70 の後）。この機械は Mac。本計算と探索的な分析 3〜5 は G-GEAR（引き継ぎ `next-session-public-keystroke-matching-exploratory-3-5-ggear.md`）。G-GEAR の作業はこのセッションでしない。

## 新しいセッションで最初に打ち込む文

結果が出る前:
```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-after-attack-me.md を読んで、照合の論文の結果の前の残り（ethics.tex の空欄）を進めて。
```
結果が出た後（G-GEAR の集計の JSON を Mac に持ってきてから）:
```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-after-attack-me.md を読んで、照合の論文の「結果が出たら」を進めて。
```

## 今の状態（2026-10-21）

- worktree `/Users/johnd/GSE-wt-matching-manuscript`・ブランチ `docs/public-keystroke-matching-manuscript`（push 済み・PR は未作成）。
- 題名は決めた（判断 69）: "Hiding the Text, Keeping the Process: Matching Processed Keystroke Logs to Texts Held by Others"。
- attack-me（manuscript・round 1・Codex 付き）は済み。判定 major、指摘は全部直した（判断 68・`.steering/20261020-public-keystroke-matching-manuscript/attack-me/manuscript-matching/round-1/verdict.md` の 7）。
- 害 (a) は「本文を持つ者による結び付き」に定義し直した。掲げられた目標の読みは著者の解釈と明記。
- 探索的な分析は 5 つ（1・2 は 10/13、3〜5 は 10/21 に手順を固定・notes.md）。§6.7 に記述。3〜5 の値は G-GEAR から。
- 頁: 本文 1〜12 頁（結論が 12 頁の上）。縮め方の (1) は済み。残りの (2)〜(5) は結果の後（outline.md の Page budget）。
- ビルド: エラー 0・未定義 0・overfull 2。文体の門 違反 0。テンプレートは scratchpad に取り直す（BUILD.md・SHA-256 を照合）。

## 結果の前に残っているもの

1. **ethics.tex の空欄 2 つ（研究者が書く）**: (a) 所属に頼らない外部の審査を受けなかった理由（案「費用を払えなかった」に確かめる印）、(b) 利害の表明（打鍵を記録するソフトを作っていること・打鍵の記録の公開の計画が当たるか。投稿版では著者を絞り込む書き方を避ける）。研究者が文を決めたら入れる。
2. **送る下書き（送るのは研究者）**: `.steering/20261012-public-keystroke-matching-prereg/reply-drafts-20261013.md`
   - 3: PC chairs への催促（10/27 ごろ）
   - 4: Dr. Tian（CC Crossley）へ草稿（結果と考察を入れた草稿ができたとき）
   - 5: The Learning Agency Lab への通知（**結果が出たらすぐ**・投稿まで約 2 週の猶予・宛先の連絡先は未確認で研究者が一次で確かめる・4 を先に送り Crossley の答えは 3 日ほどまで待つ）
3. Hanisch の出版版での照合（研究者・ACM の PDF）。

## 結果が出たら（11/9 ごろ）

- §7 結果（ENJA15 の短い小節を含む）・予測を結果と並べる（判断 65）・§9 結論・§1 の方法・害・貢献の段落（計画の文は introduction.tex の角括弧）・抄録・§8.3 持ち帰り（区間は正答率だけ）。
- 探索的な分析 1〜5 の表（付録）。3〜5 は G-GEAR の `results/exploratory_{tail,margin,score_band}.json`。§6.7 の LaTeX のコメント（結果を開く前に手順を固定したかの確認）を、G-GEAR の記録で確かめてから消す。
- 空欄: 除外の後の件数（§4）・逸脱の一覧（§6・notes.md の D3 以降）・公開元への通知の日付と応答（ethics.tex・下書き 5 を送った後）・Open science の匿名リンク。
- 頁を 12 に縮める（outline.md の Page budget の (2)〜(5)。A3 の細部と有用性の表は本文に残す）。
- 投稿前の attack-me round 2（同じ dir・stage manuscript のまま・round 1 の引き継ぎを役ごとに渡す・Codex も同じ形）。そのあと接地の本文の tmp（`outline-threat-model/round-1/tmp/` と `manuscript-matching/round-1/tmp/`）を消す。`/cross-review`。

## 守ること

- 応答は日本語。絵文字・★・⚠️ を多用しない。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- 結果を「結果が出たら」の段に入るまで見ない・書かない。脅威モデルと方法は凍結した事前登録から変えない（変更は notes.md の「逸脱」）。
- 引用は citation-ssot（[V299]–[V325] は別の枝が使う。今は [V329] まで使った）。公開する原稿に内部の番号・GSE を書かない。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- worktree で作業し、コミット前に `git branch --show-current`。push だけ（PR は研究者に確かめてから）。`git add -A` を使わない。
