# issue 計画 —— IME 論文の評価一式（依存 DAG・Allowed Files 交差表・機械の割り当て・マイルストーン）

> `issue-slicing` skill（Opus・2026-09-28）で design.md §8 の 12 本の案から切り直した。一次資料は `design.md`（確定版）・`decisions.md` 判断 1–22。
> 実行モードは **C**（`_loop-config.json.mode = "C"`）。⚠️★★★ **分解と実行は別セッション**（`/clear` してから始める）。
> ★ 分解の前に研究者が決めたこと（判断 17–21）: E1 は**単体ロガー**を評価 ／ Windows 専用の issue は **G-GEAR でループ** ／ 読みは **SudachiPy を前処理だけに pin** ／ **GSE で開発し公開時に新 repo へ書き出す** ／ 作成物は**すべて `papers/ime-observation/`**。

## 0. 全体の形

- **ループで回す issue = 27 本**（うち任意 3 本は `## Status: blocked` で既定の選択から外してある）。★ コードと、その検査（selftest・acceptance）だけを持つ。
- **ループで回さないマイルストーン = M0〜M13**（§5）。⚠️ 実機の IME を動かす・合成キーを実際に送る・外部へ公開する・凍結する、はすべて**人とメインの仕事**である（★ worker は一度も合成キーを送らない —— 実行器は既定で送らず、テストは `dryrun` だけ）。
- ★ 設計の「12 本」との対応: 1 → 007 / 2 → 008 ＋ 009 / 3 → 003 ＋ 004 ＋ 005（＋ 段取り 006）/ 4 → M1 ＋ M2 ＋ M3（道具は 010 ＋ 015）/ 5 → 016 ＋ 017 ＋ 018 ＋ 019 ＋ 020 / 6 → 011 ＋ 012 ＋ 013 ＋ 014 / 7 → M4 / 8 → M5 ＋ M6 ＋ M7 / 9 → 021 ＋ 022（＋ M8）/ 10 → 023（＋ M10）/ 11 → 024（＋ M12）/ 12 → M13。★ 土台として 001（境界・形式の契約・content-free 検査器・検証の入口）と 002（コーパス）を足した。

## 1. issue 一覧

| id | 題 | runs_on | level | 依存 |
|---|---|---|---|---|
| 001 | 論文ディレクトリの境界・ログ形式の契約・content-free 検査器・検証の入口 | any | recheck | — |
| 002 | 青空文庫の句と読み（辞書は注入可能） | any | parse | 001 |
| 003 | シナリオ生成器（計画 `plan/1`・recipes はデータ） | any | parse | 001 |
| 004 | 実行器の核と dry-run・macOS（CGEventPost） | **macos** | recheck | 001 |
| 005 | 実行器の Windows（SendInput） | **windows** | recheck | 004 |
| 006 | 1 セルの段取り（起動・リセット・前面化・manifest） | any | parse | 003, 004 |
| 007 | 参照入力欄 macOS（NSTextInputClient・`gt/1`） | **macos** | recheck | 001 |
| 008 | 参照入力欄 Windows (a) IMM | **windows** | recheck | 001 |
| 009 | 参照入力欄 Windows (b) TSF 直受け | **windows** | recheck | 008 |
| 010 | 正解の組み立て（3 定義・規則は設定・oracle 照合・除外） | any | recheck | 001 |
| 011 | 単体ロガーの核（逐語コピー・シム・manifest） | any | recheck | 001 |
| 012 | 単体ロガーの macOS ドライバ | **macos** | recheck | 011 |
| 013 | 単体ロガーの Windows ドライバ (1) キーボード・IME 窓 | **windows** | recheck | 011 |
| 014 | 単体ロガーの Windows ドライバ (2) DWM cloak・開閉 | **windows** | recheck | 013 |
| 015 | 較正パイロットの道具（ImeShadow を封印） | any | recheck | 001 |
| 016 | 統計の部品（既知の値で検証） | any | parse | 001 |
| 017 | 照合器と検出の指標・パラメータ回復 | any | recheck | 016 |
| 018 | L1 の連続量・分類の指標 | any | recheck | 017 |
| 019 | L2 測度の一致 | any | recheck | 017 |
| 020 | 実験一式と 1 コマンドの再現 | any | recheck | 006, 010, 018, 019 |
| 021 | E2 閉集合のシミュレーション攻撃と除去実験 | any | recheck | 003, 016 |
| 022 | E2 開集合の復元 | any | parse | 003, 016 |
| 023 | E3 の器（2 条件・計器の写し） | any | parse | 006, 011 |
| 024 | 公開 repo への書き出し | any | recheck | 011, 020 |
| 025 | 〔任意・縮退 1 位〕実アプリへの転移確認の比較 | any | parse | 018 |
| 026 | 〔任意・縮退 4 位〕S9 マウス確定（macOS） | **macos** | recheck | 003, 004, 007 |
| 027 | 〔任意・縮退 3 位〕現代文コーパス | any | parse | 002 |

