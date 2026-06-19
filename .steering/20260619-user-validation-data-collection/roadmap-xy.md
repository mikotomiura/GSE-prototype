# ユーザー検証 実装ロードマップ — X / Y 二軸 (2026-06-20)

> 親タスク: `.steering/20260619-user-validation-data-collection/`。本書は (a)(b)(c) の収集・算出と
> v0.3 較正 (X) を貫く実装順の真実源。決定根拠は同ディレクトリ `decisions.md` (D1-D7)、
> v0.3 較正は `docs/preregistration-v0.3.md` / `.idea/GSE_事後ラベリングシステム設計書_v0.3.md`。

## 0. 二軸の定義 (ユーザー確認 2026-06-20)

- **X = 認知推定の検証** (測定妥当性 / 較正)。問い: GSE の状態推定は信用できるか。
- **Y = GSE 自体と散歩のユーザー受け入れ検証** (受容性＋行動アウトカム)。問い: GSE+散歩は役立ち、受け入れられるか。
- 関係: 設計書「測定法が成立してから核検証へ」＝ X が論理的に先。ただし **X の主検証器
  (リアルタイムプローブ) は完成済み**であり、(a)(b)(c) は HMM 推定の正否と独立に測れるため、
  Y は X 強化を待たずに収集可。**波形 cue は X に不要** (循環論法 HIGH-1 の再導入。前回の厳密判定)。

## 1. 現状マップ (code 確認済み 2026-06-20)

