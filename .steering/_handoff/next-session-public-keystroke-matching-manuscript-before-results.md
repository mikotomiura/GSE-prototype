# 次のセッション: 公開データでの照合の論文 —— 結果の前に残りの空欄を埋め、頁を縮める準備をする

作成 2026-10-20（判断 65 の後）。この機械は Mac。本計算は G-GEAR で進めていて、このセッションでは触らない（G-GEAR の作業は G-GEAR に任せる）。
投稿の目標は PoPETs 2027 Issue 3（締切 **2026-11-30 AoE**）。間に合わなければ Issue 4（2027-02-28）。結果は 11/9 ごろの見込み。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-before-results.md を読んで、照合の論文の結果の前にできる残り（検索の範囲・合意の段落・頁の見積もり）を進めて。
```

結果が出た後のセッションは、このメモの「結果が出たら」を読んで始める（その時点で別の引き継ぎを書いてもよい）。

## 今の状態（2026-10-20 時点）

- worktree: `/Users/johnd/GSE-wt-matching-manuscript`、ブランチ `docs/public-keystroke-matching-manuscript`（push 済み・PR は未作成）。最後のコミットは判断 65 の記録（`docs(steering): 照合の論文の残りの節を書いた記録と、予測の扱い（判断 65）`）。
- 原稿: `papers/keystroke-log-release-matching/manuscript/`。`main.tex`・`sections/*.tex`・`outline.md`（主張と根拠の対応表・Structure の表に各節の状態）・`references.bib`・`BUILD.md`・`build.sh`。
- ビルド: `bash build.sh <PoPETS-2027-latex-template の dir> <出力の dir>`。テンプレートは repo に置かない（取得先と SHA-256 は `BUILD.md`）。前のセッションの展開先は scratchpad で、新しいセッションでは無いので取り直す（`curl -sSLO https://petsymposium.org/files/submission-template-2027.zip` → SHA-256 を照合 → unzip）。2026-10-20 の時点でエラー 0・未定義の参照 0・未定義の引用 0・overfull 3（小さいもの）。
- 文体の門: `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py --root . papers/keystroke-log-release-matching`（違反 0 を保つ）。⚠️ 地の文に日本語の文字を書くと門と pdfLaTeX の両方で落ちる（句読点は U+3001 などの符号で書いた）。
- 判断の記録: `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜65）。作業記録: `.steering/20261020-public-keystroke-matching-manuscript/`（`tasklist.md` を更新済み）。

### 節ごとの状態

| 節 | ファイル | 状態 |
|---|---|---|
| §1 序論 | `introduction.tex` | 骨組み。動機の 2 段落は下書き、方法・害・貢献の段落は `[...]` の計画 |
| §2 関連研究 | `related.tex` | 骨組み。"To our knowledge" の検索の語が空欄 |
| §3 脅威モデル | `threat-model.tex` | 草稿（attack-me round 1・2 で閉じた） |
| §4 データと公開の形 | `data.tex` | 草稿。除外の後の件数が `[n after exclusion]`（KLiCKe・ENJA15 とも。取得後の検査では除外 0 だった・コメントに書いた） |
| §5 攻撃者 | `attackers.tex` | 草稿 |
| §6 評価の手順 | `protocol.tex` | 草稿。逸脱の一覧は「At the time of writing」で 2 つ（D1 エスケープ・D2 列の削除）。予測は §6 末尾で触れ §7 で並べる（判断 65） |
| §7 結果・§9 結論 | | 結果の後 |
| §8 考察 | `discussion.tex` | 限界は下書き済み。合意の段落は出典待ち、持ち帰りは結果の後 |
| 倫理・Open science・AI use | 各 `.tex` | 草稿。倫理の公開元への連絡と、Open science の匿名リンクが空欄 |

## やること（結果の前・この順）

1. **§2 の検索の範囲**: 登録の前のサーヴェイ（`docs/literature/20261012-public-keystroke-matching-novelty.md`・`20261012-public-keystroke-matching-prereg-search.md`）に検索の語が残っていない。今は情報源と日付（10/12・13・OpenAlex の被引用の追跡と著者別・Hanisch の調査の全文・Google Scholar と Semantic Scholar は使っていない）だけを `[...]` に書いた。研究者に AskUserQuestion で問う。案: (a) 情報源と日付だけで書く（推奨の候補: 語を後から作ると記録と違う文になる）、(b) 投稿の前に同じ範囲で検索をやり直し、語と日付を記録して書く。
2. **§8 の合意の段落**: 「再識別や隠した本文の復元を禁じる利用条件」の段落の下書きがある。KLiCKe の条件は「出典を示せば自由」で禁止の条項が無い（[V273]）ところまでは書いた。Kaggle の規則（第 7 条など）と、教育データで使われる合意の実例を一次で確かめてから埋める。確かめられない主張は書かない。
3. **頁の見積もりと縮め方の案**: 結果の節が空で本文が約 11 頁（序論 p1 〜 結論 p11）。表 2 つと図 1 つを足すと 12 頁を超える。結果を見る前に、付録へ移せる方法の細部の候補（§5 の窓の段落・ENJA15 の区間と攻撃者・§6 の窓の規則・探索的な分析の手順・有用性の近似の規則など）を挙げ、研究者に移す順を問う。⚠️ PoPETs の付録は査読者が読まなくてよいので、結論に要るものは本文に残す（`outline.md` の Venue requirements）。移すのは結果の後でもよいが、案は今のうちに。
4. 各変更のあとビルドと文体の門を通し、`outline.md` の Structure の表と `tasklist.md` を更新して、節ごとにコミット・push する。

## 結果が出たら（11/9 ごろ・G-GEAR の出力を Mac に持ってきてから）

- §7 結果（ENJA15 の短い小節を含む・判断 61 の 4）、予測を結果と並べる（判断 65）、§9 結論、§1 の貢献と方法・害の段落、抄録、題名の最終形（題名は結果を見る前に決める予定だったので、結果の前に研究者に確かめる）。
- 空欄を埋める: 除外の後の件数（§4）、逸脱の一覧（§6・`notes.md` の「逸脱」に D3 以降があれば足す）、倫理の公開元への連絡の日付、Open science の匿名リンク。
- 頁を 12 に縮める（上の 3 の案）。
- 投稿前の attack-me（stage: manuscript）。round 1 の接地の本文 `attack-me/outline-threat-model/round-1/tmp/` はそのあと消す。`/cross-review`。

## 研究者の側で進んでいること（このセッションでは送らない）

- PoPETs の PC chairs への催促は 10/27 ごろ（`reply-drafts-20261013.md` の 3）。
- Dr. Tian へのメール（`reply-drafts-20261013.md` の 4・CC に Crossley・件名は前のスレッドへの返信）は草稿が完成したとき。The Learning Agency Lab への短い連絡の下書きは結果の後・投稿の前（判断 61・64）。
- Hanisch の出版版での照合（ACM の PDF はボットに閉じているので研究者に頼む）。§2 と §3 は arXiv 版の文で引いている。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。絵文字・★・⚠️ を多用しない。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- 結果（G-GEAR の本計算の出力）を、「結果が出たら」の段に入るまで見ない・書かない。脅威モデルと方法は凍結した事前登録から変えない（変更は `notes.md` の「逸脱」）。手順を言い換えて意味を変えない。
- 引用は `citation-ssot`（[Pn]/[Vn]・append-only）。[V299]–[V325] は別の枝 `docs/ai-fatigue-core2-discriminant` が使っているので避ける（今は [V326]・[V327] まで使った）。`references.bib` に足す書誌は Crossref か arXiv で確かめ、note に日付を書く。公開する原稿には内部の番号・GSE への言及を書かない（`papers/README.md`）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 並行セッションがあるので worktree で作業し、コミット前に `git branch --show-current` を確かめる。`.steering` と原稿の変更は push だけ（PR は研究者に確かめてから）。`git add -A` を使わない。
