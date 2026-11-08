# 次のセッション —— 論文 2: JEDM から返事が来たときの対応

> 作成: 2026-11-08。JEDM の編集部・査読者から論文 2 について返事（デスクでの判断、確認や不備の指摘、査読の結果）が来たときに、このファイルから始める。worktree `/Users/johnd/GSE-prototype-paper2`・枝 `docs/gse-paper2-stall-shape`（push は研究者に確かめる・PR は作らない）。論文 1（投稿番号 1484）の返事は別の引き継ぎ `next-session-gse-public-data-findings-paper-jedm-response.md`。両方に同じ日に返事が来たら、どちらから始めるかを研究者に聞く。

## 投稿の記録

- 誌: Journal of Educational Data Mining（JEDM）。OJS 3.5。節 Articles・単盲（研究者の確定・判断 9）。掲載料なし・CC BY-NC-ND 4.0。
- 投稿: 2026-11-08（サイトの時刻 04:31:15）・投稿番号 1486・状態 Queued（stage 1）。ダッシュボードはログインの後に https://jedm.educationaldatamining.org/index.php/JEDM から入る。
- 題: What moves with the pause definition and the adjustment: a multiverse diagnostic of pause and stall labels in keystroke logs
- 投稿した版: commit 0a472b01 の原稿（`papers/stall-shape-multiverse/manuscript/`）。本文の PDF 441,182 バイト・31 頁・SHA-256 8bab070e…、送付状の PDF 12,916 バイト・SHA-256 c50fa9b4…。どちらも投稿の画面から取り直して手元と一致した。組み直すと時刻で SHA-256 が変わるので、照合はシステムから取り直したもので。
- システムの欄にだけ入れたもの: 要旨（abstract.tex から LaTeX を外した 1,828 文字）、キーワード 6 つ、参考文献 43 件（main.bbl から素の文）、編集者への欄（送付状の本文）、所属「Independent Researcher」（API で直した）。ORCID の欄は空。
- 記録: `.steering/20261107-paper2-manuscript/submission/submission-record.md`・`submission/cover-letter.md`・`decisions.md`（判断 9 まで）・`tasklist.md`・attack-me は `attack-me/manuscript-paper2/round-1`〜`round-5`（round 5 の verdict.md §8 で閉じた）。
- 公開物: GitHub https://github.com/mikotomiura/stall-shape-multiverse （手元 `~/stall-shape-multiverse`・組み立ては `.steering/20261107-paper2-manuscript/public/assemble.py`）、Zenodo 0.1.0 = 10.5281/zenodo.24047695（原稿の Data and code availability が引く）。論文 1 のプレプリント 10.5281/zenodo.24026330 と論文 1 のアーカイブ 10.5281/zenodo.24026278 を引いている。
- 論文 1 との重なり: 基準の定義・CS1 の変換・観測区間・開けた 2 つの取り置きを共有。送付状と補足 S8 で申告した。

## 読む順

1. このファイル
2. 返事の全文。メールは研究用のアカウント（mmiura.network@gmail.com）に届く。Gmail のコネクタは別のアカウントにつながっているので、研究者が貼るか、研究者がログインした Chrome で私が読む（`browser-verification` Skill を先に読む）。
3. `.steering/20261107-paper2-manuscript/decisions.md` と `submission/submission-record.md`
4. 原稿 `papers/stall-shape-multiverse/manuscript/sections/` と `appendix/supplement.tex`（S1 は計算の順序と各結論の地位）
5. 返事の内容によって: attack-me の各 round の verdict.md（重なる指摘があれば材料・round 5 の §3 は Codex の指摘 C1〜C4）、`experiments/20261107-stall-shape-multiverse/notes.md`（計算 1〜9 の記録と読み）、`conditions*.md`

## 手順（返事の種類ごと）

