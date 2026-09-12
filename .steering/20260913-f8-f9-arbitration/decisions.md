# decisions — F-8 / F-9

## D1: ★ F-8 = **third-party の 3 本だけ** SHA 固定する（`actions/*` はタグのまま）

- **決定**: `dtolnay/rust-toolchain` / `Swatinem/rust-cache` / `softprops/action-gh-release` を
  40 桁 commit SHA へ固定。⚠️ `actions/*` は**意図的にタグのまま**。
- **理由**: ★ 危険は「可変参照」一般ではなく **「誰が動かせる参照が、何に触れる場所で走るか」**である。
  - ⚠️ `dtolnay/rust-toolchain` と `Swatinem/rust-cache` は **self-hosted** (`check` / `build-macos`) で走り、
    ★ その機械には `~/.gse/age-identity.txt`（**被験者提出物を全部復号できる鍵**）がある。
  - ⚠️ `softprops/action-gh-release` は hosted だが `contents: write` を持ち、
    ★ **被験者が落とすバイナリを差し替えうる**。→ 固定する。
  - ★ `actions/*` は GitHub 自社所有で、⚠️ **dependabot を入れない裁定（D12）の下では
    固定＝更新が完全に手動**になる。→ ★ 固定した方が古いまま放置されるリスクの方が大きい。
- ⚠️ **この非対称は無言にしない** —— ★ 理由を `ci.yml` の注記に書いた。
- ⚠️★★★ **SHA 固定は本丸ではない**: ★ 上流乗っ取りを遅らせるだけで、
  **鍵が同じ home にある限り「実機で任意コードが走れば鍵が読める」構図は変わらない**。
  → ★ `ci.yml:112` の「候補 c: 鍵を別マシン/別アカウントへ退避」を申し送りに残した。

## D2: ⚠️★★★ **annotated tag のオブジェクト SHA を掴みかけた**

- ★ 実測: `gh api repos/Swatinem/rust-cache/git/ref/tags/v2` は
  **`type: tag` / `sha: 49a0bdc…`** を返す —— ⚠️ **これはタグオブジェクトで commit ではない**。
  ★ `git/tags/49a0bdc…` を引いて **commit `6323deb…`** を得た。
- ⚠️ そのまま貼っていたら `uses:` が解決できず CI が落ちていた（★ 静かな失敗ではないが、
  「タグの SHA を書いた」ことに気づかないまま原因を探すことになる）。
- ★ 対照: `softprops/action-gh-release@v2` は `type: commit`（軽量タグ）で、そのまま使えた。
  → ⚠️ **リポジトリごとに違う。毎回 `type` を見る。** 手順を runbook §1 (h) に書いた。

## D3: ⚠️ `dtolnay/rust-toolchain@stable` は**タグですらなくブランチ**だった

- ★ 固定先は `stable` **ブランチの先端**（`6bed076…`・2026-09-03）。
- ⚠️ **意味が変わらないことを確認した**: そのコミットの `action.yml` で
  `toolchain` の既定が **`stable` のまま**（★ ブランチ名がそのまま既定値を決める作りなので、
  別ブランチの SHA を掴むと**黙って別の toolchain を入れる**）。
- ★ なお本 repo は `rust-toolchain.toml` ＋ 明示 `rustup toolchain install` で版を決めている（R-2）ので、
  ⚠️ action の既定が効く余地は小さい。★ それでも**確認してから**固定した。

## D4: ★ F-9 = **汎用 linter を入れず、不変条件検査に置き換える**

- **決定**: `actionlint` を入れない。`scripts/check_workflow_invariants.py` を置く。
- **理由（★ すべて実測）**:
  - ⚠️ **構文・式エラーで事故った実績が 0 件**（直近 40 コミットの `.github/workflows/` 変更は全部 semantic）。
  - ⚠️★★★ **F-9 を起票した契機そのものが false positive** だった ——
    ★ Codex が **secrets-filter で伏字化された diff** を見て「構文エラー」と判定したもので、
    実ファイルは健全（★ yaml パースで確認済み）。
  - ⚠️ actionlint 導入は**第三者 action / バイナリ配布を増やす** = ★ F-8 が減らそうとしている面と逆行。
  - ★ 不正 YAML は **GitHub が push 時に拒否**する。
- ★ **代わりに守るもの**: ⚠️ この repo で実際に起きるのは「**決めた判断が、検査されていない前提の上に乗る**」
  ことである（★ F-5 の 4 job / ⚠️ `ci.yml:132` に自分で書いた follow-up の放置）。
  → ★ **決定を機械に持たせた**（下記 4 条件）。
- **却下**: ★ 何もしない —— ⚠️ それだと F-8 の固定が「決めたきり」になり、
  **次に誰かが可動タグで action を足した瞬間に黙って戻る**。

## D5: ★ 検査する 4 条件と、その置き場所

| # | 不変条件 | ⚠️ 破れたときに何が起きるか |
|---|---|---|
| 1 | 全 job が実効 `permissions` を持つ | ⚠️ 既定の広い権限を継ぐ（★ F-5 の 4 job がまさにこれ） |
| 2 | third-party action が 40 桁 commit SHA | ⚠️ 上流を握った者が実機の鍵に到達しうる |
| 3 | `supply-chain.yml` が hosted のまま | ⚠️ 週次 job が鍵のある機械に載る |
| 4 | 走査 0 件は **exit 2** | ⚠️ 「検査が動いていない」を「違反なし」と読む |

- ★ 置き場所は **`frontend-check`** —— ⚠️ `supply-chain.yml` は `paths` 限定で、
  **依存や toolchain を触らない PR では 1 度も走らない**。
- ★ 変異 4 種（タグへ戻す / permissions を消す / self-hosted へ向ける / 新しい第三者を足す）で
  **赤になることを実ファイルに対して実証**した。⚠️ 空振り対照も 2 種。

## D6: ⚠️ 置換の失敗を記録する（★ やり直した）

- ⚠️ 初回は文字列全置換にしたため、**`uses:` 以外**も書き換えてしまった:
  (a) 「third-party action が可変参照のままである」という **follow-up 注記が意味不明**になった
  (b) **過去の CI ログの引用**（`Run Swatinem/rust-cache@v2` **1 秒**）まで書き換わった
- → ★ **`uses:` 行だけを正規表現で特定**して置換し直した。
  ⚠️ (a) は内容が古くなったので**別途書き直した**（★ 対処済みであることと、残る本丸を明記）。
- **教訓**: ⚠️ 設定値の一括置換は、**同じ文字列が「説明」として現れる場所**を壊す。

## ⚠️ 本タスク外で見つけたこと（★ 申し送り）

- ⚠️★★★ **`scripts/check-shell-portability.sh` が Windows で exit 1**。
  ★ `git stash` して **main の無変更ツリーでも再現**したので**既存不具合**である。
  ⚠️ 機序: 陽性対照が `mktemp` で作る **MSYS2 の `/tmp/...` パス**を、
  **ネイティブ Windows の Python が開けず** `FileNotFoundError`。
  → ★ 出力は「**走査が空回りしている（違反を仕込んだのに 0 件）**」＝ ⚠️ **番人が空振りしている**。
  ⚠️ CI は ubuntu なので**緑のまま**で、**Windows ローカルでしか見えない**。
  ★ 本セッションで同じ型（MSYS2 `/tmp` × ネイティブ Python）を**2 回**踏んでいる。
- ⚠️ `~/.gse/age-identity.txt` の退避（★ `ci.yml:112` 候補 c）——
  ★ **SHA 固定より本質的**だが実機作業が要るので別タスク。
