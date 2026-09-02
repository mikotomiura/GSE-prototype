# tasklist — self-hosted の rust-cache 無効化

## 調査（★ 一次資料まで降りる）

- [x] PR #143 の失敗を API で確認 — ⚠️ 実体は `fail` ではなく **`cancelled`**
- [x] step ごとの所要時間を実測（3 job）— ★ 実作業は全 success・3m33s〜6m00s
- [x] run ログで `Cache hit` → `No cache found.` を確認（★ 3 job すべて）
- [x] 転送速度を実測 — ⚠️ 0.0〜0.6 MB/s・578〜730MB
- [x] ⚠️ **過去の run で復元が成功していたか**を確認 → ★ 08-30/08-31 は成功。当初の見立てを訂正
- [x] Actions キャッシュ総量を実測 — ⚠️ **10.56 GB**（上限 10GB 超過）
- [x] self-hosted の `target/` 永続を実測 — ★ 2.1GB・09-02 付 `.rlib` 237 個
- [x] ⚠️ **`build-macos` も同じ欠陥を持つ**ことを発見（★ L516・dmg を作る当のジョブ）

## 実装

- [x] `check` の rust-cache に `runner.environment == 'github-hosted'` を追加
- [x] `build-macos` の rust-cache に同条件を追加
- [x] ⚠️ `build-windows`（hosted）は**触らない**
- [x] `runner.environment` をログに出す step を両ジョブに追加（★ 分岐の証拠）
- [x] ⚠️★★★ `build-macos` の **npm キャッシュ**も無効化（★ v0.1.30 実測で 10m39s＝最大ステップ）
- [x] ⚠️ `frontend-check` / `build-windows` の npm キャッシュは**触らない**（hosted）
- [x] 実測に基づく理由をコメントとして残す

## 検証

- [x] YAML として妥当（ruby -ryaml）
- [x] `actionlint` — ★ 新規の指摘なし（残るのは既存の `gse-mac` ラベル 2 件と SC2012 1 件）
- [x] ⚠️ **変異注入**: `runner.enviroment` (typo) に変えると actionlint が
      `property "enviroment" is not defined ... {..., environment: string, ...}` で**赤になる**
      → ★ 検査が実在の欠陥を捕まえること＋`environment` が実在することの**両方**を確認
- [x] ⚠️ **CI 実機**: check (win / mac) が両方緑（★ run **33604121490**）
- [x] ⚠️ job 全体が **10 分未満** → ★ win **231s (3m51s)** / mac **296s (4m56s)**（⚠️ 従来 24〜31 分）
- [x] ⚠️ **`Post Run Swatinem/rust-cache@v2` が step 一覧に無い**こと
      → ★ 実測: `Run Swatinem/rust-cache@v2` = **skipped**、post は **step 一覧に 0 件**
- [ ] ⚠️ npm 側は判定が違う: ★ `setup-node` の post は**登録されるが 0 秒で終わる**
      （`cache` が空なので primaryKey 未設定で即 return する）→ **「無い」ではなく「0 秒」で判定する**
      ⚠️ **本 PR では未検証** —— ★ `build-macos` は**タグ限定**なので本ブランチでは発火しない。
      → ⚠️ **v0.1.31 のタグを打った run で必ず確認する**（★ そこが本命の検証点）
- [x] ★ ログに `runner.environment = self-hosted` が出ること
      → ★ 実測: 両ランナーで出力。`disk_guard.outputs.wiped` は mac=`false` / win=`(null)`

## ⚠️ code-reviewer 指摘の検算（★ 鵜呑みにしない）

- [x] ⚠️ **HIGH #1 は正しかった** — `build-macos` の rust-cache は v0.1.30 実測で **1 秒 / 0 秒**。
      ★ 私のコメントは `check` の数値を流用していた。→ 訂正済み
- [x] ⚠️ **HIGH #2 も正しかった** — `build-windows` の rust-cache も **3 秒**。
      ★「hosted だから利得がある」は未実証だった。→ 理由を差し替え済み
- [x] ⚠️ **HIGH #3 も正しかった** — 鍵に job id が入るので「check が更新を担う」は成立しない。
      ★ `if:` を実測（`build-macos` / `build-windows` は**タグ限定**）→ 既存コメント 2 か所を訂正
