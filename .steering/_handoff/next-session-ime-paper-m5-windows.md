# 次セッション（G-GEAR）— IME 論文: M5 Windows の較正パイロット

> 作成: 2026-10-03（G-GEAR・OSF の登録を記録したセッションの最後に）。★ **研究者の選択で M5 は G-GEAR で行う**（判断 134）。別の Windows 実機で行うのは**数時間以上の run だけ**（M7 の本計測のセル・Windows の E3 の 8 時間の 2 条件）。⚠️ 判断 133（M5 を別の実機で）は判断 134 で改めた。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 68・133・134**、Mac の前例は `pilot-macos-1-notes.md`）・`_issue-plan.md` §5（M5・M6）・`design.md` §1.1・§1.1a・§1.1b と、`papers/ime-observation/kit/pilot/README.md`・`kit/refinput-windows/README.md`・`kit/run/README.md`、凍結した事前登録 `papers/ime-observation/experiment/preregistration.md` の **§8**（追補が変えてよい範囲）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → origin/main から作業ブランチを切る（例: feature/ime-m5-windows-pilot）。
.steering/_handoff/next-session-ime-paper-m5-windows.md を読んで §2 から始めてください。
一次は decisions.md の判断 68・133・134、design.md §1.1a、kit/pilot/README.md、kit/refinput-windows/README.md、kit/run/README.md、事前登録 §8。
⚠️ 凍結のタグ ime-observation-prereg-macos のコードは変えない。追補（M6）が変えてよいのは §8 に列挙した Windows の部分と、Windows だけが使う新しいファイルだけ。
⚠️ パイロットは ImeShadow を読まない（obs は seal_obs.py で封印してからキーの行だけで集計する）。生ログはコミットしない。
⚠️ 合成キーを送る run は研究者の答えで「離席中に自動」（2026-10-03・§1 の ★）。研究者は常に離席している扱いで、始めたいときに始めてよい。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow・data-privacy。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-03 の終わり）

- ★★★ **2026-10-03 の続き（Surface Pro 8）: M5 のパイロットを Surface で実施した**（判断 136・研究者の指示で判断 134 / 135 を改めた）。§2 の 1〜7 は済み。結果と所見は `.steering/20260927-ime-observation-paper-eval-design/pilot-windows-1-notes.md`。生ログと封印・作業ファイル（`cell-*.json`・`focus_front.py`・`away_window.py`・`run_fg.py`・`outcome.py`・`seq.py` など）は Surface の `~/ime-pilot/`。⚠️ **止まっている所**: S4 が凍結のコードの制約で MS-IME の取消にならない（ノートの所見 1）→ 研究者の判断待ち。以下の §1・§2 は当時の記述。

- **macOS の事前登録は凍結済み・OSF で公開済み**: `https://osf.io/9nh7r`（DOI `10.17605/OSF.IO/9NH7R`・`date_registered` 2026-10-02・添えたファイルの SHA-256 は凍結したファイル `fa6fd586…7773` と一致・`notes.md` に記録・PR #298）。Mac の M4（本計測）は別の流れで、Mac の引き継ぎ `next-session-ime-paper-osf-m4.md` の §2 の 3 から。
- **M5 はまだ何もしていない**: G-GEAR では書き出し・ビルド・run のどれも行っていない（判断 133・134）。
- `papers/ime-observation/` の kit は凍結のタグから変わっていない（タグと main の差は `experiment/notes.md` の追記だけ・2026-10-03 に `git diff --stat` で確かめた）。
- **研究者の選択（判断 133 の答えを判断 134 が引き継ぐ）**:
  - IME の学習は**リセットしない**（Mac と同じ。MS-IME の入力履歴の消去は設定画面の操作でコマンドが無い）。セルのファイルの `ime_settings.learning` にそう書き、`reset_cmd` は空。
  - 電源の設定は**メインが一時的に切って戻す**: `powercfg` で AC のスリープと画面オフを 0 にする。**元の値を先に記録し**、run の後に戻して読み戻しで確かめる。スクリーンセーバーとロック（`HKCU:\Control Panel\Desktop` の `ScreenSaveActive` など）も読み、要れば同様に。
- ★ **2026-10-03（Surface Pro 8）**: このメモを Surface で開いたが、研究者の答えで **Surface が判断 134 の「別の Windows 実機」**（判断 135）→ M5 はこのまま G-GEAR で行う。計測する機械の値（Windows 11 25H2 / build 26200・MS-IME の DLL 10.0.26100.8875・JIS・Rust と Python は未導入）は判断 135 に記録した → 比べる相手になる。★ **実行の時間は答えが出た: 離席中に自動**（研究者「常に離席しているようなもの・始めたいときに始めてよい」）→ 未決 1 は聞き直さず、run の前の確認も要らない。
- **未決**:
  1. ~~**実行の時間**~~ → 2026-10-03 に答え「離席中に自動」（上の ★）。以下は当時の記述: **実行の時間**（研究者に聞く前に中断した）: 選択肢は「離席中に自動（推奨・手順書の Windows の部分だけを直して走らせ直すところまで任せる・凍結済みのコードに欠陥が見つかれば止めて報告）」／「その場で 1 本ずつ」／「準備だけ」。→ このセッションの最初に AskUserQuestion で聞く（推奨と理由を添える）。
  2. ⚠️ **較正する機械（G-GEAR）と計測する機械（別の実機）が違う**（判断 134・M6 の前に研究者が決める）。パイロットは MS-IME の呼び出し列をその機械と版で較正する。推奨: 追補に計測する機械の OS と MS-IME の版を書き、M7 の前に計測する機械で短い確認の run（Mac の `verify-1` の形・全シナリオ × 3 速さ × 1）を回して、呼び出し列の型がパイロットと同じことを確かめる。→ M5 の記録に G-GEAR の OS と MS-IME の版を必ず残す（比べる相手になる）。
