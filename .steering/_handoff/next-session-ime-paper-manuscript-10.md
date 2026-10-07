# 次セッション — IME 論文: PsyArXiv のプレプリント → BRM への投稿の前の確かめ（M12 の公開の後）

> ✅ **済み（2026-10-07・判断 221）。続きは `next-session-ime-paper-manuscript-11.md`**（PsyArXiv の審査の後 → BRM への投稿）。

> 作成: 2026-10-07 昼（G-GEAR）。M12 をすべて済ませた後（判断 218〜220）。`next-session-ime-paper-manuscript-7.md` の §2 の 3〜5 を、今の状態から始められるように書き直したもの（-7 は M12 より前に書いたので §0 が古い）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 205**（プレプリントの置き場所と時期）と**判断 218〜220**（寄託・README・リリース D・公開）、`tasklist.md`、原稿 `papers/ime-observation/manuscript/`、`BUILD.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（origin/docs/ime-m12-published に判断 220 があるか・origin/main は 428a13bd 以降か・公開 repo mikotomiura/ime-conversion-logging が public で v1.0.0 = 48caf9ef か・Zenodo 10.5281/zenodo.23183438 と …23183441 が公開されているか）。
⚠️ G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/docs/ime-m12-published から枝を切る（判断 220 と引き継ぎの更新が main にまだ無い）。
.steering/_handoff/next-session-ime-paper-manuscript-10.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 205・218〜220、tasklist.md、原稿（papers/ime-observation/manuscript/）と BUILD.md。
Skill: git-workflow・verify-before-claiming・browser-verification（PsyArXiv・ScholarOne を Chrome で見るとき）・subagent-delegation・citation-ssot（書誌を足すとき）。応答は日本語。コミットは git add パス指定。
⚠️ PsyArXiv への投稿は取り消せない → 出す直前に研究者に確かめる（ライセンス・分野・OSF とのつなぎ方も研究者が決める）。アカウントのログインやフォームの送信は研究者がする（Claude はフォームを送らない・パスワードを入れない）。
⚠️ 原稿の中身（結果・解釈・Discussion・結論）は研究者のもの。新しい文は日本語で見せて採るかを聞く。新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。研究者のメールアドレスを Codex に送らない。
⚠️ 公開した Zenodo の 2 つと GitHub の v1.0.0 は変えない（直すなら新しい版として出す）。
⚠️ 判断の番号は 221〜。heredoc（python -c・sed も）でバックスラッシュを重ねない → 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH" → bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template <repo の外の出力の dir> [--submission]。頁を画像で見るときは PyMuPDF（fitz）で PNG にして Read。
```

## §1 状態（2026-10-07 昼）

- ✅ **M12 はすべて済み**（判断 207〜220）:
  - データセット `10.5281/zenodo.23183438`（38 ファイル・datasheet つき・公開日 2026-10-07）。
  - コード `10.5281/zenodo.23183441`（`ime-conversion-logging-1.0.0.zip`・3,867,948 バイト・SHA-256 `4bbbfebc…`）。
  - GitHub `mikotomiura/ime-conversion-logging` は **public**。履歴は A・B（凍結の 2 つのタグ）・C（外枠 `cb29a1a9`）・D（リリース `v1.0.0` = `48caf9ef`）。README は英語と日本語訳（`README.ja.md`）、図 4 枚。
  - 原稿の `\tbd` は 0。要旨の "The registrations, code and data are public" は真になった。
- ✅ 原稿の attack-me は round 2 で閉じた（判断 206・round 3 は回さない）。
- main は `428a13bd`（PR #319）。判断 220 と M12 の引き継ぎの更新は枝 `docs/ime-m12-published`（push 済み・`.steering` だけなので PR は出していない）。
- Codex の台帳: 2026-10-07 は 233,740 / 8 回（上限 300,000）。日付が変わっていれば 0 から。

## §2 やること

