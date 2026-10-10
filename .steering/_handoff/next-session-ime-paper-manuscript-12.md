# 次セッション — IME 論文: PsyArXiv の審査の後 → BRM への投稿（判断 224 の後）

> 作成: 2026-10-08 昼（G-GEAR）。`next-session-ime-paper-manuscript-11.md` の続き。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 205**（プレプリントの方針）・**判断 221**（選択・入力・BRM の規程）・**判断 222**（表の直し・出し直し）・**判断 223・224**（v1.0.1）、`tasklist.md`。状態は着手時に測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（PsyArXiv の j7k34_v1 の状態〔OSF の API・token なしで 403 "pending moderation" なら審査中〕・main の CI・公開 repo の main と v1.0.1 が 08583068 か）。
⚠️ G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-12.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 205・221・222・224、tasklist.md。
Skill: git-workflow・verify-before-claiming・browser-verification（OSF・ScholarOne を Chrome で見るとき）・subagent-delegation。応答は日本語。コミットは git add パス指定。
⚠️ 公開に向かう操作（公開 repo への push・Zenodo の publish）は研究者に確かめる。push は自動モードで止められる（手元の bare の写しへの push も止められた・判断 224）→ 研究者に ! で頼む。token は表示しない。
⚠️ 公開した Zenodo の 3 つ（…438・…441・…23219322）と GitHub の v1.0.0・v1.0.1 は変えない。原稿の中身・凍結のタグ・事前登録は変えない。判断の番号は 225〜。
⚠️ Chrome は OSF の段の一覧を幅 958px では描かない → ウィンドウを 1500px に広げてから読む（判断 222）。
```

## §1 状態（2026-10-08 昼）

- ✅ 公開 repo の **v1.0.1**（判断 223・224）: GitHub `mikotomiura/ime-conversion-logging` の `main` と `v1.0.1^{}` が `08583068`（タグ `56700a1c`）。Zenodo のソフトウェアの記録の新しい版 **23219322**（DOI `10.5281/zenodo.23219322`・版 1.0.1・2026-10-08）を publish 済み。全版の DOI `…23183440` は 1.0.1 に解決する。原稿とカバーレターが引くのは 1.0.0 の DOI `…23183441` のまま（研究者の選択・判断 222）。bare の写し `C:/wt/ime-conversion-logging.git` も E。
- ✅ main の CI: `c9372538`・`99e9307d`（PR #328 の merge）とも緑。
- ⏳ PsyArXiv: **`j7k34_v1`**（https://osf.io/preprints/psyarxiv/j7k34_v1 ）は 2026-10-08 02:29 UTC の時点で審査中（送信 2026-10-07T15:58 UTC・審査は 24〜72 時間）。ファイルの SHA-256 `b4bbb119…`。
- ✅ 投稿用（repo の外）: `C:/ime-submission/main-submission.pdf`（`7729cb95…`）・`supplement.pdf`（`0bb59170…`）・`title-page.tex`（住所と電話が空欄・研究者）・`cover-letter.md`（研究者が採った・`[PsyArXiv DOI]` と `[date]` が空欄）。
- ⚠️ /cross-review の Codex は 2026-10-08 未明に利用の上限に当たった（"try again at 5:06 AM"）。今日の台帳は 240,434 / 6 回。

## §2 やること

1. **PsyArXiv の審査の結果**（OSF の API で `j7k34_v1` の `reviews_state`・`doi`。審査中は token なしで 403。結果を見るには研究者のセッション〔Chrome〕で GET）:
   - **accepted**: DOI を記録し、カバーレターの `[PsyArXiv DOI]` を埋める。原稿にプレプリントの DOI を載せるかを研究者に聞く（推奨は載せない）。
   - **rejected**: 理由（PsyArXiv は却下の理由を知らせる・多くの場合は出し直せる）を読み、直して出し直すか Zenodo に切り替えるかを研究者に確かめる（判断 205）。
   - 研究者がメールで結果を知ったら、それを聞く（却下のメールを Claude が Gmail で読む案は研究者が採らなかった・判断 221）。
2. **BRM への投稿**（研究者が操作）: タイトル頁に住所と電話（研究者・repo に入れない）→ PDF にする → ScholarOne（`mc.manuscriptcentral.com/brmic`）で Claude が段ごとに項目を読む → 上げるのは `main-submission.pdf`・`supplement.pdf`・タイトル頁の PDF・カバーレター（`[date]` を投稿の日に）。推薦査読者は研究者が決める。プレプリントの DOI とライセンス（CC BY 4.0）を申告する（Springer の方針・判断 205）。⚠️ 投稿の時期は PsyArXiv の審査の結果を待つ（研究者の選択・判断 221）。
3. **記録**: 判断 225〜・tasklist。

## §3 気をつけること

- ⚠️ Springer の方針（判断 205 の逐語）: 投稿のときにプレプリントの DOI とライセンスを申告する。掲載が決まったら、プレプリントに掲載版の DOI と URL を足す（PsyArXiv の「Publication DOI」の欄）。
- ⚠️ PsyArXiv は承認の後はほぼ撤回できない。直すなら新しい版（versioning）。付いたファイルは API の `primary_file` の SHA-256 で照らす。
- ⚠️ 公開 repo の次の版を出すときは `kit/export/README.internal.md` の手順 5（判断 223 で後の版の手順を足した）。job の tmp の作業クローンは残らないので、bare の写しから `core.autocrlf=false` でクローンする。
- ⚠️ 自動モードの判定は公開に向かう操作を止めることがある → 回避せず研究者に頼む。
