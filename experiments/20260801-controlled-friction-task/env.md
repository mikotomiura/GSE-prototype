# 実行環境の固定（未実施・実施時に埋める）

> ⚠️ **本実験は未実施**。以下は実施時に確定させる項目の一覧である。

| 項目 | 固定方法 | 実施時に記入 |
|---|---|---|
| 解析 | `analyze.py` / `assign.py` / `validate_materials.py`（**Python 標準ライブラリのみ**） | — |
| Python | `python3`（`run.sh` が解決） | TBD |
| 乱数 seed | `SEED` = 20260801。用途は**ブロック順序と題材割付のみ** | 固定済み |
| ★ 並べ替え検定の seed | ★ **非該当**。**全数列挙**（G1: C(8,4)=70 / positive control: C(10,2)=45）なので seed に依存しない（`preregistration.md §3.9`） | — |
| GSE-prototype commit | 実施時の commit hash | TBD |
| Rust toolchain / `Cargo.lock` | 被験者端末で動かすアプリのビルド元 | TBD |
| `HMM_VERSION` | `engine.rs` の定数（`feat` 行の出所なので結果にも刻む）。★ **刻印手順は `protocol.md §6.1`**（実施当日・開始前に `env.md` へ、解析前に `config.json` へ） | TBD |
| ★ 実施 OS | **被験者端末**（Windows 11 / macOS）を記録する。下記の理由で結果解釈に効く | TBD |
| ★ アプリのビルド | 実施に使った**本番バイナリ**のタグ／コミット（★ 10 セッションは同一バイナリで回す） | TBD |
| ★ `GSE_DISABLE_PROBES` | **必須 = `1`**（`preregistration.md §5.4`）。⚠️ 立て忘れは `validate_blocks.py --dataset` が捕まえる | TBD |
| ★ 被験者の入力先 | **`writing-pad.html`**（`preregistration.md §2.11`）。ブラウザとプロファイル（拡張なし）を記録する | TBD |
| `gse-replay` | ★ **非該当**。`analyze.py` は NDJSON を直接集計し、`gse-replay` も HMM も通さない | — |

## ★★ P-1 の実施記録（実施当日・**最初のブロックより前**に埋める）

`protocol.md §6.1` の刻印手順に従う。⚠️ **時刻は書かない**（本 repo は一時 public 化の運用がある）。
★ **2 回**回す（`protocol.md §5.1` = 研究者判断 G-1 / G-4）。

### P-1 1 回目

| 項目 | 記入 |
|---|---|
| 実施 OS | **Windows 11** ／ ビルド番号: `______` |
| 題材 | **topic01**（`assign.py --pilot`） |
| 割付ファイル | `blocks/PILOT-win.json` |
| アプリのビルド | タグ `v0.1.22` ／ コミット `______`（★ 4 ブロックとも同一バイナリ） |
| `HMM_VERSION` | `______`（★ 実施に使う**そのビルド**の値。参考: `main` の `engine.rs` は `0.3.0`） |
| `GSE_DISABLE_PROBES` | `1`（★ launcher `launch-g1-windows.bat` 経由） |
| 起動ログの確認 | ☐ `probe scheduler DISABLED by GSE_DISABLE_PROBES=1` を確認した |
| 週の選択 | ☐ **第 1 週（blind 較正）**（★ 既定値。触っていなければ OK） |
| 入力先 | `writing-pad.html` ／ ブラウザ: `______` ／ プロファイル: 拡張なし ☐ |
| 実施日 | `______`（★ 時刻は書かない） |

### P-1 2 回目

| 項目 | 記入 |
|---|---|
| 実施 OS | **macOS** ／ バージョン: `______` |
| 題材 | **topic02**（`assign.py --pilot --pilot-topic 2`） |
| 割付ファイル | `blocks/PILOT-mac.json` |
| アプリのビルド | タグ `v0.1.22` ／ コミット `______` |
| `HMM_VERSION` | `______` |
| `GSE_DISABLE_PROBES` | `1`（★ launcher `launch-g1-macos.command` 経由） |
| 起動ログの確認 | ☐ 確認した |
| 週の選択 | ☐ **第 1 週（blind 較正）** |
| 入力先 | `writing-pad.html` ／ ブラウザ: `______` ／ プロファイル: 拡張なし ☐ |
| 実施日 | `______` ／ 1 回目からの間隔: `______`（★ **60 分以上空ける**か翌日） |
| ⚠️ 既知の欠測 | `ime_dwell_med` が構造的に欠測 → **実質 13 特徴**（`§5.1`） |

⚠️ ★ **解析の前**に `config.json` の `reproducibility.hmm_version` を同じ値に書き換えてコミットする
（`protocol.md §6.1`）。現在は `TO_BE_STAMPED_AT_EXECUTION` のままである。

## 依存の少なさについて

