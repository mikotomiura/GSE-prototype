# 新タグ候補の中身（v0.1.35 → main 58fb589）

> 2026-09-26 に `git log --no-merges v0.1.35..HEAD -- src-tauri/src src-tauri/Cargo.toml src` を一次として整理（**69 コミット**。O1 ゲートの数え方と同じ範囲・マージ込みで 71）。
> v0.1.35 は 2026-09-11。⚠️ 「被験者が受け取るバイナリに入るか」は各コミットの触ったファイルからの判断で、`bin/replay.rs` が配布 zip に同梱されないことは**未確認**（下記 B）。

## A. 配布バイナリの挙動に効く（被験者・データに影響）

| 何 | コミット | 影響 |
|---|---|---|
| ⚠️★★★ **区間指定削除が自己申告行を 1 行も消していなかった** | `1c60b2c`・`354a9eb`（9/14）／ `0577bbe`（9/25・削除の最小幅） | `redaction.rs` が `t` だけを読み、`realtime_label` / `vignette_response` は `ts`、`probe_assignment` は `scheduled_ts` を書いていたため**行が残った**。画面には「消しました（…件）」と出る。削除 UI は O1 以外でも出るので**通常運用（v0.3 較正）でも live**（コミット自身の記述）。⚠️ いつから live かは未確定・**過去コホートで区間削除が実行されたかは未調査**（同コミットの記述）。→ 同意文書の「その時間帯のお答えは消えます」が破れる |
| activity_label（ADR-031）行種・probe の層化理由 | `23d8bca`（9/14）／ 門: `e8c41f7`（同意の門を grep から型へ） | additive。O1 かつ同意承認済みのときだけ通す（`o1::activity_label_allowed`）。G1 には出ない |
| macOS の IME 確定 / 放棄の判別と `ime_shadow` 送出 | `bd5e6b8`〜`5168c28`・`1cdfed5`（研究者だけの生存表示）・`227f715`（生存カウンタ＝実際に書いた行） | additive |
| macOS の かな キーをトグル扱いする誤りを直す | `9a900bf`・`1188140` | 入力状態の遷移表を OS 非依存へ 1 本化 |
| フラグ公開順（Ordering）・macOS の公開フラグを payload の後へ | `5aa05e4`〜`3effafa`・`09bc9b4`・`581a044` | 並行性の是正（macOS の main 赤の原因を含む） |

## B. 解析側（gse-replay --features・P1 の準備）— 約 40 本

`bin/replay.rs`（+5,500 行）・`feat_offline/` ・`replay` の封筒 / 極 / 凍結値注入など。**配布 zip に載る bin ではないと思われる**が未確認（`ci.yml` の bundle 対象と `make-common-app-zip.sh` で確かめる）。

## C. CI・lint・テスト基盤

clippy 33 件 + mac 7 件の是正・MSRV 訂正・redact テストの無音 skip の panic 化・TAP_ENABLED_SNAPSHOT の間欠赤 ほか。

## 結論（提案）
- **新タグ無しの配布は不可**: A の削除欠陥が v0.1.35 に残る。被験者への約束（同意文書）に関わるため、G1 / O1 のどちらでも新タグから配る。
- 削除欠陥の**過去コホートへの影響**（`redact` が実行されたセッションがあるか）は本タスクの範囲外だが、**研究者へ報告**する（data-privacy）。
