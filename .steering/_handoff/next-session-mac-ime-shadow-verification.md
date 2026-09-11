# mac セッション開始プロンプト — **macOS の IME 確定 / 放棄を実機で確かめる（issue 008 の AC 6）**

> 作成: 2026-09-11（Windows 機 = G-GEAR のセッションから委託） /
> ⚠️★★★ **このメモを一次資料にしない。** 実体は
> `.steering/20260911-outcome-arbitration-and-o1-preflight/issues/008.md` と
> `design-008-macos-ime-shadow.md`、`blockers.md` 起票 4 / 6 / 7 にある。

## §0 ⚠️★★★ 最初に読むべき事実 —— **配布済みリリースでは絶対に再現しない**

★ macOS の `ime_shadow` 送出元は **`main` に無い**。実装は **PR #182 のブランチにしかない**。

| 事実 | 根拠 |
|---|---|
| `main` の `emit_ime_shadow` は **Windows 限定** | `git show main:src-tauri/src/lib.rs` の `#[cfg(target_os = "windows")]` |
| `input/ime_compose.rs`（状態機械）は **main に存在しない** | `git show main:src-tauri/src/input/ime_compose.rs` → NOT in main |
| 実装は `feat/macos-ime-shadow`（PR #182）にのみ在る | — |
| `v0.1.35`（配布済み）は **main 由来** | ★ なので macOS では `ime_shadow` が**構造的に 0 行**になる |

→ ⚠️★★★ **`v0.1.35` の `.app` で試すと「動いていない」ように見えるが、それは実装が入っていないだけである。**

## §1 ⚠️★★★ 最初に実行する

```bash
cd ~/<repo>/GSE-prototype          # mac 側の clone
git fetch origin
git switch feat/macos-ime-shadow   # ★ main ではない
git pull
git log --oneline -1               # 3af47a9 以降であること
```

⚠️ **PR #182 が既に main へマージ済みなら `main` で構わない**（`git log --oneline main | grep macos-ime-shadow` で確認）。

## §2 ★ やること 3 件（⚠️ 1 と 2 は実機でしかできない）

| # | 何 | 起票 |
|---|---|---|
| **1** | ⚠️★★★ **確定 / 放棄が NDJSON で区別できることの実機確認**（AC 6） | 起票 4 |
| **2** | ⚠️ **macOS 純正「ライブ変換」下での ESC の意味**を確かめる | 起票 6 |
| **3** | ★ `gse-dataset` の `schema/current.json` 同期（⚠️ **PR #182 のマージ後だけ**） | 起票 5 |

---

## §3 タスク 1: 確定 / 放棄の実機確認（AC 6）

### 3.1 起動

```bash
# ⚠️ 素の `cargo run` / `cargo build --release` は使わない
#    (custom-protocol feature が付かずメインウィンドウが Vite devUrl 依存のまま)
VITE_GSE_DEBUG=1 GSE_DEBUG=1 npm run tauri dev
```

⚠️ デバッグ機能は**二重 gate**（`VITE_GSE_DEBUG` = ビルド時 / `GSE_DEBUG` = 実行時）。
★ 本確認にデバッグ UI は必須ではないが、診断パネルで **`hook_active` / `callback_count`** を
見られる方が「フックが生きているか」を先に切り分けられる。

### 3.2 ⚠️★★★ **通常モード**であることを担保する（G1 でも O1 でもない）

| 避けること | なぜ |
|---|---|
| `GSE_G1_MODE` / `GSE_O1_MODE` を設定しない | ★ 値が `"1"` に**完全一致**したときだけ立つが、事故防止のため unset にする |
| ⚠️★★★ **repo ルートに `g1.mode` / `o1.mode` を置かない** | ★ macOS はマーカーを **exe の 4 階層上**で探す。`npm run tauri dev` の exe は `src-tauri/target/debug/gse-next` なので、**4 階層上 = repo ルート**になる |

★ **事後確認**: NDJSON の先頭 `meta` 行に `g1_mode` / `o1_mode` フィールドが**無ければ通常モード**。

### 3.3 ⚠️ TCC（Input Monitoring / Accessibility）

