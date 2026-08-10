# 設計

## 実装アプローチ

「1 ファイルに複数セッション」を **2 つの独立した検査**で捕まえる。
★ 片方が誤検知で緩んでも、もう片方が残る形にする（`§5.4` の probe 行 0 と `g1_mode` が
2 本立てになっているのと同じ考え方）。

| 本数 | どこ | 何を見る | 失敗の形 |
|---|---|---|---|
| 1 本目 | `validate_blocks.py` | 提出物の**形**（`session_start` の行数） | **FAIL**（転記検証が赤） |
| 2 本目 | `analyze.py` | 解析に**入る行** | `SystemExit`（解析が止まる） |

⚠️★ **既存の hook_health 検査 (`alive=false` AND key 行 0) は直さない。**
あれは 2026-08-09 の実測（通常作業 63 分で 1 回誤検知）に対する是正であり、
★ 緩めた条件そのものは正しい。⚠️ 今回すり抜けたのは AND が悪いからではなく、
**「1 ファイル 1 セッション」を誰も検査していなかった**からである。
→ ★ **AND を締め直すのではなく、独立した検査を足す**（`§3.6` の誤 FAIL は回復不能なので、
既存条件を厳しくして正常ブロックを落とすリスクを増やさない）。

## 変更対象

### 修正するファイル

- `experiments/20260801-controlled-friction-task/validate_blocks.py`
  - `scan_ndjson` は既に型別件数を数えている → `counts["session_start"]` をそのまま使える
  - `check_dataset` に「`session_start` ≥ 2 なら FAIL」を追加
    （★ パイロット除外はしない。`protocol.md §1` は P-1 にも適用される）
  - ⚠️ `alive=false` + key>0 の WARN 文面を修正。現状は
    「★ **誤検知の可能性が高い**」と断定的に誘導している。
    ★ **starved の長さと打鍵の空白を併記**し、判断材料を出す形に変える
    （`liveness.rs` の設計思想「判断ではなく測った量を残す」に揃える）
  - `selftest()` に 2 ケース追加（2 セッション → 赤 / 1 セッション → 緑の対照）

- `experiments/20260801-controlled-friction-task/analyze.py`
  - `read_block()` の戻り値に `n_session_starts` と `last_session_t` を追加
    （★ **数えて返すだけ**。ここでは止めない → D-3）
  - `read_block(path, from_last_session=False)` を追加。True なら最後の
    `session_start` の `t` 以降の行だけを使う
  - `load_subject_blocks()` で `n_session_starts > 1` かつフラグ無し → `SystemExit`
  - `cmd_verify_blocks()` は再開始を表示して **0 を返す**（D-3）
  - `--last-session-on-restart` を `argparse` に追加。使ったら結果に
    `restart_handling` を刻む（`--unseal` の `confirmatory_status_forfeited` と同じ作法）
  - `selftest()` に回帰ケース追加

- `experiments/20260801-controlled-friction-task/preregistration.md`
  - 規則を凍結し、改訂履歴に **★「結果を見る前に決めた」** と根拠つきで残す（D-4）

- `experiments/20260801-controlled-friction-task/notes.md`
  - §10-4 の「提案」を「実装した」に更新

### 新規作成するファイル

なし。

### 削除するファイル

なし。

## 影響範囲

- ★ **`src-tauri/` はゼロ**。データ収集の挙動は 1 バイトも変わらない（D-1）
- `analyze.py` は **P010 でフラグ無しだと止まるようになる** = 意図した破壊的変更。
  ⚠️ ただし `results/` は `.gitkeep` のみで、★ **既存の解析結果は 1 件も無い**ので
  再現性の破れは起きない（`reproducibility-discipline`）
- `--verify-blocks` の**契約（常に 0）は変えない**（D-3）
- `validate_blocks.py` は他の被験者 (P001-P009 等) には無影響（NDJSON が無く note 止まり）

## 既存パターンとの整合性

- ★ 検査を 2 本立てにするのは `§5.4` の probe 行 0 / `g1_mode` と同じ形
- ★ 明示フラグ + 結果への刻印は `--unseal` / `confirmatory_status_forfeited` と同じ形
- ★ 「判断ではなく測った量を残す」は `liveness.rs` の設計思想と同じ
- ⚠️ `validate_blocks.py` は**条件ラベルを画面に出さない**契約がある
  （`selftest` の非開示回帰テストが固定）。★ 新しいメッセージにも
  `HI` / `LO` / 課題文パスを**入れない**。ブロック番号だけで指す

## テスト戦略

★ **対照つきで確かめる**（`verify-before-claiming`）。「赤くなった」だけでは足りず、
**正常系が緑のままであること**を同じ回で見る。

1. `validate_blocks.py --selftest`
   - 2 セッションのログ → FAIL、かつメッセージに `session_start` が出る
   - ★ 対照: 1 セッションのログ → 緑（新検査が正常系を落としていない）
   - ★ 対照: 条件ラベルが漏れていない（既存の非開示テストが自動で効く）
