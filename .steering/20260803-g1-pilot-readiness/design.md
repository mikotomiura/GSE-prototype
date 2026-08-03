# 設計 — G1 パイロット P-1 の実施可能化

## 貫く原則: **失敗の可視性**（`protocol.md §1` が (a) を選んだのと同じ決め手）

> (b) の失敗は**沈黙して間違った結果を出す**が、(a) の失敗は**ファイルが無いという形で必ず露見する**。

本ラウンドの 4 つの成果物は、すべてこの原則の適用である。

| 成果物 | 沈黙しうる失敗 | どう露見させるか |
|---|---|---|
| T-1 プローブ無効化 | 「止めたつもりで止まっていない」 | ★ 実施後に **NDJSON の `probe_assignment` 行数 = 0** を機械検査する（`validate_blocks.py --dataset`） |
| T-1b 入力パッド | 被験者ごとに入力先が違う／補完が効いている | `protocol.md` で入力先を固定し、パッド自身が補完を構造的に持たない |
| T-5 `validate_blocks.py` | 転記ミスが解析まで生き残る | 割付を `assign.py` から**再生成して突き合わせる** |
| T-3 変換スクリプト | フォーム → JSON の手転記ミス | 手転記を挟まない（CSV → JSON を機械変換し、被験者 ID とブロック番号を検証） |

---

## T-1 プローブ無効化（B-1 = 案 C）

### 方針: **env 1 本・既定は無変更・純ロジックは `analysis/` に置く**

```
analysis/probe_scheduler.rs   probes_disabled_by_env(Option<&str>) -> bool   ← 純ロジック（テスト可能）
lib.rs                        std::env::var("GSE_DISABLE_PROBES") を読み、
                              true ならプローブスレッドを **spawn しない**
```

- **なぜスレッドごと止めるのか**: `poll` 側で握り潰すと「発火はしたが黙殺した」状態が残り、
  どこまで動いたのかが曖昧になる。**スレッドを起こさない**なら `probe_assignment` も
  `probe_triggered` も**構造的に発生しえない**。
- **なぜ env か**: 起動モード（`App.tsx` の週セレクタ）は凍結対象であり、
  かつ **2 つのモードのどちらでもプローブは止まらない**ことを調査済み（B-1）。
  ビルドを分けると被験者配布バイナリが 2 系統になる（`build-ci-and-pilot-distribution` の運用と衝突）。
- **なぜ `"1"` のみを真値とするか**: `GSE_DEBUG` と同じ規約に揃える。曖昧な真値解釈を持ち込まない。
  「止めたつもりで止まっていない」側の事故は**実施後に NDJSON から検出できる**ので、
  ここで寛容な解釈をする利得が無い。

### ★ 解析経路に影響しないことの論証（事前登録に書く）

| 消えるもの | G1 が使うか |
|---|---|
| `probe_assignment` / `probe_triggered` / `realtime_label` | ❌ 使わない（`§2.6` が「アプリ内プローブを使わない」と凍結） |
| `feat` 行（FS-A の出所） | ✅ **不変**（プローブは HMM を駆動しない） |
| `key` / `paste` / `ime_shadow` 行（FS-B の出所） | ✅ **不変** |

→ **FS-A / FS-B は 1 特徴量も変わらない。** HMM・リプレイ parity（`gse-replay --snapshot`）にも影響しない
（プローブは `FeatSnapshot` を生成しない）。

### `run.sh [5]` の扱い — ★ **赤にするのではなく、検査の意図を書き換える**

現行 [5] は `git status --porcelain -- src-tauri src` を見る。これは**未コミット変更しか見ない**ので、
プローブ無効化をコミットした瞬間に**黙って緑に戻る**——「G1 はコード変更ゼロで実施できる」という
主張を検査しているつもりで、実際には何も検査しなくなる。★ **これは silent pass である。**

そこで [5] の意図を次に置き換える（`preregistration.md` **第 5 版 §5-3 の訂正**として記録する）:

> **旧**: G1 はコード変更ゼロで実施できる（`src-tauri/` `src/` 非接触）
> **新**: ★ **G1 が要求するコード変更（プローブ kill switch）が入っており、それ以外の未コミット変更が無い**

- kill switch が**失われたら赤**になる（grep で存在を検査）。
- 無関係な未コミット変更があれば従来どおり赤（実験を未検証ビルドで回さない）。

---

## T-1b 入力先（B-5 = ローカル HTML 入力パッド・研究者判断 2026-08-03）

`writing-pad.html` を 1 枚置き、**ブラウザで開いて打つ**。

| B-5 の要件 | どう満たすか |
|---|---|
| 1 本文が残らない | ★ **保存機能を持たない**。`localStorage` / `sessionStorage` / fetch を一切使わない。閉じれば消える |
| 2 打鍵に余計な介入をしない（**最重要**） | `spellcheck="false"` `autocomplete="off"` `autocorrect="off"` `autocapitalize="off"` `data-gramm="false"` |
| 3 文字数が数えられる | live カウンタ。★ **数え方を 1 つに固定**（改行・空白を除く / `Intl.Segmenter` があれば書記素単位） |
| 4 両 OS で同一 | 同じ 1 ファイルを同じブラウザで開く。OS 差が入らない |
| 5 日本語 IME が普通に使える | 素の `<textarea>`。IME 変換は OS 標準どおり |

### なぜ「GSE に G1 実施モードを作る」（`blockers.md` 案 C）を採らなかったか

