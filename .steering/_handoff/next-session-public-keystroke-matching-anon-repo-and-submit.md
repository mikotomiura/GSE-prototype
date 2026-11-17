# 次のセッション（Mac）: 照合の論文 —— 匿名の複製のリンクと投稿（PoPETs 2027 Issue 3・締切 2026-11-30 firm）

作成 2026-11-17（判断 96 の後）。worktree `/Users/johnd/GSE-wt-matching-manuscript`・枝 `docs/public-keystroke-matching-manuscript`（最新 `9b3bb6e8` の後の引き継ぎのコミット）。G-GEAR の作業は無い。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-anon-repo-and-submit.md を読んで、照合の論文の匿名の複製と投稿の準備を進めて。
```

## 今の状態

- attack-me は閉じた（判断 95・96）。判定の推移 round 1〜4 major → round 5 minor。round 4・5 の直しと、それぞれの /cross-review（Claude と Codex）を済ませた。
- 本文は 12 頁（倫理の見出しは p12 右段）・本文 11,054 語・抄録 335 語・総 31 頁。投稿版・プレプリントの版ともエラー 0。文体の門 違反 0。
- 逸脱は 5 件（D6: 本計算が λ = 4・16 の二次を R7 で回していなかった。notes.md に記録・論文の §6・付録 B・D・§7.2・抄録に）。
- 残る角括弧は open science の `[anonymous link to be added]` の 1 つ（`sections/open-science.tex`）。
- プレプリントは採否まで待つ（判断 95・PoPETs 2027 の規程が査読中の公開を控えるよう求める）。OSF の伏せは採否まで解かない。プレプリントの版の切り替え（OSF と repo のリンク・個人的な連絡の日付）は採否の後。
- Dr. Tian へは原稿が完成してから送る（研究者・2026-11-17）。PDF はプレプリントの版。

## やること（推奨の順。順と範囲は最初に研究者に AskUserQuestion で確かめる）

1. **匿名の複製のリンク**（判断 63・88）: 論文用の repo（`mikotomiura/keystroke-log-release-matching`・private・最後の push は 2026-10-12）を最新にする。分析 6・7 の台本と集計（`exploratory_lambda.json`・`exploratory_scan.json`）・D6 の記録まで。anonymous.4open.science で匿名の複製を作り、`open-science.tex` の角括弧を埋める。
   - ⚠️ `results/main_a4_without_cpu_writer.json` は入れない（500 人の版との差から 1 人の KeyTAR の値が出る・判断 96）。
   - 公開 repo に `.steering` と GSE の docs を入れない（memory）。打鍵の記録・本文・書き手ごとの値も入れない（判断 88）。中身は SHA-256 で照合する。
   - 匿名の複製に著者の名前・所属・GitHub のアカウント名が出ないことを確かめる（コミットの作者・LICENSE の著作権者・README）。
2. **Dr. Tian へ送る**: 送り状の下書き（`.steering/20261012-public-keystroke-matching-prereg/reply-drafts-20261013.md`）を最新の版に合わせ、プレプリントの版の PDF を作る。送るのは研究者。
3. **投稿**（研究者が PoPETs の投稿サイト submit.petsymposium.org で押す。サイトは HotCRP で動いている。2026-11-17 にトップは "PoPETs 2027.2" だったので、Issue 3 のページが開いているかを先に確かめる）: 前に投稿版の PDF を研究者に見てもらう（memory「投稿の Submit の前に校正刷りを見てもらう」）。metadata の抄録は LaTeX のコマンドなし。投稿と同時の公開はしない（判断 95）。
4. attack-me の `round-*/tmp/`（接地の本文・git に入らない）を消す。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM（Codex を含む）に送らない。原稿の diff は Codex に送ってよい（判断 83）。
- 本文の数値は生成表から。足した数値は集計の JSON と機械で照らす。`make_tables.py` の止める条件を緩めない。
- 本文 12 頁を超えない（超えれば机上で落ちる）。足すより移す・削る。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める（PR は研究者に確かめる）。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
