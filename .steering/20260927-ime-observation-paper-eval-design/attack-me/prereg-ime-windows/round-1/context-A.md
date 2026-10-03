# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `prereg`・対象物 Windows の追補・round 1）

作成: 2026-10-03（Surface・メイン）。対象物は枝 `feature/ime-m6-windows-addendum` の `53eec8f2` で commit 済み。

## 対象物

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md` の **§10 Windows addendum**（未凍結・ファイルの SHA-256 `6fefb390a15b70cc5f36c8cb0016fb70efcd746dcad0531279a09afb2e97b817`）と、追補が持ち込んだ公開物とコード（下の「変わった箇所」）。
- §1〜§9 は macOS のセルについて **2026-10-02 に凍結・OSF に登録済み**（タグ `ime-observation-prereg-macos`）。§8 は「追補が変えてよいもの」を定める。★ **§1〜§9 は査読の対象ではない**（文脈として読む）。§10 とそれが参照する公開物・コードが、§8 の枠と §1〜§9 の規則に照らして十分か・正しいかを見る。
- 投稿先: *Behavior Research Methods*（BRM）。追補は凍結の後に OSF Registries に登録し、Windows の最初の計測より前であることを示す。
- stage `prereg`・round 1: 凍結してよいか（accept）／直してから凍結（minor）／直して再査読（major）／計画から立て直す（reject）を判定する。**原稿（論文本体）はまだ無い**。それ自体を欠陥にしない。
- ⚠️ パイロットの生ログ（`*.jsonl`）は一覧に無い。`pilot-windows.md` の数は、文書の中での整合と、コードが数えるものとの対応で見る。

## macOS の凍結のタグから変わった箇所（`git diff ime-observation-prereg-macos..53eec8f2 -- papers\` から・メインがまとめた）

| ファイル | 何が変わったか |
|---|---|
| `experiment\preregistration.md` | §10 Windows addendum を References の前に足した（10.1 追補の状態と、タグの差に現れる変更の一覧／10.2 範囲〔Windows の 1 セル: MS-IME・TSF の参照入力欄〕／10.3 道具と機械／10.4 手順の §2.3 との違い／10.5 計画〔設定・命令・SHA-256・所要時間〕／10.6 正解と範囲〔`win_tsf` の規則・逸脱 D3 による長い試行〕／10.7 停止規則とデータの収集／10.8 問 5 の Windows／10.9 凍結の前にあるデータ／10.10 Windows の限界）。凍結の印（冒頭の `frozen_at:` / `sha256:`）は**まだ替えていない** |
| `experiment\deviations.md`（新規） | 逸脱 D1（Windows の S4 を Esc 3 回）・D2（解析の計画の照合に Windows のセルの計画）・D3（Windows のセルの範囲を正解の長さで）の日付・理由・影響 |
| `experiment\pilot-windows.md`（新規） | Windows の較正パイロットの報告（設定・run・所見と直し・呼び出し列・正解の定義・計画と正解の一致・参照入力欄の選択・時計・到達と停止規則の点検・問 4 の割り当ての点検・1 試行の時間・計測への帰結・生ログを預ける基準） |
| `experiment\plan_config.windows.json`（新規） | 生成器の設定（`_note` 以外は `plan_config.macos.json` と同じ値） |
| `experiment\notes.md` | macOS の OSF の登録の記録（タグの後に足したもの・追補とは関係しない） |
| `kit\gen\generate_plan.py` | `_PROFILES` に `cancel_converted` を足し（windows は Esc 3 回・macOS の 2 つは 2 回）、S4 の照合をそれで読む（D1）。windows の `after_digit` を `["enter"]`（§8 の範囲）。コメント |
| `kit\gen\recipes.json`・`kit\gen\recipes.macos-live-off.json` | `os.windows` の S4 に Esc を 1 つ・S8 に Enter を 1 つ（2 つのファイルの `os.windows` は同じ） |
| `kit\analysis\pipeline.py` | 定数 `REGISTERED_PLAN_SHA256_WINDOWS` と `_plan_matches_cell` の Windows の分岐（D2）。`run_stages` で Windows の計画のとき `gt_scope` から範囲を作り、予測の層の診断を null に（D3）。`PRIMARY_NOTE_WINDOWS`・`long_trials_from`・`registered_plan_sha256_windows` を Windows のセルを解析したときだけ記録。`make_synthetic_run` に `os_name`。selftest `_case_windows_cell` |
| `kit\analysis\gt_scope.py`（新規） | 正解のセッションが `limit_ms` 以上の試行を「長い」とし、予測と同じ形式で `match.py` に渡す（D3） |
| `kit\run\cell.windows.json`・`focus_windows.py`・`away_windows.py`・`start_windows.py`・`README.windows.md`（新規） | Windows のセルだけが使うセルの例・前面化と IME のオン・S15 の移り先の窓・前面ロックを越える起動の包み・手順書 |

変わっていないもの（主なもの）: `experiment\config.json`・`experiment\SEED`・`experiment\gt_rules.json`（Windows のブロックも変えていない → 凍結の `sha256:` は同じ値になる）・`kit\analysis\` の他のファイル・`kit\emit\`・`kit\run\run_cell.py`・`kit\logger\`・`kit\refinput-windows\`。

## 読んでよいファイルの一覧（これだけ・絶対パス・1 行 1 件）

★ 第 1 群（先に読む: 対象物と、対象物が名指しする設定・手順・報告）

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\deviations.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\pilot-windows.md`
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
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\gt_scope.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\match.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\gt_sessions.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\l1.py`
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
