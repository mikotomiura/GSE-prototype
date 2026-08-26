# 設計 — `decide-win-runner` の self-hosted 化

> 対象は requirement.md の受け入れ条件の最後の項目。研究者決定により新しい `.steering/`
> ディレクトリは作らず、本ディレクトリ（観測台帳）内にバンドルして実施する。

## 実装アプローチ

`.github/workflows/ci.yml` の `decide-win-runner` ジョブ (`runs-on: ubuntu-latest`, L67) を
`runs-on: [self-hosted, gse-mac]` に変更する。

### なぜこれが必要か（今回の障害から判明した構造的欠陥）

- `check` ジョブは `needs: decide-win-runner` (L118) — `decide-win-runner` が動かないと
  `check(win)` も `check(mac)` も**両方**ブロックされる。
- `decide-win-runner` 自体は `ubuntu-latest`（hosted）。GitHub の hosted Actions が
  major outage を起こすと、**gse-win / gse-mac の実機は無事でも** `decide-win-runner` が
  起動できず CI 全体が止まる（observed 2026-08-26 15:11–18:01Z）。
- 一方 `check(win-selfhosted)` / `check(mac-selfhosted)` は self-hosted runner が
  GitHub 側にポーリング接続するだけなので、hosted 側の compute (Actions コンポーネント)
  が死んでいても実際には動く（今回の障害中、run `32996144273` で両方 success したのが実証）。
- → `decide-win-runner` を self-hosted 側に移せば、hosted outage の影響範囲から外れる。

### なぜ `gse-mac` を選ぶか（`gse-win` ではない）

- **循環を避ける**: `decide-win-runner` の仕事は「`gse-win` が online か probe すること」。
  これを `gse-win` 自身の上で実行すると、`gse-win` が offline のときに probe ジョブ自体が
  self-hosted のキュー滞留（`ci.yml` L46-50 のコメント参照: timeout-minutes はキュー待ちに
  効かず、滞留は 24〜48h 後にしかキャンセルされない）に巻き込まれ、判定できなくなる。
- `gse-mac` には「たまにシャットダウンしている」という既存コメント（L45, gse-win 限定）が
  無く、`check(mac-selfhosted)` は現状すでに fallback 無しで無条件に `gse-mac` へ
  ジョブを出している (L128 の三項式で mac 側は固定)。→ **mac の可用性を無条件に信頼する
  前提はこのファイルに既に存在する**。`decide-win-runner` を mac に載せても新しい信頼を
  増やすわけではない。

## 変更対象

### 修正するファイル
- `.github/workflows/ci.yml` — `decide-win-runner` の `runs-on` を `ubuntu-latest` から
  `[self-hosted, gse-mac]` に変更。変更理由と新しいトレードオフをコメントで明記する。

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 影響範囲

- `check` ジョブの `needs: decide-win-runner` の依存構造自体は変えない。
- probe スクリプト本体（`gh api` / `jq` 呼び出し、hosted へのフェイルセーフ分岐）は
  変更しない。`gh` / `jq` が `gse-mac` に無くても、スクリプトは
  `2>/dev/null || true` / `|| echo 0` で握りつぶして 30 秒後に hosted へフェイルセーフする
  設計になっているため、mac 機のツール有無に依存しない（L88-111 の既存ロジックのまま動く）。
- `RUNNER_STATUS_TOKEN` シークレットはランナー OS に依存しないので変更不要。
- `decide-win-runner` に `actions/checkout` は無く、リポジトリのチェックアウトも
  ビルド成果物も要らないので、mac 機への追加負荷はほぼゼロ（30 秒以内の API 呼び出しのみ）。

### ⚠️ 新しく生まれるトレードオフ（隠さず明記する）

- **Before**: `gse-win` が offline でも `decide-win-runner`（hosted）は必ず完走し、
  `windows-latest` へフェイルセーフする。`gse-mac` が offline のときだけ `check(mac)` が
  キューに滞留する（`check(win)` は影響を受けない）。
- **After**: `gse-mac` が offline だと `decide-win-runner` 自体がキューに滞留し、
  **`check(win)` と `check(mac)` の両方**がブロックされる（`needs:` で連鎖するため）。
  → mac offline の影響範囲が「mac 側だけ」から「win 側も道連れ」に広がる。
- ★ この広がりは許容する: mac の可用性は既にこのファイルの他所（`check(mac-selfhosted)`
  自体）で無条件に信頼されている前提であり、新しい種類のリスクを持ち込むわけではない。
  また hosted outage（今回の実際の障害）の方が発生時の影響（CI 全体停止）が大きく、
  発生時の観測可能性も低い（githubstatus.com を都度確認しないと気づけない）。

### ⚠️ security-checker レビューで判明した M-1（未解決 follow-up として記録）

`gse-mac` の実機は **1 台 = 同時実行 1 スロット**（`gh api .../actions/runners` 実測:
`macbook-air-m-arm64` 1 台のみ）。`decide-win-runner` を同じ `gse-mac` に載せると、
`check(mac-selfhosted)`（最大30分）/ `build-macos`（最大40分）と**スロットを奪い合う**。
別ブランチの run が並走中（`concurrency` group は ref 単位なので起こりうる）だと、
本ジョブは offline でなくても busy でキューに並び、最大その分だけ開始が遅れる。
offline 時の 24-48h 滞留とは性質が違う（有限）が、hosted 時代には無かった遅延。

- ★ **恒久対策**: `gse-mac` に probe 専用の別ラベル self-hosted runner
  （例 `gse-mac-probe`）を追加登録し、`decide-win-runner` はそちらを使う。
  probe は checkout 無し・30 秒以内なので専用スロットの負荷は無視できる。
