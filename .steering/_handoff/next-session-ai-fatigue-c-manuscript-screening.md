# 引き継ぎ: TRACE（AI 疲労の測定論 C）—— 逸脱と選別の結果を原稿に入れる・tasklist の整理

作成 2026-10-28。**2026-10-28 に実施済み（判断 122・TRACE `adaff0c`）。**前のセッションの判断は decisions.md の判断 114〜121。

## 0. 次のセッションでやること（研究者が選んだ組み合わせ）

研究者の指示（2026-10-28）は、次の 3 つを 1 回のセッションでまとめて行うこと。

1. 逸脱の文案を TRACE の原稿に入れる（軽い）
2. tasklist を整理する（軽い）
3. 選別の結果を、脚本で原稿に入れる（重い・本題）

始める前に、次の 4 つを読む。

- 作業の場所: worktree `/Users/johnd/GSE-prototype-af-c`（枝 `docs/ai-fatigue-c-outline`・push 済み）
- steering: `.steering/20261017-ai-fatigue-c-outline/` の decisions.md（判断 119〜121）と deviations-draft.md
- TRACE: `~/TRACE`（main・origin と同期）。原稿は `~/TRACE/manuscript/draft/`（`main.tex` 400 行・`tables.tex`・`figure1.tex`・`make_docx.py`）、外枠は `~/TRACE/manuscript/outline.md`
- 登録: `~/TRACE/registration-en.md` の GSRR-33・37・38・39・41（選別の報告の決まり）

## 1. 状態

- 選別の段 2・3 の判定は、全部終わって書き出した（b01〜b40）。
- 理由なしの保留 24 件は、判断 121 で「合意できない」（unresolved）に直した。
- 選別の表は `~/TRACE/screening/screening*.csv`（TRACE `61596c7`）。数は次のとおり。
  - 段 2（347 件）: 含める 100・除外 128・E6 の保留 95・含めるかの unresolved 24
  - 段 3（含めた 100 件）: 中心-B 71・中心-A 24・中心の unresolved 5
- `release` は止まっている。AI の網の答えの引用 3,430 行（`~/TRACE-screening/quote-review.csv`）に、著者 1 が scale_item を付けるまで動かない。研究者の選択で後回しにした。
- 較正の 1 回目は、研究者の符号化待ち。Drive の `TRACE_calibration/pass1/` の 2 冊は、置いたときの SHA-256 のまま（10-28 に確かめた）。
- 選別の締めの日は 2026-12-31（GSRR-39）。それまでは保留の記録が判定し直されうる。そのため、いま原稿に入れる数は締めの前の暫定値になる。

## 2. タスク 1: 逸脱を原稿に入れる

- 文案: `.steering/20261017-ai-fatigue-c-outline/deviations-draft.md`。D1〜D8 すべてに英文案があり、要確認の項目は 0。
- 入れる先:
  - 表 2 に行として入れる: D1・D2・D3・D6・D7。`tables.tex` の「Deviations from the registration and from the outline」の殻（列は Date・Registration item or outline section・Change and reason・Codes or tables affected）。
  - 方法の節の文として入れる: D4・D5・D8。`main.tex` の Eligibility and screening（182〜221 行あたり）。
  - Use of AI の宣言: `main.tex` 384〜387 行あたり。D2（共著者の ChatGPT）と D8（Codex の入力）を足し、`\tbd{and any other use in preparing the manuscript}` を埋める。
  - 限界の節: `main.tex` 373 行の `\tbd{Limitations added by deviations from the registration, if any.}`。D1 の見直しと D2 で足すことがあるかを研究者に聞く。
- 研究者の選択で決まっていること（判断 121）:
  - D2 は判断 91 の研究者の理解（判定は共著者のもので、ChatGPT は補助）で書く。共著者への確かめは取らない。
  - D8 の Codex は入力だけ。
- 表 2 の英文は長いので、組んで表が崩れないか確かめる。手順は `cd ~/TRACE/manuscript/draft && latexmk` と `make_docx.py`。組む前に figure1 を組む必要がある（判断 80）。
- 草稿の Drive の版（`TRACE` 直下と共著者フォルダの docx・PDF）を置き換えるかは研究者に聞く。置き換える前に、Drive の版が前に置いたときのままかを cmp で確かめる。

## 3. タスク 3（本題）: 選別の結果を脚本で原稿に入れる

### 3.1 一次資料

- 登録 GSRR-37（237 行）: 選別の一致の報告の決まり。次の 8 点を報告する。
  - 段 1 の 2 割の標本: 百分率・kappa・2×2 の表・どちらかが含めた記録の中での一致
  - 段 2・3: 2 人とも判定した全件で、百分率・kappa
  - 各著者が先へ送った数
  - 中心の段で境界にした数
  - 網・混ぜた記録・監査の一致は別に
  - 網が送った記録のうち、著者 1 が除外していた数と、最後に含めた数
  - 追加候補と確かめの標本を分け、合わせた数も
  - 含めるかの unresolved は、2 人の判定のまま数え、最終を unresolved と報告する
- 登録 GSRR-39（243 行あたり）: 締めの日・遅い層・確かめの数（coverage count）の報告の形。
- 登録は「結果の値は脚本で原稿に写す」としている（`main.tex` 373 行の限界の文も同じ）。

