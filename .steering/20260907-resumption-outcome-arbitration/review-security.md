# security-checker 報告

対象: 未コミット変更 (ADR-024 / `receipt_free_resumption`) / 実施日: 2026-09-07

## 結論サマリ

**CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 4。** 依頼の重点 6 項目はすべて実コードで確認し、
規約違反は 1 件も見つからなかった。コマンドインジェクション・入力検証欠落・秘密情報混入・
外部送信経路の追加・PII ガードの弱体化なし。`wall_server.rs` は ADR-015 で削除済みのため
HTTP エンドポイントの検査対象は存在しない (`grep -rn "wall_server"` で不在を確認)。

## 重点確認 6 項目 (すべて実測。★ 沈黙ではなく明示)

### 1. data-privacy ルール 1 (文字内容) — **確認した / 問題なし**

`src-tauri/src/analysis/metrics.rs` の新規型を逐語確認:
`ResumptionEvent` (:377-384) = u64 3 本 / `ResumptionOutcome` (:400-403) = u64 + enum /
`ResumptionOutcomeKind` (:388-396) = fieldless enum 3 値 /
`ReceiptFreeResumption` (:411-427) = u32 5 本 + Option<f64> 2 本。
String / char / Vec<u8> は 1 つも無い。`OutcomeConfig::away_gap_ms` (:159) も u64。
→ ★ 「時刻と件数以外を持っていない」を満たす。

### 2. ルール 7 / ADR-023 §Migration:1002-1004 — **確認した / 問題なし**

`PasteEvent` (:179-182) = `timestamp: u64` / `chars: u64` のままで、diff に定義変更が 1 行も無い。
新規 3 関数 (`segment_resumptions` / `classify_resumption` /
`compute_receipt_free_resumption`) が受け取る受領チャネルは `pastes: &[PasteEvent]` **だけ**。
CGT 挿入 / suggestion accept / IME / クリップボード内容に相当する型・呼び出しは新規コードに皆無。
`replay.rs` の diff は **テストの assert 名のみ**で `collect_paste_events` は無改変。
→ ★ 「M2 (改名) を『receipt の実装を揃える』作業に拡大解釈しない」を守れている。

### 3. 外部へ出る量 (`--metrics --json`) — **確認した / 生の時刻列は載っていない**

`OutcomeMetrics` の新フィールドは `receipt_free_resumption` (:260) の 1 本のみで、
その中身は件数 5 + 比率 2 だけ。`ResumptionEvent` を保持していない。
`ResumptionOutcome` は `Serialize` を derive していない (:399) → `elapsed_ms` 列は出ない。
`ResumptionEvent` / `segment_resumptions` は metrics.rs 以外から **1 箇所も参照されていない**
(`grep -rn` 済み)。`OutcomeConfig` は非 Serialize (:138) → `away_gap_ms` も出ない。
fixture `scripts/fixtures/analysis_join/metrics/P101/windows/sess_a.metrics.json` の実 JSON も
絶対時刻ゼロ。→ ★ **「生の時刻列が出力に載っている」という事実は無い。指摘なし。**

### 4. `scripts/build_analysis_db.py` の PII ガード — **確認した / 穴なし**

diff が触ったのは `OUTCOME_*_FIELDS` / 新規 `_lift_outcome_field` / `_collect_metrics_rows` の
2 行だけ。`_check_survey_privacy` (:245-274)、`FORBIDDEN_SURVEY_SUBSTRINGS` (:78-)、
`EXIT_PRIVACY` (:61)、main のガード呼び出し (:482-485) は**すべて無改変**で、
呼び出し順序 (survey 収集 → ガード → DB 構築) も不変。
`_lift_outcome_field` (:158-177) は**ホワイトリスト名でしか読まない** (`outcome.items()` の
全走査もワイルドカードも無い) ので、metrics.json に未知フィールドが増えても DB へ素通りしない。
`LEGACY_FIELD_ALIASES` (:130-134) が読むのも旧 3 名の数値だけ。
既存の privacy 回帰テスト `test_t5b_privacy_guard_rejects_japanese_pii_column` は削除も改変もなし。

### 5. `AWAY_IDLE_MS` の pub 化 — **確認した / ADR-018 D1 違反なし**

`grep -rn "AWAY_IDLE_MS" --include=*.rs .` の全 8 ヒットを確認。
`intervention.rs:257` / `:419` は既存の介入抑制 (変更なし)、`metrics.rs:9` / `:172` / `:1701`、
`probe_scheduler.rs:153` はコメントのみ。
→ ★ **新たな利用箇所は「事後の層別解析の既定値」1 つだけ**で、実行時に「離席した」
「中断が完了した」と宣言する経路は増えていない。ADR-018 D3 が禁じる
`completed` / `achieved` / `達成` に相当する語は新規コード・新規 JSON フィールド名に皆無。

### 6. 秘密情報・認証情報・実メールアドレス — **確認した / 検出 0 件**

`git diff` 全体を `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` で走査 → **実アドレス 0 件**。
`api_key|secret|token|passw|PRIVATE KEY|AKIA|ghp_|xox[bp]-` のヒットは
`scripts/md2pptx.py` の `for token in (...)` (第三者由来文字列の検査ループ・変数名) のみ。
fixture の識別子は `P101` / `P102` / `P104` の擬似 ID だけ。

