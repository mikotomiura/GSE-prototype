# 次セッション — IME 論文: macOS の印の時刻・図・要旨と残りの節 → 原稿の attack-me

> 作成: 2026-10-05 夜（G-GEAR・表の道具の残り〔判断 171・172〕、結果の節の草稿〔判断 174〕、Windows の開いた集合の確認〔判断 173〕、完了時レビュー〔判断 175・176〕、PR を出したセッションの最後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 156・165〜176**、
> 外枠 `papers/ime-observation/manuscript/outline.md`（Rule for the abstract・Claims and evidence・Tables and figures・Open items）、
> 凍結した事前登録（§6.1〜§6.10・§10.7）・`deviations.md`（D1〜D10）・`data.md`・`data.windows.md`・`experiment/results/`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 docs/ime-manuscript-outline（origin と一致・PR の状態を gh pr view で確かめる）で作業する。
.steering/_handoff/next-session-ime-paper-manuscript-1.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 156・165〜176、outline.md、manuscript/tools/results_tables.py、凍結した事前登録、deviations.md（D1〜D10）、experiment/results/。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。値を見た後で表の道具の規則を変えない（変えるなら研究者に聞く）。評価の語を使わない（登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue）を書かない（D の番号は書いてよい）。_style_check.py を回す。
⚠️ 判断の番号は G-GEAR が 180〜（Mac が印の時刻で 177〜179 を使う）、逸脱は D11（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
Skill: verify-before-claiming・citation-ssot・reproducibility-discipline・subagent-delegation・git-workflow・attack-me（原稿の段）。応答は日本語。コミットは git add パス指定（-A 禁止）。heredoc にバックスラッシュを含めない（Write / Edit）。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: MiKTeX 25.12 は PATH に無いので PATH="~/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。雛形は ~/tools/sn-template/sn-article-template。組むのは manuscript/build.sh（PYTHON=python・相対パス可・出力先は原稿の外）。
```

## §1 状態（2026-10-05 夜）

- ✅ **表の道具**（`manuscript/tools/results_tables.py`・selftest 109 件・変異 66 本が狙った確認で赤）: 表 7（参照が確かめること）・KT1・表 8（macOS は 3 つの比較）〜12・補遺（層ごとの計画と正解・印の時刻・参照の KT1・全比較 × 全スコープの層ごとの検出・スコープの構成・予測の層・層ごとの 1 対 1 の一致・文ごとの一致・閉じた集合）。生成物 16 ファイル。
- ✅ **Windows の印の時刻**（§6.9・判断 171）: `results/windows/clock_sync_windows-msime-tsf.json`・117 ブロックすべてで印が見つかった。
- ✅ **結果の節の草稿**（判断 174）: `sections/results-agreement.tex`（§6）・`results-text.tex`（§7）・`recoverability.tex` と `cost.tex` の結果。
- ✅ **完了時レビュー**（判断 175・176）: code-reviewer（HIGH 0）・security-checker（HIGH 0）・Codex 2 巡（パス限定・5 ファイル）。指摘はすべて一次で確かめ、直すか理由を記録した。
- ✅ PR（番号は §2 の 0 で `gh pr view` して確かめる）。
- ⚠️ `build.sh` の表示で「result values not generated: 4」は macOS の印の時刻（意図どおり・§2 の 1 で消える）。

### 研究者に伝えた結果の要点（判断 173・174）

- 問 4: macOS の 2 セルとも `no_time`・`counts_only` が K = 10・100 で near chance にならず、**推奨は none**。
- Windows の問 4 の値は macOS OFF と同じ（2 つの計画が句・文字キー・時刻を共有し、違いは S2 と S4 の手順だけ —— 判断 173 で回し直して確かめた）。原稿にも書いた。
- macOS ON は計画と正解の食い違いの多くが「セッションなし」（S10 の遅い・中）。Windows の参照は IME が消費しないキーしか受け取らないので、参照の側の KT1 は対にできない。

### 研究者が覆せる判断（未確認）

- ★ **「全試行の範囲」の読み**（判断 175）: 外枠の「the same range over all trials」を「全試行の側で同じ作り方（30 試行以上の層）をやり直す」と読んでいる（値を見る前に実装）。もう一方の読み（主の範囲で選んだ層の全試行の区間）にするなら `abstract_values` の `kept` 1 か所。
- 結果の節の**定性的な記述**（「OFF は除外なし」「文ごとの abandonment rate と fraction of time converting の偏りは全セル・全速さで負」など）は表を読んで書いた —— 結果のファイルが変われば手で直す（`--check` は捕まえない・判断 174 に一覧）。

## §2 やること

0. **PR の状態**: CI が緑なら merge・main の CI を確かめる（git-workflow ルール 6）。赤なら 1 回だけ原因を見て報告。
1. **macOS の印の時刻**（★ Mac で・専用の引き継ぎ `next-session-ime-paper-mac-markers.md`。G-GEAR では Mac の枝を取り込むだけ）: macOS のタグの `kit/pilot/clock_sync.py`・`seal_obs.py`（`git archive`・LF）・`obs.jsonl` の**写し**から `seal_obs.py` でキーの行だけに → 印の仕様 `{"oracle_keys": ["left","right","left","right"], "gt_vks": [123,124,123,124], "obs_categories": ["navigation","navigation","navigation","navigation"], "max_gap_ms": 300}`・窓は既定 → `results/clock_sync_<cell>.json`（2 セル）→ `data.md` に節（`data.windows.md` の「Marker times of section 6.9」の形）→ 道具で生成し直す（生成されていない値 0 になる）→ 外枠の Open items を「済み」に。
2. **図 2〜5**（外枠の Figures）: 道具は標準ライブラリだけ。作図を別のスクリプト（matplotlib など）にするか、TeX で描くかを決める（依存を足すなら reproducibility の記録）。図 1（構成）・`fig:components` も。
3. **要旨と結論**（外枠の Rule for the abstract・§13）: (i)〜(iv) を `\rv` で。250 語に収まらなければ (iv)、次に (ii) を本文に回す。Windows は「別の構成概念との一致」として macOS と並べない・CPU は系どうしを比べない。
4. **残りの節**: §1（序論）・§11（推奨・`sec:...`）・§12（限界・`sec:limitations`）・§13（結論）・Declarations・Open Practices・Data availability（`sec:availability`）。外枠の Section plan と Claims and evidence（RE1〜RE5）に沿う。
5. **原稿の attack-me**（stage `manuscript`・判断 145 の 10-18〜22）: 外枠の round 1・2 の引き継ぎを渡す（判断 150-4）。
6. **M12**（判断 145・167）: Zenodo（データ・DOI の予約は先にしてよい・公開は都度確認）と GitHub の公開 repo。E3 の標本・`working` の観測ログ・パイロットの生ログを含めるかを研究者に聞く。

## §3 気をつけること

- ⚠️ 表の道具を直したら selftest と変異（scratchpad の使い捨て・狙った確認で赤になることを FAIL の名前で確かめる）。確認どうしが干渉して変異が緑になることがあった（判断 175・176）—— 陰性の確認は、ほかの確認が先に捕まえない形に作る。
- ⚠️ `run-codex-review.sh` は 1 回で 3〜8 万トークン使う（判断 175）。台帳はブランチごとに記帳される —— 回す前に origin/main の台帳も見る・merge のときは和（判断 175 の merge で 238,050 / 5 回）。書き戻しで CRLF が混ざるが、`git add` で LF になる（コミットした blob を確かめる）。
- ⚠️ heredoc の中のバックスラッシュが壊れた（このセッションで 2 回）→ スクリプトは Write で書いて回す。
- ⚠️ `build.sh` の雛形を `/c/...` の形で渡すと TeX が見つけられなかった（判断 175 で直した・今は相対・MSYS の形どちらでも可）。