- `src/` ＋ `src-tauri/` の本格改修 ＋ **両 OS の CI ビルド** ＋ 事前登録第 5 版（content-free 明記）が要り、
  P-1 までの検証負荷が最大になる。**P-1 は「手順が回るか」を見る回**であって、新機能の初回投入に使う回ではない。
- ★ **WebView2 内 textarea の IME 挙動が `ime_shadow`（Windows）にどう出るかが未知**。
  入力先を変えると `ime_dwell_med` の出方が変わりうるのはどの案でも同じだが、
  自前 WebView は**最も検証されていない経路**である。
- ★ `§2.8` は「**実施手順**」の変更をパイロット後に明示的に許容している。
  したがって **P-1 をパッドで回し、確証本番までにアプリ内モードへ上げる道は残る**（判定基準に触れない）。

⚠️ **どの案でも P-1 で `ime_shadow` 行が出ているかを実測する**（`validate_blocks.py` が行数を出す）。

### ⚠️ 残るリスク（`protocol.md` に手当てを書く）

- ブラウザ拡張（Grammarly 等）が textarea に介入しうる → **拡張なしのプロファイル / 別ブラウザ**で開く手順を書く
- 被験者が誤って本文をコピー＆ペーストで持ち出す → `§5.1` の `external_paste_chars = 0` 宣言と
  合わせ、**パッドはペーストを禁止しない**（禁止すると打鍵挙動への介入になる）。代わりに
  `validate_blocks.py` が `paste` 行を報告する

---

## T-5 `validate_blocks.py`（転記ミスの検出だけ・除外も判定もしない）

```
python3 validate_blocks.py                       # blocks/ を全件検査
python3 validate_blocks.py --dataset ~/gse-dataset   # NDJSON の実在・probe 行 0 も検査
python3 validate_blocks.py --selftest
```

| 検査 | 種別 |
|---|---|
| ブロック 1..10 が揃い、1 と 10 が `copy`、2..9 が HI4/LO4 | **FAIL** |
| 条件列・題材 ID・課題文パスが `assign.py` の決定的出力と一致 | **FAIL**（再生成して突き合わせる） |
| `file`（NDJSON 名）が全ブロックにあり、重複していない | **FAIL** |
| `manipulation_check_answers` が 7 件あり、ブロック 3〜9 に対応。`harder` が当該ペアの 2 択に入る | **FAIL** |
| `produced_chars` が 300〜400 から極端に外れる | ★ **WARN**（除外ではない） |
| `--dataset` 時: NDJSON が実在する | **FAIL** |
| ★ `--dataset` 時: `probe_assignment` / `probe_triggered` / `realtime_label` 行が 0（B-1 の客観検証） | **FAIL** |
| `--dataset` 時: `ime_shadow` 行数・`paste` 行数の報告 | **INFO** |

- ★ **判定・除外・しきい値を一切持たない。** `§2.9` の適格性ゲートも `§3` の判定も
  `analyze.py` の責務であり、こちらは触らない（`§3.6` に触れない）。
- ★ **条件ラベルを画面に出さない**（P-1 は研究者本人が被験者なので、検査で条件が見えると盲検が更に崩れる）。
  不一致は「ブロック 5 の条件が割付と違う」とだけ言い、値は出さない。
- **セッション日時を出力しない**（NDJSON 名を echo しない）。

## T-3 フォーム

`Form_G1/GSE_G1_Form_Builder.gs`（`Form_Phase1` の型を踏襲: `openById` 固定 ID / `clearForm` /
`recordFormUrl` / 管理シート）。**3 フォームを 1 本の builder に**:

| | G1-C 同意 | G1-M 強制比較 | G1-S 終了後アンケート |
|---|---|---|---|
| いつ | 開始前・1 回 | ブロック 3〜9 の直後・計 7 回 | 最後の copy ブロックの後・1 回 |
| PII | 氏名・メール | ★ **被験者 ID のみ** | ★ **被験者 ID のみ** |
| 形式 | 必須チェックボックス ＋ 記名 | ★ **二択のみ**（「どちらでもない」なし・リッカート禁止） | 自由記述 ＋ 二択 |
| 絶対に書かない | どのブロックが難しい条件か | ★ **HI / LO** | ★ **HI / LO** |

- 変換: `forms_to_blocks.py`（CSV → `manipulation_check_answers`）。手転記を挟まない。
- ★ 強制比較フォームは**ブロック番号だけ**を持ち、条件を知らない。変換後の妥当性は `validate_blocks.py` が見る。

## T-4 終了後アンケート

★ **`§2` に「取るが判定には使わない」と明記してから取る**（後から使い道を決めると `§3.6` の穴になる）。
用途は (1) デブリーフ / demand characteristics、(2) ★ **B-1 の実測**（プローブが出なかったことの主観確認）、
(3) 手続きの改善、(4) 生態学的妥当性の記録。

## テスト戦略

| 対象 | どう検証するか |
|---|---|
| `probes_disabled_by_env` | `cargo test --workspace`（純ロジックの単体テスト） |
| プローブスレッド非起動 | ★ **実機**（P-1 当日に NDJSON の probe 行 0 を `validate_blocks.py` が検査）。ユニットテストでは覆えない |
| `validate_blocks.py` | `--selftest`（合成データで FAIL/WARN/PASS を回帰固定）＋ `run.sh [4]` に組み込む |
| `forms_to_blocks.py` | `--selftest` |
| `writing-pad.html` | ブラウザで開いて手動確認（文字数・補完なし・保存なし） |
| 全体 | `bash run.sh` GREEN ／ `validate_materials.py --strict` ／ `analyze.py --selftest` |
