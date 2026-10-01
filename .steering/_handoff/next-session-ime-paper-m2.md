# 次セッション — IME 論文: M1 の後（M1 の枝の PR → M2 の残り → M3 の事前登録）

> 作成: 2026-10-01（G-GEAR で、Mac の M1 と再パイロットの push を確かめたセッションの最後に）。
> 前の handoff（`next-session-ime-paper-after-merge.md`）の後継。前のものは読まなくてよい（§5・§6 の結果はこのメモに取り込んだ）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の次のファイル。状態は着手時に `git fetch` で測り直す。
> - `pilot-macos-1-notes.md`（M1 と再パイロットの記録）
> - `decisions.md`（判断 79・80）
> - `tasklist.md`
> - `_issue-plan.md` §5（マイルストーンの Done）
> - `blockers.md`（B15）
> ★ M1 の作業は枝 **`feature/ime-m1-pilot`** にある（`19c537c0` まで・**PR はまだ**）。このメモも同じ枝に置いた。

## §0 打ち込む用

> ★★★ **A は 2026-10-01 に終わった**（G-GEAR）。PR #283 で main に入った（merge `0081efe7`・main の CI success）。経緯は判断 81〜84 と `tasklist.md`。→ **次は B**。B は main から新しい枝を切って始める。
> ⚠️ B を始めたら、最初に `tasklist.md` の「⚠️ Mac: 024-acceptance.sh を回し…」の項目を済ませる。一覧の SHA-256 を G-GEAR の値と比べる（判断 68）。あわせて `build.sh` と、例の `focus_cmd` の前面の確認（§3-7）を確かめる。
> ⚠️ 生成器は、パイロットの config（マーカー ← → ←・`nav_count_max` ≥ 3）だと計画を作らずに止まるようになった（§3-6・判断 84）。本番の n・think を研究者に確かめるときに、マーカーの長さもあわせて決める。

> ★★★ **B の大半は 2026-10-01 に終わった**（Mac・枝 `feature/ime-m2-gt-rules`・判断 85〜89）。
> - 済み: Mac の確認（024 の SHA-256 一致・`build.sh`・`focus_cmd`）／本番の n = 75・think 0.2〜20 秒・マーカー ← → ← →（判断 85）／`experiment/gt_rules.json`（判断 86）／持ち越しの除外 `carry_over`（判断 87）／`experiment/pilot-macos.md`／完了時レビュー 3 系統（判断 88・89）。
> - **残り（M2）**: パイロットの生ログの預け方。`pilot-macos.md` の「Raw logs」に書いた基準（runner の run だけ・観測の key 行と gt の `key_down` の両方が送出に対応・手打ちは預けない）を検査する道具（`reach.py` の逆向き）を作り、`experiment/data.md` の手順（`pipeline.py --pack`）で預ける。
> - **M3 に持ち越す論点**: (1) ライブ変換 ON で、先頭が自動確定した後に取り消したセッション（`pilot2-on` の取り消し 27 試行中 11）を、観測側の放棄とどう照合するか。診断用のフィールドを足すかも含めて決める（判断 88）。(2) `settle_ms` を事前登録で固定する（50 ms の窓の前提・判断 89）。(3) 本番の生成の config（n・think・マーカー・`nav_count_max`）のファイルを作って凍結する（判断 85）。(4) `cell.example.json` の `learning`・`predictive_candidates` の記述を、パイロットの実際に合わせる。

> ★★★ **2026-10-01（G-GEAR）**: PR #285 の後の main（`500c5685`）で G-GEAR の確認が済んだ（024 の一覧の SHA-256 が Mac の `bc2e6816…5f3c` と一致・Windows で回る 22 本は SCOPE / GUARD を除いて失敗 0 件・`tasklist.md`）。
> - **M3（事前登録の下書き）を G-GEAR で始めた**。研究者に 8 問 → 判断 90〜97（上の (1) は判断 96 で「照合はそのまま・層別の診断を足す」に決まった）。残りの段取りは `tasklist.md` の M3 の項目。
> - ⚠️ M2 の残り（生ログの預け方）は、生ログが Mac にしか無いので Mac で行う。M3 と並行してよい（触るファイルが重なるのは `pilot-macos.md` だけで、こちらは Clocks の 1 文、Mac は Raw logs の節）。
> - ⚠️ Mac で確かめること: パイロットの生成の config の全体（`cand_index_max`・`key_hold_ms`・`iki_sigma`・`inter_trial_ms`・`marker_gap_ms`）。repo の記録は速さ・think・n・マーカーだけ（判断 90）。

