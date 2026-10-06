# 次セッション（Surface）— IME 論文 M12: Windows の書庫と標本を束ねて記録し、書き出しを確かめ、G-GEAR へ移す

> ✅ **済み（2026-10-06・Surface・判断 217・枝 `docs/ime-m12-surface-deposit`）**: §2 の 1〜9 を実行。残りは §2.10（研究者が `C:/ime-deposit/` の Windows の書庫と標本 14 ファイルを G-GEAR の `C:/ime-deposit/` へ移す）。結果と見つけたことは判断 217。

> 作成: 2026-10-06 夜（G-GEAR・判断 215 の後）。`next-session-ime-paper-manuscript-9.md` の §2.2 を、機械ごとの引き継ぎに分けて具体にしたもの（研究者の求め）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 207・213・214・215**、`papers/ime-observation/experiment/data.windows.md`（Deposits・Run checks・Check of section 10.8）と `data.md` の **Deposit procedure**（手順 1〜5）と 2026-10-06 の節（Mac が同じことをした形）、`experiment/pilot-windows.md`（Raw logs）、`experiment/datasheet.md`（Parts 2）、`manuscript/sections/dataset.tex` §11.3（What was not deposited）、`kit/export/deposit.internal.{json,py}`（docstring が照合の仕様）。状態は着手時に `git fetch` で測り直す。
> 並行: Mac（`next-session-ime-paper-m12-mac.md`）と同時に進めてよい。G-GEAR（`next-session-ime-paper-m12-ggear.md`）は両方の後。

## §0 打ち込む用

```
git fetch → origin/docs/ime-m12-deposit-prep から枝 docs/ime-m12-surface-deposit を切る（main ではない）。
.steering/_handoff/next-session-ime-paper-m12-surface.md を読んで §2 を実行してください。
一次は decisions.md の判断 207・213〜215、experiment/data.windows.md と data.md の Deposit procedure、pilot-windows.md の Raw logs、datasheet.md の Parts、dataset.tex §11.3、kit/export/deposit.internal.json と deposit.internal.py の docstring。
Skill: git-workflow・verify-before-claiming・data-privacy（書庫・--pack・run.json・封印を扱うとき）・subagent-delegation。応答は日本語。コミットは git add パス指定。
⚠️ 判断の番号は 217（Mac が 216 を使う。番号を詰めない）。逸脱は D13〜。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。ログ（obs / oracle / gt / plan）は開かない。run.json は欄を名指して読む。封印したセッション行は寄託のためだけに写しで --unseal し、読まない。生ログ・キーコードを外部の LLM に出さない。
⚠️ IMM の入力欄のパイロットの run は寄託しない。--pack に --also-user・--also-home（この機械のログイン名とホーム）を渡すが、値は記録に書かない。
⚠️ heredoc でバックスラッシュを重ねない（python に渡ると壊れる）→ 置換は Edit か、Write で書いたスクリプトで。Windows の python の出力行には CR が付く（while read では ${f%$'\r'}）。
⚠️ PR は出さない（枝を push するだけ。G-GEAR が Mac の枝と合わせて 1 本の PR にする）。
```

## §1 状態（2026-10-06 夜・G-GEAR で測った）

- ✅ G-GEAR にある Windows のもの: 計測の書庫 `windows-msime-tsf-2.zip`（Downloads・SHA-256 `f2287a74…cd06` で `data.windows.md` と一致）とその展開した写しだけ。**§2.2 の品（下）は G-GEAR に無く、まだ束ねていない**（`data.windows.md` に書庫の SHA-256 が無い）。`--pack` は測った機械で回す決まり（判断 207-4）なので Surface で行う。
- ✅ 判断 214（Mac）: macOS の書庫 9 つと標本を束ね、`data.md` に Deposits の行・「Machine that ran the deposit check」の行・`git_commit` の表を書いた。**同じ形を Windows で作る**（`data.md` の 2026-10-06 の節を手本に）。
- ✅ 判断 215（G-GEAR）: 寄託は **1 ファイルずつ**。一覧 `kit/export/deposit.internal.json` に Windows の項目を**仮の名前と仮の label**で置いた（`sha256: null`）。照合の道具 `kit/export/deposit.internal.py` が、一覧と記録と手元のファイルを突き合わせる。

