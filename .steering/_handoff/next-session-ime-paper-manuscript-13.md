# 次セッション — IME 論文: 次の出し先を研究者が決めた後の投稿の準備（判断 233 の後）

作成 2026-10-10（G-GEAR）。`next-session-ime-paper-manuscript-12.md`（PsyArXiv の審査の後 → BRM）と `next-session-ime-counts-only-fix.md`（D13）の続き。応答・記録・完了報告は日本語で。記号（★・⚠️）を多用しない。

このメモは一次資料ではない。一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の判断 205（プレプリントの方針）・221（BRM の規程と入力）・225〜233（D13 と v1.0.2）と `tasklist.md`。状態は着手時に測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る:
- 判断の最後の番号（main と、記録だけの枝 origin/docs/ime-release-1.0.2-published〔判断 232・233〕—— main に入っていなければ取り込んでから次の番号を使う）
- 公開 repo mikotomiura/ime-conversion-logging の main とタグ（v1.0.2 = a668fad5 のはず）
- 研究者が決めた次の出し先
.steering/_handoff/next-session-ime-paper-manuscript-13.md を読んで §2 を上から実行してください。
G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
公開に向かう操作（公開 repo への push・Zenodo の publish・投稿）は研究者に確かめる。push は自動モードで止められる → 研究者に ! で頼む。token は表示しない。
```

## §1 状態（2026-10-10）

- PsyArXiv は対象範囲の外として却下（最終・再投稿不可・arXiv か TechRxiv を勧められた）。
- 逸脱 D13 を入れた（PR #341）: `no_runs`・`bin1s_count`・`counts_only` は英字の連なりの長さを持つ（`counts_only` は `no_time` と同じ情報）と記述を直し、長さを捨てた 2 組（`letter_runs_unit`・`all_runs_unit`）を事後の解析で測った。2 組とも 10 候補では偶然の水準の近く、100 候補では届かず、事後にも推奨できる粒度なし。登録の値と推奨（なし）は変えていない。要旨は 250 語。
- 公開 repo の v1.0.2（PR #342・E `a668fad5`・タグ `037a599c`）と Zenodo の新しい版 23273986（DOI `10.5281/zenodo.23273986`）を出した。原稿は登録の解析に 1.0.0（`…23183441`）を、D13 の解析に 1.0.2 を引く。全版の DOI `…23183440` は 1.0.2 に解決する。データセット 23183438 は変えていない。
- repo の外の `C:/ime-submission/`（投稿用 PDF・補遺・タイトル頁・カバーレター）は D13 の前のもの。カバーレターに `[PsyArXiv DOI]` の空欄がある。

## §2 やること（上から）

1. 研究者が決めた出し先を聞く（決まっていなければ AskUserQuestion で、推奨と理由を添えて）。候補: arXiv（2026-01-21 から個人的な endorsement が要る・memory `project_arxiv_endorsement_2026`）・TechRxiv・プレプリントを出さずに BRM（ScholarOne・判断 221 の規程）。
2. 出し先の規程を一次で確かめる（語数・ファイルの形・AI の開示・プレプリントの扱い）。BRM なら判断 221 と引き継ぎ -12 §2 の 2 がそのまま使えるが、プレプリントの DOI の申告は無くなる（プレプリントを出さない場合）。
3. 投稿用の PDF（`build.sh --submission`）・補遺・カバーレターを今の原稿から作り直し、`C:/ime-submission/` に置く（repo に入れない）。カバーレターの PsyArXiv の行を直す。
4. 外枠を出し先に合わせて変えるなら、変える前に attack-me を回すか研究者に聞く（判断 229 の選択: 外枠を変えるときに回す）。
5. 投稿は研究者が行う。Claude は入力欄の値を一次で読む（Chrome は browser-verification Skill を先に読む）。

## §3 気をつけること

- レビューの LOW（研究者に伝え済み）: 「near chance among 10 candidates」は平易に読むと強く響く（正答率 16〜17%・偶然の 1.6〜1.7 倍）。言い方を変えるなら `results_tables.py` の `q4x.byk` と本文を同時に。
- 公開 repo の次の版は `kit/export/README.internal.md` の手順 5（後の版が足したか変えたコードを論文が使うときの DOI の扱いを判断 231 で足した）。作業クローンは bare の写しから `core.autocrlf=false` で作る。
- Codex の台帳（`.codex/budget.json`）は枝ごとに分かれる。merge では起点からの差分の和を採る。
