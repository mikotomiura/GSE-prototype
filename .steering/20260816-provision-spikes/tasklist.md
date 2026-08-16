# tasklist — 配布自動化 spike

⚠️ ★ **spike の結果を「たぶん」で埋めない。** 全て「可 / 否 + 実測値 + 実測日」で書く。

## 0. 下ごしらえ（★ Console に触る前）
- [x] `browser-verification` skill を読む（⚠️ `claude-in-chrome` を使う前の必須参照）
      → ★ **S-6 に制約が 1 つ増えた**: §4 は「認証情報の入力は**絶対にやらない**」、
        §2.5 は「OAuth の同意画面は別ウィンドウで **MCP から操作できない**」。
        → Console の UI 操作は私、⚠️ **ログインと「許可」ボタンは研究者**。
- [x] `~/.venvs/gse-provision` を作り、`google-api-python-client==2.198.0` /
      `google-auth-oauthlib==1.4.0` / `pytest==9.1.1` を入れた（Python 3.14.4・import 実測済み）
- [x] `scripts/requirements-dev.txt` に**バージョン固定**で追記（既存規約に合わせた）
- [x] ⚠️ `.gitignore` が実際に無視するか **`git check-ignore` で実測**
      → `token.json` / `client_secret_123.json` / `credentials.json` / `my_token.json` /
        `.env.local` / `experiments/…/token.json` = 全て IGNORED。
      ★ **陽性対照**: `NOTIGNORED.json` / `README.md` / `src/main.tsx` は追跡対象のまま
        （＝ 検査が「常に IGNORED と言う」空回りではないことを確認）

> ★ **2026-08-16 時点: §1〜§5 は spike-3 の後半を除いて完了。**
> 結果は `spike-results.md`（★ 全項目に実測値と実測日）。
> ⚠️ 最重要の発見: **spike-1 は「可」だが `drive.file` は「作れるが見えない」**ため、
> 手作業で作った既存フォルダを収束器が見つけられず**重複を作る**。設計の決め直しが要る。

## 1. 資格情報（★ Console 作業・S-6 のガードを守る）
- [ ] `scripts/provision-credentials.md` を先に書く（⚠️ **秘密そのものは置かない**）
- [ ] Cloud プロジェクト作成 → Drive API 有効化
- [ ] OAuth 同意画面: スコープは `drive.file` **のみ**
- [ ] ⚠️★ 公開状態を「本番」にする — **押す前に研究者へ確認**（S-1 / Stop 条件）
      ★ 審査を求められたら**止めて相談**
- [ ] 「デスクトップアプリ」クライアントを作成し `client_secret.json` を取得
- [ ] `~/.config/gse-provision/`（**0700**）へ配置
- [ ] ⚠️ 初回認可を **cwd がそこ以外**の場所で走らせない工夫を入れる
      （★ `InstalledAppFlow` は既定で cwd に `token.json` を書く）
- [ ] `git status` / `git ls-files` で**秘密が追跡下に無い**ことを確認

## 2. `drive_client.py` 初版（★ Drive を叩く前に、偽 API で先にテストを書く）
- [ ] `drive_client.py`: folder 作成 / file 作成 / list / permissions.create /
      permissions.list / permissions.delete
- [ ] 偽 API の単体テスト（⚠️ **陽性対照込み** — 全部止めるガードが緑にならないこと）
  - [ ] ★ 照合が赤 → **共有まで進まない**（本丸・D-4）
  - [ ] ⚠️ 許可リスト外（`g1-submit.json` / `pubkey.txt`）を置いたら赤（陰性対照）
  - [ ] ⚠️★ `allowFileDiscovery=true` が返ったら「共有済み」と記録しない
  - [ ] ⚠️★ 撤回フラグ → **共有が外れた状態へ寄る**（D-7・共有する側と**対**で書く）
  - [ ] 既に正しい状態 → **API 呼び出し 0 回**（冪等）
- [ ] `~/.venvs/gse-provision/bin/python -m pytest` が **exit 0**

## 3. 入力の用意（★ 実被験者の割付を捨てフォルダに置かない）
- [ ] `assign.py --pilot --pilot-label spike --json` → `blocks/PILOT-spike.json`
- [ ] `build_task_pages.py` → `pages/PILOT-spike/blockNN.html`
      ⚠️ **通らなければここで止まって相談**（`pages/PILOT-*` は現存しない = 未実行の経路）
