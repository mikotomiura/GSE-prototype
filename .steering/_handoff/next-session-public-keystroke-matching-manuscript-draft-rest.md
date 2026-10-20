# 次のセッション: 公開データでの照合の論文 —— 結果に依存しない残りの節を書く

作成 2026-10-20（判断 63 の後）。この機械は Mac。本計算は G-GEAR で進めていて、このセッションでは触らない（G-GEAR の作業は G-GEAR に任せる）。
投稿の目標は PoPETs 2027 Issue 3（締切 **2026-11-30 AoE**）。間に合わなければ Issue 4（2027-02-28）。結果は 11/9 ごろの見込み。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-draft-rest.md を読んで、照合の論文の結果に依存しない残りの節（攻撃者・評価の手順・データから）を書いて。
```

## 方針（研究者と 2026-10-20 に決めた）

- 結果を待たずに書ける節は、今のうちに書いておく。理由: 結果が出てからの 3 週間に、結果・考察・投稿前の attack-me・公開元への連絡が重なる。方法を結果より先に書けば、結果に引きずられた書き方にならない。
- **§5・§6・§4 はしっかり書く**。事前登録が凍結済みで、英語の論文の文に直すだけなので。
- **§2・§1・§8 は骨組みと段落の下書きにとどめる**。結果を見て強調の置き方が変わりうるので、磨き込みは結果の後にする。

## 今の状態（2026-10-20 時点）

- worktree: `/Users/johnd/GSE-wt-matching-manuscript`、ブランチ `docs/public-keystroke-matching-manuscript`（push 済み・PR は未作成）。最後のコミットは 94f89786 と、この引き継ぎのコミット。
- 原稿: `papers/keystroke-log-release-matching/manuscript/`（判断 60）。`main.tex`・`sections/*.tex`・`outline.md`（主張と根拠の対応表）・`references.bib`・`BUILD.md`・`build.sh`。
- ビルド: `bash build.sh <PoPETS-2027-latex-template の dir> <出力の dir>`。テンプレートは repo に置かない（取得先と SHA-256 は `BUILD.md`）。前のセッションの展開先は scratchpad で、新しいセッションでは無いので取り直す。
- 文体の門: `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py --root . papers/keystroke-log-release-matching`（違反 0 を保つ）。
- 判断の記録: `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜63）。作業記録: `.steering/20261020-public-keystroke-matching-manuscript/`。

### 節ごとの状態

| 節 | ファイル | 状態 |
|---|---|---|
| §3 脅威モデル | `threat-model.tex` | 草稿。attack-me（stage: outline）round 1・2 を経て直した（判断 61・62）。閉じてある |
| 倫理 | `ethics.tex` | 草稿。公開元への連絡の段落は `[To be completed ...]`（結果の後） |
| Open science | `open-science.tex` | 草稿。匿名の複製のリンクは `[anonymous link to be added]` |
| AI use | `ai-use.tex` | 草稿 |
| §1・§2・§4・§5・§6・§8 | 各 `.tex` | "To be written." |
| §7 結果・§9 結論 | | 結果の後 |

⚠️ `outline.md` の Structure の表は Open science を "Not written" のままにしている。直す。

## やること（この順）

1. **§5 攻撃者**（`attackers.tex`）: 事前登録 `experiments/20261012-public-keystroke-matching/preregistration.en.md` の Attackers・Attackers on windows・Alignment から。KeyTAR は脅威モデルの外の参照として書く（§3.4 と合わせる）。
2. **§6 評価の手順**（`protocol.tex`）: Release forms・Check on synthetic logs・Segments・Candidates, scope and numbers・Reported quantities・Utility・Summary table and figure・Diagnostics から。加えて:
   - 探索的な分析 2 つ（判断 55・56）を「事前登録に無い探索的な分析」と明記する。
   - `config.json` の SHA-256 が登録時の値（54158b3b…）と今の値（afc73eec…）で違う理由を書く。取得の記録を埋めたためで、逸脱ではない（`notes.md` l.178）。
   - 予測（Predictions）は「結果の前に書いた・外れても結論は変えない」として触れるかを決める（触れるなら §6 か §7 の冒頭）。
3. **§4 データと公開の形**（`data.tex`）: Data（KLiCKe・ENJA15・KeyTAR）・Checks after acquisition・Handling of logs から。除外後の件数は `[n after exclusion]` の空欄にする。
4. **§2 関連研究**（骨組み）: `outline.md` の Section 2 の対応表から。新しさの根拠は `docs/literature/20261012-public-keystroke-matching-novelty.md`（claim #10 #11 #14）・`20261012-public-keystroke-matching-prereg-search.md`・`20261013-length-unicity-and-dp-release.md`。"To our knowledge" に添える検索範囲（情報源・語・日付）を 1〜2 文で書く。
5. **§1 序論**（骨組み）: `outline.md` の First page の計画から。貢献の段落は `[after results]` の空欄。
6. **§8 考察**（骨組み）: 限界（事前登録の What is not concluded と §3.5）を先に書き、公開の条件（再識別しない合意）の段落を置く。公開する側への勧めは `outline.md` の「What a releasing party takes away」の型だけにする。
7. 各節を書いたらビルドと文体の門を通し、`outline.md` の表と `tasklist.md` を更新して、節ごとにコミットする。

## まだ決まっていない・後でやること

- §7 結果・§9 結論・貢献の段落・題名の最終形（題名は結果を見る前に決める）。
- 投稿前に attack-me を stage: manuscript で回す（結果の後）。round 1 の接地の本文 `attack-me/outline-threat-model/round-1/tmp/` はそのあと消す。
- Kaggle の公開の側への連絡（判断 61・64）: Dr. Tian へのメールに Crossley を CC で入れる形にした（下書き済み）。The Learning Agency Lab への短い連絡の下書きは結果の後・投稿の前（送るのは研究者）。Kaggle の主催は Vanderbilt University と The Learning Agency Lab、Citation の著者に KLiCKe の共著者 Crossley が入る。論文では共通の著者がいることを文で書かない。
- Hanisch を出版版で照合する（ACM の PDF はボットに閉じているので研究者に頼む）。
- 投稿版で、所属の書き方が匿名性を損なわないか確かめる。
- PoPETs の PC chairs への催促は 10/27 ごろ（下書きは `reply-drafts-20261013.md` の 3・送るのは研究者）。
- Dr. Tian へのメール（`reply-drafts-20261013.md` の 4）: 件名は前のスレッドへの返信「Re: Question about the terms of use of the KLiCKe corpus for a secondary analysis」に決めた（2026-10-20）。空欄は遅れのお詫び・主な結果の 1〜2 文・投稿予定日。CC に Crossley（アドレスは研究者が入れる）。送るのは草稿が完成したとき。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。絵文字・★・⚠️ を多用しない。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- 結果（G-GEAR の本計算の出力）を見ない・書かない。脅威モデルと方法は凍結した事前登録から変えない（変更は `notes.md` の「逸脱」）。手順を言い換えて意味を変えない。
- 引用は `citation-ssot`（[Pn]/[Vn]・append-only）。[V299]–[V325] は別の枝 `docs/ai-fatigue-core2-discriminant` が使っているので避ける（今は [V326]・[V327] まで使った）。公開する原稿には内部の番号・GSE への言及を書かない（`papers/README.md`）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 並行セッションがあるので worktree で作業し、コミット前に `git branch --show-current` を確かめる。`.steering` と原稿の変更は push だけ（PR は研究者に確かめてから）。`git add -A` を使わない。
