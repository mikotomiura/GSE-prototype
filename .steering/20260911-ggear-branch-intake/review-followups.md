# レビュー指摘への対応 — G-GEAR 取り込み

★ 2026-09-11、マージ済みの取り込みに対して `code-reviewer` / `security-checker` /
`cross-reviewer` (Claude + Codex) を並列で実行した結果と対応。
⚠️ **指摘は鵜呑みにせず、1 件ずつ一次資料で検算してから直した。**

## 対応した指摘

| # | 出所 | 指摘 | 検算 | 対応 |
|---|---|---|---|---|
| **1** | code-reviewer **HIGH** | ADR-024 の**主要アウトカム `receipt_free_resumption` に replay 回帰が 1 本も無い** | ✅ 実測で `event_count: 0` / 全 `None` を確認 | fixture `resumption_outcomes.ndjson` 新設 ＋ ゴールデンテスト追加 |
| **2** | code-reviewer MEDIUM | `_lift_outcome_field` の `value is None` が、**新スキーマの正当な null を旧名で上書き**しうる | ✅ コード上のコメント自身が「現存しない」という*観測*を根拠にしていた | `if name in outcome:` へ変更 |
| **3** | code-reviewer MEDIUM | `run.sh` / `config.yaml` の Step 2b 指示に**旧名が残存** | ✅ 3 箇所を実測 | 新名へ置換 |
| **4** | security-checker MEDIUM | `frontend-check` job に `permissions:` が無く、既定の `GITHUB_TOKEN` 権限が渡る | ✅ `permissions:` は release job (881 行) のみと実測 | `permissions: contents: read` を明記 |
| **5** | security-checker MEDIUM | `.codex/budget.json` の `history` から **7 件が消えている**（上限を上げた同じ commit で） | ✅ 消えた 7 件と消費量を特定。⚠️ **回転コードは repo 内に存在しない**＝手作業の削除 | 7 件を復元し append-only の規約をコメントに明記 |

### #1 の fixture 設計と手計算

`resumption_outcomes.ndjson` は 3 エピソードがそれぞれ離席候補ギャップ (≥180s) を持ち、
**3 分類すべて**を踏む:

| 事象 | 再開時刻 | 結末 | 経過 |
|---|---|---|---|
| EV1 | 200_000 | `Receipt` (paste@230_000) | 30_000 |
| EV2 | 600_000 | `NextAwayCandidate` (601_000 から) | 1_000 |
| EV3 | 1_400_000 | `Censored` (観測終端 2_100_000) | 700_000 |

★ CIF を**手計算と突き合わせた**:
`t=1_000`: n=3, d2=1 → S=2/3 / `t=30_000`: n=2, d1=1 → CIF += (2/3)(1/2) = **1/3**
→ `receipt_free = 2/3`。実測値 `0.6666666666666666` と一致。

⚠️ **陽性対照 3 本**で、テストが空振りしていないことを確認した:

| 変異 | 結果 |
|---|---|
| EV1 の離席ギャップを 148s (<180s) に縮める | ✅ FAILED |
| EV1 の受領 paste を削除 | ✅ FAILED |
| 観測終端を 1_500_000 に縮め Censored を地平の内側へ | ✅ FAILED |

## 対応しなかった指摘 (理由つき)

| 出所 | 指摘 | 判断 |
|---|---|---|
| cross-review (Codex) | `classify_resumption` が `observation_end_ms` を探索の上限に使っていない | ⚠️ **契約と実装の不一致は事実**だが、唯一の呼び出し元 `compute_outcome_metrics` が `observation_end_ms` を全入力の `max()` として渡すため**現状は発火しない**。★ 別タスクへ申し送り |
| cross-review (Codex) | ソート前提が `debug_assert!` のみ (release で無効) | ★ 本 PR 固有の逸脱ではなく、コードベース全体の慣習。スコープ外 |
| cross-review (Codex) | `outcomes` の再識別リスク | ★ `ResumptionOutcome` は相対時間と 3 値のみ。絶対時刻を持つ `ResumptionEvent` は意図的に `Serialize` を derive していない (防御済み) |
| code-reviewer LOW | `probe_scheduler.rs` の 516/817/853 のリテラル `180_000` | ★ すべて `mod tests` 内。516 は旧パラメータ集合の意図的固定。⚠️ 817/853 は `AWAY_IDLE_MS` へ揃えてよい → **別 PR へ申し送り** |
| code-reviewer MEDIUM | `OUTCOME_AVG_FIELDS` の CIF 平均が Aalen-Johansen でない旨が列名に出ない | ★ 分析成果物の設計判断。研究者判断へ回す |
| security-checker MEDIUM | `python-pptx` の transitive 依存が未固定 | ★ `requirements-dev.txt` への集約は別 PR。⚠️ 本 PR では job 権限の最小化のみ |

## ⚠️ このセッションで自分が壊した測定器 (2 件)

1. `cargo fmt --check` の結果を `&& echo "fmt OK"` で読み、**`head` の成功を fmt の成功と誤読**した。
   ★ 実際は差分が出ていた (その後 `cargo fmt` で解消)。→ ★ exit code を直接見ること。
