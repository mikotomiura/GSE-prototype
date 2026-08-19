# 次セッション開始プロンプト — リブート後の「収集開始ゲート」を閉じる

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-19 に `.steering/20260819-g1-reboot-and-instrument-fix/` を実施し、
**ADR-013 の実装**と **G-1 の修正**を終えた。⚠️ **収集はまだ始められない**（§1）。

---

===

## §0 ⚠️★★★ 前セッションで確定したこと（★ 議論し直さない）

★ **研究者決定（2026-08-19）**: **G1 をリブートする。範囲は「計器＋運用」に限り、
設計の問い（何を測るか・条件・ブロック構成・分析計画）は 1 文字も変えない。**

| # | 決定 | 記録 |
|---|---|---|
| 1 | ★ P010 は**確証標本から外しパイロットへ**（⚠️ 削除しない）。確証標本 **0/3 名** | `preregistration.md` **第 17 版** |
| 2 | ★ **3 名を取り直す**（⚠️ 残り 2 名ではない）。`n = 3` は不変 | 同上 |
| 3 | ★ 較正プロトコル（T-C）は **G1 に相乗りさせない** | `decisions.md` 判断 3 |
| 4 | ★ 宣言 `task_kind` は **ADR-010 D3 の写し**（routing のみ・正しくさせようとしない） | 判断 5 |
| 5 | ★ リブート後の G1 は **現状の完全 lock のまま**回す（App.tsx 無変更） | 判断 6 |
| 6 | ★ 提出番号は **試行の連番**（中断分も番号を消費する） | 判断 4 / `protocol.md` |

### ★ 前セッションで実装したもの（★ 全部検証済み）

- `src-tauri/src/capabilities.rs`（**新規**）/ `meta` に `app_version` + `capabilities`
- `starve_window`（micro 帯の 60 秒窓集計・⚠️ `n_lt30 == 0` の窓は出さない）/ `dropped_delta`
- G-1: 実行中の再押下は **`Rotate`** で「前を閉じて新ファイル」（⚠️ カウンタは増やさない）
- 検証: `cargo test --workspace` 408 緑 / ゴールデン **6 本 byte-equal** /
  `HMM_VERSION` **`0.4.0` 据え置き** / schema parity 緑 / `validate_blocks.py --selftest` 緑

## §1 ⚠️★★★ 本セッションで閉じるゲート — **収集開始の前提**

⚠️ **これが終わるまで新コホートの収集を始めない**（ADR-013 D5 / `preregistration.md` 第 17 版）。

| # | やること | 状態 |
|---|---|---|
| **G-a** | ⚠️★★★ **電子同意フォームとの突合** | ★ **未了。本セッションの本命** |
| G-b | ★ gse-dataset 側の `schema/current.json` をコミットする | ⚠️ **未コミットのまま**（前セッションでコピーのみ） |
| **G-c** | ⚠️★★★ **配布アプリを v0.1.27 で作り直す** | ★ **版は上げ済み・タグは未作成**（下記） |
| G-d | ★ 募集の再開（3 名） | 研究者判断 |

### ⚠️★★★ G-c — **配布アプリの入れ替えは必須**（★ 版は上げてある）

★ **なぜ必須か**: 被験者が回すアプリが**新しい計器を持っていなければ**、
`capabilities` / `starve_window` / `dropped_delta` / G-1 のローテートは**1 行も効かない**。

★ **版は 2026-08-19 に `0.1.26 → 0.1.27` へ上げた**（`Cargo.toml` / `package.json` /
`tauri.conf.json` / `Cargo.lock`）。⚠️★★★ **上げないと ADR-013 の動機を再生産する** ——
`v0.1.26` は**既にリリース済み・配布済み**なので、そのまま配ると
**同じ `app_version` を名乗る 2 つの異なる能力セット**が生まれ、
★ **`app_version` を刻んだ意味が消える**（逐語「v0.1.25 と v0.1.26 を分けない」と同型）。

⚠️★★ **手元でビルドして配ってはならない。** `make-distribution.sh` 逐語:
「★ **アプリを手元でビルドしない。配るのは CI が作ったリリース成果物だけである**。
手元ビルドは署名・entitlements の後処理が CI と揃わない」。