- [x] ★ **中「掃除役が 0 になる」は誇張だった**（⚠️ 自分で検算して**部分的に否定**した）。
      ★ `Cleaning cargo registry` が走るのは **save が発生する run だけ**である。
      ⚠️ save=0 秒だった run (33584750446) のログを見ると `Cleaning cargo registry` も
      `Saving cache` も **1 件も出ていない**（primary key ヒット時は post が即 return する）。
      → ★ **掃除はもともとほぼ走っていなかった**ので、本 PR で失われる掃除はほぼ無い。
      ⚠️ ただし 09-02 のような save が走る run では実際に走っていた（ログに実在）。
- [x] ★ 中「`~/.npm` 永続が未実測」→ 実測した（**3.7GB**・08-25 以降の更新 148 個）
- [x] ★ 小「`.steering/` が untracked」→ ⚠️ **既に追跡済み**（098ecf2）。レビューが見たのは古い状態

## レビュー

- [x] `code-reviewer` + `security-checker` を並列起動
- [x] ★ `/cross-review`（Codex）— ⚠️ **自己ブロックせず完走**（32,412 token / 日次 200,000 内）

### ★ `/cross-review` の結果（★ 一致 HIGH は 0 件）

- [x] ⚠️★★ **Codex のみ HIGH: PII をコードに固定していた** —— ★ 「実名が漏れる」と警告する
      当のコメントに **Windows 実機名（研究者の実名を含む）を平文で書いていた**。→ ★ 実値を消し、
      「値は実機か `gh api` の `runner_name` を見よ」に置き換えた。
      ⚠️ **ただし d1633f3 の履歴には残る**（★ private repo なので許容するが「消えた」とは書かない）。
- [x] ★ Claude のみ Low: `build-macos` のコメントが `check` ジョブの鍵を自ジョブのものとして
      引用していた → ★ 「これは本ジョブの鍵ではない」と明記して訂正
- [x] ★ Claude のみ Low: 本チェックリストが実測に追いついていない → ★ 更新した
- [x] ⚠️ **Codex の `shell: bash` 指摘は却下（false positive）** —— ★ 同ジョブの既存
      「Schema drift check」が変更前から両 leg で `shell: bash` を使っており、
      ★ 本 PR の Windows leg で当の step が**実際に成功している**（実測で反証）
- [x] ★ Codex Medium「hosted fallback 初回 cold が未測定」→ **部分採用**。
      ⚠️ 未測定なのは事実（★ 隠してはおらず design.md に明記済み）→ follow-up 化（下記）

## 外界の操作（★ 研究者承認済み・2026-09-02）

- [x] ★ Actions キャッシュの **rust 系 16 本（9650MB）を削除** → **10.56 GB → 1.13 GB**
      （⚠️ `node-cache-*` 3 本は残した）
- [x] ★ PR **#145** 作成
- [x] ⚠️ `rustup` 復旧 ＋ `cargo-sweep 0.8.0` 導入 ＋ launchd 再配置（★ 研究者の依頼）
- [ ] ⚠️ **PR #145 のマージ**（★ 研究者の確認待ち）
- [ ] ⚠️ マージ後、**#143 / #144 を再実行**して緑を確認

## ⚠️★★★ CI が露わにした別の欠陥 — テストのレース（★ 本 PR で直した）

★ 本 PR の CI で `submission_receipt_tests::only_a_real_send_writes_the_receipt` が
mac で落ちた（553 passed / 1 failed）。⚠️ **CI 変更が原因ではない。**

- [x] ★ 原因を特定: `IN_FLIGHT_TEST_LOCK` は `SUBMIT_IN_FLIGHT*` を触る 2 本に掛かっているのに、
      ⚠️ **`SUBMIT_LAST_SENT_*` を書き換える 2 本には掛かっていなかった**
      （`only_a_real_send_writes_the_receipt` / `reset_sent_receipt_clears_both_values`）。
      ★ モジュール自身のコメントが予告した失敗形態（「単独では緑・全体では赤」）そのもの。
- [x] ⚠️ **誤った安心の出どころも特定**: 「静的変数を共有するので**この 1 関数の中で**順に検査する
      （並列テスト安全）」というコメント。★ 1 関数内で順に見ても**別のテスト関数**は防げない。
- [x] ★ **手元で再現した**: 修正前 **40 回中 1 回失敗**
      （⚠️ `rustup` を復旧しないと再現すらできなかった → §5-6 を先に実施した）
- [x] ★ 修正: ロックを `SUBMIT_GLOBALS_TEST_LOCK` に改名し、**グローバルを触る 4 本すべて**に掛けた
- [x] ★ 検証: 修正後 **200 回中 0 回失敗**

### ⚠️★★★ 変異が当たらなかった（★ 正直に記録する）

