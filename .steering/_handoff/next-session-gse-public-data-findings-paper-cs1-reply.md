# 次のセッション —— 論文 1: CS1 の著者から返事が来たときの対応

> 作成: 2026-11-07。CS1 の著者（Dataverse の termsOfAccess の連絡先・2026-11-04 に利用を承諾した人）から、推定の行と取り置きの id の一覧の公開についての返事が来たときに、このファイルから始める。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`。JEDM の返事は別の引き継ぎ `next-session-gse-public-data-findings-paper-jedm-response.md`。前の引き継ぎ 11 の §2 の 1 を、投稿の後の状態に合わせて書き直したもの。

## 問い合わせの記録

- 送った文: `.steering/20261105-public-data-findings-paper/cs1-author-request-draft.md`（研究者が 2026-11-06 に、11 月 4 日のスレッドへの返信として送った）。
- 求めたのは 2 つ:
  1. 推定の行: 分析した停止（約 4,500）と対の短い停止ごとに、2 つの信号の値（停止の始まりと 30 秒前）・統計に使った対の識別子・データセットの匿名の SubjectID と AssignmentID。
  2. 取り置きの一覧: 確認の検定に使った 146 人の匿名の SubjectID。
  - 打鍵・入力や削除の文字・時刻・課題の中身は含めない、と書いた。
- 約束（今も有効）: データを再配布しない・公開は集計値だけ。原稿の Data and code availability（`papers/public-data-findings/manuscript/sections/availability.tex`）はこの約束どおり「neither the data nor the per-pause estimate rows are redistributed」と書いて投稿した。

## 読む順

1. このファイル
2. 返事の全文。研究用のアカウント（mmiura.network@gmail.com）に届く。Gmail のコネクタは別のアカウントなので、研究者が貼るか、研究者がログインした Chrome で私が読む。
3. `cs1-author-request-draft.md` と `.steering/20261105-public-data-findings-paper/decisions.md`（判断 35〜37: 公開の範囲）
4. 公開 repo `~/stall-runup-equivalence` の `tools/check_release.py`（取り置きの一覧を漏れとして探す検査・`PRIVATE_LISTS`）と `tools/verify.sh`
5. データの置き場 `~/gse-public-data/cs1/`（`holdout.json` など。中身は外部の LLM に送らない）

## 手順（返事の種類ごと）

まず返事を逐語で写し、何が許され、何に条件が付いたかを 1 件ずつ表にする（推定の行・取り置きの一覧・条件）。読みに迷う文があれば、解釈を決めずに研究者に聞く。

### A. 両方を許された
1. 公開する形を研究者に確かめる（AskUserQuestion）: ファイルの形（CSV か JSON か）・列・置く場所（公開 repo の `experiments/` の下）。列は問い合わせに書いた範囲を超えない。
2. 推定の行を作るスクリプトを書き、条件（何をどの入力から出すか）を先にコミットしてから走らせる。値は既存の結果（論文の集計値）と照合する（行から統計を計算し直して、原稿の AUC と表の値に一致すること）。
3. `check_release.py` を直す: 今は取り置きの一覧の id を見つけると漏れとして赤になる。許された一覧のファイルとその場所だけを許可する形にし、他の場所に出たら赤のままにする。陽性対照（許可外の場所に id を置くと赤）を `control_check_release.sh` に足す。
4. README（英・日）に、ファイルの説明と CS1 の著者の許しを書き、データそのものは著者に求めること（Dataverse の DOI 2 つ）を残す。
5. `tools/verify.sh ~/gse-public-data` が 0 → コミット（`Claude-Session:` を書かない）→ 版を上げる（0.3.0 の見込み）。push・release・Zenodo の公開は研究者に確かめる。
6. 原稿の Data and code availability と限界の文は、投稿中は変えない。直すのは JEDM の改訂の段（査読への対応と合わせて）か、査読なしで採録なら校正の段。直す文の案だけ先に `.steering/20261105-public-data-findings-paper/` に書いておく。編集者に今知らせるかは研究者に聞く（推奨: 改訂の時に応答書で触れる）。

### B. 片方だけ許された（例: 取り置きの一覧だけ）
- A の手順を、許された方だけで行う。許されなかった方は今のまま出さない。

### C. 断られた・集計値だけにとどめるよう求められた
1. 何もしない。原稿・公開 repo・プレプリントは今の記述（集計値だけ・データは著者に求める・コードで作り直せる）のままで合っている。
2. 返事の要点と日付を `decisions.md` に判断として記録する。

### D. 条件が付いた（著者に先に見せる・引用の形・ライセンスの指定など）
1. 条件を逐語で写し、満たす方法を研究者に聞く。
2. 著者に見せる場合は、研究者が送る返信を下書きする（研究用のアカウントは Chrome で下書き。送るのは研究者）。

## 終わったら

- `decisions.md` に判断を足し、引き継ぎ 17 と JEDM の引き継ぎの「CS1 の著者の返事」の行を更新する。
- JEDM の改訂の段で availability の文を直すことを、JEDM の引き継ぎの C に書き足す（A か B の場合）。

## 気をつけること

- 書き手ごとの値・推定の行・取り置きの id を、許しが来るまで repo（GSE と公開 repo の両方）・コミットのメッセージ・外部の LLM に出さない。許された後も Codex には送らない。
- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報を入れない。
- Zenodo は API だけ。token は `~/zenodo/zenodo_token.txt` をプロセスの中で読むだけ。OSF は触らない。
- 投稿中は原稿の内容を変えない（変えるのは査読への対応として）。
- `.codex/budget.json` は未ステージのまま。返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
