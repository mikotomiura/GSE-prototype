# 引き継ぎ —— 論文 3 を Springer Nature の様式へ移し、投稿前の未決を閉じる

> 作成: 2026-11-20（同日に未決の解決を足して改訂）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 45、作業記録は `.steering/20261120-gse-paper3-supplement/`、分量は `.steering/20261107-gse-paper3-per-person-learning/paper-write/length-log.md`、未決の元の一覧は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-10/context-A.md` の末尾。

## 0. 入口の文
```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-springer-template.md を読んで、論文 3 を Springer Nature の様式へ移し、投稿前の未決 1〜7 を閉じてください。
```

## 1. 今の状態（fb05f5ee）
- 本文 main.tex: 序論〜結論 6,916 語（予算 6,800）・要旨 249 語（上限 250）・17 頁。4.4 の見出しに 3 pt の overfull が 1 つ。
- 補足 supplement.tex: Online Resource S1〜S13・14 頁・本文の初出の順・警告 0。
- Statements に AI の利用の宣言を 1 文足した（研究者の選択）。
- 新しい計算の予定は無い（未決 5 のハッシュだけは計算が要る）。

## 2. やること（この順）

### 未決 1: Springer Nature の様式（sn-jnl）へ移す
- 様式と補足の置き場（1 つの PDF を Online Resource と呼んでよいか・ファイル名の規則）を投稿規程の原文から取る（paper-write Step 0。curl が拒否されたら Chrome。記憶で決めない）。
- 移した後に要旨（250 語以下）・本文の語数・頁を測り直し、length-log に書く。overfull が残れば直す。

### 未決 2: Uto et al. 2020 の評価の設計を全文で確かめる
- references.md の [P270] に「UEC リポジトリの submitted version を全文で読んだ・frame 30 s・step 10 s」とある。全文をもう一度取り、評価の設計（後の時点の予測か・本人の単純な比べの相手があるか）を確かめる。
- 序論の「見つからなかった」と S1 の表の Uto の行（今は「---」）を、確かめた範囲で埋める。食い違えば序論の文を直す。

### 未決 3: Liu & Meng の雑誌版の文言
- 今は arXiv 1510.08539v1 で照合している。雑誌版（2016）の該当の文を Chrome で取り、本文の言い換え（relevance と robustness の交換）と食い違わないかを確かめる。取れなければ「arXiv 版で照合」を S1 に 1 句書く。

### 未決 4: S1 の検索の記録を作り直す（推奨・研究者に確かめてから）
- 今の記録には検索語・検索した日・選別の件数が残っていない（S1 にそう書いた）。序論は「our literature searches」に弱めてある。
- 案: OpenAlex・arXiv・ACL Anthology・EDM の proceedings で、検索語と日付と件数を残す小さな検索を 1 回だけ回し（literature-review の作法・既存の文献は番号だけ挙げる）、S1 に表で載せる。新しく関係する文献が出たら citation-ssot（枝をまたぐ採番に注意）。
- 回すかどうかは AskUserQuestion で聞く（推奨と費用を添える）。

### 未決 5: 元の記号列の記録ごとのハッシュ
- kit の README と限界の 1 文は「記録ごとのハッシュは未公開」としている。CoAuthor の 1,157 セッション・CS1 の 177 課題の記号列ごとの SHA-256 を、repo の外の中間（`~/gse-public-data/`）から作る。ハッシュの一覧に書き手の ID を出すか（データの公開の ID だけか・ID を出さず順序だけか）を先に決める。
- 書き手ごとの値を出さない方針（Data availability）とぶつからないかを、出す前に AskUserQuestion で確かめる。出すと決めたら、限界の文・Data availability・kit の README・S3 を直す。

### 未決 6: Code availability の URL と DOI
- 公開 repo（GitHub）と Zenodo の DOI を用意する。中身は kit・当てはめのコード・後の確かめのコード・集計値・tex だけ（`.steering/` と GSE の docs は入れない。memory「公開 repo に .steering と GSE の docs を入れない」「公開アーカイブは GitHub＋図と gif と日本語版の README」）。投稿先や状態は書かない。
- Zenodo は API で（token は `~/zenodo/zenodo_token.txt`・表示しない）。DOI は下書きで予約し、公開は論文の採否に合わせる。
- repo を作る・公開する前に、中身の一覧と公開の時期を AskUserQuestion で確かめる（外への公開なので必ず先に聞く）。
- 決まったら Code availability の文に URL と DOI を入れる。

### 未決 7: Data availability で書き手ごとの値を出さない理由
- 今の文は「No per-writer values of real writers are released」だけで理由が無い。理由（データの提供元の条件か・再識別の恐れか・研究者の方針か）を AskUserQuestion で研究者に聞き、1 句で書く。

## 3. 終わったら
- 数値の照合（Opus・読むだけ）を本文と補足にもう一度通す（様式の移行で数値が崩れていないか・足した文）。
- length-log・decisions（判断 46 から）・tasklist を書き、[skip ci] で枝にだけ push。PR は出さない。
- 完了の報告で、閉じた未決と残った未決を分けて書く。研究者に決めてもらうことは AskUserQuestion で聞く（報告の地の文の問いで終えない）。

## 4. 守ること
- papers/ に GSE の名前・内部のパス・判断の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値は開かない（未決 5 のハッシュはスクリプトで作り、値を人が読まない）。CoAuthor の記録も値も Codex に送らない（/cross-review の Codex は回さず、理由を報告に書く）。
- push は枝だけ・PR は出さない（[skip ci]）。worktree の `.codex/budget.json` はコミットしない。