- ⚠️ **バイナリを変えたら権限のリセットが要る**: `tccutil reset ListenEvent <bundle-id>`
- ⚠️ ad-hoc 署名では CDHash が不安定で Input Monitoring が効かないことがある
  → ★ その場合は Accessibility フォールバックに落ちる（それでも本確認は成立する）
- quarantine: `xattr -dr com.apple.quarantine <path>`
  ⚠️★★★ **`xattr -cr` は禁止**（他の属性まで消す）
- ★ 出典: `docs/development-guidelines.md:32-38`

### 3.4 ⚠️★★★ 操作手順（★ 順番に意味がある）

1. **Dashboard の「開始する」を押す**
   ⚠️ 押さないと `key` 行が出ない。★ また**起動時に開いたファイルとは別のファイルへローテートする**ので、
   押す前に打った変換は**前のファイル**に入る（★ 混乱の元なので必ず先に押す）
2. 日本語入力モード（かな）にする
3. ★ **確定パターン**: 「ねこ」と打つ → **Space** で変換 → **Enter** で確定 …… これを **3 回**
4. ★ **放棄パターン**: 「いぬ」と打つ → **Space** で変換 → **ESC** …… これを **3 回**
5. ⚠️ **各回のあいだに 2 秒ほど空ける**（★ 100ms ポーリングで要約を回収させる。
   連続で打つと**行が 1 本落ちる**のは既知の挙動）
6. アプリを終了する（★ `session_end` を書かせる）

### 3.5 NDJSON を見る

```bash
# 保存先: GSE_DATASET があれば $GSE_DATASET/raw/<participant_id>/
#         無ければ ~/Documents/GSE-sessions/
ls -lt ~/Documents/GSE-sessions/*.ndjson | head -3
F=~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson   # ★ 最新のものを選ぶ

# ⚠️ まず通常モードであることを確認する
head -1 "$F" | jq '{g1:.g1_mode, o1:.o1_mode, caps:.capabilities}'

# ★ 本体
grep '"type":"ime_shadow"' "$F"
jq -r 'select(.type=="ime_shadow")|[.t,.dwell_ms,.nav,.abandon]|@tsv' "$F"

# ★★★ これが AC 6 の合否
jq -r 'select(.type=="ime_shadow")|.abandon' "$F" | sort | uniq -c
```

⚠️ 上の jq は**リポジトリに記録が無い**（本メモのために組んだもの）。
★ 行の形は `{"type":"ime_shadow","t":…,"dwell_ms":…,"nav":…,"abandon":…}`。

### 3.6 ★ 合否

| | 期待 |
|---|---|
| ✅ **合格** | `abandon` に **`true` と `false` の両方**が出る（★ 目安: `false` 3 件 / `true` 3 件前後） |
| ⚠️ 不合格 A | `ime_shadow` が **0 行** → §0 のブランチ違い / TCC / 通常モードでない、を順に疑う |
| ⚠️ 不合格 B | 全部 `false`（ESC が拾えていない）→ ★ **起票 6 の可能性が高い**（→ §4） |
| ⚠️ 不合格 C | 行数が操作回数と合わない → ★ **合算・打ち切り**（起票 7）か、連続打鍵による欠落 |

⚠️★★★ **`gse-replay` では確認できない。** `replay.rs` は `ime_shadow` を
**読み飛ばすだけ**（`--snapshot` / `--metrics` のどれにも現れない）。→ **jq / grep が唯一の手段**。

---

## §4 タスク 2: ライブ変換下での ESC（起票 6）

⚠️★★★ **macOS 純正の日本語 IME は「ライブ変換」が既定で ON** であり、
**Space を押さずに変換が進む**（`survey-input-channels.md:153` 逐語「推定が特に外れる」）。

★ 本実装はセッションを **`composing` の寿命**（最初の英数字キー 〜 終端キー）で取ったので、
**Space を押さなくてもセッションは成立する**（`active` が立たないだけ）。
⚠️ **ただし ESC の意味が違う可能性がある** —— ライブ変換では ESC 1 回が「読みに戻す」だけで、
変換の放棄にならないかもしれない。→ ⚠️ **`abandon` が過大に立つおそれ**。