1. **PsyArXiv のプレプリント**（判断 205）。BRM に出す版と同じものを出す。
   - 先に研究者に聞く（AskUserQuestion・推奨と理由を添える）:
     - **ライセンス**: 推奨は CC BY 4.0（データセットと文書と同じ。OSF のヘルプは CC0 か CC BY 4.0 を推奨）。
     - **分野**（PsyArXiv の分類）: 候補を一次（PsyArXiv の投稿画面の分類の一覧）で確かめてから示す。
     - **OSF の事前登録とのつなぎ方**: 2 つの登録（`osf.io/9nh7r`・`osf.io/4jwzn`）と同じ project に紐づけるか。
     - **どの PDF を出すか**: `main.pdf`（組版どおり）か `main-submission.pdf`（ダブルスペース）か。推奨は読みやすい `main.pdf`。
   - ⚠️ **OSF のプロフィール名「Mikto Miura」を、先に研究者が直す**（判断 200 の 8・PsyArXiv の著者名に出る）。
   - ビルド: `build.sh --submission` で エラー 0・未定義 0・生成されていない値 0 を確かめる（前回は overfull が main 0・main-submission 1・補遺 167）。補遺（`supplement.pdf`）も添えるかを研究者に聞く。
   - 投稿の画面の入力は研究者がする（Claude は Chrome で画面の項目を読み、入れる値の案を示すだけ）。PsyArXiv の事前の審査（24〜72 時間）で止まったら、Zenodo に切り替えるかを研究者に確かめる（判断 205）。同じ原稿にプレプリントの DOI を 2 つ付けない。
   - プレプリントの DOI が出たら記録する（判断に）。原稿に載せるかは研究者に聞く（BRM の投稿の申告に要る）。
2. **BRM への投稿の前の確かめ**:
   - 投稿規程の語数の上限を一次で確かめる（BRM の規程のページには上限が無かった・round 2 の取得 2026-10-06。ScholarOne の画面でも確かめる。memory: BRM は ScholarOne・規程は curl ＋ cookie で原文が取れる）。
   - カバーレター（研究者と相談して書く・プレプリントの DOI とライセンスの申告を含める＝Springer の方針の逐語は判断 205）。
   - タイトル頁（`manuscript/submission/title-page.tex` を repo の外に写して記入・住所と電話は研究者が入れる）。
   - 要旨を変えたら `.steering/20260927-ime-observation-paper-eval-design/issues/_count_abstract.py` で 250 語以内にする（今は 248 語）。
   - 図 1（AI が描画のコードを書いた図）の説明文に AI の開示が要るかを編集部に確かめる（round 2 の Y39）。
   - 投稿の操作は研究者がする。
3. **記録**: 判断 221〜・tasklist の「プレプリント」「投稿」の行。PR は出荷フロー（git-workflow ルール 6）。

## §3 気をつけること

- ⚠️ PsyArXiv はほぼ撤回できない（撤回は法的な義務があるときだけ・FAQ）。出す版は、公開した材料（Zenodo・GitHub）と食い違わないこと。原稿を直したら、`build.sh` と文体の検査（`_style_check.py`・repo 直下から）を通してから出す。
- ⚠️ Springer の方針（判断 205 の逐語）: 投稿のときにプレプリントの DOI とライセンスを申告する。掲載が決まったら、プレプリントに掲載版の DOI と URL を足す。
- ⚠️ 原稿は公開 repo（`v1.0.0`）にも入っている。投稿のために原稿を直したら、公開 repo の次の版（`v1.0.1` など）と Zenodo の新しい版を出すかを研究者に聞く（同じ concept DOI の下に版を足せる）。`v1.0.0` は書き換えない。
- ⚠️ 自動モードの判定は、公開に向かう操作（公開 repo への push・上げの記録の読み取りなど）を止めることがある → 回避せず研究者に `!` で頼む（memory「新しい repo への push は止められる」）。
- ⚠️ G-GEAR から Zenodo への大きいファイル（55 MB 以上）の上げは切れる（memory）。今回の作業では大きいファイルは上げない見込み。
- 値の置き場所・層を名指す文・`number_word()` の注意は -7 の §3 のとおり（原稿を直すときに読む）。
