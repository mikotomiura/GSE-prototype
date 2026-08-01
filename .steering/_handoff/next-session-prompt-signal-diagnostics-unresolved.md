# 次セッション開始プロンプト — 信号診断で未解決に残した 3 件の原因特定

このファイルの「===」以下をコピペして開始する。

**このタスクは Loop Engineering の初実戦になる** (導入済みだが `_loop-config.json` が
まだ存在せず一度も回していない)。下の「§0 Loop Engineering の扱い」を必ず先に読むこと。

---

===

`experiments/20260801-signal-diagnostics/` は `.idea` の設計根拠を再現可能にした実験だが、
**3 件を「原因不明」のまま残している**。候補定義を総当たりすれば特定できるはずなので潰す。

## §0 Loop Engineering の扱い ★最初に判断すること

このリポジトリには Loop Engineering (issue 単位の有界自律ループ) が導入済み。
**複数 issue に割って回す作業は `docs/loop-engineering.md` を Read してから始めること**
(CLAUDE.md の loop 節が要求。用語 / Done・Stop / budget / events 契約 / モデル割当の単一 SSOT)。

### このタスクは loop に向くか — 先に判断する

**向く面**: 3 件は独立した調査項目で、それぞれ「原因特定 → 実装/文書の更新」で完結する。
**向かない面**: 調査タスクなので **AC を exit code や test 名で言いにくい**
(issue-slicing 基準 4 に抵触しうる)。「原因が特定できた」は機械判定できない。

→ **推奨**: AC を「調査の結論が出た」ではなく **成果物の状態**で書く。例:
- 「`results/probe_variants.txt` に候補 N 通りの結果が出力されている」
- 「`notes.md` §1 の該当行が ✅ か『追跡不能』に確定している」
- 「`notes.md` の数値と `results/diagnostics.json` の整合チェックが exit 0」

判断がつかなければ **loop に載せず通常のタスクとして進めてよい**。
その場合も判断理由を `.steering/[task]/decisions.md` に書くこと。

### loop に載せる場合の必須事項

1. **入口**: `/start-task` の grill でゴールを確定 → `to-prd` → `to-issues` で縦切り分解。
   **分解は Opus** (切り方の誤りが最も高価)。
2. **セッション境界**: 分解と実行は**別セッション**。`to-issues` 後に `/clear` して新セッションで実行。
   *issue ファイルだけを読んで実行が成立しないなら、分解が失敗している。*
3. **`acceptance.sh` が必須**。`experiments/` を触っても `cargo test` / lint は
   **無条件に緑**になる (Rust に触らないため)。issue-slicing の締めの検査に
   「test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか」とある通り、
   これが無いと「客観に見えて無意味な緑」を量産する。最低限:
   ```bash
   GSE_DATASET=... ./experiments/20260801-signal-diagnostics/run.sh   # exit 0
   # 同一 seed で 2 回実行し results/diagnostics.json が byte-equal
   # notes.md の数値 ⇔ results/diagnostics.json の整合 (前セッションで使った突合スクリプト)
   ```
4. **Allowed Files が交差するので並列にできない**。3 件はいずれも
   `diagnostics.py` / `notes.md` / `metrics.json` / `results/` を触る。
   issue-slicing 基準 3 により **`## Dependencies` で直列化**すること。
   並列 issue に見えるが交差しているので、そのまま parallel に流すと壊れる。
5. **`verify_level`**: ③ ICC は ADR の主張に直結するので **`recheck`**。①② は `parse` で可。
6. **モード**: `_loop-config.json` が未作成 = **Loop Engineering の初回実行**。
   `docs/loop-engineering.md` §実行モード に「新しい実行モードを初めて使う時は、
   最も安い issue 1 本を `parallel=1` で回して基盤を検証する」とある。
   **① (最も安い) を 1 本だけ回して基盤を確認してから** ②③ に進むこと。
   `--dry-run` では権限・cwd 境界・hook 発火が観測できない (実測で 2 回空振りした前例あり)。
7. **TASK-PRE / TASK-POST**: issue 確定直後に `codex-consult` で独立性の第二意見 (1 回)、
   全 issue 緑の後に `/cross-review` (1 回)。issue ループの内側に Codex を入れない。

## まず読む (着手前・順守)

