# 引き継ぎ（G-GEAR）: 自前ランナーの check が `link.exe not found` で落ちるのを直す

作成 2026-11-26（Mac から）。応答と記録は日本語で書く。記号を多用しない。判断が要るところは AskUserQuestion で聞く。この作業は G-GEAR の上で行う（Mac からは直さない）。

## 症状

- CI の `check (gse-win-selfhosted, x86_64-pc-windows-msvc)` が、ランナー `g-gear-win-x64`（ラベル `gse-win`）で毎回 30 秒ほどで落ちる。
- ログの最初の誤り: `error: linker 'link.exe' not found` と `note: the msvc targets depend on the msvc linker but 'link.exe' was not found`。続いて `proc-macro2`・`quote` のビルドスクリプトがコンパイルできずに止まる。コードのコンパイルの前に落ちているので、PR の中身のせいではない。
- 最後に緑だったのは run 44577900883（main・2026-11-19 17:30 UTC・同じランナー）。最初に赤を見たのは 2026-11-23 01:55 UTC 以降。2026-11-25 04:20 UTC の main の run 45546079577 でも同じ赤。
- ci.yml の最後の変更は be9a97bf（2026-11-19 17:02 JST = 08:02 UTC・check の上限を 45 分に）で、緑の run 44577900883 より前。つまり ci.yml を変えずに緑から赤になった。11-19 から 11-23 の間に G-GEAR の上で何かが変わった（Windows Update・Visual Studio の更新や修復・別の作業での環境変数の変更など）と見るのが先。

## 確かめる順

1. ランナーを動かしているアカウントと起動の形（サービスか、`run.cmd` を手で起動したか）を確かめる。サービスなら、そのアカウントの環境で `link.exe` が見えるかが問題になる。
2. Visual Studio Build Tools（または Visual Studio）の「C++ によるデスクトップ開発」と MSVC v14x のツールセット・Windows SDK が入っているかを、Visual Studio Installer で見る。`vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath` が空なら、ツールセットが外れている。
3. 開発者用でない普通の PowerShell で `rustup default` と `rustc -vV` を見て、ホストが `x86_64-pc-windows-msvc` のままかを確かめる。rustc は `link.exe` を PATH ではなく vswhere などで探すので、ツールセットが入っていれば普通は見つかる。
4. 再現: ランナーの作業場所（`C:\actions-runner\_work\...`）の外の空のフォルダで `cargo new t && cd t && cargo build` を、ランナーと同じアカウントで行う。ここで同じ誤りが出れば、CI ではなくマシンの問題と確定する。
5. 直し: 多くは Visual Studio Installer で Build Tools を「修復」するか、外れた C++ のワークロードを入れ直すことで戻る。直した後はランナーのサービスを再起動する（環境を読み直させるため）。
6. 4 の空のプロジェクトで `cargo build` が通るのを見る。

## 直った後

- PR #435（枝 `fix/clock-jump-gate`・run 45128616213）の失敗したジョブを re-run する: `gh run rerun 45128616213 --failed`。Windows の check の緑を見る。
- PR #435 のマージと v0.1.43 の版上げは Mac 側の作業（`.steering/_handoff/next-session-gse-clock-gate-merge-and-v0.1.43.md`・Mac の作業ツリーにだけある）。G-GEAR ではマージしない。研究者に「Windows の check が緑になった」と伝えて終える。
- 直した手順と原因（分かれば）を、この引き継ぎの末尾か `.steering/` の新しい記録に書き、研究者に伝える。

## してはいけないこと

- ci.yml を変えて Windows の check を飛ばしたり hosted に向け直したりしない（11 月は Actions の含まれる分が尽きていて hosted は走らない。変数 `GSE_WIN_FORCE_HOSTED` も触らない）。
- 原因が分からないまま Rust のツールチェーンを消して入れ直すなどの大きな操作をする前に、研究者に確かめる。
- G-GEAR で長い計算が走っているときは、ランナーの再起動や re-run の前に研究者に確かめる。
- 記録の内容（打鍵・NDJSON の生ログ）を外部の LLM に送らない。

## 実施の記録（2026-11-26・G-GEAR）

### 原因（一次で確かめた）