## 2. 依存 DAG と波

★ **依存先の成果物は後続の worktree に入らない**（`docs/loop-engineering.md` 2026-09-27 の是正）。→ ★ **波の切れ目ごとに、依存先を base（`feature/ime-eval-kit`）へ merge して push してから**次の波を回す。⚠️ 中間の merge も通常の merge ゲート（watchdog の再検証・clean な checkout での全 acceptance・レビュー）を通す。

```
W1  001
     │
W2  002  003  004[mac]  007[mac]  008[win]  010  011  015  016
     │    │ \   │  \              │              │ \ \        │ \
W3  027* │  006  005[win]         009[win]  012[mac] 013[win] 017  021  022
     │    │   │                                        │       │ \
W4  026*[mac]  023                                  014[win] 018  019
                                                            │  \  │
W5                                              025*       020
                                                            │
W6                                                         024
（* = 任意・既定で blocked）
```

- ★ 図に描いていない依存: **020 は 006 にも依存**する（run ディレクトリの形と、計画・oracle の検査器を使う）。
- **循環なし**（`plan_check.py` で機械的に確認・2026-09-28）。
- **最長 chain = 6 段**（001 → 016 → 017 → 018 → 020 → 024）。直列時の総 attempt の上限 = 6 × `max_attempts` 6 = 36。
- ★ **クリティカルパス（macOS の凍結 M3 まで）**: 001 → {003, 004, 007, 010, 011, 015, 016} → {006, 012, 017} → {018, 019}（＋ M0 → M1 → M2）→ M3。

## 3. Allowed Files 交差表

★ 交差があるのは次の 8 組だけで、**すべて依存で順序づけてある**（`plan_check.py` の出力 `unordered intersections: []`）。それ以外の組は交差ゼロ（∅）で、基準 3 の意味では並列可能。

| 組 | 共有するファイル | 順序づけ |
|---|---|---|
| 003 ↔ 026 | `kit/gen/recipes.json` | 026 が 003 に依存 |
| 004 ↔ 026 | `kit/emit/backend_macos.py` | 026 が 004 に依存 |
| 007 ↔ 026 | `kit/refinput-macos/RefInput.swift` | 026 が 007 に依存 |
| 008 ↔ 009 | `kit/refinput-windows/{Cargo.toml, Cargo.lock, README.md, src/core.rs}` | 009 が 008 に依存 |
| 011 ↔ 012 | `kit/logger/src/driver_macos.rs`（011 は空の差し込み口だけ） | 012 が 011 に依存 |
| 011 ↔ 013 | `kit/logger/src/driver_windows.rs`（同） | 013 が 011 に依存 |
| 011 ↔ 014 | `kit/logger/src/driver_windows.rs` | 014 が 013 → 011 に依存 |
| 013 ↔ 014 | `kit/logger/{manifest.windows.json, src/driver_windows.rs}` | 014 が 013 に依存 |

### ⚠️ 交差を避けるために意図した配置（★ 後から崩さないこと）