## §2 やること

1. **候補を確かめる**（datasheet の Parts 2・`pilot-windows.md` の Raw logs・`dataset.tex` §11.3）:
   - E3 の `working` の run（`data.windows.md` の Run checks の行 `windows-msime-tsf, question 5 working`・manifest `1e5f40ac…`）
   - TSF の入力欄のパイロット: `short-tsf`・`pilot-tsf`・`verify-tsf`・`toolcheck-tsf`
   - runner が中止した 3 つの試み（`pilot-windows.md` 37〜41 行: `SetForegroundWindow` に拒まれた 2 つと、S15 の窓が閉じて 4 試行で止まった 1 つ。⚠️ 試行の中で止まったものは §11.3 の規則で通らない見込み → `--check-deposit` で決める）
   - ★ §10.8 の確かめの run（パイロットの `verify` 計画 39 試行・2026-10-04 00:27〜00:37 JST・計測の cell ファイル・plan の SHA-256 `f02e046b…`）と、その最初の開始（鍵を送る前に runner が中止）（研究者の選択・判断 213-3）
   - 管理者権限で拒まれた計測の開始（`data.windows.md` 38 行・manifest `0027d0a4…`・oracle はヘッダだけ）: §11.3 の規則（「runner が中止した run は、同じ確かめを通るか、参照のログも観測のログも残さなかったときだけ寄託する」）で決め、決めた理由を `data.windows.md` に書く（今の表は "No"）。
2. ★ **中止した 3 つの試みは `--pack` の前に**、`run.json` の **`abort_reason` の文字列だけ**を読み、アプリ名や窓の題が入っていないかを確かめる。先に `kit/run/run_cell.py` の前面の窓の確かめが失敗したときの文（`abort_reason` に入る文）を一次で読み、何が入りうるかを知ってから読む（security-checker の残し・判断 213）。入っていたら止まって研究者に聞く。
3. **束ねる**（`data.md` の Deposit procedure 1〜5）: 各候補の**写し**で、封印したセッション行を `kit/pilot/seal_obs.py --unseal` で戻し（読まない）、`python kit/analysis/pipeline.py --check-deposit` を通してから `--pack <run> --out <archive.zip> --also-user <この機械のログイン名> --also-home <この機械のホーム>`。書庫の名前は一覧の名前に合わせる: `windows-e3-working-1.zip`、`windows-pilot-<run ディレクトリ名>.zip`、§10.8 の確かめは `windows-check-verify.zip`・その最初の開始は `windows-check-verify-start-1.zip`（変えてよい。変えたら一覧も同じに）。通らなかった候補は束ねない。
4. **標本**: E3 の `idle` と `working` の `samples.tsv` と `conditions.txt`（4 ファイル）。`--pack` は標本を束ねず確かめもしない → 目と検索で、パス・ログイン名・ホームが無いことを確かめる。`samples.tsv` の SHA-256 が `data.windows.md` の値（`idle` `43ab3b39…`・`working` `638da0ea…`）と一致することを確かめる。
5. **`data.windows.md` に記録する**（Mac の `data.md` の形に合わせる）:
   - ★ Deposits の表に 1 書庫 1 行。**第 1 セルは一覧の `label` で始め、続けて ` (` と説明**（例: `windows-pilot-short-tsf (calibration pilot; packed on the measuring machine on 2026-10-0X)`）。**第 3 セルは小文字の SHA-256 をバッククォートで囲んだものだけ**（道具は崩れた行・表の外の SHA-256 を問題にする）。`label` に `|` を入れない。
   - 「Machine that ran the deposit check」の行（無ければ `data.md` と同じ形で節を足す）。
   - Mac の 2026-10-06 の節と同じ形の節: 各 run の `git_commit`・`git_dirty`・中止の有無・`run.json` の SHA-256、寄託した候補と**通らなかった候補とその理由**、管理者権限で拒んだ開始を寄託するかとその理由。
   - ★ `conditions.txt` の SHA-256 を `idle`・`working` で 1 行ずつ: **1 行に SHA-256 は 1 つだけ**、その行に条件の語（`idle` か `working`）と語 `conditions` を入れ、もう一方の条件の語は書かない。
