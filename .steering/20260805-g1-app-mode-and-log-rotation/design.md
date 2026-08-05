# 設計 — G1 専用アプリモードとセッションログのローテート

> 設計の本体は `.steering/20260805-g1-p1-analysis-and-material-fix/decisions.md` の **D-7**。
> 本ファイルは**実装の形**と、調査/実測で D-7 に足したものだけを書く。

## 実装アプローチ

「G1 モードか」だけを判定する小さなモジュールを足し、**効果は `lib.rs` が適用する**。
⚠️ ★ **起動時に 1 回だけ判定する**（実行時トグルにしない）。プローブを
「スレッドごと起こさない」ことで「発火はしたが黙殺した」を構造的に消している設計を壊さないため。

```
g1::detect_from_env()            起動時 1 回だけ
  ├─ marker: <アプリを包むフォルダ>/g1.mode      ← 配布形（mac は exe の 4 階層上 / win は 1 階層上）
  └─ env:    GSE_G1_MODE=1                        ← 開発・検証
        │
        ▼  G1_MODE (OnceLock) ─── run() が書き、以後は読み取り専用
        │
        ├─► プローブスケジューラを起こさない  (既存 GSE_DISABLE_PROBES と OR。★ 既存は無変更)
        ├─► start_session (2 回目以降) が LogEntry::Rotate を送る
        ├─► 5:00 でブロック自動終了スレッド → LogEntry::BlockEnd + emit("g1-block-ended")
        └─► meta 行に "g1_mode":"marker"|"env"    ＋ 画面に「G1 モードで動作しています」
```

## 変更対象

### 新規作成するファイル
- `src-tauri/src/g1.rs` — 判定の純ロジック。`BLOCK_DURATION_MS` / `G1Source` / `decide` / `marker_path_for`

### 修正するファイル
- `src-tauri/src/logger.rs` — `LogEntry::BlockEnd` / `Rotate`、`LogTarget`(共有)、
  `write_meta_start` / `write_meta_end`、`next_session_path`
- `src-tauri/src/lib.rs` — `G1_MODE` / `G1_BLOCKS_STARTED`、`get_g1_mode`、ローテート、
  5 分自動終了スレッド、single-instance プラグイン、`LogState`/`LogStatusState` の共有ハンドル化
- `src-tauri/src/schema_dto.rs` — `Meta.g1_mode`（加算的） → `schema/current.json` 再生成
- `src-tauri/Cargo.toml` — `tauri-plugin-single-instance`
- `src/App.tsx` — G1 表示 / ブロック終了の受け取り / 二重起動の警告
- `experiments/20260801-controlled-friction-task/` — 第 10 版・`protocol.md`・`config.json`・
  `analyze.py`(版数)・`validate_blocks.py`(検査追加)・`participant-guide.md`・`README.md`・
  `record-sheet-pilot.md`・`launch-g1-macos.command`(廃止スタブ化)

### 削除するファイル
- なし（`launch-g1-macos.command` は**消さず**、実行すると理由を出して止まるスタブにした。
  ⚠️ 古いコピーを持っている人がダブルクリックしうるため、消すより止めるほうが安全）

## ★ 判断の要点（なぜこの形か）

### 1. ローテートは `SessionLogger::start` の再入ではなく `LogEntry` にした

⚠️ 引き継ぎは「`SessionLogger::start` を**再入可能**にする」と書いていたが、
★ **`Sender<LogEntry>` は分析 / IME / probe / wall / hotkey の 5 系統に clone 済み**である。
logger を作り直すと**全部の Sender を差し替える**必要があり、差し替え漏れ = 静かな記録欠落になる。
→ ★ **consumer スレッドの中で writer を差し替える**。channel も Sender も生きたまま。

### 2. `BlockEnd` と `Rotate` を分けた

★ ブロック終了時に新ファイルを開くと、10 ブロック目の後に **`meta` 1 行だけの 11 本目**が残る。
⚠️ `gse-submit` は `find_latest_session_ndjson` で**最新 1 本**を選ぶので、
★ **被験者が「提出する」を押すと空ファイルが出る**。
→ 閉じる (`BlockEnd`) と開く (`Rotate`) を分け、開くのは次の `start_session` だけにした。

### 3. ローテートは **G1 モードのときだけ**

⚠️ ★ 通常運用 (Phase1) で「戻る → 開始する」でファイルが分かれると、
上と同じ理由で **前半が提出されなくなる**。★ 既定の挙動を 1 バイトも変えない。

### 4. 5 分タイマーは Rust スレッド。ページ側のタイマーは**残す**

役割が違う（D-7 の「見直しタイミング」の決着・`protocol.md §4.4` に表を入れた）:

| 誰が | 何を止めるか |
|---|---|
| `writing-pad.html` (D-6) | ★ **被験者の打鍵**（readOnly ＋ 告知） |
| アプリ (本タスク) | ★ **NDJSON のブロック境界** |

⚠️ ★ WebView の背面タイマーはスロットリングされうる（G1 中、GSE の窓は背面）。ログ境界は託せない。
★ 手順を「ページを開く → 開始する」に統一したので、**ページの 5:00 が先に来る**
= 打鍵の取りこぼしが構造的にゼロ。

### 5. 二重起動は自作ポート排他 → **Tauri 公式プラグイン**（調査 R-3 / 実測 R-7）

⚠️ ★ 実測で「同じ bundle ID でもパスが違えば 2 プロセスが共存し、NDJSON が 2 本に割れる」ことを
確認したので**必須**になった。公式文書の指示どおり**最初に登録**する。

### 6. ファイル名の衝突を構造で防ぐ

⚠️ ★ `chrono_like_filename()` は**秒粒度**。同じ秒に 2 回ローテートすると
`create_file_at` の `truncate(true)` が**前のブロックを消す**。
→ `next_session_path()` が既存を避けて `_2`, `_3` … を付ける（**静かな全損の防止**）。

## 影響範囲

- **通常運用 (Phase1)**: ★ **挙動は変わらない**。`meta` 行は byte-identical、ローテートも
  自動終了も起きない。増えたのは single-instance プラグイン（2 個目の起動を止める）だけ。
- **ゴールデン / フィクスチャ**: `g1_mode` は `Option` で G1 時のみ出るため回帰なし
  （`meta_line_is_byte_identical_when_not_g1` が固定）。
- **gse-dataset**: `schema/current.json` を再生成した（加算的）。parity check は `/finish-task` Step 3。
- **P-1 の既存データ**: `validate_blocks.py` の新検査は `"confirmatory": False` を除外するので緑のまま。

## 既存パターンとの整合性

- `g1::g1_enabled_by_env` は `analysis::probe_scheduler::probes_disabled_by_env` と
  **同じ厳しさ**（`"1"` 完全一致）に揃えた。
- マーカーの探索は `lib.rs` の `gse-submit` 解決（`current_exe()` の隣・mac/win 分岐）に倣った。
- `LogStatus` の fail-loud（#1 層 2）は**壊さず拡張**した。ローテート先が temp に落ちたら
  バナーが出るよう、値のコピーでなく共有ハンドルにした。

## テスト戦略

- **Rust 単体**: `g1.rs` に 10 本（env の綴り・両 OS のマーカーパス・優先順位・`meta` 文字列の固定）
- **Rust 結合**: `logger.rs` に 5 本
  - ローテートで**2 本に分かれ、各々が自分の `meta` を持つ**（★ 本タスクの核心）
  - 2 本目の `session_start` が**新ファイルの実時刻**（`find_session_start` の基点）
  - `BlockEnd` → `End` で `session_end` が **1 行だけ**
  - ★ **G1 でないときの `meta` 行が従来と byte-identical**（ゴールデン非回帰の要）
  - ファイル名衝突の回避
- **Python**: `validate_blocks.py` に `g1_mode` 検査（★ **probe 行 0 とは独立の 2 本目**）
- ★★ **わざと壊して赤を実測する**（Rust 5 通り / Python 4 通り）。
  ⚠️ 前タスクで「追加した検査 3 本のうち 2 本が、何を壊しても赤にならなかった」ため。
- **回帰**: `cargo test --workspace` / `gse-replay --snapshot` (golden 2 本) / `emit_schema` diff
- **実機**: ★ プラグインが 2 プロセス共存を実際に止めるかを、R-7 と同じ手順で再測する

## ロールバック計画

- G1 モードは**引き金が無ければ何も起きない**ので、`g1.mode` を置かず env も立てなければ
  従来どおり動く（= 実質的なフィーチャフラグ）。
- 完全に戻すなら本ブランチを revert する。⚠️ ただし `schema/current.json` の再生成と
  gse-dataset 側の parity は連動して戻す必要がある。

## ⚠️ やらないこと（★ 期待を持たせない）

- **Gatekeeper は消えない**。`.app` は ad-hoc 署名で未公証（D-7 §「解決しないもの」1）。
  ★ ただし調査で**第 3 の道**が見つかった（機関の Apple Developer アカウントでの公証・R-5）
- **`gse-submit` が最新 1 本しか出さない**制約はそのまま（★ 既知の穴として記録・別トラック）
- **Windows は未実測**（二重起動・マーカーの探索階層とも）