| 判断 | 理由 |
|---|---|
| 形式の契約（`FORMATS.md`）と content-free の検査器を **001 に集めた** | ★ 後続 26 本が同じ契約の上で並列に動く。`plan` / `oracle` / `corpus` の検査は**生産側**（003 / 004 / 002）が自分の selftest で持つ → `validate_logs.py` を複数の issue が触らない |
| `kit/check.sh` は `# kit: selftest` の目印で**自動で拾う** | ★ 後続の issue が入口を編集しない（交差しない・pin 済み verify の前提を変えない） |
| 単体ロガーの `Cargo.toml` の依存・features を **011 で全部宣言** | ★ 012（Mac）と 013 / 014（Windows）が `Cargo.toml` を触らない → **別の機械で並列に回せる** |
| ドライバのサブモジュールは `src/driver_<os>/` に置く | ★ `main.rs` を 011 だけが持つ |
| manifest を `manifest.json`（011）/ `manifest.macos.json`（012）/ `manifest.windows.json`（013・014）に分けた | ★ 照合器は `manifest*.json` を全部読む → 012 と 013 が交差しない |
| 実行器のバックエンドは**名前で読み込む**（`backend_<name>.py`） | ★ 005 が 004 の核を触らない |
| `analysis/` の各段は別ファイル・統計は 016 に集約 | ★ 017 / 018 / 019 が交差しない。再実装の禁止を各 acceptance が検査する |
| E3 の計器は `kit/e3/` へ**写す**（GSE の `experiments/` を実行時に読まない） | ★ 境界（`papers/README.md`）と、公開時の書き出し |

## 4. 機械の割り当て（判断 18）

| 機械 | issue | 起動 |
|---|---|---|
| **Mac** | 004 / 007 / 012 /（026・任意） | `bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues <ids>` ⚠️ `_loop-config.json` の `events_path` は G-GEAR のパスなので、Mac では**実行の前に** `/Users/johnd/GSE-prototype/...` に書き換える（★ 下の §7） |
| **G-GEAR（Windows）** | 005 / 008 / 009 / 013 / 014 | 同上（`events_path` はそのまま） |
| **どちらでも** | 残りすべて | ★ 既定は G-GEAR（本 config のまま回せる） |

★ acceptance は冒頭で `require_os` を呼び、**違う OS では exit 2 で止まる**（⚠️ 失敗ではなく「この機械で回すな」）。
⚠️ **`--issues` を付けずに回さない** —— 既定の選択は「blocked 以外すべて」なので、別の機械の issue も拾ってしまう。★ 各波で**その機械の id だけ**を渡す。

### 波ごとのコマンド（★ 波の間に merge → push を挟む）

```bash
T=.steering/20260927-ime-observation-paper-eval-design
# W1（G-GEAR・★ 基盤の検証を兼ねて 1 本だけ）
bash scripts/loop-run.sh "$T" --issues 001
# W2
bash scripts/loop-run.sh "$T" --issues 002,003,008,010,011,015,016   # G-GEAR
bash scripts/loop-run.sh "$T" --issues 004,007                        # Mac
# W3
bash scripts/loop-run.sh "$T" --issues 005,009,013,006,017,021,022   # G-GEAR
bash scripts/loop-run.sh "$T" --issues 012                            # Mac
# W4
bash scripts/loop-run.sh "$T" --issues 014,018,019,023               # G-GEAR
# W5 / W6
bash scripts/loop-run.sh "$T" --issues 020
bash scripts/loop-run.sh "$T" --issues 024
```

⚠️ 同じ run の中で依存先が `issue_done` になっても、依存先の成果物は後続の worktree に入らない。→ ★ **1 つの `loop-run.sh` の呼び出しに、同じ波の issue だけを渡す**（上のとおり）。

## 5. ループの外のマイルストーン（人とメインの仕事）