- ⚠️ **本タスクでは実施しない**: 物理マシン（gse-mac 実機）への runner サービス追加登録が
  必要で、このセッション（Windows 機）からは実行できない。次に gse-mac 実機を触る機会に
  まとめて対応する。
- ★ 上記トレードオフの延長として許容し、`ci.yml` のコメントに明記した上でマージする
  （研究者への確認は求めず、この記録をもって決定とする — 影響は「有限の遅延」であり
  「CI が止まる」種類の障害ではないため）。

### ⚠️★★★ code-reviewer レビューで判明した HIGH 2件・MEDIUM 2件（反映済み）

1. **HIGH: 根拠に使った run が主張と矛盾していた**。当初コメントは「outage 中に
   `check(win/mac-selfhosted)` が success した実績 (run 32996144273)」を引用したが、
   `gh api` 実測でその run の hosted ジョブ (`decide-win-runner`/`frontend-check`) は
   **4秒で完走**しており、障害が既に収まった後の run だった（`requirement.md` 観測台帳 #4
   自身が「障害復旧後」と記録している）。→ `verify-before-claiming` 原則の違反。
   **正しい根拠**に差し替えた: `requirement.md` の「決着」節が引く実測
   （hosted 2 ジョブが `runner_name` 空のまま 15分キューで cancelled、self-hosted 2台は
   `online, busy=false`）。あわせて **本変更が効く範囲は限定的**（job は生成されるが
   hosted 割り当てだけ死ぬケースのみ救える。run 自体が空 = job 0件のケース
   [実例: run 32985752839] は runs-on をどこに向けても救えない）ことをコメントに明記した。
2. **HIGH: `jq` 不在時に偽の「gse-win did not come online」ログが出る**。`jq` 呼び出しの
   `|| echo 0` が判定不能を「オフライン確定」の文言に化けさせる設計だった。probe ループの
   前に `gh`/`jq` の存在確認 (`command -v`) を追加し、無ければ理由を明示して即 hosted へ
   fail-safe するよう変更した。
3. **MEDIUM: `check(mac-selfhosted)` を指す行番号コメント (`L128`) が本 diff 自身で陳腐化**。
   行番号参照をやめ「`check` ジョブの mac 側 `runs-on`」という内容ベースの参照に変更した。
4. **MEDIUM: `decide-win-runner` が failure すると `check` が win/mac 両方 skip され
   CI シグナルが消える**（self-hosted 化で新たに生まれた失敗経路。hosted の使い捨て VM は
   実質 failure しなかった）。`check` の `if:` を `!cancelled()` にし、`runs-on` の win 側に
   `|| '["windows-latest"]'` フォールバックを追加して、decide-win-runner failure でも
   hosted へ落ちて `check` が走るようにした。
5. **参考情報として追記**: `.idea/20260801-self-hosted-runner-setup.md:70-71` に
   「Mac の電源とネットワークが前提。スリープ中はジョブがキューに溜まる」と明記されており、
   「gse-mac は gse-win と違って無条件に安全」とまでは言えない（運用前提が守られている
   限りという条件付き）。ci.yml のコメントにこの条件を明記した。

### ⚠️ /cross-review (Claude + Codex) で判明した論点（ブロッキングではないが記録）

1. **スコープの穴**: `frontend-check` は本変更の対象外で `runs-on: ubuntu-latest`
   (hosted) のまま残る。hosted outage が再発した場合、`check` (win/mac) は本変更で
   救えるが **`frontend-check` は引き続きブロックされうる**。requirement.md の受け入れ
   条件は「CI 発火/緑化」全体を指しているため、「outage 再発時に CI が完全に緑になる」
   という期待と本変更の実効範囲にはギャップがある。frontend-check の self-hosted 化は
   本タスクの範囲外（decide-win-runner のみが対象）。
2. **security-checker の「fork PR 経路は確認済み」という記述の精度**: 検証対象が
   fork PR に絞られていた。self-hosted (`gse-mac`) を `pull_request` トリガーで使う
   リスクは fork PR に限らず**同一リポジトリ内 PR でも同型で存在する**(ワークフロー
   定義自体が PR head の内容で評価されるため)。ただし `check(mac-selfhosted)` が
   2026-08-01 から既に `actions/checkout` + `cargo build/test` という**遥かに大きい
   攻撃面**で同種のリスクを受容しており、`decide-win-runner` (checkout 無し・固定
   ~30行の bash・低権限スコープの secret のみ) の増分リスクは相対的に小さい。
   チーム規模 2-3 人・private repo という前提も踏まえ、**追加対応は不要**と判断する。

## 既存パターンとの整合性

- `check(mac-selfhosted)` の `runs-on: fromJSON('["self-hosted","gse-mac"]')`
  (L128 の三項式内) と同じラベル指定パターンを使う。

## テスト戦略

- 単体テスト: 対象外（GitHub Actions ワークフロー定義であり、リポジトリの Rust/TS
  テストスイートの対象外）。
- 統合テスト: 本ブランチ (`chore/main-ci-firing-guard`) への push で実際に
  `decide-win-runner` が `gse-mac` 上で起動し、`runs_on` 出力が解決されることを
  実 run で確認する（GitHub Actions 以外に検証手段が無いため、これが実質的な統合テスト）。
- E2E テスト: 不要。

## ロールバック計画

`runs-on: [self-hosted, gse-mac]` → `runs-on: ubuntu-latest` に 1 行 revert すれば
即座に元の挙動に戻る（依存関係・出力インターフェースは変えていないため、他ジョブへの
波及は無い）。
