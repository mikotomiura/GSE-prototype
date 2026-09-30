# M1 macOS 較正パイロット 1 回目の記録（2026-10-01・Mac・内部記録）

> 公開物の `experiment/pilot-macos.md` は、正解の定義が決まってから英語で書く。これは内部の生の記録。
> ⚠️ 観測側の ImeShadow は**読んでいない**（`seal_obs.py` で封印してから、キーの行だけで集計した）。

## 条件

- 機械: MacBook Air（Apple Silicon）・macOS 27.0・JIS キーボード・入力ソース ABC ＋ 日本語ローマ字（`com.apple.inputmethod.Kotoeri.RomajiTyping`）・**ライブ変換 ON**（研究者が入力メニューで確認）
- 観測: 単体ロガー（書き出し `9f1d28dc` からビルド・判断 68・`manifest_sha256` `0aa2983e…`）。参照入力欄: `refinput-macos` を repo の外で `.app` に包み bundle id `org.imeobs.refinput` を付けた（下の所見 1）
- 計画: コーパス `c8f890cb…`・仮の config（n = 3・速さ 300 / 200 / 120 ms・think 0.2〜20 s・マーカー F13 / F14 / F13）・seed 1・126 試行・6 ブロック。S15 の移り先は Finder
- IME の学習は**リセットしていない**（研究者の判断・普段の学習を消さない）。ブロックの頭で `focus_cmd` がかなキー（key code 104）を押して日本語にした
- run: 短い試験 `short-1`（9 試行）→ 本体 `pilot-1`（126 試行・22.9 分・打ち切りなし・6 ブロックすべてで前面の確認が取れた）。生ログは `~/ime-pilot/runs/`（git に入れない）

## 結果

| 項目 | 値 |
|---|---|
| フックへの到達（`reach.py`） | 送った押下 4,000 のうち 3,982。欠けは S14 の 9 試行の `ime_off` / `ime_on` の 2 押下ずつだけ（英数 0x66・かな 0x68 は `is_observed_key` の外＝**設計どおり観測しないキー**）→ **観測するキーの到達は 100%** |
| 時計（`clock_sync.py`・gt 側だけ） | gt − oracle の中央値 3.0 ms（壁時計）/ 2.6 ms（単調時計）。ブロック 0 だけ 102 ms（起動直後・短い試験でも 106 ms）。観測側はマーカーが届かず測れない（所見 2） |
| 1 試行の実時間（`call_types.py`） | 中央値 7.8 s・p95 26.3 s（S13 の 21 s 待ちを含む）。**待ち・マーカー込みで 126 試行 22.8 分 = 10.9 s / 試行** → 本番 1 セル 3,150 試行なら**約 9.5 時間**（design.md の見積もり 7.5 時間より長い） |
| 割り当てられない呼び出し | 41（`first_rect` 28・`do_command` 12〔`noop:` を含む〕・`focus_in` 1） |

## 所見（M2 で直す）

1. **参照入力欄に bundle id が無い**: 送出側の前面化は `tell application id "<bundle id>"` と前面の bundle id の読み戻し。`swiftc` の素の実行ファイルでは確認が通らない → `refinput-macos/build.sh` で `.app`（Info.plist に `CFBundleIdentifier`）を作る。
2. **マーカー F13〜F19 は観測側に原理的に届かない**: 逐語コピーの `is_observed_key`（`kit/logger/src/driver_macos/keymap.rs`）は macOS で F1〜F12 だけ。gt 側には届く（vk 105 / 107）。→ マーカーを F1〜F12 から選ぶ（IME の状態を変えないもの・F6〜F10 は変換中に意味を持つので避ける）。⚠️ F1〜F12 は `FORMATS` のキーの列挙・送出の keymap・生成器の語彙に無い → 足すのはコードの変更。あわせて `marker.json` の `max_gap_ms` は `marker_gap_ms`（150）より大きくする（実測の間隔 152〜227 ms）。
3. ★ **変換した後の合成 Enter が確定しない**: Enter の直後 600 ms 以内の最初のイベントは `insert_text` 27 回・**何も起きない 54 回**。直前が文字（S3・S11）なら 18 / 18 で確定、直前が Space（S1・S2・S13）・→（S7）・前面の切り替え（S15）なら 0 回（S12 は 2 / 9）。確定しないと未確定の文字列が次の試行へ持ち越され（marked text の長さが 16 → 17 → 18）、**試行が独立でなくなる**。原因は未確定（候補: `CGEventPost` の Return が候補の状態の IME に効かない経路・キーを押している時間・イベントの source）。→ 次の手: osascript の `key code 36` との比較・押下時間を振る短い実験（手を離してもらう・数分）。
4. **最初の IME の状態が計画に無い**: 生成器はブロックの頭で日本語にする手順を持たない。パイロットは `focus_cmd` でかなキーを押して補った → recipes かブロックの行で持つ。
5. **ライブ変換 ON では打鍵の途中で `insert_text` が出る**（区切りの自動確定）。呼び出し列の型は 1 シナリオあたり 6〜9 に割れた（`first_rect` を除いて 3〜8）。→ 正解の定義はこの割れを吸収する必要がある。所見 3 を直してから数え直す。
6. 本番の n: 1 試行 10.9 s（待ち込み）では 1 セル約 9.5 時間。1 晩に収めるなら n か think の上限（20 s）を見直す（M2）。