| id | 何を | どこで | 前提 | Done（観測できる条件） |
|---|---|---|---|---|
| **M0** | コーパスの確定: 作品を選ぶ・青空文庫から取得（★ 研究者の承認）・venv に `sudachipy` / `sudachidict_core` を入れて版を `kit/corpus/requirements.txt` に pin・`build_corpus.py` を回す | どちらでも | 002 | `kit/corpus/data/phrases.jsonl` がコミットされ `build_corpus.py --validate` が exit 0、SHA-256 と版が記録されている |
| **M1** | ★ macOS の較正パイロット（design.md §1.1a）: 参照入力欄 ＋ 実行器（**実際に送る**）＋ 単体ロガー（**`seal_obs.py` で ImeShadow を封印**）で S1–S15 を各数回・3 速さ。IME のリセット手段・マーカーのキー・前面化の手段を確かめる | Mac | 003 004 006 007 010 011 012 015 024 ＋ M0 | `experiment/pilot-macos.md`（呼び出し列の型・oracle 一致率・時計の差とドリフト・フックへの到達率・1 試行の実時間）と封印の `seal.json`。⚠️ **封印を開けていない** |
| **M2** | macOS の正解の定義を決める（`gt_rules` の `mac_nstic`）・recipes とマーカーを直す・n を 1 試行の実時間で見直す（判断 14） | Mac | M1 | `experiment/gt_rules.json` と `kit/gen/recipes.json` の差分がコミットされ、根拠が `pilot-macos.md` にある |
| **M3** | ★ **preregistration の凍結（macOS 版）**: 手順・定義・指標・n・速さの値（`[Pn]` で接地・citation-ssot）・除外規則・E2 の段・解析コードの commit | Mac | M2 ＋ 016 017 018 019 021 022 | `experiment/preregistration.md` に `frozen_at:` と `sha256:` の行があり、`run.sh`（020）が本番を止めなくなる。★ 凍結の commit にタグ。★ **凍結した事前登録を OSF Registries に登録し（判断 73・研究者が行う）、登録の URL・登録の日時・凍結の commit の書き出しの一覧の SHA-256 を `experiment/notes.md` に記録する。登録の日時が M4 の最初の run より前** |
| **M4** | macOS 本計測（1 晩 1 セル: 標準 IME のライブ変換 ON / OFF・〔任意〕Google 日本語入力） | Mac | M3 ＋ 012 | 全 run ディレクトリが `validate_logs.py` / `emit.py --validate` を通り、`run.json` の SHA-256 が `data.md` にある |
| **M5** | ★ Windows の較正パイロット（(a) IMM / (b) TSF の両経路・両者の区間が同じか） | G-GEAR | 005 008 009 013 014 015 024 ＋ M0 | `experiment/pilot-windows.md` と封印 |
| **M6** | ★ **preregistration の追補の凍結（Windows 版）**: 正解の経路の選択と定義 | G-GEAR | M5 | 追補に `frozen_at:` と `sha256:`、実測より前であることの記録。★ **追補も OSF に登録し（判断 73・別の登録か更新かは M6 の前に一次で確かめる）、URL と登録の日時を `experiment/notes.md` に記録する。登録の日時が M7 の最初の run より前**。★ 追補の節に「Status の日付は macOS の凍結の日で、印は追補で差し替えた」と 1 文（§8 で Status は書き換えられない・判断 132）。`run.sh` は `experiment/run.sh` と書く |
| **M7** | Windows 本計測（MS-IME 必須・〔任意〕Google 日本語入力） | G-GEAR（研究者） | M6 | M4 と同じ |
| **M8** | E1 の解析（`run.sh`）と E2 の実行（021 / 022 を本番のログに） | どちらでも | M4 M7 ＋ 020 | `experiment/results/*.json` と E2 の結果 JSON がコミットされる |
| **M10** | E3 の計測（両 OS・作業中 / 無操作） | 両方 | 023 024 ＋ 012 014 | `summarize_e3.py` の結果 JSON（「測れていない」でない） |
| **M11** | 〔任意〕実アプリへの転移確認 | 両方 | 025 ＋ M4 / M7 | 比較の結果 JSON |
| **M12** | 公開: ライセンス全文を置く → `export.py` → **研究者が新しい公開 repo を作る** → push → リリース → Zenodo の DOI。★ 公開 repo の最初の commit は、凍結のタグ `ime-observation-prereg-macos` から `--allow-missing-license` で書き出したものそのもの（一覧の SHA-256 `29b183ba…6c49`・98 ファイル・判断 131）にしてタグを付け、ライセンスと M12 の書き出しはその上に積む（事前登録 §9 の「公開物から一覧を計算し直せる」）。⚠️ 公開 repo は書き出した dir を `git init` した**新しい履歴**で作る（GitHub の fork・private repo の公開への切り替え・private の履歴の push は使わない —— 凍結の commit の 40 桁は OSF の登録で公開になるので、private repo が同じネットワークに入るとその commit のツリーが取り出せる・判断 132）。`experiment/notes.md` に「公開 repo のどの commit・タグが凍結の書き出しそのものか」「後の commit はライセンスなどを足すので一覧が変わる」を 1〜2 文足す | どちらでも | 024 ＋ M8 M10 | DOI が `CITATION.cff` と原稿にある。公開 repo の最初の commit から一覧の SHA-256 が計算し直せる。⚠️ 外部への操作なので研究者が行う（または承認を得て行う） |
| **M13** | 執筆と BRM への投稿（12 月）・〔任意〕CHI 2027 Posters（2027-01-21）—— カバーレターで併願を開示（判断 13） | — | M8 M10 M12 | 投稿の受付 |

