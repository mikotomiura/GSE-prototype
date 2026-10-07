# 次セッション — IME 論文: PsyArXiv の審査の後 → BRM への投稿（判断 221 の後）

> 作成: 2026-10-07 午後（G-GEAR）。PsyArXiv に送った後（判断 221）。`next-session-ime-paper-manuscript-10.md` の §2 の 1 の後半と 2 を、今の状態から始められるように書き直したもの。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 205**（プレプリントの方針）と**判断 221**（選択・PDF・入力・送った後の確かめ）、`tasklist.md`。状態は着手時に測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（origin/docs/ime-preprint に判断 221 があるか・origin/main は 428a13bd 以降か）。
⚠️ G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/docs/ime-preprint から枝を切る（判断 220・221 と引き継ぎがまだ main に無い）。
.steering/_handoff/next-session-ime-paper-manuscript-11.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 205・221、tasklist.md。
Skill: git-workflow・verify-before-claiming・browser-verification（OSF・ScholarOne を Chrome で見るとき）。応答は日本語。コミットは git add パス指定。
⚠️ 投稿の操作（ScholarOne のログイン・入力・送信）は研究者がする。Claude は画面の項目を読み、値を照らすだけ。パスワードを入れない。
⚠️ 原稿・公開物（Zenodo の 2 つ・GitHub v1.0.0・PsyArXiv の bkuds_v1）は変えない。新しい計測はしない。判断の番号は 222〜。
```

## §1 状態（2026-10-07 午後）

- ✅ PsyArXiv に送った: **`bkuds_v1`**（https://osf.io/preprints/psyarxiv/bkuds_v1 ）・**pending**（審査 24〜72 時間）・DOI はまだ無い。PDF は `C:/ime-preprint/Miura-2026-IME-conversion-logging-preprint.pdf`（241 頁＝本文 75 ＋補遺 166・SHA-256 `80e878bf…`・OSF に付いたファイルと一致）。CC BY 4.0・分野 3 つ・申告欄に DOI と登録のリンク・Supplements なし（判断 221）。
- ✅ BRM の確かめ: 本文の語数の上限は規程に無い（要旨は 250 語以内＝248 語）。図 1 の AI 開示は宣言とカバーレターで足りる（研究者の選択・説明文は変えない）。
- ✅ カバーレターの下書きを研究者が採った: `C:/ime-submission/cover-letter.md`（英語が正・日本語訳つき）。`[PsyArXiv DOI]` と `[date]` が空欄。
- 投稿用（repo の外）: `C:/ime-submission/main-submission.pdf`（78 頁・`f265446c…`）・`supplement.pdf`（`1b5c79cc…`）・`title-page.tex`（住所と電話が空欄）。
- OSF の名前は「Mikoto Miura」に直っていた（API）。tasklist の「OSF のプロフィール名」の行は、研究者に確かめてから済みにする。

## §2 やること

1. **審査の結果を測る**（OSF の API を研究者の Chrome のセッションで GET: `https://api.osf.io/v2/users/me/preprints/` の `bkuds_v1` の `reviews_state`・`doi`・`preprint_doi_created`。承認なら `accepted`・DOI は `10.31234/osf.io/bkuds_v1` の形のはず＝**値は API で確かめてから書く**）。
   - **accepted**: DOI を判断 222 に記録し、カバーレターの `[PsyArXiv DOI]` を埋める。原稿にプレプリントの DOI を載せるかを研究者に聞く（推奨は載せない: 原稿と公開 repo v1.0.0 が変わる。Springer の方針はカバーレターでの申告で足りる・判断 205 の逐語）。
   - **rejected**: 理由（メール・API の review_actions のコメント）を読み、判断 205 どおり **Zenodo への切り替えを研究者に確かめる**（同じ原稿にプレプリントの DOI を 2 つ付けない）。
   - **pending のまま**: 待つ（72 時間を過ぎたら研究者に知らせる）。
2. **BRM への投稿**（研究者が操作）:
   - タイトル頁: 研究者が `C:/ime-submission/title-page.tex` の 2 か所（住所・電話）を埋め、`pdflatex` でビルド（Claude は値を見ない・repo に入れない）。
   - ScholarOne（`mc.manuscriptcentral.com/brmic`）: 研究者がログインした後、Claude が段ごとの項目を読む（語数の欄・記事の種類・ファイルの種類・著者・推薦査読者の欄・申告）。値の案は decisions.md と原稿から作り、研究者が入れる。推薦や除外の査読者を求められたら研究者が決める（実在の人の名前を Claude から提案しない）。
   - 上げるもの: `main-submission.pdf`（本文）・`supplement.pdf`（補遺）・タイトル頁の PDF・カバーレター（DOI を埋めた版）。
3. **記録**: 判断 222〜・tasklist の「プレプリント」「BRM への投稿」の行。`.steering` だけの変更は push だけ（PR 不要）。

## §3 気をつけること

- ⚠️ Springer の方針（判断 205 の逐語）: 投稿のときにプレプリントの DOI とライセンスを申告する。掲載が決まったら、プレプリントに掲載版の DOI と URL を足す。
- ⚠️ PsyArXiv は承認の後はほぼ撤回できない。直すなら新しい版（versioning）。
- ⚠️ 確認の画面には File の段が出なかった（判断 221）。版を足すときも、付いたファイルは API の `primary_file` の SHA-256 で照らす。
- ⚠️ 自動モードの判定は公開に向かう操作を止めることがある → 回避せず研究者に頼む。