### A. M1 の枝の PR（どちらの機械でも・先に）〔済み・PR #283〕

```
git fetch → git switch feature/ime-m1-pilot → git pull --no-rebase（force しない）。
.steering/_handoff/next-session-ime-paper-m2.md を読んで、§2 の「PR の前にすること」から始めてください。
GENERATOR_VERSION を上げ、完了時レビュー（/cross-review: code-reviewer ∥ security-checker ∥ Codex）を回し、
push → PR → CI 緑なら merge → main の CI まで（git-workflow ルール 6）。
Skill: verify-before-claiming・subagent-delegation・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。
```

### B. M2 の残り（Mac・パイロットの gt ログは Mac の `~/ime-pilot/runs/` にだけある）

```
git fetch。A の PR が merge 済みなら main から新しい枝（feature/ime-m2-gt-rules など）を切る。まだなら feature/ime-m1-pilot のまま。
.steering/_handoff/next-session-ime-paper-m2.md を読んで §3 の M2 の残りを進めてください。
最初に、本番の n と think の上限（1 セル約 10 時間）を研究者に AskUserQuestion で確かめる（推奨と理由を添える）。
次に、正解の定義（gt_rules の mac_nstic）を再パイロットの呼び出し列の型から決める。⚠️ 観測側の ImeShadow の封印は開けない。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-01 の終わり）

- main は `97381a7b`（#280 まで）。
  - #278: M0 のコーパス
  - #279: attack-me skill と、査読者役の専用エージェント `paper-reviewer`
- **M1（macOS の較正パイロット）は Mac で終わった**（`pilot-macos-1-notes.md`・判断 80）。
  - 1 回目で次の所見が出た:
    - 変換の後の Enter 1 回では確定しない。macOS 27・ライブ変換 ON の IME 本来の挙動で、研究者の手打ちでも同じ。
    - マーカー F13 / F14 が観測側に届かない。
    - 参照入力欄に bundle id が無い。
    - 最初の IME の状態が計画に無い。
    - 本番の所要時間が見積もりより長い。
  - 直したもの:
    - macOS の recipes: Enter 2 回・数字の後に Enter・Esc 4 回。
    - マーカー: ← → ←。
    - `build.sh` の `.app`（bundle id `local.ime-observation.refinput`）。
    - `focus_cmd` でかなキーを押す。
  - 再パイロットの結果:

    | run | 試行 | 持ち越し | 時計（中央値） |
    |---|---|---|---|
    | ON | 126 | 2（S8・S10 各 1） | obs − oracle 1.0 ms |
    | OFF（ON 用の手順のまま） | 117 | 0 | obs − oracle 1.5 ms |
    | OFF 用の手順書 `kit/gen/recipes.macos-live-off.json`（`verify-off`） | 39 | 0 | — |

  - ImeShadow は封印して読んでいない。
- G-GEAR での検査（枝の `3e729f99`・clean な worktree・2026-10-01）:
  - `kit/check.sh`: 27 の selftest がすべて緑。`--compile`: 28 ファイル緑。`_style_check.py`: 違反 0 件。
  - Windows で回る acceptance 22 本: **SCOPE を除いて失敗 0 件**。SCOPE の赤は、main の上では比較の基準の枝が決まらないためで、B15 として記録済み。macOS 専用の 004 / 007 / 012 は exit 2。
  - 024 の書き出しの一覧の SHA-256: `ba963bd9181d359600fa50601f5c3078e02ccc6b1fb39c668576a68b0597cdc1`（91 ファイル・`3e729f99`）。⚠️ `19c537c0` は `papers/` を変えたので、値は変わっている（まだ測っていない）。
  - `19c537c0` の OFF 用の手順書を検算した: Windows の節と `kana_layout` は `recipes.json` と同一。差は macOS の S1・S5・S7・S11・S12・S13・S15 だけ。
- Codex の台帳: main の 2026-10-01 は 199,404 / 5 回（上限 300,000）。M1 の枝は台帳を変えていない（merge のときは main 側のまま）。

## §2 M1 の枝の PR（`feature/ime-m1-pilot` → main）の前にすること

> ★ **2026-10-01（G-GEAR）に 1〜7 を進めた**（判断 81〜83）。1〜4 は `5e9f873a`。6 の merge は `5a9cc805`（衝突は Mac の §6 を §7 にした）。5 の Claude の 2 系統は CRITICAL / HIGH 0 で、指摘は判断 82 のとおり直した。Codex は研究者の選択で上限を一時的に 350,000 に上げて 1 回回した（P1 2 件・P2 2 件を判断 83 のとおり直し、上限は 300,000 に戻した）。2 巡目は code-reviewer で、足した規則の境界条件を見た（HIGH 1・MEDIUM 5 を判断 84 のとおり直した）。結果と PR の番号は `tasklist.md` を見る。下の本文は当時の指示として残す。

1. **`GENERATOR_VERSION` を上げる**（今は `"1.1.0"`・`kit/gen/generate_plan.py:45`）。
   - `kit/gen/README.md:92-93` は「`recipes.json` の手順の意味が変わったら上げる」と定めている。
   - M1 で macOS の手順を変え、OFF 用の手順書も足したので、この規則に当たる。
   - この値を固定している acceptance は無い（G-GEAR で grep 済み）。上げても検査は壊れない。
2. **OFF 用の手順書は selftest の外にある**（README 自身が「selftest は `recipes.json` だけを見る・OFF 用は実機で確かめた」と書く）。
   - selftest で OFF 用の手順書も照合するか、実機の確認だけにするかを決める。
   - 照合するなら、`_scenario_checks` に OFF の分岐が要る（今の macOS の分岐は Enter 2 回を期待する）。
3. 〔軽い〕`_scenario_checks(..., os_name="macos")` の既定値。今は selftest の 2 か所だけが呼び、どちらも OS を渡している。既定を無くすかどうか。
4. 〔軽い〕`kit/run/cell.example.json` と実際のパイロットの条件の食い違い:
   - `learning` は「毎ブロックでリセット」だが、パイロットはリセットしていない（研究者の判断）。
   - `layout` は「US keyboard」だが、パイロットは JIS。
   - 例として直すか、`pilot-macos.md` に条件として書くか。
5. **完了時レビュー**: code-reviewer ∥ security-checker ∥ Codex（`scripts/run-codex-review.sh <base>..<head> -- <paths>` でパス限定）。
   - この枝にはコードの変更がある: `generate_plan.py`・`simulate_obs.py`・`build.sh`・recipes 2 本。
   - 回す前に、origin/main の台帳の今日の値を見る。
6. **merge で衝突が 1 件見込まれる**: `.steering/_handoff/next-session-ime-paper-after-merge.md`。
   - main（G-GEAR の §6）と、この枝（Mac の §6）が、どちらも末尾に「§6」を足している。
   - 両方を残し、片方を §7 にする。
7. merge の後の注意:
   - main の上の acceptance は、SCOPE を除いて数える（B15）。
   - 書き出しの一覧の SHA-256 は、同じ commit どうしで両機械の値を比べる（判断 68）。

## §3 M2 の残り（`_issue-plan.md` §5 の M2・Mac）

1. **本番の n と think の上限を研究者が決める**。
   - 現状: 1 試行は待ちを含めて約 11 秒で、n = 75 の 1 セルは約 9.5〜10 時間（design.md §1.5 の見積もりは 7.5 時間）。
   - 材料: think（0.2〜20 秒）は `dwell_ms` の誤差と 20 秒打ち切りの境界を見るための幅。20 秒を超える場合は S13 が別に受け持つ。
   - 数値は `pilot-macos-1-notes.md` から一次で取り直す。
2. **正解の定義**（`gt_rules` の `mac_nstic`・M2 の Done は `experiment/gt_rules.json` と recipes の差分が根拠つきでコミットされていること）。
   - ON の呼び出し列の型は、どのシナリオも 2 つの形に収まった。違いは、打鍵の途中の自動確定 `(set_marked → insert_text)*` の有無だけ。
   - 残る型の外れ: S12（かな入力）で 1 回目の Enter が確定し、2 回目が改行になった 2 件。S8 と S10 の持ち越しが各 1 件。
   - OFF の型は、OFF 用の手順書でまだ数えていない（n = 3 程度の再パイロットが要るか）。
3. **`experiment/pilot-macos.md`**（公開物・学術的な英語・正解の定義が決まってから書く）。
   - ⚠️ M1 の Done（`_issue-plan.md` §5）は次を挙げる: 呼び出し列の型・**oracle 一致率**・時計の差とドリフト・フックへの到達率・1 試行の実時間。このうち oracle 一致率は、内部の記録にまだ無い。
4. **パイロットの生ログの置き場**。design.md §1.1a は「パイロットの生ログも公開物に含める」と書く。
   - `experiment/data.md` の預け方に従う（`kit/analysis/pipeline.py --pack`）。
   - 生ログは今 Mac の `~/ime-pilot/runs/` にあり、git の外。
   - ⚠️ **預ける前に除外の基準を決めて書く**（security-checker の MEDIUM・判断 82）。研究者は参照入力欄とテキストエディットで手打ちの対照をしている（`pilot-macos-1-notes.md`）。単体ロガーはシステム全体の打鍵を観測するので、人が触った run を預けると研究者本人の打鍵の時刻と長さが公開される（Zenodo の DOI は取り消せない）。
     - (a) 預けるのは計画どおりの run（runner の manifest があり、aborted でないもの）だけ。
     - (b) 各 run で「oracle に対応する押下が無い観測の key 行」が 0 件であることを確かめる。⚠️ 今の `reach.py` は oracle → 観測の向きしか数えない（逆向きを数える道具が要る）。
     - (c) 手打ちの探査（`enter_probe*`・`esc_probe*`）の出力と、手打ちの対照の記録は対象外と明記する。
5. IME の学習をリセットしなかった（研究者の判断）ことは、`pilot-macos.md` の条件に書く。
   - あわせて、パイロットの実際の IME の設定を書く。`cell.example.json` の `predictive_candidates` は `"off"` だが、S10（予測候補を Tab で選ぶ）は両方の macOS の手順書で既定で有効（code-reviewer の範囲外の指摘）。
6. ⚠️ **マーカーの長さ**（判断 82・84）。生成器は、計画を作るときに「観測に残るマーカーが矢印だけなら、試行の中の矢印の最長の連続より長い」を検査するようになった。パイロットの ← → ← は、S7 が矢印を 3 回続けて押す計画（`nav_count_max` ≥ 3）では exit 2 になる。E2 は検査しない（すでに走った計画を読むため）。
   - 本番の config を決めるときに、研究者が次のどちらかを選ぶ（推奨と理由を添えて AskUserQuestion）: 4 打鍵のマーカー（← → ← →）にする／`nav_count_max` を 2 以下にする。
   - マーカーを変えたら、`pilot/README.md` の例の JSON（`oracle_keys` / `gt_vks` / `obs_categories`）と e2/README の記述も合わせる。
7. Mac で確かめること（G-GEAR では試せない）:
   - `refinput-macos/build.sh` を回す（bundle id の検査を `[[ =~ ]]` と `LC_ALL=C` にした。macOS の bash 3.2 で通るか）。
   - ⚠️ `cell.example.json` の `focus_cmd` に、かなキーを押す前の前面の確認を足した（判断 83・84。0.2 秒おきに 5 回まで読み直してから確かめる）。式は送出側の `FRONT_QUERY` と同じだが、**この数行は実機で試していない**。参照入力欄を前面にした状態で通ること、別のアプリが前面だと非 0 で止まること（`run_cell.py` がブロックの前に abort する）を、短い run で確かめる。
   - ⚠️ `focus_cmd` は送出フラグがあるときだけ走るようになった（判断 83）。`dryrun` で前面化を試すときもフラグが要る。
8. **持ち越しの扱い**（Codex の P2・判断 83）。ON の再パイロットで S8 / S10 が各 1 件、未確定の文字列を次の試行へ持ち越した。キー列の照合では見つからず、`gt_sessions.py` の `oracle_agreement` は不一致を数えるだけで除外はしない。
   - 正解の定義（`gt_rules`）と事前登録（M3）で、持ち越した試行と次の試行をどう扱うか（除外か・別に数えるか）を決める。

## §4 その先のマイルストーン

- **M3: 事前登録の下書き（macOS 版）** → ★ **凍結の前に `attack-me`（stage `prereg`）でプレ査読** → 凍結 → OSF Registries への登録（研究者・判断 73）。
  - 査読者役と監査役は `paper-reviewer` で起動する（道具は Read・Grep・Glob だけ）。
  - 下書きは起動の前に commit する。
  - `prereg` では、固定の根拠のファイルまで「読んでよいファイルの一覧」に入れる（`run.sh` → `pipeline.py` → 部品・`config.json`・`SEED`）。
  - 封印物（`sealed/`）がある時期なので、起動の前に研究者に知らせる。`Read` は構造では縛れない。
- **M5: Windows の較正パイロット**（G-GEAR）。Windows の recipes はまだ仮説のまま。MS-IME でも Enter や Esc の効き方が想定と違う可能性がある。
- **M12（公開）の前に直すこと**: 書き出し器は公開 repo 用の `.gitattributes` を作らない（判断 84）。手順書・コーパス・ロガーの manifest・`experiment/*.json` などは SHA-256 を比べるので、公開 repo を `core.autocrlf=true` で clone すると値が食い違う。書き出しに `.gitattributes`（`eol=lf`）を足す。
- **M12（公開）の前の確認**（研究者・未回答）。M0 の作品のうち『人間失格』『斜陽』『堕落論』『夫婦善哉』は、著者が 1945 年より後に没し、1931 年以降に出版されている。このため米国で保護が復活している可能性がある（私の法的な読みで、専門家の判断ではない）。

## §5 気をつけること

- ⚠️ 凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない（判断 11・封印は開けない）。人の打鍵データを使わない。新しい公開 repo を作らない（M12・研究者）。
- ⚠️ **OFF のセルは、同じ手順書を最後まで通して使う**。
  - 計画の生成も E2 の閉集合の攻撃（予想ログを recipes から作る）も、`--recipes kit/gen/recipes.macos-live-off.json` を渡す。
  - 観測側のマーカー（← → ←）は、E2 で `--markers-in-obs` を付けて扱う（判断 80）。
  - ★ `closed_set.py` は、計画のヘッダーの `recipes_sha256` と `--recipes` のファイルの SHA-256 が違えば exit 2 で止まるようになった（判断 83）。⚠️ OFF 用の手順書は判断 83 で S11 を空にしたので、SHA-256 が `19c537c0` の版から変わった。パイロットの `verify-off` の計画はその古い版を指す（E2 にかけるなら、その版を `git show 19c537c0:…` で取り出して渡す）。
- ⚠️ Codex の台帳は枝ごとに記帳される。merge では両側の増分を合算する（`git checkout --` で戻さない）。回す前に origin/main の台帳も見る。
- ⚠️ 両方の機械が同じ枝に push するときは、push の前に `git fetch` → `git pull --no-rebase`（force しない）。
- ⚠️ heredoc の中のバックスラッシュは潰れる → 文書は Write / Edit で書き、`od -c` で確かめる。
- Mac だけにある道具（git の外・`~/ime-pilot/`）: `live_conversion.sh`（入力メニューを Accessibility で操作し、✓ を読み戻す）・`enter_probe*.py`・`esc_probe*.py`・生ログ。
- G-GEAR の `.claude/settings.local.json`（machine-local）に `deny: Read(//c/zenodo/**)` を足した（2026-10-01・研究者の承認）。Zenodo の手順はトークンをプロセスの中で読むので影響しない。
