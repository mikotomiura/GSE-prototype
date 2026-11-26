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
