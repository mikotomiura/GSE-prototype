# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `prereg`・対象物 Windows の追補・round 2）

作成: 2026-10-03（Surface・メイン）。対象物は枝 `feature/ime-m6-windows-addendum` の `f32087e8` で commit 済み（公開物とコードを最後に変えたのは `b41c00b3`）。

## 対象物

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md` の **§10 Windows addendum**（未凍結・ファイルの SHA-256 `6fefb390a15b70cc5f36c8cb0016fb70efcd746dcad0531279a09afb2e97b817`）と、追補が持ち込んだ公開物とコード（下の「変わった箇所」）。
- §1〜§9 は macOS のセルについて **2026-10-02 に凍結・OSF に登録済み**（タグ `ime-observation-prereg-macos`）。§8 は「追補が変えてよいもの」を定める。★ **§1〜§9 は査読の対象ではない**（文脈として読む）。§10 とそれが参照する公開物・コードが、§8 の枠と §1〜§9 の規則に照らして十分か・正しいかを見る。
- 投稿先: *Behavior Research Methods*（BRM）。追補は凍結の後に OSF Registries に登録し、Windows の最初の計測より前であることを示す。
- stage `prereg`・**round 2**（round 1 の指摘を受けて直した版）: 凍結してよいか（accept）／直してから凍結（minor）／直して再査読（major）／計画から立て直す（reject）を判定する。**原稿（論文本体）はまだ無い**。それ自体を欠陥にしない。
- ⚠️ パイロットの生ログ（`*.jsonl`）は一覧に無い。`pilot-windows.md` の数は、文書の中での整合と、コードが数えるものとの対応で見る。

## round 1 から変わった箇所（`git diff 53eec8f2..f32087e8 -- papers\` から・メインがまとめた）

★ round 2 は、この表の箇所を重点に見る。round 1 の版の「タグからの変更」（§10 の全体・D1〜D3・`pilot-windows.md`・新しい道具）は引き継ぎ（`carryover-*.md`）に書いた。

| ファイル | 何が変わったか |
|---|---|
| `experiment\preregistration.md` | **§10 を書き直した**（10.1〜10.11）: 10.1 状態（凍結の印の扱い・門が 2 つの凍結を区別しないこと・タグの差の一覧を網羅）／10.2 範囲（§1.1 を 10.3 が置き換える）／**10.3 Windows のロガー**（新設: IME の窓の WinEvent の経路と cloak の経路・切り替えの条件・150 ms の畳み込み・20 秒の打ち切りは cloak の経路だけ・25 秒の安全弁・`nav`/`abandon`・行の時刻・記録するキー・構成概念の違い）／10.4 道具と機械（TSF の参照が編集の終わりから合成を推定すること・既定の設定・計測の時の状態は約束の形）／10.5 手順（S14 のキー）／10.6 計画（Windows のタグのファイルの SHA の表・所要時間 12〜13 時間）／**10.7 正解・範囲・解析**（`windows_def` を主に・長い試行は oracle の送出の幅〔D3〕・感度 `under_limit_gt_duration`・境界の帯・層ごとの表・over_limit の読み方・診断・行 0 の扱い・**問 4 の Windows の命令と推奨の扱い**・**Windows の解析の命令**）／**10.8 停止規則**（D2 の参照の検査・**D4**・`data.windows.md`）／10.9 問 5（CPU の量の違い・`cpu_all_zero` は不十分）／10.10 凍結の前のデータ（封をした行を解析しないこと・IMM の run は寄託しない）／10.11 限界 |
| `experiment\deviations.md` | D1〜D4 と「The macOS cells are unchanged」（命令とハッシュ）に書き直した。**D3 を「送出の幅」に改めた**・**D4 を新設**・D2 に参照の検査を足した |
| `experiment\data.windows.md`（新規） | Windows の run の一覧・寄託・点検の表（D4 と `src` の列） |
| `experiment\pilot-windows.md` | 数の言い方（各 run・参照に届いた押下の意味）・参照の選択の理由・計測への帰結・Raw logs（IMM の run は寄託しない） |
| `kit\analysis\scope_windows.py`（新規・`gt_scope.py` を置き換え） | 送出の幅の長い試行・正解の長さの版・境界の帯・層ごとの集計・診断 |
| `kit\analysis\pipeline.py` | `observation_abort_segments`・`reference_abort_reasons(dlv, os_name)`（D4）・`WINDOWS_GT_SRC` と `_gt_src`（D2 の参照の検査）・`run_stages` の範囲と感度と診断・`PRIMARY_NOTE_WINDOWS`・説明文・selftest `_case_windows_cell` |
| `kit
un\cell.windows.json`・`kit
un\README.windows.md` | パスを公開物の根からに・解析の入口の案内・注記を §10.8 の参照に |

## 読んでよいファイルの一覧（これだけ・絶対パス・1 行 1 件）

★ 第 1 群（先に読む: 対象物と、対象物が名指しする設定・手順・報告）

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\deviations.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\pilot-windows.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\data.windows.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\plan_config.windows.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\plan_config.macos.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\config.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\gt_rules.json`
- `C:\GSE-prototype\papers\ime-observation\experiment\SEED`
- `C:\GSE-prototype\papers\ime-observation\experiment\run.sh`
- `C:\GSE-prototype\papers\ime-observation\experiment\notes.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\data.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\env.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md`
- `C:\GSE-prototype\papers\ime-observation\kit\run\README.windows.md`
- `C:\GSE-prototype\papers\ime-observation\kit\run\cell.windows.json`
- `C:\GSE-prototype\papers\ime-observation\kit\run\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\recipes.json`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\recipes.macos-live-off.json`
- `C:\GSE-prototype\papers\ime-observation\kit\emit\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\emit\keymap_windows.json`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-windows\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\pilot\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\e3\README.md`