★ 「ロックを 1 本だけ外す」変異を注入したが、**250 回中 0 回失敗**＝**変異が当たらなかった**。

⚠️ **したがって「この検査は実在の欠陥を捕まえる」とは言えない。**
★ 説明: `only_a_real_send...` がロック待ちの列に並ぶようになった結果**開始が後ろへずれ**、
速い `reset_sent_receipt...` が先に終わってしまう。→ ⚠️ **部分修正でも「たまたま」緑になる。**
★ つまりこの harness は**部分修正と完全修正を区別できない**。

→ ★ 根拠として採用するのは **対照（原状: 1/40）と修正後（0/200）の比較**であり、変異ではない。
→ ⚠️ 最終形は 4 本すべてがロックを取るので**構造として排他が成立している**（タイミング頼みではない）。
★ memory `measurement-instrument-false-positives` の「変異が当たらない」型の実例をまた 1 つ踏んだ。

## ★ 掃除機構の復旧（★ 研究者の依頼・2026-09-02）

- [x] ⚠️ `rustup` を復旧（★ `~/.cargo/bin/rustup` 本体が消え 13 個の symlink が全部宙吊りだった）
      → ★ toolchain 実体 1.98.0 は無事で `unchanged` と表示された
- [x] `cargo install cargo-sweep` → **0.8.0** を導入
- [x] ⚠️ `install-cargo-sweep-launchd.sh` を流し直し、**ドリフトしていた複製**を正本へ更新
      （★ 複製は 08-31 版・正本は 09-01 版だったので**上書きは新しい方への更新**だと確認してから実行）
- [x] ★ `--verify` が **7 項目すべて緑**（未達 0）
- [x] ⚠️★★ **「緑」で止めず実走させた** → `exit 0`・両 root を発見（`local=1 runner=1`）
- [x] ⚠️ **ただし解放は 0 バイト**（★ `Cleaned nothing`）。`--time 14` なので
      14 日より新しい成果物しか無い今は**何も消さない**。→ ★ 機構は動くが**今日の効果はゼロ**

### ⚠️★★★ ディスクの主犯は Rust ではなかった（★ 実測）

| 場所 | 実測 |
|---|---|
| ⚠️ `~/Library` | **44 GB**（うち `Application Support` 30GB / `Caches` 11GB） |
| ⚠️ `~/.vscode` | 10 GB |
| ⚠️ `~/.ollama` | 8.2 GB |
| `~/actions-runner` | 4.4 GB（★ target 2.7GB） |
| `~/GSE-prototype` | 4.2 GB（★ target 3.6GB） |
| `~/.npm` | 3.7 GB |
| `~/.rustup` | 1.6 GB |

★ `Application Support` の内訳: Claude 12GB / Google 9.5GB / Notion 2GB / discord 1.8GB。
★ `Caches` の内訳: Google 5.7GB / VSCode ShipIt 1.5GB。

→ ⚠️ **Rust 関連は合計約 10GB** で、使用中 162GB の 6% にすぎない。
→ ★ **週次掃除を直しても空き容量の問題は解けない。** ⚠️ 消すかどうかは研究者の判断が要るので触っていない。

## ⚠️ 本 PR が生んだ follow-up（★ 未測定を未測定として残す）

- [ ] ⚠️★★ **hosted フォールバック初回の実測** —— ★ G-GEAR offline 時に `windows-latest` へ
      落ちた run が `timeout-minutes: 30` に収まるか。⚠️ **一度も測っていない**
      （★ 参考値: hosted の cold `tauri build --no-bundle` 12m09s / tools 9m42s）。
      → ★ 次に G-GEAR が落ちたときの run を必ず見る。
- [ ] ⚠️ **v0.1.31 のタグ run で `build-macos` の npm キャッシュが 0 秒になること**を確認
      （★ タグ限定ジョブなので本 PR では発火しなかった＝**本命の検証点が未消化**）
- [ ] ★ テストロックの将来漏れを構造で防ぐ（⚠️ 現状 4 本は grep で漏れ無しを確認済みだが、
      新規テストが取り忘れても誰も気づかない）。→ helper 関数化などは別 PR

## ⚠️ 本 PR の範囲外（★ 引き継ぎメモの残件）

- [ ] v0.1.31 のタグ切り・配布物差し替え（引き継ぎメモ §1b）
- [ ] `cargo-sweep` の実機導入（§5-7）
- [ ] `rustup` の復旧（§5-6）
- [ ] self-hosted の action を commit SHA でピン留め（§5-1）