6. **一覧を埋める**（`kit/export/deposit.internal.json`）: Windows の各項目の `sha256` を入れ、`name`・`label`・`contents`（英語・datasheet の表にそのまま入る・`|` を入れない）を実物に合わせて直す。通らなかった候補の項目は消し、寄託することにした開始（管理者権限）があれば足す（`part` は Measurement か Calibration pilot か、datasheet の Parts に合わせて）。`label` は Deposits の行の第 1 セルの頭と同じ文字列。
7. **道具で照合する**: Windows の書庫と標本をすべて 1 つのフォルダに置き（OneDrive の下は避ける）、
   - `python -I papers/ime-observation/kit/export/deposit.internal.py --selftest` → ok（ジャンクションのテストが走る）
   - `python -I papers/ime-observation/kit/export/deposit.internal.py --from <フォルダ> --allow-pending`
   - ★ 期待: `windows-*` の項目がすべて `ok`（`windows-msime-tsf-2.zip` も、Surface に元の書庫があればそのフォルダに写す。無ければ MISSING で構わない）、FAIL は **`macos-*` の MISSING と（Mac がまだなら）macOS の `conditions.txt` の pending だけ**。記録・datasheet・一覧の形の FAIL が 1 つでも出たら直してから進む。
8. **書き出しの確かめ（Surface）**: 2 つの凍結のタグのきれいな worktree でタグ自身の `export.internal.py --allow-missing-license`（一覧が `29b183ba…` と `f61af353…` に一致）、`origin/docs/ime-m12-deposit-prep`（または 6 までを commit した枝）の新しいクローンで本番の形の書き出し（exit 0・**195 ファイル**）と、その木で `bash kit/check.sh`（31 本）。3 つの木とも Surface のログイン名・ホーム・ホスト名が 0 件。⚠️ `git archive` を使うなら `-c core.autocrlf=false`。
9. **記録とコミット → push**: `decisions.md` に判断 217、`tasklist.md` の M12 に 1 行、本ファイルの冒頭に「✅ 済み」。文体の検査 `python .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py` → 違反 0。`git add` はパス指定（`papers/ime-observation/experiment/data.windows.md`・`papers/ime-observation/kit/export/deposit.internal.json`・`.steering/…/{decisions,tasklist}.md`・本ファイル）。`git push -u origin docs/ime-m12-surface-deposit`。PR は出さない。
10. **研究者が移す**: Windows の書庫（working・寄託するパイロットと確かめの run）と標本 4 ファイルを G-GEAR の **`C:/ime-deposit/`** へ（OneDrive の下に置かない）。`windows-msime-tsf-2.zip` は G-GEAR の Downloads にあるので移さなくてよい。

## §3 気をつけること

- ⚠️ 書き出しは、それを回す機械の値しか探さない。Surface で回して Surface の値が無いことを確かめるのがこのセッションの役目（3 台とも通るまで公開に切り替えない）。
- ⚠️ `--pack` は manifest と 4 つのログだけを束ねる。`*.stderr.txt`・`runner.error.txt` は束ねない（測った機械に残す）。
- ⚠️ `--remote` / `--upload` は Surface で回さない（token は G-GEAR だけ）。
- ⚠️ 研究者のメールアドレスを外部の LLM に送らない（/cross-review は G-GEAR でまとめて回す）。
- ⚠️ `pkill` は git-bash で効かない（サーバを立てたら PowerShell でそのポートのプロセスだけ止める）。