- [ ] manifest（byte 数 + SHA-256）を作る

## 4. spike 実走（★ 捨てフォルダ。⚠️ 本番の親フォルダに触らない）
- [ ] 捨ての**親**フォルダを用意する
      ⚠️★ **新 OAuth クライアント自身に作らせない**（それでは spike-1 の条件を満たさない）
- [ ] **spike-1**: `drive.file` で既存の親の下に子フォルダを作れるか
      → 否なら ★ 代替（親もアプリに作らせる）へ切り替えて**続行**
- [ ] **spike-4**: 上げた HTML の `mimeType` が `text/html` のままか
- [ ] **spike-5**: `files.list(fields=...)` が `sha256Checksum` を返すか（★ 4 と同じ 1 回で）
- [ ] `data-privacy` skill を読む（★ spike-2 を**押す前**に。否だったときの代替
      `type=user` は匿名性の設計に触るので、判断が要る場面で初めて読むのでは遅い）
- [ ] **spike-2**: `permissions.create(type=anyone, role=reader, allowFileDiscovery=false)`
      → ★ 設定後に `permissions.list` で**読み返す**
      → ⚠️ 否なら **止めて相談**（匿名性の設計に触る）
      → ★ 確認できたら**即座に共有を外す**（公開を残さない）
- [ ] **spike-3**: トークン発行時刻を記録し、失効の有無を**日付をまたいで**確かめる
      ⚠️ ★ 即断できない項目なので「測定開始日と再確認予定日」を明記する

## 5. 後始末と記録
- [ ] 捨てフォルダを Drive から削除
- [ ] `blocks/PILOT-spike.json` / `pages/PILOT-spike/` を削除
- [ ] `spike-results.md` を書く（★ 全項目に実測値と実測日）
- [ ] ⚠️ **本番に触れていない証拠**: `git status` に `dist/_drive/` `blocks/P0*.json` が無い
      ＋ 本番の親フォルダの子フォルダ数が spike 前後で不変
- [ ] `/review-changes`（code-reviewer + security-checker 並列）
- [ ] `/cross-review`（⚠️ ブロックされたら **skip 理由を完了報告に明記**）
- [ ] `/finish-task`

## ⚠️ 見つけたが直していないこと（別タスク）

### ★★ 1. `drive.file` の「作れるが見えない」問題（⚠️ 実装前に決着が要る）
`spike-results.md` の選択肢 A / B / C。★ 推奨は **A（親もアプリに作らせる）**。
⚠️ これを決めないと `provision.py` を書けない（重複フォルダを作る設計になる）。

### ★ 2. 配布状況ビューア（研究者の要望・2026-08-16）
「P-ID × フォルダ有無 / 枚数 / 照合の緑赤 / 共有の有無 / ★ **重複の検出**」を一覧で見る。

⚠️★ **設計上の必須条件**: ビューアを配布器と**同じ目（`drive.file`）で作ってはならない。**
同じ盲点を継承し、★ **重複が存在するのに全部緑に見える**（今日実測した非対称そのもの）。
→ GAS 側（別権限）から見るか、最低でも「どちらの目で見たか」を画面に明示する。
★ 既存の `checkMaterialsProvisioning()` が原型。⚠️ ただしあれは「共有済み = ✅」としか読まないので、
重複を検出できない（`decisions.md` D-7 の議論と同じ穴）。

### 3. spike-3 の後半（★ 期日つき）
- [ ] **2026-08-23**: `creds.refresh()` が通るか（テストモードの 7 日失効と対照できる位置）
- [ ] **2026-09-16**: 1 か月後の再確認

### 4. ★ 変異テストのハーネスが追跡下に無い
`scratchpad/mutate.py`（23 変異）で「守りが本当に赤を出すか」を確かめたが、
⚠️ **scratchpad にあるのでコミットされない** = 次の人が再実行できない。
★ `scripts/` へ昇格するか、`.steering/` に手順だけ残すかを別タスクで決める。
⚠️ ハーネス自体が偽陰性を出した（`__pycache__` の古い `.pyc`）ので、
昇格するなら `PYTHONDONTWRITEBYTECODE=1` を必ず含めること。

### 5. 捨てフォルダがゴミ箱に残っている
⚠️ `SPIKE-DELETE-ME-20260816` は**ゴミ箱に入れただけ**（完全削除はしていない）。
★ 研究者の判断で空にする。
