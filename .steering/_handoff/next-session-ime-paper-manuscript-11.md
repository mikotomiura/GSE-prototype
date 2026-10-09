# 次セッション — IME 論文: 公開 repo の v1.0.1 → PsyArXiv の審査の後 → BRM への投稿（判断 222 の後）

> 作成: 2026-10-07 午後（G-GEAR）・**書き直し: 2026-10-08 未明**（表の直しと出し直しの後・判断 222）。`next-session-ime-paper-manuscript-10.md` の続き。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 205**（プレプリントの方針）・**判断 221**（選択・入力）・**判断 222**（表の直し・検査・取り下げと出し直し・v1.0.1 の DOI の向け先）、`tasklist.md`、`papers/ime-observation/kit/export/README.internal.md`（公開の手順）。状態は着手時に測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（main の CI（c9372538）が緑か・枝 docs/ime-preprint-resubmit の判断 222 の記録・公開 repo mikotomiura/ime-conversion-logging の main と v1.0.0 が 48caf9ef か・PsyArXiv の j7k34_v1 の状態）。
⚠️ G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-11.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 205・221・222、tasklist.md、kit/export/README.internal.md。
Skill: git-workflow・verify-before-claiming・browser-verification（OSF・ScholarOne を Chrome で見るとき）・subagent-delegation。応答は日本語。コミットは git add パス指定。
⚠️ 公開に向かう操作（公開 repo への push・Zenodo の publish）は研究者に確かめる。push は自動モードで止められる → 研究者に ! で頼む。Zenodo の下書きと DOI の予約は自動で可、publish は都度確認（memory）。token は表示しない。
⚠️ 公開した Zenodo の 2 つ（…438・…441）と GitHub の v1.0.0 は変えない（新しい版として足す）。原稿の中身・凍結のタグ・事前登録は変えない。判断の番号は 223〜。
⚠️ Chrome は OSF の段の一覧を幅 958px では描かない → ウィンドウを 1500px に広げてから読む（判断 222）。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH" PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template <repo の外> --submission
```

## §1 状態（2026-10-08 未明）

- ✅ 表のはみ出しを直した（判断 222・PR #326 → main `c9372538` に merge 済み）: 表 1・2・13 は横向き、表 4・7 は縦の longtable。`build.sh` は「floats too large」と `tools/check_page_bounds.py`（頁の外・頁番号への重なり・番号の無い頁）を数える。直した 3 つの PDF でどれも 0。main の CI（`c9372538` の push）は起動を確かめた → 着手時に結果を `gh run list --branch main` で確かめる。
- ✅ PsyArXiv: 1 回目の `bkuds_v1` は取り下げた（404・記録も残らない）。直した 248 頁で出し直した **`j7k34_v1`**（https://osf.io/preprints/psyarxiv/j7k34_v1 ）・**pending**（送信 2026-10-07T15:58 UTC）。ファイルの SHA-256 `b4bbb119…`・タイトル・要旨・メタデータ・申告を API で照らした。
- ✅ 投稿用（repo の外）: `C:/ime-submission/main-submission.pdf`（直した版・`7729cb95…`）・`supplement.pdf`（`0bb59170…`）・`title-page.tex`（住所と電話が空欄・研究者）・`cover-letter.md`（研究者が採った・`[PsyArXiv DOI]` と `[date]` が空欄）。
- ⏳ 公開 repo の **v1.0.1** は未着手（研究者の選択で次のセッション）。

## §2 やること

1. **main の CI**（`c9372538`）が緑かを確かめる（赤なら原因を見る）。判断 222 の記録と本ファイルは枝 `docs/ime-preprint-resubmit` に push 済み（`.steering` だけなので PR なし・次の PR で main に入る）。
2. **v1.0.1**（判断 222 の DOI の向け先・`kit/export/README.internal.md` の手順）:
   - Zenodo: 記録 23183441 から新しい版の下書きを作り（API `actions/newversion`）、DOI を予約する（自動で可）。
   - GSE repo: `papers/ime-observation/CITATION.cff`・`.zenodo.json` の版を `1.0.1`・DOI を予約した新しい版の DOI に、`README.md`・`README.ja.md` のバッジを全版の DOI `10.5281/zenodo.23183440` に。**原稿（`references.bib`・`declarations.tex`）の 1.0.0 の DOI（…441）は変えない**。PR → CI → merge。
   - 新しいクローン（`core.autocrlf=false`）から本番の形の書き出し（`--style-check`）→ 公開 repo の作業クローン（bare の写し `C:/wt/ime-conversion-logging.git`）で D（`48caf9ef`）の上に E を組む（`#!` の実行ビット・作者は noreply・英語のメッセージに元の commit の 40 桁と DOI）→ 注釈付きタグ `v1.0.1` → `git -c core.autocrlf=false archive` の木と書き出しのバイト一致 → zip（`--prefix=ime-conversion-logging-1.0.1/`）。
   - 研究者に確かめて: GitHub へ push（研究者が !）→ Zenodo の下書きに zip を上げ、メタデータ（版 1.0.1・関連の識別子）を整え → publish（研究者に確かめる）。
   - データセットの記録（…438）と共有するファイルが変わっていないかを確かめる（変わっていれば研究者に相談）。
3. **PsyArXiv の審査の結果**（API で `j7k34_v1` の `reviews_state`・`doi`）:
   - **accepted**: DOI を記録し、カバーレターの `[PsyArXiv DOI]` を埋める。原稿にプレプリントの DOI を載せるかを研究者に聞く（推奨は載せない）。
   - **rejected**: 理由（PsyArXiv は却下の理由を知らせる・多くの場合は出し直せる）を読み、直して出し直すか Zenodo に切り替えるかを研究者に確かめる（判断 205）。
4. **BRM への投稿**（研究者が操作）: タイトル頁に住所と電話（研究者・repo に入れない）→ ScholarOne（`mc.manuscriptcentral.com/brmic`）で Claude が段ごとに項目を読む → 上げるのは `main-submission.pdf`・`supplement.pdf`・タイトル頁の PDF・カバーレター。推薦査読者は研究者が決める。
5. **記録**: 判断 223〜・tasklist。

## §3 気をつけること

- ⚠️ Springer の方針（判断 205 の逐語）: 投稿のときにプレプリントの DOI とライセンスを申告する。掲載が決まったら、プレプリントに掲載版の DOI と URL を足す（PsyArXiv の「Publication DOI」の欄）。
- ⚠️ PsyArXiv は承認の後はほぼ撤回できない。直すなら新しい版（versioning）。付いたファイルは API の `primary_file` の SHA-256 で照らす。
- ⚠️ プレプリントの PDF は `C:/ime-preprint/tools/combine_preprint.py`（本文と補遺をつなぐ・名前付きのリンクの注釈を生のまま写し、行き先だけを頁と点に替える・判断 222）と `preprint_meta.py`（入力欄の平文）で作る（repo の外・`python -I` で）。
- ⚠️ 自動モードの判定は公開に向かう操作を止めることがある → 回避せず研究者に頼む。