2. `PYTHONUTF8=1 $c` でゲートを一括実行したら **全件 exit=127**。
   ⚠️ **zsh は未クォート変数を単語分割しない**ため、コマンド全体が 1 語になっていた。
   ★ 「全部赤」を欠陥と読まずに測定器を疑ったので助かった
   (memory: `measurement-instrument-false-positives`)。

## v0.1.35 の版上げ (2026-09-11)

★ `check-o1-release-readiness.sh` が「タグ v0.1.34 は古い」で赤だったため、
README の手順どおり 3 ファイル ＋ `Cargo.lock` を揃えて **0.1.34 → 0.1.35** へ上げた。

⚠️★★★ **版上げの副作用**: `check-measurement-binary.sh` が **exit 3** に転じる。

```
repo (src-tauri/Cargo.toml)        : 0.1.35
app  (CFBundleShortVersionString)  : 0.1.34   ← ~/Desktop/O1_計測用_macOS/gse-next.app
```

★ これは**欠陥ではなく、バンプの当然の帰結**である (手元の計測用 .app が古くなった)。
→ ★ **CI が v0.1.35 を公開したら、計測用 .app を差し替えて再確認すること。**
⚠️ 差し替えるまでの間に 8h 計測を回すと、**測っている版と repo の版が違う**。

### ⚠️ soak 証拠の引き継ぎについて (★ 推論であって観測ではない)

★ v0.1.34 の「9h51m 落ちなかった」は **v0.1.34 のバイナリで採った観測**である。
⚠️ v0.1.35 は別バイナリなので、**同じ観測をしたわけではない**。
★ 引き継げると判断した根拠は「差分が `hook_macos.rs` (SIGSEGV 修正の在処) に
1 行も触れていない」ことであり、⚠️ **新しいバイナリでの soak は未実施**。

## v0.1.35 配布物の実物検算 (2026-09-11)

★ 「ゲートが緑でも配布物が壊れていた」前例があるので、**dmg を実際にマウントして**確かめた
(memory: `gate-green-but-artifact-broken`)。

| 項目 | 結果 |
|---|---|
| `CFBundleShortVersionString` | **0.1.35** |
| 署名 | `com.johnd.gse-next` / adhoc (★ 従来どおり) |
| Release 成果物 | `gse-next.exe` / `gse-next_0.1.35_aarch64.dmg` / `gse-submit.exe` / `gse-unpack(.exe)` |
| `check-o1-release-readiness.sh` | **20 件 / 0 件** へ復帰 |

### ★ 「実行時中立」を推論から観測へ上げた

⚠️ 当初「差分は実行時中立のはず」は**推論**だった。→ ★ v0.1.34 の dmg も落として
**両バイナリを狙い撃ちで照合**した:

| 文字列 | v0.1.34 | v0.1.35 | |
|---|---|---|---|
| `O1: pointer tap installed` | 2 | 2 | 一致 |
| `observe_macos.rs` | 2 | 2 | 一致 |
| `ime_macos.rs` | 1 | 1 | 一致 |
| `tap_enabled` | 1 | 1 | 一致 |
| `pflow_exit` | **0** | **0** | 一致 |
| `recovered_episode_count` | **0** | **0** | 一致 |

★ **改名した名前は新旧どちらのアプリ本体にも入っていない** —— `analysis/metrics.rs` が
`lib.rs` から到達不能で、serde のフィールド名ごと落ちるため。
→ ★ **改名が被験者の挙動を変えないことの直接の裏づけ**になった。
⚠️ ただし byte 同一の証明ではない (ビルド時刻等が違う)。

### ⚠️ ここでも測定器を 2 回壊した

1. `strings -a BIN | grep -c "^名前$"` と**完全一致**で数えたら、
   ⚠️ **陽性対照まで 0 件**になった。★ `strings` の行は記号だけではないので
   完全一致では拾えない。→ `grep -cF` の部分一致へ。
   ★ **「0 件」を欠陥と読む前に陽性対照を見た**ので誤報を出さずに済んだ。
2. 両バイナリの**文字列集合の差分** (`comm`) を取ったら v34 側 1029 件 / v35 側 1027 件と出て、
   ⚠️ **v0.1.35 にだけ O1 pointer 関連が入っているように見えた**。
   ★ 実際はリンカが隣接する文字列リテラルを**連結する境界が違うだけ**で、
   狙い撃ちで数えると両方 2 件。→ ⚠️ **集合差分はこの用途の計器として不適**。

## ⚠️ 未実施のまま残ること

- ★ **v0.1.35 での soak は未実施。** v0.1.34 の「9h51m 落ちなかった」は
  v0.1.34 のバイナリで採った観測である。⚠️ 上の照合で
  `hook_macos.rs` 由来の文字列が一致することまでは見たが、**動かして観測はしていない**。
- ★ **計測用 `.app` の差し替え**が要る (`~/Desktop/O1_計測用_macOS` は 0.1.34 のまま)。
  ⚠️ 差し替えるまで `check-measurement-binary.sh` は exit 3。
- ★ **Windows の exe は未検算** (macOS からマウントできないため)。