1. `docs/loop-engineering.md` — loop の単一 SSOT (上記 §0 の根拠)。
2. `experiments/20260801-signal-diagnostics/notes.md` — **突合表と未解決点の単一真実源**。
   §1 の表で ⚠️ / ◯ が付いている行が対象。§4 は「解消しない限界」なので触らない。
3. `experiments/20260801-signal-diagnostics/diagnostics.py` — 現在の実装。
   特に `d4_icc()` / `d2_d3()` の `pearson` / `d1_d5()` のセル数え。
4. `.idea/20260801-architecture-signal-and-online-learning.md` §1 — 再現対象の記載値
   (gitignore・追跡外)。
5. `.steering/20260801-phase1-signal-diagnostics-repro/decisions.md` — D4/D5 に
   「`.idea` を正としない」「食い違ったらまず自分の実装を疑う」という前回の方針がある。
6. Skill: `reproducibility-discipline` (experiments/ を触るため必須) /
   `git-workflow` (コミット規約)。

## 背景 (なぜ残ったか)

前セッションでは「再現できた/できない」の仕分けまでで止め、**できなかったものの原因を追わなかった**。
`.idea` 側に式・前処理が書かれていないことを理由にしたが、候補は有限で総当たりできる。
この 3 件は ADR-008/009 の根拠に直結するので、曖昧なまま昇格させたくない。

なお前セッションでは、**「不一致」と報告したうちの 1 件が自分のバグだった**
(paste 比を丸めた値で計算していた。生値なら 96.6 で `.idea` の 97 倍と一致)。
今回も **まず自分の実装を疑う**こと。

## 未解決 3 件と検証方針

### ① 「並べ替え検定 68 件」(notes.md §2-A1) — 最も安い。基盤検証用

`.idea` §1.1 は「並べ替え検定 68 件」と書くが、再現では既存特徴量セル **63/70** 算出可能。

**仮説と検証**: 数える集合の定義違い。以下を総当たりして 68 になる組み合わせを探す。
- `per_feature_cindex.py` の FEATS は **12 個** (f1/f3/f4/f5/f6/raw_x/raw_y/ewma_x/ewma_y/
  p_stuck/p_flow/p_inc)。12 × 5 被験者 × 2 ターゲット = 120 のうち算出可能は?
- 7 特徴量版 (現行の `FEATS`) は 70 中 63。
- Q1 のみ / Q2 のみ で数えた場合。
- pooled 列を 1 セルとして数えた場合。

→ 68 になる定義が見つかれば「定義の違い」として決着。見つからなければ
**「再現不能」を維持**し、それ以上追わない (結論は再現できているので実害はない)。

### ② r=0.78 vs 再現 0.763 (notes.md §1 表)

`.idea` §1.3 は「実 X と『0.25·φ(F1) のみ』の相関は r=0.78」。再現は 0.763 (β_writing 固定) /
0.761 (実 β)。

**仮説と検証**: 相関の取り方の違い。以下を試す。
- 相手を `raw_x` でなく **`ewma_x`** にした場合 (`.idea` は「実 X」としか書いていない)
- 重み 0.25 を掛けない素の φ(F1) との相関 (スケール不変なので同じはずだが確認)
- 被験者ごとに計算して平均した場合 (プールでなく)
- 丸め前の値で計算した場合との差

→ 0.78 になる条件が特定できれば notes.md の判定を「一致 (条件: …)」に更新。
できなければ **「差 0.017 は追跡不能」と明記**して閉じる。
どちらにせよ §2-B の結論 (f1 支配は支持されない) は標準化寄与で出しているので影響しない。

### ③ ICC が系統的に 1.2–1.3 倍 (notes.md §2-C) ★最重要・verify_level=recheck

`.idea`: f1=0.060 f3=0.055 f4=0.159 f5=0.156 / 再現: 0.080 / 0.073 / 0.204 / 0.200。

**この差は ADR の主張に直結する**。「個人適応すべきは β でなく写像係数」という設計判断は
「平均水準の個人差が小さい」ことを根拠にしており、ICC の絶対値が動くと強さが変わる。

**仮説と検証**: 式と前処理の組み合わせを総当たりする。
- **式**: ICC(1) + k0 補正 (現行) / ICC(1) + k=n/k 平均 / 分散比 SSB/SST /
  MSB/(MSB+MSW) / ICC(1,k)