### 3.2 前のセッションで出した値（暫定・締めの前）

登録済みの集計の脚本で出した値。

```
cd ~/TRACE && cp screening/screening*.csv <tmp>/
uv run -q python scripts/c_synthesis.py --screening <tmp>/screening.csv \
  --coverage-sample registration-attachments/coverage/new-records.csv
# → <tmp>/out/screening_agreement.csv（pool all / candidates / coverage_sample × 段 1〜3）と coverage.csv
```

一致率（百分率・kappa）:

| 群 | 段 1 | 段 2 | 段 3 |
|---|---|---|---|
| 合わせて | 113 件で 82.3%・0.654 | 317 件で 80.8%・0.713 | 90 件で 88.9%・0.743 |
| 追加候補 | 53 件で 84.9%・0.651 | 205 件で 87.8%・0.812 | 85 件で 89.4%・0.744 |
| 確かめの標本 | 60 件で 80.0%・0.471 | 112 件で 67.9%・0.428 | 5 件で 80.0% |

その他の値:

- 確かめの数: 300 件すべてが決まった。含める 7（2.3%・95% 区間 0.9〜4.7%・新しい記録 10,854 件に掛けて約 253 件）。含めるか保留は 64（21.3%）。
- 監査（`screening/screening-audit-summary.csv`）: 30 件のうち、最後に含めたのは 0、保留は 10。

注意: 段 1 の 2 割の標本の一致率のうち、登録の 80% の線の判断に使うのは `screening/coauthor/sample-agreement.csv`（元の値で 97.3%）である。上の表の段 1 は、見直しの後の値による補足になる（判断 93・94）。原稿でどちらを本文に出すかは、D1 の文と合わせて決める。

### 3.3 方針の案（次のセッションで研究者に確かめてから進める）

- 脚本で値をマクロの .tex（例 `manuscript/draft/values-screening.tex`）に書き出し、`main.tex` と `tables.tex` はマクロを引く。締めの日に同じ脚本を走らせ直せば数が入れ替わる。手で数を打たない。
- 埋める候補:
  - `main.tex` の方法の節の穴
    - 187 行: 2 割の一致率
    - 192〜193 行: unresolved の件数
    - 226 行: 締めの日
    - 179 行: 新しい記録の数（10,854。`new-records.csv` から）
    - 38 行: 抄録の締めの日
  - 表 3（Sets and their composition）の Records の列: 本体・遅い層・確かめの層・締めの日に全文で保留・含めるかで unresolved・選別していない
  - 図 1（流れ図）と、表 3 の注の一致の段落
- 決まっていないこと（研究者に聞く）:
  - 結果の節（`main.tex` 295 行）は「表を作った後に書く」とし、表の値は「符号化まで横棒」と書いてある（`main.tex` 311〜313 行・外枠も同じ）。選別の値を、いま方法の節と表 3・図 1 に入れてよいか。それとも方法の節の穴だけにするか。外枠からの逸脱にならないかを、`outline.md` の該当の行で確かめてから聞く。
  - 締めの前の暫定の値を入れるなら、どこに「暫定」と書くか（原稿の中か、共著者への案内だけか）。
- 脚本は新しく作る（登録の添付ではない）。`c_synthesis.py` を変えずに、その出力（`out/*.csv`）と `screening/*.csv` だけを読む。
- 確かめ: 値が CSV と一致することを、脚本の中で照らす。組版して PDF の文字に数が出ることを見る。
- レビュー: 脚本ができたら code-reviewer と /cross-review を通す（前のセッションの道具の変更と同じ）。

## 4. タスク 2: tasklist の整理

`.steering/20261017-ai-fatigue-c-outline/tasklist.md` に、済んだのに未チェックの項目が残っている。前のセッションで見えたものは次のとおり。

- 115 行: `screening-csv`・`release`
- 121 行: h3 を知らせる → 取り込み・2 人で決める・締める
- 104 行: h2 を共著者に送る
- 51・52・85・86 行: 研究者の確かめ
- 64・82・83 行: 登録の下書きの書き換え。登録は済んでいるので、もう要らないかもしれない。判断の記録と照らす。

残すものは「release の前の引用の確かめ（3,430 行）」「較正の 1 回目」「締めの日の作業（2026-12-31）」「逸脱の文案の残り」などとして並べ直す。

## 5. 守ること（前のセッションからの継続）

- 返答・記録・AskUserQuestion は日本語で書く。記号や絵文字を多用しない。決めてほしいことは、推奨と理由を添えて AskUserQuestion で聞く。
- 記録ごとの判定の値、抄録、全文を repo に写さない（道具が書く CSV は除く）。steering には件数だけ書く。
- TRACE で rebase・squash をしない（直しは新しいコミットで）。`git add -A` を使わない。PR は研究者が確かめてから出す。
- DB を触るときは、毎回次を確かめる。
  - Excel が閉じていること
  - DB が最後の版であること（SHA-256。いまは `74ee2b49…`）
  - 控えを読み取り専用で取ったこと
- Drive の共有の設定と、GitHub の公開設定は変えない。
- 次に `update_trace_db.py` を回すときは、`drive_links_with_override.py` を使う（S13-18.pdf の Drive ID の件・判断 117）。