★ 第 2 群（コード。記述が実装と合っているかを確かめる箇所だけ開く。上の「変わった箇所」を優先する）

- `C:\GSE-prototype\papers\ime-observation\kit\analysis\pipeline.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\scope_windows.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\match.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\gt_sessions.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l1.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l2.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\open_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\main.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\delivery.py`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\generate_plan.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\run_cell.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\focus_windows.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\away_windows.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\start_windows.py`
- `C:\GSE-prototype\papers\ime-observation\kit\emit\backend_windows.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\closed_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-windows\src\tsf.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-windows\src\bin\refinput_tsf.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_cloak.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\ime_winevent.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\cloak.rs`
- `C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\keyboard.rs`

⚠️ 一覧に無いもの（`kit\corpus\data\` の刺激のコーパス、他の `kit\` のファイル、`papers\ime-observation\` の外）は読まない。⚠️ **Grep は一覧のファイルだけを対象にする**（ディレクトリ全体を Grep しない）。生ログ（`*.jsonl`・`*.ndjson`）・`runs\`・`sealed\` は一覧に無い。

## 測った値（メインが機械で測った・2026-10-03）

測り方は macOS の round と同じ（4 字下げのコマンド行を除き、空白で区切った語のうち英数字を含むものを数えた）。

| 項目 | 値 |
|---|---|
| §10 の語数 | 1,927 語（小見出し 10・字下げのコマンド 1 つ） |
| `deviations.md` | 1,087 語（D1〜D3） |
| `pilot-windows.md` | 2,468 語（表 6） |
| `README.windows.md` | 606 語 |
| タグからの差分 | 15 ファイル・+1,449 / −25 行 |

## 投稿規程の一次の抜粋（この round で取り直した）

- URL: `https://link.springer.com/journal/13428/submission-guidelines`（取得 2026-10-03・`curl -sL`〔cookie つき〕で HTML を取り、テキストにして逐語を照合した。原本の SHA-256 `1df2819e4913c9d9b4c9dae26737becb2680c5bae19bf617805d82a7a814834c`）。以下はすべて**照合済み**（原文に逐語で在る。J2 の "Initiative's" は原文では曲がった引用符）。

| # | 要件 | 逐語 | 照合 |
|---|---|---|---|
| J1 | 誌の範囲 | "Authors are encouraged to write their articles in such a way that readers can easily use the materials in their own work (e.g., by making stimuli and programming code available)." | 照合済み |
| J2 | TOP Level 2 | "follows the Open Science Initiative's Level 2 Transparency and Openness Guidelines. … BRM readers want practical solutions." | 照合済み |
| J3 | Open Practices Statement | "All submitted manuscripts must include an Open Practices Statement immediately prior to the References section of the paper." 例文: "… was preregistered (url for the preregistration)." | 照合済み |
| J4 | 生データの公開 | "… including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes …" | 照合済み |
| J5 | 投稿時の確認 (d) | "the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power." | 照合済み |
| J6 | n の決め方 | "the Method section should make clear what criteria were used to determine the sample size." | 照合済み |
| J7 | 精度で設計する | "designing experiments to measure effects to a desired degree of precision (range of confidence interval)." | 照合済み |
| J8 | 共変量 | "Covariate analyses should either be planned in advance (and in that case would benefit from preregistration) or be described as exploratory." | 照合済み |
| J9 | 除外 | "Best practice is to set inclusion/exclusion criteria in advance (and pre-register where appropriate) and stick to them …" | 照合済み |
| J10 | 要旨 | "There must be an abstract of no more than 250 words." | 照合済み（⚠️ 事前登録には適用されない） |
| J11 | 事前登録の書式・追補・逸脱 | 規程は事前登録の書式・必須の節・追補や逸脱の扱いを定めていない（原文の "preregistration" は 3 か所で、例文・共変量・変数の選択の文だけ） | 規定なし（取得した範囲の原文に該当の文が無い） |