★ M9 は欠番（design.md §8 の 9 を M8 に統合した）。
★ 2026-09-30・判断 68: パイロットと本計測（M1 / M4 / M5 / M7 / M10）のロガーは **024 の `export.py` の書き出しからビルドする**（ログの `manifest_sha256` が公開の manifest と一致する）。→ M1 / M5 / M10 の前提に 024 を足した（M4 / M7 は M3 / M6 を経て同じ）。
★ 2026-09-30・判断 73: 凍結（M3 / M6）は OSF Registries への登録で公開の日時を示す（private の GSE のタグだけでは読者が確かめられない）。→ M3 / M6 の Done に登録と記録を足した。

## 6. 縮退順（判断 14）と優先度

遅れたら**上から**落とす: ① 実アプリへの転移確認（025 ＋ M11）→ ② Google 日本語入力（M4 / M7 のセル）→ ③ 現代文コーパス（027）→ ④ S9 マウス確定（026）→ ⑤ E2 の開集合（022）。
★ ①③④ は `## Status: blocked`（任意）で既定の選択から外した。⑤（022）は外さない（最後に落とすもの・任意ではない）。

## 7. `_loop-config.json` の注意

- `events_path` は **G-GEAR の絶対パス**（`/c/GSE-prototype/...`）。⚠️ Mac で回すときは、実行の前に Mac の絶対パス（`/Users/johnd/GSE-prototype/...`）へ書き換え、**その変更はコミットしない**（`git diff` に残ったら戻す）。
- `verify` は OS に依存しない 3 本（`kit/check.sh`・`kit/check.sh --compile`・`scripts/check-shell-portability.sh`）。★ Rust / Swift のビルドとテストは**各 issue の acceptance** が持つ（OS ごとに違うため）。
- ⚠️ **W1（001）の前は verify が赤**（`kit/check.sh` が無い）。001 が作る。★ W2 以降はベースラインで緑になる。
- `allowed_tools` に `cargo` と `swiftc` を入れた（Rust / Swift の issue のため）。⚠️ `pip` は入れていない（M0 で人が入れる）。

## 7b. 残るリスク（★ 分解では閉じられなかったもの）

- ⚠️ **011 の macOS 側は 011 の検査でコンパイルされない**（G-GEAR で回すため）。→ 011 は macOS 側を「空の差し込み口 ＋ `Cargo.toml` の宣言」だけに留める。★ 012 が初めて macOS でコンパイルし、`main.rs` / `Cargo.toml` の直しが要れば 012 は **Stop**（→ 研究者が 011 の追補として直す）。逆も同じ（Windows 側は 013 が初めて）。
- ⚠️ **実機の挙動は worker が確かめられない**（参照入力欄・実行器・フック・TSF）。★ acceptance が見るのは selftest・ビルド・構造（禁止 API・コールバックの規則）まで。実機での確認は M1 / M5（パイロット）が最初である。→ パイロットで壊れていれば、その場で追補の issue を切る。
- ⚠️ `recipes.json` の手順（ESC の回数・予測候補のキー・IME の ON / OFF のキー）は**仮説**。M1 / M5 でデータとして直す前提（003 の設計）。

## 7c. 分解の後のレビュー（2026-09-28・Opus の独立検査・23 件）と反映

★ 「issue ファイルだけで実行が成立するか」を独立に検査させ、指摘を**一次で確かめてから**反映した（`capabilities.rs:319-332` の形・逐語コピー 5 か所の `.steering/` を実測）。