★ **正しい手順**:

```bash
# 1. 本タスクの変更をコミット (★ 人の判断で)
# 2. タグを打って push → CI (.github/workflows/ci.yml) が両 OS をビルドしリリースを作る
git tag v0.1.27 && git push origin v0.1.27
#    build-windows (windows-latest)        → gse-next.exe / gse-submit.exe
#    build-macos   (aarch64-apple-darwin)  → gse-next_0.1.27_aarch64.dmg
# 3. 配布フォルダを組む (★ gh release download 経由)
cd experiments/20260801-controlled-friction-task
./make-distribution.sh <被験者ID> both --tag v0.1.27
```

⚠️ **macOS は `.dmg` で完結する**（`.zip` ではない）。`.app` に `gse-submit` と `pubkey.txt` が
同梱され、アプリ内提出が正規ルートである（`ci.yml` 逐語）。
⚠️★★ **Windows 機からは macOS ビルドを作れない**ので、**CI を通す以外の経路は無い**。
⚠️ 配り直したら **実機で G-1 (二度押し) と `starve_window` の出力を 1 回は目視確認**すること。

### ⚠️ G-a の中身（★ repo 側は 3 文書とも済んでいる）

★ **済**（2026-08-19）:
1. `consent.md` の記録項目表
2. `participant-guide.md`
3. ★★★ **同意の *正本ソース*** `Form_G1/GSE_G1_Form_Builder.gs`
   （同意フォーム本文の「▼ 記録するもの / しないもの」＋ 事前資料メール）

★ 追記した内容: `starve_window`（＝「1 分ごとの短い中断の回数と合計」）/ `app_version` /
⚠️ **在席の判定にマウス等の操作が効くこと**（★ マウスの動き自体は記録しない）/
⚠️ **静止して考えている時間はほとんど数えられないこと**。

⚠️ **未**: ★★★ **実フォームへの反映と突合**。
`.gs` を直しても**配布済みの Google フォームは変わらない** ——
逐語「`.gs` を直しただけでは実フォームは変わらない／**3 文書を同時に直す**」
（`consent.md:153-191`・★ **同型の事故の実績がある**）。

→ ★ 手順: `migrateConsentForm()` を実行 → `checkConsentFormParity()` で突合。
⚠️ **自動検査 (`scripts/check_g1_emails.py`) はこの drift を見ていない**ので、手順として明記すること。
⚠️ **既登録者は旧文面で同意済み**なので、再同意の要否も研究者判断で決めること。

→ ★ `browser-verification` Skill を**最初の 1 回で必ず**読んでから
`mcp__claude-in-chrome__*` を使うこと。

## §2 ⚠️ 前セッションで見つけて**直さなかった**もの（★ 意図的）

| # | 何 | ⚠️ なぜ直さなかったか |
|---|---|---|
| 1 | 通常運用では channel 満杯時に `session_start` 行が**黙って落ちる** | ★ 容量ガードは **G1 限定**にした。無条件にすると**通常運用の挙動が変わる**（研究者決定 #2 の外）。→ `decisions.md` 判断 9 |
| 2 | `App.tsx` の argumentative lock | ★ 方針だけ凍結（判断 5/6）。⚠️ 解除実装は **`g1_mode()` 条件付き**にすること |
| 3 | ADR-013 Migration 3 / 4（解析側の規約とテンプレート） | ★ 未了。⚠️ 「収集済み信号を使う解析は最初に `capabilities` を機械判定する」を `development-guidelines.md §10` と解析テンプレへ入れる。★ **`config_gated` の 0 行は「判定不能」**であることを必ず含めること |
| 4 | ⚠️★★★ **ブロック自動終了スレッド × 「開始する」押下の競合** | ★ **pre-existing** だが、G-1 修正で「実行中の押下」が想定内になったぶん**確率が上がった**。自動終了は `session_active=false` → `SESSION_START_MS=0` → **アイドル待ち最大 1500 ms** → `BlockEnd` の順で、この窓に押下が入ると **`BlockEnd` が新ファイルへ `session_end` を書く**（逆順なら**始まったばかりのブロックを殺す**）。→ ★ `SESSION_START_MS` の `compare_exchange` か「ブロック遷移の排他」が要る。**別タスクの粒度**（`blockers.md` D-1） |

