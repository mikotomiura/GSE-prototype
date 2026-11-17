# 次のセッション（Mac）: 照合の論文 —— 投稿の前の仕上げ（PoPETs 2027 Issue 3・締切 2026-11-30 firm）

作成 2026-11-17（判断 93 の後）。worktree `/Users/johnd/GSE-wt-matching-manuscript`・枝 `docs/public-keystroke-matching-manuscript`（最新 `bf0d2450` の後の引き継ぎのコミット）。G-GEAR の作業は無い。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-pre-submission.md を読んで、照合の論文の投稿の前の仕上げを進めて。
```

## 今の状態

- 分析 6・7 は原稿に入った（判断 93 と追記）。粗い形は探索の攻撃者で大きく上がった（N = 1,000: R4(4) 0.35→48.2%・R7(0.25) 14.3→62.3%・R4(8) 0.14→2.4%・R7(0.5) は 2.2% のまま）。抄録・序論・§7・§8・結論に 1 文ずつ。問い 1〜4 の答えは登録のまま。
- 本文は 12 頁（結論は p12 右段で終わる・余白は約 0.3 頁）。総 31 頁。投稿版・プレプリントの版ともエラー 0。文体の門 違反 0。
- 残る角括弧は open science の `[anonymous link to be added]` の 1 つだけ（`sections/open-science.tex:9`）。
- Dr. Tian へ: 送り状は `.steering/20261012-public-keystroke-matching-prereg/reply-drafts-20261013.md` の下書き 8、PDF は `~/Downloads/keystroke-log-release-matching-draft-20261117.pdf`（SHA-256 は判断 93 の追記）。送るのは研究者。プレプリントの版にだけ謝辞（Yu Tian の名）を足した。2026-11-17 の返事で personal communication の 2 点と謝辞に同意を得た。
- attack-me の判定の推移: round 1〜3 とも major revision。round 3 の後に判断 85（直し）・89（全員の付録）・91・92（倫理）・93（探索 6・7 で C2 の言い方が変わった）が入っている。

## やること（推奨の順。順と範囲は最初に研究者に AskUserQuestion で確かめる）

1. **Dr. Tian**: 返事は 2026-11-17 に来た（判断 93 の追記 2）。personal communication の 2 点と謝辞に同意。原稿は変えない。下書き 8 と PDF を研究者が送ったかだけ確かめる（未送なら送ってもらう）。attack-me で原稿が変われば、camera-ready の前に最新版を送ればよい。
2. **attack-me round 4**（原稿の全体・Codex を加える）。重点: 探索 6・7 を入れた後の C2 の言い方（登録の結果と探索の結果の書き分け・「4 倍以内」の範囲）、抄録の長さ（306→348 語）。Codex には round 1〜3 で保留にした論点の一覧を添え、判定に数えないよう頼む（memory「Codex には既知の未決を渡す」）。major が続くなら直す範囲を研究者と決める。締切まで 13 日なので、round 4 の直しは 1 回で閉じる前提で計画する。
3. **匿名の複製のリンク**: 論文用の repo（`mikotomiura/keystroke-log-release-matching`・private）を、分析 6・7 の台本と集計（`exploratory_lambda.json`・`exploratory_scan.json`）まで含めて最新にし、anonymous.4open.science で匿名の複製を作り、`open-science.tex` の角括弧を埋める（判断 63・88）。公開 repo に `.steering` と GSE の docs を入れない（memory）。中身は SHA-256 で照合する。
4. **プレプリントの版の切り替え**（判断 88）: プレプリントの版でだけ OSF と repo のリンク・personal communication の日付を埋める仕組み。PoPETs の査読中のプレプリントの扱いを petsymposium.org で読む（前は DNS が SERVFAIL）。arXiv の endorsement は研究者が確かめる。
5. **投稿**（研究者が HotCRP で押す）: 前に投稿版の PDF を研究者に見てもらう（memory「投稿の Submit の前に校正刷りを見てもらう」）。投稿と同時に OSF の伏せを解く・repo を公開して Zenodo（API・token は memory）・arXiv（だめなら OSF Preprints）。公開物に投稿先や状態を書かない（memory）。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM（Codex を含む）に送らない。原稿の diff は Codex に送ってよい（判断 83）。
- 本文の数値は生成表から。足した数値は集計の JSON と機械で照らす。`make_tables.py` の止める条件を緩めない。
- 本文 12 頁を超えない（超えれば机上で落ちる）。足すより移す・削る（paper-write）。
- 引用は citation-ssot。公開する原稿に内部の番号・GSE・著者名を書かない（文体の門）。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める（PR は研究者に確かめる）。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