---

## 指摘一覧

### CRITICAL / HIGH / MEDIUM

**該当なし。**

### LOW

**LOW-1** `src-tauri/src/analysis/metrics.rs:376` — `ResumptionEvent` が使われていない
`Serialize` を derive している (現状どこにも直列化されていないので違反ではない・上記 3)。
この derive があるため、出力側に 1 行足すだけで **絶対時刻 3 本 × 事象数** =
離席候補タイムラインが JSON に載る状態になっている。ADR-018 D3 が「観測として残すが
判定に使わない」とした対象そのものであり、件数集計より格段に粒度が高い。
- 修正方針: 未使用の `Serialize` を derive から外し、`ResumptionOutcome` と同じ扱いに揃える
  (`ResumptionOutcomeKind` の `Serialize` + `#[serde(rename_all)]` :389-390 も未使用)。
  外せば「出せない」ことが型で担保され、AC-2 と同じ構造的保証になる。

**LOW-2** `src-tauri/src/analysis/intervention.rs:11-18` — 新 doc コメントが
「本定数は『離席候補』の唯一の真実源 (SSOT)」「別の場所で 180_000 を再定義しないこと」と
断定しているが、**既に再定義が 2 箇所ある**: `probe_scheduler.rs:170` と `:201` の
`away_idle_ms: 180_000`。テスト `away_gap_default_matches_intervention_ssot`
(metrics.rs:1697-1702) は `OutcomeConfig` しか見ておらずこれを検出しない。
- 影響: 脆弱性ではないが、将来 `AWAY_IDLE_MS` を変えたとき **プローブ側の離席除外だけが
  古い閾値で動き続ける** (離席中に較正プローブが発火しうる)。
- 修正方針: (a) `probe_scheduler.rs` の既定値を `AWAY_IDLE_MS` 参照に変える、または
  (b) doc の主張を「`OutcomeConfig::away_gap_ms` の既定値の SSOT」に限定する。
  ★ 断定を残すなら (a) を伴わせること。

**LOW-3** `src-tauri/src/analysis/metrics.rs:392-393` / `:419` および
`scripts/build_analysis_db.py:124` — 外部アーティファクト (metrics.json の
`left_again_count`、DB 列 `rfr_left_again_count_sum`) に **`left_again`** という名前が出る。
コード内コメントは一貫して「離席**候補**」と限定しているのに公開名から「候補」が落ちており、
系が「また離席した」と判定したように読める。ADR-018 D1 / ADR-023 D2 の「時計の事実」という
立て方と含意がずれる (D3 が明示的に禁じた語には該当しないため LOW)。
`ResumptionEvent` を `physical_return` と呼ばなかった判断 (:382) と非対称。
- 修正方針: `left_again` → `gap_again` / `re_gap` 等へ。改名するなら metrics.rs /
  build_analysis_db.py / fixture 3 本 / テストを同時に。

**LOW-4** `C:\GSE-prototype\out.txt` (未追跡・16,351 bytes) — 本 diff とは無関係だが、
repo 直下に第三者論文の本文抽出テキストが未追跡かつ `.gitignore` 対象外で置かれている
(`git check-ignore -v out.txt` → NOT ignored)。`git add -A` で著作物の全文抽出が
誤ってコミットされうる。キーストローク由来データではないためプライバシー規約違反ではない。
- 修正方針: 削除するか `.gitignore` に追加。

---

## プライバシー規約チェック (data-privacy Skill・毎回実施)

- [x] **R1** 文字内容がログ/出力に含まれない — 新規型は数値のみ (上記 1)。
      `is_text_producing` / `is_backspace` の vk 判定は無改変で content-free のまま
- [x] **R2** リアルタイム外部送信なし — 新規コードに I/O・ネットワーク呼び出しゼロ (純粋関数)
- [x] **R3** ML 収集のオプトイン/匿名化/バッチ — 収集経路 (`logger.rs` / `submission.rs` /
      `packaging.rs`) に変更なし
- [x] **R4** Wall Server — repo に存在しない (ADR-015)。該当なし
- [x] **R5** Tauri CSP — `tauri.conf.json` 未変更
- [x] **R6** 停止/削除経路 — `recording.rs` / `redaction.rs` 未変更。**新しい行種を足していない**
      ので `LogEntry::line_type()` の一時停止ゲートに穴は空いていない (新指標は NDJSON ではなく
      再処理側で算出される)
- [x] **R7** 非打鍵チャネルは凍結表の中だけ — 新規チャネル追加なし (上記 2)。座標・HWND・
      アプリ識別子・役割カテゴリの混入なし
- [x] セッションログはローカル保存のみ (経路無改変)

## 依存ライブラリの脆弱性

**該当なし。** `src-tauri/Cargo.toml` / `Cargo.lock` / `package.json` / `package-lock.json` は
本 diff で **未変更** (git status で確認)。新規 Rust コードは追加 crate を使わず std のみ
(`cif_receipt` / `segment_resumptions`)。`build_analysis_db.py` も新規 import なし。
→ 本 diff に起因する新規 CVE 面はゼロ。依存グラフが動いていないため
`cargo audit` / `npm audit` の実行は本差分に対して不要と判断した。
