# 次セッション — IME 論文: 結果の表の道具の残り（表 7・KT1・表 8 の macOS）→ 結果の節を書く

> 作成: 2026-10-05 夕（G-GEAR・D10 の Windows の直した解析〔判断 166〕と、表の道具の前半〔判断 168〜170〕を済ませたセッションの最後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 156・165〜170**、
> 外枠 `papers/ime-observation/manuscript/outline.md`（Rule for the abstract・Claims and evidence の RF1・KT1・AG1〜AG8・RC1〜RC3・Tables and figures）、
> 凍結した事前登録（§6.2〜§6.10・§10.7）・`deviations.md`（D1〜D10）・`data.md`・`data.windows.md`・`experiment/results/`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 docs/ime-manuscript-outline（origin と一致していること）で作業する。
.steering/_handoff/next-session-ime-paper-results-3.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 156・165〜170、outline.md、manuscript/tools/results_tables.py、凍結した事前登録、deviations.md（D1〜D10）、experiment/results/。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果を見てから規則を変えない。規則をコードに写したら selftest と変異（scratchpad の使い捨てスクリプトで 1 本ずつ）を済ませてから実物で生成する。LaTeX のログの overfull の行には表の値が出るので、数字を伏せて見る。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue）を書かない（D の番号は公開の逸脱なので書いてよい）。_style_check.py を回す（.tex / .bib も対象）。結果の値は \rv{<key>} と生成した表で読み、手で写さない。評価の語を使わない（登録 §6.1）。
⚠️ 判断の次の番号は 171、逸脱は D12（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
Skill: verify-before-claiming・citation-ssot・reproducibility-discipline・subagent-delegation・git-workflow（attack-me は原稿の段で）。応答は日本語。コミットは git add パス指定（-A 禁止）。heredoc にバックスラッシュを含めない（Write / Edit）。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX: G-GEAR は MiKTeX 25.12（PATH に無いので PATH="/c/Users/johnd/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH" を付ける）と雛形 C:\Users\johnd\tools\sn-template\sn-article-template。組むのは manuscript/build.sh（PYTHON=python）。
```

## §1 状態（2026-10-05 夕）

- ✅ **D10 の Windows の直した解析**（判断 166）: `experiment/results/d10/windows/e1_*.json`。登録の解析は G-GEAR でも 4 ファイルがバイト一致。3 セルの登録と直した解析がそろった。記録は `data.windows.md` の「Analysis under deviation D10」。
- ✅ **寄託先**（判断 167・研究者）: データ = Zenodo（データセットの記録・データ単独の DOI）、コードと材料 = GitHub の公開 repo。日程は M12（10-23〜27）。DOI の予約は先にしてよい（memory「Zenodo token」・公開は都度確認）。E3 の標本・`working` の観測ログ・パイロットの生ログを含めるかは M12 で研究者に聞く。
- ✅ **表の道具**（`manuscript/tools/results_tables.py`・selftest 52 件・変異 29 本すべて赤）:
  - 判断 168: 表 11（§6.8 の判定と推奨・要旨の (iii)）・表 12（E3・要旨の (iv)）・補遺の閉じた集合の全集合・層の表の D10 の「Corrected」列と値 `<cell>.d10.*.merge.differ`。
  - 判断 169: 表 10（文ごとの一致・主の範囲）と補遺 `text-agreement.tex`（全試行・合算と混合〔重みを §6.7 と照合〕・試行の差の 3 つの見方）。
  - 判断 170: 開いた集合の表 `table-open-set.tex`（K0・K1・K1+・長さの知識 2 つ）。
  - 生成物 `manuscript/generated/` は 11 ファイル（`--check` 一致）。補遺 `supplement.tex` は層の表・文ごとの一致・閉じた集合を読み込む。表 10〜12 と開いた集合はまだ main に読み込んでいない（結果の節で）。
  - ⚠️ 表 12 の数が 4 つ LaTeX のログ経由で画面に出た（判断 168）。推奨と問 4 の値は見ていない。
- ⚠️ 補遺の overfull は 29 → 55。増えたのはすべて「横向きのページの出力時」の型（既存の層の表と同じ・頁が増えた分）。main は HEAD と同じ（1 件）。

## §2 やること

1. **表 7（RF1）と KT1** を道具に足す。外枠の RF1 の行（`outline.md` の Claims and evidence）が中身の SSOT:
   - 計画と正解の一致を型ごとに（§6.3 の前半・Wilson 区間・層ごとと全体）→ `e1_l1.json` に `disagree`・`no_session`・`open_at_end` の鍵がある（★ 場所と形を先に確かめる）。
   - 届き方（`e1_delivery.json` の `observation` / `reference` の `reach`・`segments`・`timing`、`presses`・`send_lateness_ms`）。入力モードのキーの有無の 2 版（`all_presses` / `excluding_mode_keys`）。
   - フォーカスの喪失（`reference_focus_loss`）と、その試行の観測の行（AG1 の偽陽性と読む・主の値は変えない）。
   - 印の時刻（§6.9・時計のずれと経路の遅れが合わさったもの）→ どの結果のファイルのどこにあるかを先に確かめる（`e1_detection.json` の `config.clock_offsets_ms` と `uncorrected_blocks` が候補）。
   - Windows のパイロットの 2 つの欄の差（`experiment/pilot-windows.md`・結果のファイルではない）と「外部の時計なし」は本文で書く（生成しない）。
   - KT1: `timing.delay_ms` / `interval_error_ms`（n・平均・最小・5 %・中央・95 %・最大）と対にできなかった試行の数を、系と速さごとに（★ 速さごとの形があるか先に確かめる）。
2. **表 8 の macOS の 3 つの比較と予測の層**: 外枠は「Table 8: detection per speed and cell (three comparisons on macOS, the primary comparison on Windows)」。今の `table-detection.tex` は主の比較（`gt_obs`）だけ。`gt_pred`・`pred_obs` と予測の層（`diagnostics.prediction_layers`・macOS だけ）を足す。⚠️ D10 の登録の側の「値なし」の注は 32 か所すべて予測の層の `received_carry` の速さごとの併合の率（判断 159）→ `--` と D10 の注で出す。
3. **表 11 の「規則の性質」**（§6.8 の確率の表）: 結果ではなく登録の値。結果の節で §6.8 を引くか、静的な表として置くかを決める（判断 168）。
4. **結果の節を書く**（`sections/results-*.tex`・外枠の §6〜§9 の順: RF1 → 問 1・2 → 問 3 → 問 4 → 問 5）。値はすべて `\rv{}` と生成した表。評価の語を使わない（登録 §6.1）。要旨と結論は外枠の「Rule for the abstract」（Windows は「別の構成概念との一致」で macOS と並べない・CPU は系どうしを比べない）。D10 は登録と直した解析を横に並べる（補遺の層の表と `\rv{<cell>.d10.*}`）。開いた集合の表を本文に置くか補遺に回すかもここで決める。
5. **出荷**: 結果の節の後に、この枝の完了時レビュー（code-reviewer ∥ security-checker ＋ /cross-review〔パス限定・`run-codex-review.sh -- <paths>`〕）→ git-workflow ルール 6。⚠️ Codex の前に origin/main の `.codex/budget.json` も見る（memory「台帳はブランチごと」）。⚠️ この枝は `kit/e2/closed_set.py`（D8）と `kit/analysis/match.py`（D10）を変えたので、完了時レビューに含める。PR は結果の節の後（判断 155-3）。
6. 結果の節の後: 原稿の attack-me（stage `manuscript`・判断 145 の 10-18〜22）。

## §3 気をつけること

- ⚠️ 道具の変異のスクリプトは scratchpad の使い捨て（セッションをまたいで残らない）。新しい規則ごとに作り直す。「例外で落ちた」のでなく「狙った確認で赤」になることを、落ちた確認の名前で確かめる（判断 168 で 1 本直した）。
- ⚠️ 表の幅: この雛形は本文の幅が狭い。列の多い表は `sidewaystable`、補遺は `landscape` ＋ `longtable`。見出しの 1 語が列より広いと overfull になる（`\-` で分綴の位置を指定できる）。確認は一時の写しの `main.tex` の末尾に `\input` を足して `build.sh` で組み、HEAD の版と overfull を比べる（数字を伏せて）。
- ⚠️ heredoc の中の正規表現のバックスラッシュが壊れた（このセッションでも 1 回）→ スクリプトは Write で書いて回す。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