| 機能 | 軸 | 状態 |
|---|---|---|
| リアルタイムランダムプローブ (`probe_scheduler`/`realtime_label`/`ProbeCard`) | **X 主検証器** | ✅ 実装済 (Task A-E) |
| 二軸性テスト (`VignetteTest`/`vignette_response`) | X | ✅ |
| C-index 評価＋cohort Go/Kill (`calibration_eval`/`cohort`/`run-calibration-cohort.sh`) | X | ✅ |
| `context_beacon` / `task_checkpoint` / 波形cue | X (比較条件・延期) | ❌ 未 (次段・D-14) |
| ペースト回数捕捉 (`paste`) | Y(a) | ✅ 実装済 (未マージ feature/clipboard-paste-count、実機未検証) |
| 介入判定ログ (`intervention_decision`) | Y | ✅ |
| Wall/Zen/早期解除 (`wall_server`) | Y 介入 | ✅ UI / ⚠️ **ユーザー応答(⏸/early-unlock/順守)のNDJSON記録は未確認=おそらく無** |
| (a)(b) 指標算出 | Y | ❌ (#5) |
| **成果物スナップショット (diff量=案A 前提)** | Y(b) | ❌ **捕捉機構が存在しない** |
| (c)自己効力感・NASA-TLX (アンケート) | Y | ❌ 外部フォーム (#3 周辺) |
| anonymize / package / DuckDB join | Y パイプライン | ❌ (#3/#4/#6) |
| Physical Anchor / 散歩 (Lv3/Lv4 歩行介入) | Y 介入実体 | ❌ 未 (Wall が "walk away" と言うのみ) |

## 2. 支配原則：捕捉の不可逆性

パイロットで録り損ねた信号は永久に失われる。よって **「捕捉(capture)」は「算出(analysis)」より前**。
特に **案A は捕捉前提を持つ**: diff量 は成果物から取るが、成果物を session 単位で保存する機構が無い。
⏸/early-unlock 等の介入応答も未ログの疑い。これらは #5 (算出) より前に入れる。

## 3. 実装ロードマップ (A→F)

### Phase A — 捕捉完全性 (パイロット前・不可逆ギャップ閉鎖) ★最優先
- **A1** Y(a): #2 ペースト捕捉の検証。**macOS のコンパイル＋テストは CI で可** (§6)。残るは Win/mac
  実機での Ctrl+V/Cmd+V 挙動の手動確認 → main マージ。
- **A2** Y受容: 介入応答イベントの NDJSON 記録 (Wall提示/⏸押下/early-unlock/Zen完了/順守)。
  ⏸押下数は設計書で「GSE 思想の実証データ」と明記＝独立指標。未ログなら新 variant (schema 同期手順要)。
- **A3** Y(b): **成果物スナップショット機構 (案A 前提)**。session start/end で作業対象を保存
  (coding=作業ディレクトリ git snapshot/diff、文章=テキスト保存)。**中身は raw NDJSON 同様 暗号化ローカルのみ**、
  metrics には数値 diff量 だけ。要設計: 成果物⇔session 紐付け、track別取得法、被験者端末での保存/暗号化。
- 根拠: A1-A3 は「録り損ねたら終わり」。全てに優先。

### Phase B — Y アウトカム指標算出 (#5)  依存= A3
- (a) session 単位ペースト回数・導入前後比較 / (b) diff量÷総打鍵数＋Mehta KS[11]補助 → `metrics.json`。
- `handoff-ab-metrics.md` がこれ。**A3 を前提として取り込むよう改訂が必要** (diff量供給=A3 成果物)。

### Phase C — データパイプライン (#3/#4/#6＋アンケート取り込み)
- `anonymize.py` / `package-session` (anonymize→age暗号化) / (c)・NASA-TLX の survey CSV /
  **DuckDB で (a)(b)(c) を P-ID join** (D5)。外部被験者収集＋横断分析が可能に。

### Phase D — X 強化 (任意・次段)  context_beacon (＋任意で波形cue比較), task_checkpoint
- X 主検証器は完成済み。強化が要るなら **波形cueでなく `context_beacon` (confound-free cue) が先**。
  波形cueは context_beacon と対でのみ「波形読みバイアス定量」目的の任意追加 (PreReg-3)。
  task_checkpoint は機能妥当性、無理なら「未評価」と正直記載。**パイロットのブロッカーではない**。

### Phase E — Y 介入の実体＝Physical Anchor / 散歩 (要・研究設計判断)
- 現状「散歩」は Wall 文言のみ。選択肢: (i) 最小 Lv3/Lv4 実装 / (ii) **Wizard-of-Oz** (手動歩行
  プロンプト＋自己申告) / (iii) v1 は Wall 受容のみで散歩は次段。n=3-5 受容パイロットなら (ii) が
  費用対効果最良の見込み。

### Phase F — 通しパイロット (Task E cohort＋自己ドッグフード→3-5名)
- X: cohort Go/Kill (PreReg-2/4/5)。Y: (a)(b)(c) 前後比較＋受容。
- 設計書 §11 の正直な立て付け (効果量推定・重大破綻検出のみ、母集団一般化は主張しない)。

## 4. 推奨パス

**A → B → C →〔D は任意・並行〕→ E 判断 → F。**
理由: X コア完成済 → ボトルネックは Y の 捕捉(A)→指標(B)→パイプライン(C)。波形cueは X に不要。
**直近の次タスク = Phase A (capture completeness)**。#5 単体ではなく A3(成果物)＋A2(介入応答ログ)を先に。

## 5. 要・ユーザー判断のフォーク (研究設計)

1. **X と Y を同一セッションで取るか分離か** (プローブ割り込みが Y を交絡)。
2. **Y の前後比較設計** (pre=GSEなし vs post=GSEあり。PreReg-5: 最初2回β較正→凍結→8回前向き)。
3. **A3 成果物取得法** (track別: coding=git / 文章=テキスト、保存・暗号化フロー)。
4. **Phase E 散歩** = (i)実装 / (ii)WoZ / (iii)次段 のどれか。

## 6. ビルド / CI / 検証経路 (2026-06-20 訂正)

`.github/workflows/ci.yml` は **`feature/*` push と PR(→main) で `check` ジョブを windows-latest と
macos-latest の matrix で実行**: `cargo build --target` / `cargo test --workspace` / snapshot 回帰 /
schema drift。**= macOS のコンパイル＋テスト検証は、ブランチを push すれば CI で可能**
(本機 Windows での「macOS 検証不可」は誤り)。tag `v*` push で Win(nsis)/mac(dmg) ビルド＋Release。

- **CI で出来る**: 両 OS の build/test/snapshot/schema drift、frontend tsc+vite、リリースビルド。
- **CI で出来ない**: OS フックの**実機挙動**手動確認 (Input Monitoring 権限・実 Ctrl+V/Cmd+V の発火)。
- **`act` (nektos/act) の限界**: Linux コンテナのみ＝**macOS ランナーは再現不可**。macOS は GitHub
  Actions クラウド (macos-latest) が必要。act は本プロジェクトの OS 依存検証には不向き。
- **無料枠の注意**: `project_ci_exhausted` メモは「3000h 超過で利用不可」と記録。月次リセット/public
  repo 無制限の可能性あり要再確認。macOS ランナーは 10x 課金。**実運用前に残枠を確認**。
- 含意: A1 の macOS **ビルド/テスト**は CI で閉じられる (実機挙動のみ別途 Mac 実機)。