- 2026-11-23 00:51:55 JST（= 11-22 15:51 UTC）に `"C:\Program Files (x86)\Microsoft Visual Studio\Installer\setup.exe" uninstall --installPath "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"` が実行され、終了コード 0 で終わっている（`%LOCALAPPDATA%\Temp\dd_installer_20261123005155.log`）。外されたインスタンスは 860ee57e で、`Microsoft.VC.14.xx.Tools.HostX64.TargetX64` の各版（MSVC 14.44.35207 の `link.exe` を含む）がその中にあった（`dd_setup_20261123005202.log`）。
- `Microsoft Visual Studio\2022` と `Shared` と `ProgramData\Microsoft\VisualStudio\Packages\_Instances` の更新時刻が同じ 11-23 00:52。最初の赤（11-23 01:55 UTC）の約 10 時間前。
- 残っていたのは Visual Studio Build Tools 2026（18.4・インスタンス 454f18a9・2026-04-04 導入）だけで、入っているワークロードは `Microsoft.VisualStudio.Workload.MSBuildTools` のみ。`VC` のフォルダが無い。`vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath` は空だった（手順 2 の「ツールセットが外れている」形）。
- Windows SDK（10.0.26100.0）と Rust（既定 `stable-x86_64-pc-windows-msvc`・1.98.1・ホスト `x86_64-pc-windows-msvc`）は残っていた。手順 3 は問題なし。
- 誰が外したか: Claude のセッション記録（`~/.claude/projects/*/*.jsonl`）に該当の操作は無い。直後（15:56 UTC〜）に同じ機械でストレージの整理のセッションが始まっているので、その直前に手で外したと見られる（推測・研究者に確かめていない）。
- ランナーはサービス `actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64`（`C:\actions-runner\.service`）。サービスのアカウントの一覧を読む操作は自動モードに拒まれたので、アカウントは memory（NetworkService）のまま確かめていない。

### 再現（手順 4）

- ランナーの作業場所の外（scratchpad）で `cargo new linkrepro && cargo build` を、MSYS2 の `/usr/bin/link.exe` を外した PATH で実行すると、CI と同じ `error: linker 'link.exe' not found` / `note: the msvc targets depend on the msvc linker but 'link.exe' was not found` が出た。CI ではなくマシンの問題と確定。
- ランナーと同じアカウント（サービス）ではなく johnd で回した。rustc は `link.exe` を vswhere とレジストリで探すので、アカウントによらず同じ結果になると見ている。

### 直し（手順 5）

- 研究者の選択（AskUserQuestion）: 「2022 を戻す」（Build Tools 2026 に C++ を足す案は採らない）。理由は 11-19 の緑と同じ MSVC 14.44 に戻り、11-19 以前の run とそのまま比べられ、他の機械の記録（14.44.35207）とも揃うため。
- `winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --source winget --override "--wait --passive --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"` → `Successfully installed`・exit 0。Build Tools 2022 17.14.37906.3 が `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools` に入り、`VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\link.exe` が前と同じパスに戻った。vswhere の VC ツールの問い合わせもこのインスタンスを返す。
- 手順 6: 同じ空のプロジェクトで `cargo build` が通り、`Hello, world!` が出た。
- ランナーのサービスは再起動していない。rustc は実行のたびに vswhere で探すので、環境を読み直させる必要がないと見て、先に re-run で確かめた（結果は下）。

### 直った後

- `gh run rerun 45128616213 --failed`（PR #435・`fix/clock-jump-gate`）→ attempt 2。Windows の check は `g-gear-win-x64` で走り、success（job 139696795834・2026-11-26 04:40:18〜04:56:02 UTC・約 16 分）。ログの `rustup show active-toolchain` は `1.98.1-x86_64-pc-windows-msvc`（rust-toolchain.toml の固定どおり）。ランナーのサービスを再起動せずに通ったので、再起動は要らなかった。
- `frontend-check` も attempt 1 で落ちていた（この引き継ぎに書かれていなかった）。ubuntu-latest のホストのジョブで、`runner_name` が空・ログ無し。attempt 2 でも同じく割り当て無しで落ちた。11 月の含まれる分の不足によるもので、G-GEAR とは関係ない。main の run 45546079577 でも同じ形で落ちている。12 月に分が戻るまで、PR #435 の run 全体は緑にならない。
  - 追記（同日）: attempt 2 の frontend-check の注記の逐語は「The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings」。分の不足だけでなく、支払いの失敗か使用上限の設定の問題である可能性がある。`gh api users/mikotomiura/settings/billing/...` は gh の token に `user` の scope が無く 404 で読めなかった。研究者が GitHub の Billing & plans で確かめる。
  - 代わりの確かめ: PR #435 の先頭 a4380225 を detached の worktree に出し、ci.yml の frontend-check の run 手順 37 本を G-GEAR の手元で順に回した（`uses:` の 2 本は worktree と手元の node 24.14.1 で代えた・Python 3.11.9 の venv・pip の手順は venv の中）。36 本は exit 0。20 番（`check_collection_continuity.py --self-test`）だけ、Windows の既定の文字コード cp932 で `⚠` を出せず UnicodeEncodeError で落ちたので、`PYTHONUTF8=1` で回し直して緑（9 項目）。この落ち方は Ubuntu（UTF-8）の CI では起きない。手元の Windows で回したものなので、ubuntu-latest の CI と同じではない（OS・node の版が違う）。マージの判断の材料にはなるが、CI の緑の代わりにはならない。
- PR #435 のマージと v0.1.43 は Mac 側の作業なので、G-GEAR ではしていない。
- 別プロジェクト（`C--Users-johnd`）の memory `project_gse_dev_env.md` に、2022 の MSVC 14.44.35207 のパスが直接書かれている。同じパスに戻ったので、書き換えは要らない。