2. `analyze.py --selftest`
   - 2 セッション + フラグ無し → `SystemExit`
   - 2 セッション + フラグ有り → 通り、最終セッションの打鍵数だけを数える
   - ★ 対照: 1 セッション → フラグの有無で結果が変わらない
3. ★ **実データでの確認**（P010・`/tmp/p010`）
   - `validate_blocks.py --dataset` が block07 で FAIL
   - `analyze.py` がフラグ無しで止まり、フラグ有りで **1387 打鍵 / 4:44** を出す
     （★ 期待値は本セッションで独立に実測済み・`notes.md §10-3`）
   - ⚠️ **判定は出さない**（`§3.4` の見る順序。`--verify-blocks` と selftest に留める）
4. ⚠️★ **壊して赤を見る**: 新検査を無効化した版で 3 が緑に戻ることを確かめ、
   検査が空回りしていないことを固定する（`notes.md §9-5` で踏んだ「位置は包含の証拠にならない」型）

## ロールバック計画

- 変更は Python 2 ファイル + md 2 ファイル。`git revert` で戻せる
- ⚠️ `preregistration.md` は**凍結文書**なので、revert する場合は改訂履歴にも
  「撤回した」と残す（履歴を消さない）
- ★ `blocks/P010.json`（gitignore 対象・この Mac にしか無い）は本タスクで触らない

---

## ★ 実装中に変わったこと（Step 2 最終化・2026-08-10）

### 1. ⚠️★★ `/cross-review` で Codex が**本物の穴**を見つけた → API を分割した

当初設計は `session_start_ts(path) -> list[int]` の 1 本だった。
⚠️ これは **`t` が有効な `int` の行しか数えない**ので、`validate_blocks.py::scan_ndjson`
（`type` だけで数える）と**基準がずれていた**。

★ 2 本目の `session_start` の `t` が壊れていると、
**validate_blocks は 2 本と数えて FAIL するのに analyze は 1 本と数えて黙って混ぜた**
（★ Codex の指摘を鵜呑みにせず、`t` を文字列にした NDJSON で**自分で再現した**）。
⚠️ 本タスクが塞ごうとした「沈黙して間違った結果を出す」経路そのものが残っていた。

→ **`session_starts(path) -> (構造上の本数, cutoff に使える時刻の列)`** に分割した。
★ 「壊れているか」を見る数え方と「どこから読むか」を決める時刻は**別の問い**である。

さらに `read_block` の戻り値に **`restart_cutoff_applied`** を足し、
★ **起点が決められないときは `--last-session-on-restart` を付けても止める**ようにした。
⚠️ ここで黙って全行読むと `restart_handling` に「最終セッションを採った」と刻まれるのに
実際は混ざっている ＝ **結果そのものが嘘をつく**（v0.1.26 で塞いだ「レシートが嘘をつく」と同型）。

### 2. ★ 予定になかった修正: 版一致検査が単一真実源を見ていなかった

`preregistration.md` が第 13 版なのに `config.json` と `PREREG_REVISION` は
**10 のまま 3 版遅れて緑**だった（実測）。検査が `analyze.py ↔ config.json` しか見ておらず、
★ **両方が同じだけ遅れれば緑になる**。→ 文書の見出しを直読みする検査を足した。

### 3. ⚠️ 第 14 版は「データ前に凍結」と名乗れなかった

`config.json` の `frozen_before_any_data` を **false** にし、
外から検証できる `frozen_before_any_analysis: true` を立てた（`decisions.md` D-4 の前提を修正）。

### 4. 直さなかったもの（★ 理由つき）

- **`malformed_lines` が cutoff 前の行も数える**（Codex 指摘 1）
  → ★ 壊れた行には `t` が無く、**どちらのセッションか原理的に決められない**。
  docstring に明記して**黙って正確なふりをしない**。
- **`t` の単調性が暗黙の前提**（同 2）→ ★ `anonymize.rs` を読んで**自分で裏を取り**、
  前提と「崩れたら cutoff が壊れる」を docstring に書いた。コードは変えていない。

## ★ 配布への影響: 無し（実測で確認）

`git status -- src-tauri src` が空 ＝ **アプリは 1 バイトも変わっていない**。
`make-distribution.sh` が zip に入れるのは実行ファイル / `launch-g1-windows.bat` /
`pubkey.txt` / `g1-submit.json` / `pages/block*.html` / `初回セットアップ_mac.sh` のみで、
★ 本タスクの変更ファイルは 1 つも含まれない
（`validate_blocks.py` は line 85 の**梱包前ゲート**として走るだけ・`--dataset` 無しなので新 FAIL は出ない）。
→ ⚠️ **次回 G1 実施に向けた zip 再配布は不要。**