- 参考（2026-10-03 に G-GEAR で読んだ値）: Windows 11 `26H2`・build `26300`。入力方式は `{03B5835F-F03C-411B-9CE2-AA23E1171E36}`（Microsoft IME・日本語）だけで、Google 日本語入力は入っていない。MS-IME の版とキーボードの配列はまだ読んでいない。Python は 3.11.9（判断 52）—— 着手時に測り直す。

## §2 やること

1. **機械の前提を確かめて記録する**（`tasklist.md` の M5 の下に。公開用の版は M6 で `experiment/env.md` の Windows の節にする想定）:
   - git・git-bash（hook は bash 前提）・Python 3（版を記録）・Rust（`cargo` と MSVC のビルド道具）・`gh` の認証。
   - Windows の版（`DisplayVersion`・`CurrentBuild`）・MS-IME の版・キーボード（JIS か）・入力方式（ローマ字入力）・予測入力の設定（既定のまま変えない）。
   - ⚠️ **G-GEAR は Windows の CI の self-hosted runner**（memory）。run と CI の job が重ならないようにする（負荷で送出の時刻が遅れる・`emit/README.md` の `--selftest --full` の注意）→ run の間は push しない。
2. **書き出しとビルド（判断 68: パイロットのロガーは書き出しからビルドする）**:
   - タグのクリーンな worktree: `git worktree add --detach <dir> ime-observation-prereg-macos`。
   - その `papers/ime-observation` で `python kit/export/export.internal.py --out <out> --allow-missing-license`。
   - 一覧を `.steering/20260927-ime-observation-paper-eval-design/freeze-export-list-macos.txt`（98 行）とバイト比較し、SHA-256 が `29b183ba245939ad82d9fa2d7db26e1a18520e2966f4aa9ec74478a4e51e6c49` になることを確かめる（3 台目の機械でも一致するか・計算の定義は `issues/024-acceptance.sh` の `LIST_PY`）。
   - 書き出した側で: `kit/logger` を `cargo build --release`、`kit/refinput-windows` を `cargo build --release --bins`、`bash kit/check.sh`（selftest）、`refinput_imm.exe --selftest` と `refinput_tsf.exe --selftest` を `validate_logs.py --kind gt` に通す、`python kit/emit/emit.py --selftest --full`（他の処理を止めて）。
3. **パイロットの計画（コミットしない作業ファイル・例: `%USERPROFILE%/ime-pilot/`）**:
   - 生成器の設定は `experiment/plan_config.macos.json` を写して `n_per_cell_scenario_speed` を 3 にした仮のもの（Mac の M1 は n = 3・126 試行・6 ブロック）。速さ 480 / 240 / 120 ms・think 0.2〜20 秒・マーカー ← → ← →（4 キー）・`nav_count_max` 3 は凍結の値のまま。
   - `python kit/gen/generate_plan.py --config <pilot config> --recipes kit/gen/recipes.json --corpus kit/corpus/data/phrases.jsonl --os windows --seed <任意・記録する> --out <plan>`。Windows の手順は `recipes.json` の `os.windows` と `_PROFILES["windows"]`（Enter 1 回で確定・Esc 1 回で取消）。
4. **セルのファイル（Windows だけが使う新しいファイル・2 経路で 2 つ）**: `kit/run/README.md` の表のとおり。
   - `refinput_cmd`: (a) IMM は `refinput_imm.exe --out {out}`、(b) TSF は `refinput_tsf.exe --out {out}`。窓の題は (a) `refinput_imm (gt/1 win_imm)`・(b) `refinput_tsf (gt/1 win_tsf)`（`src/bin/*.rs`）→ `backend_opts.focus_window` に入れる。
   - `logger_cmd`: `ime-observation-logger --out {out}`。`backend`: `windows`。
   - `focus_cmd`: 参照入力欄が前面にあることを確かめてから IME をオンにするコマンド（Mac の M1 の所見 4 と同じ論点・`keymap_windows.json` の `ime_on` は VK 22 = `VK_IME_ON`）。まだ無い → このセッションで作る。
   - S15 の `focus_away` の移り先（`backend_opts.away_window`・Mac は Finder）を決める。
   - `ime_settings` に学習をリセットしないこと・初期状態の作り方・予測入力の既定を書く。