- **前処理**: feat 全件 (現行・124,517) / **ラベル窓集約 (n=200)** / 外れ値除去あり
- 特に **窓集約 (n=200)** は有力。`.idea` の他の数値が窓集約ベースなので揃えた可能性がある。

→ 4 特徴量すべてで `.idea` に一致する組み合わせが見つかれば、
**どちらが正しいかを判断して notes.md と結論を更新**する
(「`.idea` が正」なら現行実装を直す。「現行が正」なら `.idea` の値を誤りとして記録)。
見つからなければ LOO 範囲併記のまま維持。

## 実装方針

- 候補定義の総当たりは **本体の `diagnostics.py` に混ぜない**。
  `experiments/20260801-signal-diagnostics/probe_variants.py` として分け、
  結果を `results/probe_variants.txt` に出す。本体は結論が出てから直す。
- 総当たりスクリプトも `run.sh` から再現できるようにするか、
  「一度きりの調査」として `notes.md` に結果だけ残すかは判断して decisions.md に書く。
- **数値を書き換えるときは `results/` を再生成し、notes.md の突合表と
  `metrics.json` の整合を機械確認する**。この整合チェックは `acceptance.sh` に入れること
  (§0-3)。

## やらないこと (スコープ外)

- ADR-008/009 の起票 — 本タスクの結論が出てから別タスク。
- `engine.rs` / `features.rs` など凍結対象の変更。診断は Python 側で完結させる。
- 新規データ収集。既存 40 セッションのみ。
- 統計上の限界 (notes.md §4 の 3 件: セッション内依存・ICC の独立性仮定・
  Bonferroni 到達可能性の近似) の解消 — これらは**設計上の限界**として明示済み。
- Loop Engineering そのものの改修。使ってみて問題があれば
  `.steering/[task]/loop-retrospective.md` に記録するに留め、本タスクでは直さない。

## 検証 (= acceptance.sh の中身)

1. `GSE_DATASET=... ./experiments/20260801-signal-diagnostics/run.sh` が exit 0。
2. 同一 seed で 2 回実行し `results/diagnostics.json` が **byte-equal** (決定性)。
3. φ 等価性検査が PASS のまま (閾値: r≥0.999 / 残差中央値≤1e-3 / >0.01 が≤0.5%)。
4. `notes.md` の数値が `results/diagnostics.json` と一致 (機械確認)。
5. `metrics.json` も併せて更新されている。
6. 出力の PII 検査 (`assert_no_pii`) が通る。

## 完了時

- notes.md §1 の突合表を更新 (⚠️ → ✅ または「追跡不能」と確定)。
- decisions.md に「何が原因だったか / どちらを正としたか」を記録。
- `.idea` の該当節に結果を追記 (gitignore なのでコミットには乗らない点に注意)。
- loop に載せた場合は `.steering/[task]/loop-retrospective.md` を書く
  (**Loop Engineering の初実戦なので、枠組み自体への気づきを残すこと**)。
- `/finish-task` (`/cross-review` = TASK-POST 含む)。

## 現在の状態 / 注意

- ブランチ `chore/phase1-signal-diagnostics` / コミット `457fc34` (実験本体) +
  `40a873e` (本ハンドオフ)。**push・PR 未実施**。
- **ユーザーの Loop Engineering 導入作業が未コミットで並行している**
  (`docs/loop-engineering.md` / `.claude/skills/grilling/` / `.claude/agents/loop-*.md` /
  `scripts/loop-*.sh` / `CLAUDE.md` の loop 節 など 30 ファイル前後)。
  → **コミット対象を自分のファイルに限定する**こと。前セッションで
  `.claude/commands/implement.md` の削除を 2 回巻き込んで作り直している。
  `git add` は必ずパス指定で行い、`git add -A` / `git commit -a` を使わない。
- `.claude/commands/commands_setup/` は `commands_setup_research_inloop` に置き換わっており、
  **前々タスクで修正したテンプレートの作業コピーは無い**。差分は
  `.steering/20260801-codex-tooling-template-portability/template-changes.patch` にある
  (新系統に flock バグが残っているかは未確認・別タスク)。