`analyze.py` は標準ライブラリのみで動く（`json` / `statistics` / `math` / `itertools` / `pathlib`）。
L2 罰則つきロジスティック回帰も自前実装（Newton 法・14 特徴 × 6 標本）である。
numpy / scipy を使っていないのは、**再現に lockfile を要さないため**
（`experiments/20260802-within-person-scope-detector/env.md` と同じ方針）。
将来 numpy を導入する場合は `requirements.txt` を本ディレクトリに追加すること。

## ★ 訂正（2026-08-02・第 2 版）— Tier 0/1 は凍結解除を待たない

> ~~⚠️ 実施は **Phase1 完了 ＋ 研究者承認による凍結解除後**。凍結中に `engine.rs` / `schema_dto.rs` を
> 変更してはならないため、**FS-B（Tier 0/1 特徴量）は凍結解除まで計算できない**。~~
> （第 1 版・**誤り**。訂正する。）

**訂正内容**: NDJSON は既に以下を持っており、Tier 0/1 は**すべてオフラインで計算できる**。

| 必要なもの | NDJSON 上の出所 |
|---|---|
| `keys` / `bs_rate` / `silence_*` / `burst_*` | `key` 行（**打鍵 1 打ごと**に `{t, category, press}`） |
| `external_paste_chars` | `paste` 行 |
| `ime_dwell_med` | `ime_shadow` 行の `dwell_ms` |
| FS-A（F1/F3/F4/F5/F6） | `feat` 行（1Hz） |

凍結されているのは **Tier 0/1 を実行時の推論経路（`feat` 行・HMM）へ配線すること**であって、
**オフライン解析には無関係**である。`analyze.py` は `src-tauri/` を 1 行も変更していない。

> ### ★ 追記（2026-08-03・第 5 版）— 「コード変更ゼロ」は撤回した
>
> ⚠️ **解析は依然として `src-tauri/` に依存しない**（上の訂正は有効である）。
> ★ しかし **実施のためにアプリ側の 1 行が要る**ことになった: `§2.6` は「アプリ内プローブを
> 使わない」と凍結しているのに、アプリは放っておくと出す。`§3.6` が事後のブロック除外を
> 禁じているので、**止められるのは実施前だけ**である（`preregistration.md §5.4`）。
> → **プローブ kill switch**（`GSE_DISABLE_PROBES=1`）を実装した。
> 消えるのは `probe_assignment` / `probe_triggered` / `realtime_label` の 3 行だけで、
> **FS-A（`feat` 行）も FS-B（`key` / `paste` / `ime_shadow` 行）も HMM も不変**である。

→ ★ **技術的には、G1 は Phase1 の凍結解除を待たずに実施できる。**
⚠️ ただし `ADR-009 D7` / `personalization-and-online-learning.md §8.2` は
「G1 は凍結解除後の最初のタスク」と書いている。**実施順序の決定は研究者判断**であり、
本文書はそれを変更しない。

## ★ 実施 OS が結果に効く点（`preregistration.md §5.1`）

- **`ime_shadow` は Windows 限定**である（`lib.rs` の `emit_ime_shadow` が
  `#[cfg(target_os = "windows")]`）。
  → **macOS で実施すると `ime_dwell_med` が構造的に欠測**し、全ブロックで 0 になる。
- **`external_paste_chars`** は、課題文を**紙で配る**運用（`protocol.md`）ではペーストが
  発生しないため、どの OS でも全ブロック 0 になる見込みである。
  ★ 記入パッド（`§2.11`）はペーストを**禁止しない**（禁止は打鍵挙動への介入になる）ので、
  実際に 0 だったかは `validate_blocks.py --dataset` が `paste` 行数として報告する。
- 特徴量セット（FS-B = 14 特徴）は**変えない**。分散ゼロ特徴は標準化後 0 に潰し、
  **`degenerate_features` として必ず出力する**（`preregistration.md §5.1`）。
- ★ **可能なら Windows 11 で実施することが望ましい**（FS-B を設計どおり 14 特徴で評価できる）。
  これは推奨であって判定基準ではない。

## 入力 NDJSON の形式（匿名化後）

`analyze.py` は **`analysis/anonymize.rs` を通した形式**を入力に取る:

- `key` の `vk` は **`category`** に置き換わっている（本文再構成不能）。
- 絶対 epoch 時刻 `t` は **session_start 相対 ms** になっている。

→ ★ **1 ブロック = 1 セッション**（`protocol.md §1`）なので、
`t` はそのまま**ブロック内の相対時刻**として使える。

## 実行時間の目安

並べ替えは全数列挙（70 / 45 通り）で、各回に leave-one-pair-out 16 fold の当てはめを再実行する。
被験者 1 名あたり数秒〜十数秒（FS-A / FS-B / `keys` 単独 / positive control の合計）。