### A. 採否を決めずに確認や不備の指摘が来た場合（書式・ファイル・宣言・利益相反・論文 1 との重なりなど）
1. 指摘を逐語で写し、何を直せば足りるかを JEDM の頁（Submissions・Author Guidelines・Competing Interest Guidelines。curl で取り直す）で確かめる。
2. 書式だけなら直して組み直し（`manuscript/BUILD.md`・テンプレートは JEDM の頁の `2024_08_02_jedm-latex.zip`）、ダッシュボードで差し替える。上げるのは Chrome で私がしてよいが、送る前に研究者に確かめる。同意の印と送信は研究者が押す（自動の安全確認に止められる）。
3. 論文 1 との重なりを問われたら、補足 S8 と送付状の段落を材料に、共有するもの（定義・変換・観測区間・取り置き）と違うもの（問い・設計・結果）を答える。
4. 内容に触れる直しは C と同じ扱いにする。

### B. デスクでの不採録
1. 理由を逐語で写す。
2. 次の投稿先は研究者が決める。目的から選ぶ（memory の feedback-venue-by-purpose・無料の道を先に）。
3. 新しい投稿先の規程を取り直し、テンプレート・語数・宣言を当て直す。

### C. 査読の結果（major / minor revision）
1. 指摘を 1 件ずつ表にする（番号・査読者の言葉の逐語・種類・対応の案）。置き場は `.steering/20261107-paper2-manuscript/revision-1/`（新しく作る）。
2. 各指摘の正否を、メインが一次資料（スクリプト・results の JSON・条件・引いた文献の本文）で確かめる。査読者の言葉を根拠にしない（`verify-before-claiming`）。
3. 対応の採否は研究者が決める。AskUserQuestion で 1 件 1 問、概要と論点と推奨を書いて聞く。推奨は「研究として強いか」で決める。
4. 新しい計算が要る場合は、計算の前に条件（`conditions-round10.md` から）を書いてコミットし、読み方を先に置く。看板の形は結果を見て替えない。書き手ごとの値・CS1 のデータは repo の外・外部の LLM に出さない（CS1 は集計値だけ）。作業場は `~/gse-public-data/paper2_work`・Python は `~/gse-public-data/venv-paper2`。
5. 原稿を直す。直しは足すより移す（本文は 6,878 語・細部は補足へ）。地位（[P]/[A]/[E]/[D]）を S1 に足す。応答書を英語で書き、指摘ごとに直した箇所を示す。
6. 直しの後に attack-me を stage `revision` で回す（同じ panel＋E・Codex を加え、既知の未決の一覧を添える）。推移を見て minor が続けば閉じる。
7. 組み直し、ダッシュボードの改訂の段から改訂稿・応答書を上げる（送る前に研究者に全頁を見てもらう）。
8. 公開 repo を組み直して版を上げるか研究者に聞く（`public/assemble.py` → `python3 -I tools/verify.py --private ~/gse-public-data` が 0 → `tools/readme_media.py --check` → push と Zenodo の newversion は研究者に確かめる）。原稿の DOI をその版に差し替えると、その版の写しは前の版の DOI のままになる。

### D. 不採録（査読の後）
1. 理由と査読の文を逐語で写し、C の 1〜2 と同じく正否を確かめる。
2. 直すかと次の投稿先は研究者が決める。

### E. 採録
1. 校正と著作権の手続きは研究者がする。
2. 公開 repo の README（英・日）と CITATION.cff、Zenodo の記録に誌の書誌（巻・号・頁・DOI）を足す（push・release・Zenodo は研究者に確かめる）。採録までは公開物に投稿先や状態を書かない（研究者の指示・2026-11-08）。

## 査読が進むまでにしてよいこと

- 待つあいだに原稿の内容を変えない。他誌に出さない。
- 状態を見るなら、研究者がログインした Chrome でダッシュボードを読むか、`/index.php/JEDM/api/v1/submissions/1486` を読む（書き換える呼び出しはしない。URL に token が付くファイルの一覧は出力で止められるので、必要な項目だけ返す）。

## 気をつけること

- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報・投稿先や状態を入れない。公開 repo のコミットに `Claude-Session:` を書かない。
- Zenodo は API だけ。token は `~/zenodo/zenodo_token.txt` をプロセスの中で読むだけ。
- パスワードは入れない（ログインは研究者）。同意の印と最後の送信は研究者が押す。
- `.codex/budget.json` は未ステージのまま。
- 返答とファイルは日本語、記号を控える。公開物・応答書・原稿は英語の学術的な文。未決は AskUserQuestion で日本語で聞く。
