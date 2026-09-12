# decisions — F-8 / F-9

## D1: ★ F-8 = **third-party の 3 本だけ** SHA 固定する（`actions/*` はタグのまま）

- **決定**: `dtolnay/rust-toolchain` / `Swatinem/rust-cache` / `softprops/action-gh-release` を
  40 桁 commit SHA へ固定。⚠️ `actions/*` は**意図的にタグのまま**。
- **理由**: ★ 危険は「可変参照」一般ではなく **「誰が動かせる参照が、何に触れる場所で走るか」**である。
  - ⚠️ `dtolnay/rust-toolchain` は **self-hosted** (`check` / `build-macos`) で走り、
    ★ その機械には `~/.gse/age-identity.txt`（**被験者提出物を全部復号できる鍵**）がある。
  - ⚠️★★★ **訂正 (security-checker M-5)**: 初稿は `Swatinem/rust-cache` も
    「self-hosted で走る」と書いたが**事実と違う** —— ★ `check` / `build-macos` の
    当該 step には `if: … runner.environment == 'github-hosted'` が付いており、
    **self-hosted では 1 度も走らない**（実測: `ci.yml:562` / `:994`）。
    ★ 固定が効くのは **hosted fallback と `build-windows`** である（結論は変えない）。
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


---

## D7: ★ レビュー 2 系統の反映（⚠️ **4 条件のうち 2 つが実質機能していなかった**）

⚠️★★★ **「変異テストを通した」だけでは足りなかった。** ★ 私の変異は*自分が想定した壊し方*
しか試しておらず、レビューは**別の壊し方**を持ち込んで 2 つの不変条件を素通りさせた。

| # | 出所 | 指摘 | 対応 |
|---|---|---|---|
| **H-1** | code-reviewer | ⚠️ runbook の **(h) がコードフェンスの外**にあり、`# (h)` が**見出しに化け** `<repo>` が HTML タグ扱いで消える | ★ フェンス内へ移した（実測で内側になったことを確認） |
| **H-2** | ⚠️ **2 系統一致** | ⚠️★★★ **hosted 判定が否定リスト**で 4 通り迂回できた —— `runs-on: gse-win`（self-hosted ラベルを書かない）／`${{ … }}` 式／`{group: …}`／**ファイル改名** | ★ **許可リストへ反転**（`ubuntu-*` / `windows-*` / `macos-*` と**証明できる**ときだけ通す）＋ 改名検知を `main()` に |
| **H-3** | code-reviewer | ⚠️★★★ **permissions 不変条件が原理的に発火しない** —— top-level 宣言がある限り「宣言の有無」は常に真。★ `write-all` も `id-token: write` も**素通り**（実測） | ★ **広さを見る**判定へ（`read-all`/`{}`/read は可、write は job 単位の allowlist）。⚠️ `release` の `contents: write` のみ許可 |
| **M-1** | security-checker | ⚠️ **composite action の中身が死角** —— `./` は免除なので `.github/actions/*/action.yml` 内の `uses:` を誰も見ていない。★ `disk-guard` は**鍵のある実機で無条件に走る** | ★ 走査対象に追加（規則 2 のみ適用） |
| **M-2** | security-checker | ⚠️ `actions/*` の免除が **ref を見ていない** —— `actions/checkout@main` が通る。★ 裁定は「**可動タグ**のまま」であって「何でもよい」ではない | ★ 免除を `vN[.N[.N]]` に限定 |
| **M-4** | ⚠️ **2 系統一致** | ⚠️ **PyYAML が本 repo 初の外部 python 依存**で未宣言。docstring の「runner に同梱」は**未実測の断定**だった | ★ `requirements-dev.txt` に固定 ＋ CI で install ＋ **版をログに出す**。⚠️ 今日の CI では在ったことも確認（step 21 success） |
| **M-5** | security-checker | ⚠️ `Swatinem/rust-cache` の走る場所の記述が誤り ／ `✅ 対処した` が実測より強い | ★ D1 を訂正 ＋ `ci.yml` の注記を「**third-party だけ**閉じた」へ書き換え |
| **L** | code-reviewer | `_uses_ref` の `#` 除去は**実経路では死にコード**（YAML が先に剥がす）／版名コメント検査が `ci.yml` 決め打ち／`docker://` の digest を誤って赤にする／注記「全 PR / push で走る」が不正確（**tag push では走らない**） | ★ すべて反映（docstring に明記／全 workflow を回す／digest 分岐／走る範囲を正確に） |

### ⚠️ 反映の過程で**自分が入れた退行**も 2 件（★ 記録する）

- ⚠️ HOSTED_ONLY の実在検査を `check()` に入れたため、**合成 fixture すべてに誤検出**が出る形になった
  （★ レビューが「`main()` 側に置け」と先回りしていた）→ `missing_hosted_only()` に分離。
- ⚠️ `report()` のカウンタに `composites` を足したのに旧呼び出しを直さず **`KeyError`**。
  → ★ 既定値でマージする形にした。

## D8: ⚠️★★★ **残る非対称を「対処済み」と書かない**

★ security-checker M-5 の指摘どおり、**鍵のある実機には `actions/*` が 4 本、可変タグのまま残る**
（`checkout` ×3 / `setup-node` / `upload-artifact` ×2 / `release` の `download-artifact` ×4）。
⚠️ 「`softprops` を固定したので被験者のバイナリを守った」は**閉じていない** ——
★ 成果物を用意するのは `download-artifact` である。

- **決定**: ⚠️ 裁定（`actions/*` はタグのまま）は**変えない**が、
  ★ `ci.yml` の注記を「**third-party だけを閉じた。`actions/*` 4 本は可変のまま**」へ書き換えた。
- ⚠️ **申し送り F-10**: ★ 「鍵に触れる場所 / `contents: write` を持つ場所」という **D1 自身の基準**に
  揃えるなら `actions/checkout`（self-hosted 3 job）と `actions/download-artifact`（`release`）も
  固定すべき、という指摘には**理がある**。→ ★ **研究者裁定に回す**。
