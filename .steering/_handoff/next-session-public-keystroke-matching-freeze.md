# 次のセッション: 公開データでの照合の論文 —— 事前登録の凍結と、取得の前のコード

作成 2026-10-12（`.steering/20261012-public-keystroke-matching-prereg/` 判断 6〜15・attack-me round 1）。

## このセッションのゴール

`experiments/20261012-public-keystroke-matching/preregistration.md`（下書き）を、attack-me の指摘への対応（研究者が採否を決めたもの）を入れて凍結できる状態にし、研究者が凍結を決めたら凍結する。凍結の後、データを使わない部分（合成の記録で公開の他の列から長さが戻らないかの検査 `scripts/synthetic_logs.py`）のコードを書く。データの取得と本計算はしない（取得の開始条件を満たしてから）。

## 背景（これだけ読めば始められる）

- 研究者の判断: `.steering/20261012-public-keystroke-matching-judgement/decisions.md`（判断 1〜5）と `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜15）。要点:
  - 研究者は研究機関に所属しない（判断 7）。取得の開始条件: KLiCKe = 著者の返事を見て研究者が進めると決めた（問い合わせは送付済み・返事待ち）／ ENJA15 = ライセンスの種類と利用条件を一次で確かめた／ KeyTAR の公開モデル = 研究者が 15 GB の取得を認めた。
  - 公開の形は R0〜R7（判断 8・置換・並べ替え・抑制は [V275] の名前を借りた当方の定義）。攻撃者は A1〜A4（判断 10 で KeyTAR の公開モデルを足した）。有用性を副次で測る（判断 11）。合否は判定せず、主な表を固定する（判断 13）。取得の後・本計算の前の検査を許す（判断 14）。研究者本人の記録は使わない（判断 6）。
- 再検索の結果: `docs/literature/20261012-public-keystroke-matching-prereg-search.md`（同じ研究は 0 件のまま・近い先例 [V275]）。
- attack-me round 1 の記録: `.steering/20261012-public-keystroke-matching-prereg/attack-me/prereg-public-matching/round-1/`（`verdict.md` に裏取りの判定・直す順・研究者の採否）。

## やること

1. `verdict.md` の「研究者に問うこと」のうち未回答のものを AskUserQuestion で問う（推奨と理由を添える）。採った指摘を事前登録に入れる。
2. 直しが major 以上なら attack-me の round 2（同じ立場・同じ接地の文献・引き継ぎを役ごとに書く・再掲を求めない）。`tmp/sources/` は round 1 の dir にある（無ければ `panel.md` の URL と SHA-256 から取り直す）。
3. 研究者が凍結を決めたら、事前登録の冒頭の状態の行を「凍結: <日時>・コミット <sha>」に書き換えてコミットする。
4. 凍結の後、`scripts/synthetic_logs.py`（人のデータを使わない合成の記録で、各公開の形の出す列から区間の長さが戻るかを確かめる）と自己検査を書く。結果は `notes.md` に書く。
5. PoPETs のオンライン発表や録画の提出の要否を、採録論文の案内か PC chairs への問い合わせで確かめる（問い合わせは研究者が送る）。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。★・⚠️ を多用しない。
- docs を先に読む。必須 Skill（`reproducibility-discipline`・`citation-ssot`・`verify-before-claiming`・`subagent-delegation`・`attack-me`）を参照してから手を動かす。
- データ（KLiCKe・ENJA15・KeyTAR）を取得しない（開始条件を満たし、研究者が決めるまで）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex に渡すのはコードと文書の差分だけ。
- 有料の DB と有料の本文は使わない。
- `git add -A` や `git add <dir>` を使わず、ファイルを明示してステージする。並行セッションがあるので git worktree で作業する。
- 完了時は `/cross-review` を 2 巡し、commit → push → PR → CI → merge → main の CI を確かめる。Codex の予算は、回す前に origin/main の台帳も見る。
