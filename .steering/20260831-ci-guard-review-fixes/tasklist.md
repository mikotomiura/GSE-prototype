# タスクリスト

## 調査 (実測)

- [x] PR #134/#136/#137/#138 の状態を確認 (→ #136/#137/#138 MERGED・#134 CLOSED)
- [x] `chore/ci-disk-hygiene` の実在を確認 (→ **削除済み**。中身は `main` にある)
- [x] `bash scripts/check-o1-release-readiness.sh` (→ 通過 18 / 未達 1)
- [x] ⚠️ 指摘 #3 の前提を検証 (→ **launchd 登録は済んでいた**。レビューの前半は誤り)
- [x] ⚠️ `cargo-sweep` の実在を検証 (→ **不在**。指摘 #4 が実際に起きていた)

## 実装

- [x] `.github/actions/disk-guard/action.yml` を新設 (実体を 1 か所に)
- [x] `check` を composite action 呼び出しに置換 ＋ `wiped` でキャッシュ復元を条件化
- [x] `build-macos` に同じガードとキャッシュ条件を追加 (指摘 #1)
- [x] fail-closed / `df -Pk` / warning 格上げ / 掃除後の再判定 (指摘 #4)
- [x] ⚠️ 自分が作り込んだサブシェル欠陥を修正 (`::error::` が変数に飲まれていた)
- [x] `scripts/maintenance/` に正本 ＋ インストーラ ＋ README (指摘 #3)
- [x] `.steering/20260831-ci-disk-hygiene/requirement.md` の誤 `[x]` を訂正 (指摘 #3)
- [x] fork 遮断を 3 ジョブに追加 (指摘 #5 / §2 候補 b)

## 検証

- [x] ガード本体を 4 状態で実走 (ok / nodf / low / sweepless) — 全て期待どおり
- [x] ★ **陽性対照**: 旧コードを注入して fail-open を再現 (exit 0 で素通りすることを確認)
- [x] `actionlint` を main と差分比較 (新規指摘ゼロ)
- [x] `shellcheck` 新規シェル 2 本 ＋ composite action 本体 (rc=0)
- [x] `scripts/check-shell-portability.sh` (通過 7 / 未達 0)
- [x] `install-cargo-sweep-launchd.sh --verify` を現状に対して実行 (❌ 2 件を正しく検出)
- [x] ⚠️ `security-checker` — 実施。**新規 HIGH ゼロ / MEDIUM 2 / LOW 4**
  - [x] ⚠️★★★ MEDIUM: **fork ゲートは防御でなく事故防止**だった (workflow 定義は PR head 側から
        読まれるので攻撃者が `if` を消せる) → ★ **コメントの誤りを訂正**した
  - [x] ★ 実測で裏取り: PRIVATE / `422` (private では fork PR 承認を事前設定不可) /
        `sha_pinning_required: false` / `main` にブランチ保護・ruleset **無し**
  - [x] LOW: symlink 経由の `rm -rf` 脱出 → 塞いだ (陽性対照つき)
  - [x] LOW: sweep の check-then-act 競合 → WARN をログに残す
  - [x] LOW: `workflow_dispatch` + タグで `release` が走る → **コメントを訂正** (挙動は不変)
  - [ ] ⚠️ MEDIUM: **action の SHA ピン留めが無い** → ★ 別 PR (下記 follow-up)
- [x] ⚠️ `code-reviewer` — 実施。**HIGH 1 / MEDIUM 4 / LOW 6**。★ 依頼した 6 観点のうち
      式・`needs:` 連鎖・bash・誤爆閾値は「問題なし」と根拠つきで確認された
  - [x] ⚠️★★★ HIGH: sweep の**黙った部分成功** (`swept -gt 0` は 2 本のうち 1 本成功で緑。
        ★ CI workspace 側がハードコードで不在になると「ローカルだけ掃除して緑」)
        → ⚠️ **枯渇するのは CI workspace 側**。local / runner を**別々に判定**し、
        パスは `.runner` の `workFolder` から導出する形に変えた
  - [x] ⚠️★★ MEDIUM: **fail-closed が df の列ズレを捕まえていなかった** ——
        `int("ccc")` は awk の仕様で **0 を返す** (★ 自分で再現した)。
        → `free before: 0 GiB` で検査を素通りし **target を削除**して誤った診断で終わっていた。
        ⚠️ `-P` で防ごうとしたケースが**破壊に化けていた**。→ 数値検査を awk の中へ移した
  - [x] MEDIUM: `gse-win` レグが無防備 → ⚠️ **実測が無いので掛けない**。★ 除外の根拠を
        `if:` の直上に明記し follow-up に起票 (推測で fail-closed を入れると CI ごと止まる)
  - [x] MEDIUM: `build-macos` が `check` と同一閾値 → ⚠️ **推測で数字を置かない**。
        `du -sh` で実測してから `with:` を足す旨を注記 ＋ follow-up
  - [x] MEDIUM: sweep の TOCTOU → 各 `cargo-sweep` の**直前で再検査**して skip
  - [x] LOW: `cargo sweep` → `cargo-sweep sweep` に統一 (⚠️ cargo が壊れた実績があるため)
  - [x] LOW: キャッシュ **保存も飛ぶ**ことを注記 (★ 将来「バグ」と誤修正されないため)
  - [x] LOW: `bootout` → `bootstrap` の競合にリトライ
  - [x] LOW: skip 時の outputs は「空文字」ではなく **`null`** → 注記を訂正
  - [x] LOW: 旧 steering の `[ ]` に「→ 本タスクで完了」を付す
- [x] ⚠️★★ **自分の推測が 2 件外れたので訂正した** (★ 実測しなければ気づかなかった)
  - `.runner` のキー名は `workDirectory` ではなく **`workFolder`**
  - ⚠️ **BSD sed は BRE の `\|` を解さず、エラーも出さずに 0 件マッチ**する
    → ★ `sed -E` に変更。⚠️ 気づかなければ「検出しているつもりで常にフォールバック」だった
    (memory `macos-default-tools-break-gates` と同型)
- [ ] ⚠️ `/cross-review` (Codex)
- [ ] ⚠️ **CI が実際に緑になること** (★ push するまで分からない。予測しない)

## ⚠️ follow-up として起票するもの (★ 本 PR の外)

| # | 何 | 重さ |
|---|---|---|
| 1 | ⚠️ **self-hosted で走る action を commit SHA でピン留め**する。★ fork ゲートはこの経路に**一切効かない** (上流乗っ取りは push/tag でも成立)。`dtolnay/rust-toolchain@stable` は**タグでなくブランチ**である点に注意 | HIGH |
| 2 | ⚠️ 候補 **c**: `~/.gse/age-identity.txt` をランナーと別マシン/別アカウントへ退避 (★ 唯一の本質的対策) | HIGH |
| 3 | ⚠️ **public 化するなら直後に** fork PR 承認を "all external collaborators" にする運用手順を docs に置く (★ private のうちは事前設定できない) | 中 |
| 4 | `main` にブランチ保護 / ruleset が**無い** (実測)。★ 無レビュー相乗り事故 (e641874) の再発防止としても効く | 中 |

## ⚠️ やっていないこと (★ 明示する)

- [ ] ⚠️ `cargo test` — **走らせていない**。Rust に 1 行も触っておらず、かつ実機の `rustup` が
      壊れてローカルで cargo が起動しない
- [ ] ⚠️ 実機でディスクを枯渇させた本番検証 — **できない** (合成ハーネスで代替した)
- [ ] ⚠️ `install-cargo-sweep-launchd.sh` の**実行** — `cargo` が壊れているため未実行。
      ★ `rustup` 復旧後に研究者が実行する
- [ ] ⚠️ §2 候補 c (鍵の退避) — 研究者の運用判断