5. **run**（各 run の前に研究者が離れていることを確かめる・`--i-understand-this-sends-keys`）:
   - 短い試し（数試行）を (a)・(b) で 1 本ずつ → 前面化・IME のオン・確定と取消が意図どおりかを見る。
   - 本体を (a)・(b) で 1 本ずつ（約 25 分ずつの見込み・Mac の M1 は 126 試行で約 23 分）。
   - ⚠️ `SetForegroundWindow` は前面ロックで拒否されることがある（`emit/backend_windows.py` は読み戻しで止まる）。Claude Code の裏のシェルから起動したとき通るかは未確認。
6. **封印と集計**（`kit/pilot/README.md` の手順 2〜5）: 各 run の `obs.jsonl` をすぐ `seal_obs.py` で封印 → `call_types.py`（(a) と (b) で 2 回・`types` と `per_trial` の区間を比べる）→ `reach.py` → `clock_sync.py`（マーカーの指定は README の例の `gt_vks` を Windows の VK に直したもの）。
7. **確かめること**（`refinput-windows/README.md` の未確認の点）:
   - (a) IMM: どの `WM_IME_*` / `IMN_*` が届くか・順序・`GCS_RESULTSTR` の有無で確定と取消を分けられるか。
   - (b) TSF の経路 1: MS-IME の composition で `OnEndEdit` が来るか・`ITfRangeACP` で長さが取れるか・候補窓の `BeginUIElement` が来るか・`tsf_end` の `result_len` で確定と取消を分けられるか。どれかが成り立たなければ経路 1 は不十分（停止条件）。
   - 2 経路が同じ区間を返すか（食い違えばそれ自体を報告する・design §1.1a）。
   - MS-IME の挙動: Space の後の Enter 1 回で確定するか（Mac のライブ変換 ON は 2 回要った）・Esc 何回で取り消すか・持ち越し（未確定の文字列が次の試行へ残る）の件数。
   - 合成キーが観測側のフックに届くか（`reach.py`）・時計の差とドリフト（`clock_sync.py`）・1 試行の実時間（本番の所要時間の見積もり）。
8. **記録**: 内部の記録 `pilot-windows-1-notes.md`（`.steering/` の同じタスク・`pilot-macos-1-notes.md` の形）。M5 の Done は `experiment/pilot-windows.md`（公開用の英語）と封印の `seal.json`（`_issue-plan.md` の M5）。正解の定義の選択（経路 (a) / (b)）と `gt_rules` の Windows のブロックは M6。
9. 出荷（git-workflow ルール 6）。完了時レビューは `code-reviewer` ∥ `security-checker` ∥ `/cross-review`。

## §3 気をつけること

- ⚠️★★★ **凍結のコードを変えない。** 事前登録 §8 で追補が変えてよいのは、`experiment/gt_rules.json` の Windows のブロック・2 つの手順書の `os.windows`・`kit/gen/generate_plan.py` の `_PROFILES["windows"]` と、追補の節・Windows のセルだけが使う新しいファイル。**既存の Windows のコード**（`kit/logger/src/driver_windows*`・`kit/refinput-windows/` の既存ファイル・`kit/emit/backend_windows.py`・`kit/run/run_cell.py`・解析のコード）は**追補でも変えられない**。パイロットでそこに欠陥が見つかったら、直さずに止めて研究者に戻す（逸脱として `experiment/deviations.md` に記録するかは研究者が決める）。
- ⚠️ **ImeShadow を読まない・数えない・突き合わせない**（`kit/pilot/README.md` の Boundary）。封印（`sealed/`）は開けない。封印の前の `obs.jsonl` を他の道具に通さない。
- ⚠️ 参照入力欄の `key_down` の `vk` は押したキーそのものなので、**参照入力欄に人の打鍵を入れない**（合成キーだけ）。参照のログのキーコードを表示・転記しない。生ログ（gt・oracle・plan・obs・封印）は git に入れず、外部の LLM（Codex を含む）にも渡さない。
- ⚠️ 合成キーは前面の窓に入る。run の間は誰も PC に触れない。ロック画面に入らないよう電源の設定を先に（§1）。
- ⚠️ タグ `v*` は `ci.yml` のリリースのビルドを走らせる。Windows の追補のタグは `ime-observation-prereg-windows`（判断 131）で、M6 で付ける（M5 では付けない）。
- ⚠️ 作業ツリーに別トラックの未追跡のファイルがあることがある。`git add` はパス指定で。
- ⚠️ git-bash で `git show origin/main:<path>` は `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない。Windows の Python に `/c/...` の形のパスを渡さない。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。予算ガードの hook は `C:\GSE-prototype` の台帳を読む（別の場所に clone したときは確かめる）。
- 記録の直しが 1 件残っている: IME 論文の CHI 2027 Posters への併願は 2026-09-28 に取り下げ済み（p321 のタスクの判断 15）だが、このタスクの判断 8・13 と `_issue-plan.md` の M13 にまだ残っている。追記で「BRM だけ」にする。