## §3 ★ その次 — GSE 研究全体のアジェンダ（⚠️ 本セッションでは実行しない）

★ 前引き継ぎ `next-session-prompt-g1-reboot-and-instrument-fix.md §10` の **R-A〜R-F** をそのまま引き継ぐ。
⚠️ **期限があった R-F2（較正の G1 相乗り）は 2026-08-19 に「相乗りさせない」で決着済み**なので、
★ 残りは順番を入れ替えてよい。

★ **リブートで待ちが伸びたもの**（⚠️ G1 の *判定* に依存する側）:
**R-A1**（Stage 2 昇格・約 50 セッション）/ **ADR-011 D4「読む実装」** / **R-A4**。

★ **待ちが伸びていないもの**（⚠️ ここを進めるのが合理的）:
- **R-D（表現層）** —— ★ 系統 B は **HMM の前段**なので **MhD の判定に依存しない**。
  ★ 保留 3 件（**R-D1 / R-D2 / R-D3**）は「**文献では埋まらない・手を動かすと決まる**」と特定済み。
- **R-B4 Stage 0** —— ★ **P010（パイロット）を入力に使える**。
  ⚠️ **`--last-session-on-restart` が要る**（block07）。
  ★★★ **リブート後の新ログには `starve_window` が載る**ので、左打ち切りが緩む。
- **R-E2**（reason code のログ化）/ **R-C2**（AI 依存の文脈）—— G1 非依存。

## §4 ⚠️ 落とし穴（★ 実測・前セッションで踏んだものを含む）

1. ⚠️★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）。`cd src-tauri` してから叩く
2. ⚠️★★ **Windows コンソールは cp932** → Python は **`PYTHONUTF8=1` を必ず付ける**
   （★ 2026-08-19 に `python -c` で `UnicodeEncodeError` を踏んだ）
3. ⚠️★★ **bash の heredoc は長い日本語で壊れる** → ★ `Write` でファイルにしてから実行する
4. ⚠️★★★ **`check_schema_parity.py` は `--dataset` 必須**。
   ★ さらに **`| tail` にパイプすると `$?` が tail のものになり、赤を見落とす**
   （★ 2026-08-19 に実際に見落としかけた）。→ **リダイレクトしてから `echo $?`**
5. ⚠️★★ **`emit_schema` の diff は `required` の増加を必ず確認する**。
   ★ 2026-08-19 に `dropped_delta` が `required` に入り、**旧ログが検証に落ちる**ところだった
   → DTO を `Option` にして回避（`schema_dto.rs` のコメント参照）
6. ⚠️★ Rust のソース走査テストで **`&src[i-48..i]` のようにバイト数で切らない**
   （★ 直前が日本語コメントだと**文字境界で panic** する・2026-08-19 実測）
7. ⚠️★ `/cross-review` の `secrets-filter` は実在形式のセッション名に反応する（fail-closed）。
   ★ **パス限定で回す**（`scripts/run-codex-review.sh -- <paths>`）。⚠️ `--ack-filtered` で迂回しない
8. ⚠️★★★ **Codex は repo を読めない**（`--sandbox read-only` は Windows 1312 でシェルが起動しない）。
   ★ 資料はプロンプトに貼り「シェル禁止」を明記する（★ 失敗 3 回で 162k 消費した実績）

## §5 ★ 進め方

1. `/start-task` で `.steering/[YYYYMMDD]-consent-form-reconciliation/` を作る
2. ★ `browser-verification` Skill を読んでから Chrome を使う（**最初の 1 回で必ず**）
3. G-a → G-b の順に閉じる
4. `/finish-task`（★ `/cross-review` は**パス限定**で）

⚠️★★★ **収集を再開したら、また `src-tauri/` の記録仕様には触れなくなる**
（`preregistration.md §3.6` がブロックの事後除外を禁じているため）。
→ ★ **触るなら収集開始の前に触ること。**