| 指摘 | 反映 |
|---|---|
| H1 `obs/1` の `capabilities` の形が GSE と違う | 001: GSE と同じ `{unconditional, threshold_gated, config_gated}`・値は名前の配列。acceptance に陽性・陰性を追加 |
| H2 逐語コピーの `.steering/` が 024 の秘匿検査に当たる | 001 / 024: manifest に載った逐語コピーの範囲だけ許す許可リスト |
| H3 manifest の `--self` / `--update` が後続を赤にする | 011: 差し込み口は `manifest.json` に載せない・`--update --manifest <file>` は 1 ファイルだけ書く |
| H4 抜粋の終了アンカーをコピー側に置けない | 011: コピー側は `// @excerpt-begin <id>` 〜 `// @excerpt-end <id>`、GSE 側は行全体一致・1 回だけのアンカー |
| H5 doc comment ごとの抜粋とアンカーの検査が両立しない | 011 〜 014: 抜粋に `symbol`（関数名）を持たせ、検査は `symbol` で行う |
| H6 実行器のバックエンドの境界が未定 | 004: `SUPPORTED_KEYS` / `Backend(opts)` / `open` / `send` / `close`・`--backend-opt`。005 / 026 はこの形で差し込む |
| M1 試行間・マーカーの待ちを計画に入れる場所が無い | 001 / 003: `gap_before_ms` / `marker_gap_ms` を `plan/1` に追加 |
| M2 011 の macOS 側がコンパイルされない | 011: `driver_api.rs` で境界の型を固定・macOS 側にロジックを置かない（§7b に残るリスクとして記録） |
| M3 JSON の空白の有無が暗黙の前提 | 001: 区切りに空白を入れない規則・`validate_logs.py` が拒否 |
| M4 020 の依存の抜けと run ディレクトリの形 | 020: 006 を依存に追加・run ディレクトリの形を明記 |
| M5 混合比の層が定義できない | 003: ブロックを速さで揃える／019: 層 = 速さ |
| M6 021 が import する関数が未定 | 003: `build_trial(...)` / `load_recipes(...)` を公開 |
| M7 009 の道 2 が必ず赤 | 009: 禁止は `.GetText(` の**呼び出し**だけ（実装は許す） |
| M8 base の前提 | `_acceptance-lib.sh`: ローカルの `feature/ime-eval-kit` を先に見る |
| M9 `mouse_click` の拒否と 026 の矛盾 | 004: 拒否は `SUPPORTED_KEYS` で行う（026 はバックエンドに足すだけ） |
| M10 manifest の `path` の基準 | 011: `path` は `kit/logger/` 基準・`gse_path` は repo ルート基準 |
| L1 / L2 / L3 / L4 / L5 / L7 | 015: 1 行以下に緩和／007: 複数行のシグネチャ／020: `[ -f ]` で確かめる／003: 変異で検査し直し（陽性対照つき）／017: `match` の入出力の形を固定、018・019: 差の符号 = 観測 − 正解／024: `[P269]` を許す |
| L6 selftest の実行時間 | 001: `check.sh` が所要時間を出し、30 秒超を警告（重い検査は `--full` へ） |

## 8. 分解の締めの自己検査

- [x] 各 issue を単体 merge しても main が壊れないか → ★ すべて `papers/` の中の追加（001 だけ `docs/` に 2 行）。GSE のビルド・CI の対象外。各 acceptance が `forbid_gse_changes` で `src-tauri/` などの差分 0 を検査する。
- [x] 各 AC に対応する test 名 / コマンドを「今」書けるか → 27 本すべての AC 表と `NNN-acceptance.sh` に書いた。
- [x] Allowed Files 交差表を作ったか → §3（交差 8 組・すべて順序づけ済み）。
- [x] DAG に循環がないか・最長 chain → 循環なし・**6 段**。
- [x] recheck を基準 5 で選別したか → **19 / 27**（content-free・合成入力の送出・フック・正解の定義・論文の数を出す解析・公開）。parse は 8 本（コーパス・生成器・段取り・統計の部品・E2 開集合・E3・任意 2 本）。
- [x] AC が書けない「リファクタするだけ」の issue を作っていないか → 無い。
- [x] pin 済み verify の前提を変える issue を最初の単独ウェーブに置いたか → ★ verify の入口 `kit/check.sh` を作る **001 が W1 の単独**。
- [x] test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか → ★ **27 本すべて**に `NNN-acceptance.sh`（共通の関数は `_acceptance-lib.sh`）。⚠️ verify は Python の selftest しか見ないので、Rust / Swift の issue は acceptance だけが実質の門である。