## 原因の分析と修正（2026-10-01・同じ日の続き）

### 所見 3（Enter が確定しない）の原因 —— IME の挙動であり、合成キーの問題ではない

- 送り方を 13 通り変えた（フラグの上書きなし・session tap・CombinedSession の source・osascript・押下 250 ms・`\r` の明示・キーボード種別の明示・テンキーの Enter・Space の長押し・2 秒待つ・↓ の後）→ **すべて確定しない**。**Enter を 2 回押すと 2 回目で確定**（`enter_probe*.py`・`~/ime-pilot/`）。
- 対照: テキストエディットでも同じ（文字 → Enter は確定・Space → Enter は未確定のまま Esc で消える）。**研究者の手打ちでも同じ**（参照入力欄・テキストエディットの両方で Space → Enter 1 回は下線が残る）。
- 判定: macOS 27・標準の日本語入力・ライブ変換 ON では、Space で候補の窓が開き、**候補の窓の Enter は候補を選ぶだけ**・確定は 2 回目の Enter。数字で候補を選んだ後も同じ。研究者は普段 Space を押さずライブ変換のまま Enter 1 回で確定している（だから気づかない）。
- Esc: ライブ変換の段を 1 回に 1 段戻す（漢字に変換された文字列 → かな → ローマ字の綴り → 取り消し）。**最大 3 回**。余った Esc は `do_command` になるだけ（`esc_probe*.py`）。

### 修正（`b38b9904` ＋ 次の commit）

| 所見 | 修正 |
|---|---|
| 3 | recipes（macOS）: S1 / S2 / S7 / S12 / S13 / S15 は Enter 2 回・S8 は数字の後に Enter・S5 は Esc 4 回。`generate_plan.py` / `simulate_obs.py` の selftest の照合を OS ごとに（Windows は据え置き）。陰性対照: 旧 recipes で selftest が赤 |
| 2 | マーカーを矢印キー（← → ←）に（研究者の選択・判断 80）。観測側で `navigation`・E2 は既存の `--markers-in-obs` |
| 1 | `refinput-macos/build.sh` が bundle id `local.ime-observation.refinput` の `.app` も作る |
| 4 | `run/README.md` の前提 4a と `cell.example.json`（`focus_cmd` でかなキー） |

### 確認（直した版・実機）

- `verify-1`（全 14 シナリオ × 3 速さ × 1・42 試行・7.8 分）: 確定するシナリオは**すべて確定**、取り消し系（S4 / S6 / S14）は持ち越しなし。**持ち越しは S5 の 3 件だけ**（Esc 2 回では足りない → Esc 4 回に直した）。観測側でマーカーが一致（3 ブロックすべて）・**観測 − oracle の中央値 4 ms**・gt − oracle 6 ms（ブロック 0 は約 100 ms・起動直後）。到達の欠けは S14 の IME キーだけ（設計どおり）。
- `verify-s5`（S5 / S3 × 3 速さ × 3・18 試行）: 持ち越し **0 件**（S5 8 / 8・S3 9 / 9）。

### 残り（M2）

- 本番の n / think の上限: 1 試行 10.9 s（待ち込み）→ 1 セル約 9.5 時間（研究者の判断）。
- ライブ変換 OFF のセルは未パイロット（Enter 1 回で確定するなら別の recipes ファイル）。
- 正解の定義（`gt_rules` の `mac_nstic`）は、直した手順で呼び出し列の型を数え直してから（n = 3 程度の再パイロット）。