⚠️ この点は**リポジトリ内に一次記録が無い**（★ 推測で埋めないこと）。

### 手順

「システム設定 → キーボード → 入力ソース → 日本語 → **ライブ変換**」の **ON / OFF 両方**で:

1. かなを打って **ESC 1 回** → `ime_shadow` が出るか / `abandon` は何か
2. かなを打って **ESC 2 回** → 同上
3. かなを打って **Enter** → `abandon=false` が出るか

★ 結果を表にして `design-008-macos-ime-shadow.md` §7 へ追記する。
⚠️ **外れていたら `ime_compose::step` の `0x1B` 腕を見直す**（★ 直すのは Windows 機でよい）。

---

## §5 タスク 3: `gse-dataset` の schema 同期（起票 5）

⚠️★★★ **PR #182 が main へマージされるまで実行しない。**

★ 2026-09-11 に Windows 機で実測した事実:
- `gse-dataset/schema/current.json` は **prototype の `main` と一致している**
- drift しているのは **未マージの PR #182 分だけ**
- → ⚠️ **いま同期すると dataset が main を追い越し、main 上の全員に drift が見える**

### マージ後の手順

```bash
cd <GSE-prototype>
git switch main && git pull
python scripts/check_schema_parity.py --dataset <gse-dataset のパス>
# → DRIFT が出たら、スクリプトが出す修復コマンドどおりに実行する:
cd src-tauri && cargo run --bin emit_schema > schema/current.json
cp src-tauri/schema/current.json <gse-dataset>/schema/current.json
# ⚠️ 両側をコミットする
```

⚠️ 差分は **`description` 1 行のみ**で、**フィールドの追加 / 削除 / 改名はゼロ**。
→ ★ **既存の NDJSON は引き続き妥当**。

⚠️ `gse-dataset` には**別作業の未追跡ファイル**（`metrics/P000/macos/*.json`）がある。
★ **`git add -A` を使わず、`schema/current.json` だけをパス指定でコミットする。**

⚠️ `check_schema_parity.py` は **Windows の cp932 で drift の中身を出す前に落ちる**不具合があり、
★ **PR #183 で修正済み**。mac（UTF-8）では元から問題ない。

---

## §6 ⚠️ 作業規約（★ 省略しない）

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。**
  `cd src-tauri` するか `--manifest-path src-tauri/Cargo.toml` を付ける
- ⚠️ **`git add -A` / `git add <dir>` を使わない。** パスを明示する
- ⚠️ **キーストローク内容・NDJSON 生ログを外部 LLM（Codex 等）へ送らない**
  ★ 送ってよいのは **`abandon` の件数など集計値**だけ
- ⚠️ **既存のテストを無断で削除しない**
- ★ Skill: `hook-constraints` / `data-privacy` / `browser-verification`（ブラウザを使うなら）
- コミット: `[type]([scope]): [説明]` + 本文 + `Refs: .steering/20260911-outcome-arbitration-and-o1-preflight/`
- 応答は**日本語**で

## §7 ★ 終わったら書き戻す場所

1. `design-008-macos-ime-shadow.md` **§7** に実機結果を追記
2. `issues/008.md` の **AC 6 の行**を ⚠️ 未実施 → ✅ に更新し、Status を `done` にする
3. `blockers.md` の **起票 4 / 6**（★ 7 は直せない限界なので観察結果だけ）を解決に更新
4. ⚠️ **合わなかった場合は「合わなかった」と書く**（★ 直すのは別作業。記録を先に残す）

## §8 ★ 併走している状況（⚠️ mac では触らない）

| 何 | 状態 |
|---|---|
| **PR #182**（issue 008 本体） | ⚠️ **CI 全緑 / MERGEABLE**。★ マージは研究者判断 |
| **PR #183**（`check_schema_parity` の Windows 落ち） | ⚠️ レビュー待ち |
| **issue 007**（転帰定義の一本化・次の主タスク） | ★ `next-session-outcome-arbitration-adr029.md` で別セッションへ |
| **issue 009**（修飾キー同時押下フラグ） | ⚠️ **007 の裁定次第で不要になる**。着手しない |
