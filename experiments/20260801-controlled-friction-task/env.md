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
| ★★ 実施形態 | **来所 / 無人在宅**（`preregistration.md §2.14`・第 9 版）。⚠️ **被験者ごとに記録し、報告時に内訳を併記する。判定にも除外にも使わない**（`§3.6` 無変更） | TBD |
| ★ アプリのビルド | 実施に使った**本番バイナリ**のタグ／コミット（★ 10 セッションは同一バイナリで回す） | TBD |
| ★ `GSE_DISABLE_PROBES` | **必須 = `1`**（`preregistration.md §5.4`）。⚠️ 立て忘れは `validate_blocks.py --dataset` が捕まえる | TBD |
| ★ 被験者の入力先 | **`writing-pad.html`**（`preregistration.md §2.11`）。ブラウザとプロファイル（拡張なし）を記録する | TBD |
| `gse-replay` | ★ **非該当**。`analyze.py` は NDJSON を直接集計し、`gse-replay` も HMM も通さない | — |

## ★★ P-1 の実施記録（実施当日・**最初のブロックより前**に埋める）

`protocol.md §6.1` の刻印手順に従う。⚠️ **時刻は書かない**（本 repo は一時 public 化の運用がある）。
★ **2 回**回す（`protocol.md §5.1` = 研究者判断 G-1 / G-4）。

> ### ⚠️ ★ 実施順は計画と逆になった（2026-08-04 実測）
>
> 計画では **Windows を先**に回すことになっていた（`ime_dwell_med` が取れて 14 特徴になるため）。
> 実際に先に回ったのは **macOS 回**である。★ **入れ替えたのは順序だけ**で、割付・題材・
> ブロック構成は `blocks/PILOT-*.json` のまま変えていない。
> ⚠️ 以下の見出しは「1 回目 / 2 回目」ではなく **OS で引く**。

### P-1 Windows 回（`PILOT-win`）— ★ **未実施**

| 項目 | 記入 |
|---|---|
| 実施 OS | **Windows 11** ／ ビルド番号: `______` |
| 題材 | **topic01**（`assign.py --pilot`） |
| 割付ファイル | `blocks/PILOT-win.json` |
| アプリのビルド | タグ `v0.1.22` ／ コミット `______`（★ 4 ブロックとも同一バイナリ） |
| `HMM_VERSION` | `______`（★ 実施に使う**そのビルド**の値。参考: `main` の `engine.rs` は `0.3.0`） |
| `GSE_DISABLE_PROBES` | `1`（★ launcher `launch-g1-windows.bat` 経由） |
| 起動ログの確認 | ☐ `probe scheduler DISABLED by GSE_DISABLE_PROBES=1` を確認した ／ ☐ **確認できなかった**（⚠️ ★ Windows の release ビルドは `windows_subsystem = "windows"` でコンソールを持たないため、ダブルクリック起動では**出ない見込み**。客観検証は `validate_blocks.py --dataset` の `probe_assignment` 行 0 で行う） |
| 実施形態 | **来所**（★ P-1 は研究者本人。`§2.14-7` により形態の区別は非該当） |
| 週の選択 | ☐ **第 1 週（blind 較正）**（★ 既定値。触っていなければ OK） |
| 入力先 | `writing-pad.html` ／ ブラウザ: `______` ／ プロファイル: 拡張なし ☐ |
| 実施日 | `______`（★ 時刻は書かない） |

### P-1 macOS 回（`PILOT-mac`）— ★ **実施済み 2026-08-04**

| 項目 | 記入 |
|---|---|
| 実施 OS | **macOS 26.5.2**（BuildVersion `25F84`・`sw_vers` で実測） |
| 題材 | **topic02**（`assign.py --pilot --pilot-topic 2`） |
| 割付ファイル | `blocks/PILOT-mac.json`（★ 4 ブロックとも `file` を転記済み・`.gitignore` 対象） |
| アプリのビルド | タグ `v0.1.22` ／ コミット `7a939b8` ／ `CFBundleShortVersionString` = `0.1.22` |
| `HMM_VERSION` | **`0.3.0`**（★ ★ **配布バイナリが出した NDJSON の `meta` 行から実測**。`engine.rs` を読んだ値ではない。結果として `main` の `engine.rs` と一致した） |
| `GSE_DISABLE_PROBES` | `1`（★ launcher `launch-g1-macos.command` 経由） |
| 起動ログの確認 | ★ **非該当**（`open -a` 起動では stdout が出ない。`protocol.md` / launcher から除去済み） |
| ★ 客観検証 | ☑ **全 4 ブロックで `probe_assignment` / `probe_triggered` / `realtime_label` が 0 行**（`validate_blocks.py --dataset` 緑） |
| 週の選択 | ☑ **第 1 週（blind 較正）**（既定値のまま） |
| 入力先 | `writing-pad.html`（`pages/block0N.html` 内蔵）／ ブラウザ: **未記録** ／ プロファイル: **未記録** |
| 実施日 | **2026-08-04**（★ 時刻は書かない） |
| ⚠️ 既知の欠測 | `ime_dwell_med` が構造的に欠測 → **実質 13 特徴**（`§5.1`）。★ **実測でも `ime_shadow` は全 4 ブロックとも 0 行**で、想定どおりだった |
| ⚠️ ★ 未記録 | **`produced_chars`（記入パッドの文字数）を 4 ブロックとも取れていない**。研究者 1 名で被験者と実験者を兼ねたため転記の手が無かった（`§3.5` の報告義務は確証実施で満たす必要がある。P-1 は判定をしないので欠落しても判定に影響しない） |

> ### ⚠️ ★★ ブロック長が 5 分に収まっていない（実測・研究者確認済み）
>
> | ブロック | 条件 | 打鍵数 | 実測長 |
> |---|---|---|---|
> | 1 | copy | 2306 | **11:37** |
> | 2 | HI | 926 | 4:04 |
> | 3 | LO | 1113 | **7:14** |
> | 4 | copy | 2181 | **9:57** |
>
> ★ **原因は「タイマーを使わず、書き終わるまで書いた」**（2026-08-05 に研究者本人が確認）。
> ⚠️ **席を外した形ではない**——1 分バケットで見ると打鍵は途切れずに続いている。
> → `protocol.md §4.4`（タイマーは実験者側で持つ）は、**実験者と被験者が同一人物のとき成立しない**。
> ★ 対処は `.steering/20260805-g1-p1-analysis-and-material-fix/decisions.md` の **D-2**。

⚠️ ★ **解析の前**に `config.json` の `reproducibility.hmm_version` を同じ値に書き換えてコミットする
（`protocol.md §6.1`）。★ **2026-08-05 に macOS 回の実測値 `0.3.0` を刻印済み**。

⚠️ ★★ **Windows 回でこの値を書き換える前に、必ず上の macOS 回の値と突き合わせること。**
食い違ったら「2 回の P-1 が別の HMM で回った」ことになるので、
★ **上書きせず両方を残す**（`config.json` の `hmm_version_stamping` にも同じ指示がある）。

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
