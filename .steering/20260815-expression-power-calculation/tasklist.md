# タスクリスト — 表現層の検出力計算

## 0. 準備
- [x] 引き継ぎ §1 の 5 文書を指定順に読む
- [x] ⚠️ 引き継ぎと一次の食い違いを 1 件検出（★ B1 未実施の理由 = S5C-D9「音を聞ける環境ではない」）
- [x] ★ 研究者判断: **PS-Q1 を先に動かす** / **音は今は聞ける**
- [x] ★ 研究者判断: **効果量＝両方（標準化 ＋ 実測）** / **骨格＝G1 型**
- [x] `/start-task` で `.steering/20260815-expression-power-calculation/` を作成
- [x] `reproducibility-discipline` を Read
- [x] 一次確認: numpy/scipy/pandas 不在 / G1 の確証データ無し / P000 の生 NDJSON は在る

## 1. 実験ディレクトリ（`reproducibility-discipline` ルール 1〜3）
- [x] `experiments/20260815-expression-power/` を作る
- [x] `SEED` / `power.config.json`（★ HMM_VERSION 0.3.0 / EXPR_VERSION 0.3.0-step4 / repo ad697f1 を刻んだ）
- [x] `env.md`（★ numpy/scipy/statsmodels/pandas 不在を実測で記録・自前実装 4 件の対応表）
- [x] `data.md`（⚠️ **commit で固定できない**ことを実測し manifest sha256 で固定・生ログ 0 バイト）
- [x] `run.sh`（1 コマンド再現・`PYTHONIOENCODING=utf-8 PYTHONUTF8=1`）

## 2. 計算本体
- [x] `scripts/power_calc.py`
  - [x] 到達可能性（★ 効果量非依存）: 個人水準 `1/C(B,B/2)` / 符号検定 `2^-n` / コホート
  - [x] ★★★ Mann-Whitney 厳密帰無 → **B=8 では AUC 0.9375 以上でなければ p<0.05 に届かない**
  - [x] 検出力: 解析式（正規近似）
  - [x] 検出力: 並べ替えモンテカルロ（seed 固定）
  - [x] 4 設計（束ねる / 完全 factorial / 一部実施 / dismantling）の比較
  - [x] 識別（1 of k のみ真のときの検出確率と FWER）
  - [x] 資源（総ブロック数 → 分）
- [x] `scripts/block_variance.py`（★ 実測アンカー・**集計値のみ**出力・入力 manifest を刻む）
  - [x] ⚠️★ **窓の取り方を修正** —— 5 分窓では 1 セッションに 2 窓入らなかった。
        ★ `spec` §8 逐語「1 ブロック = 1 セッション」に合わせ**セッション = ブロック**へ変更
  - [x] 打鍵率（keys/min）／ `p_stuck > 0.70` の割合
- [x] `scripts/summarize.py`（★ JSON → 研究者が読む Markdown 表）
- [x] `scripts/power_selftest.py` — **43 ok / 0 fail**
  - [x] 検査 1: Mann-Whitney 帰無の総和・次数・対称性
  - [x] 検査 2: ★★★ **C(8,4)=70 / 最小 p=1/70 / AUC 0.9375 / 帰無 95%点 0.875 の再現**
  - [x] 検査 3: 解析式 ⇄ モンテカルロ（4 セル・差 ≤0.032 / 許容 0.06）
  - [x] 検査 4: 到達不能の境界（★ B=4/6 は δ=50 でも棄却率 0・B=8 は 1）
  - [x] 検査 5: 帰無の第一種過誤が**厳密値**（3/70・12/252）と 3SE 以内で一致
  - [x] 検査 6: seed 固定で 2 回走らせて **byte-equal**（sha256 一致）
  - [x] 検査 7: 決定的部分は seed 非依存 / モンテカルロ部分は seed 依存

## 3. 結果と還元
- [x] `results/` に JSON（`power.json` / `block_variance.json`）＋ Markdown 表（`summary.md`）
- [x] `notes.md`（仮説の接地・出典 [P110]/[P108]/[V81]・限界 8 件）
- [x] ★★★ **AC-3: PS-D3 の推論は「前半成立・後半は支持されない」と明示**（EP-D3）
- [x] `.steering/.../decisions.md` に EP-D1〜D6 と EP-Q1〜Q6 を記録（★ 自分の予想が外れた事実も記録）
- [x] ⚠️ 研究者へ **PS-Q1 の材料**として返す（★ 決めていない）
- [x] ⚠️ `spec` §8 への還元（★ **2026-08-16・研究者の指示で実施**）—— ★ 「ブロック数を逆算して回避する」を
      **実数に置き換えた**: `C(8,4)=70` の離散性で B=8 は最小 AUC 0.9375 が要るが、**B=10 なら 0.84**。
      ★ **k=4 が「不能」になるのは B=8 のときで、B=10 なら k=12 まで到達可能（1 人あたり +10 分）**。
      ⚠️ **到達可能性と識別可能性は別問題**である旨も併記した（[P110]）

## 4. レビュー
- [x] ⚠️ `code-reviewer` + `security-checker` の並列起動 —— ★ **2026-08-16 に実施した**
      （★ EP-D6 の「動作条件で Agent 禁止」は解消した）。
      ⚠️★★★ **結果として、同日中に spec §8 へ還元した結論のうち 2 件が誤りだと判明した**
      （EP-D12「AUC 要求の k 非依存」は実装の都合／EP-D13「B=10 で k=12」は片側限定かつ要求 AUC=1.000）。
      → ★ **spec §8 は訂正済み**。⚠️ **`notes.md` / `results/summary.md` は未修正（EP-Q7）**。
      ⚠️ security-checker の H1/H2/M1/M3 は commit `636e082` で修正済み。
      ⚠️ HIGH 3 件（EP-D14/D15 と M-f）と MEDIUM 8 件は**研究者判断待ち**（decisions.md 末尾）。
      ★ 旧記録（Agent 禁止時の機械的自己検査）:
  - [x] 実セッション名の混入 **0 件** / `vk` 読み出し **0 件**
  - [x] `scripts/secrets-filter.sh` を全成果物に適用 → **rc=0**
  - [x] `__pycache__` は `.gitignore:50` で除外（`git check-ignore` 実測）
- [x] ⚠️ `/cross-review`（EP-Q6）—— ★ **2026-08-16 に `scripts/run-codex-review.sh 1adf092~1..1adf092 -- <scripts/run.sh/config>` で実施**。
      ★ 指摘 6 件のうち `run.sh` の summarize ガード非対称は修正済み（`2f22716`）。
      ⚠️ 「SEED が無い」は**誤検知**（★ 私がレビュー範囲のパスから SEED を外していた）
- [x] `/finish-task`（EP-Q5）—— ★ **2026-08-16 に研究者の指示で実施**（steering 最終化 / テスト / レビュー 3 系統 / commit）。
      ⚠️★★★ **ただし本タスクは「完了」ではなく「区切り」である** —— EP-Q7/Q8/Q9 が未決のまま残る

## 5. 追加で実施した検証（★ 研究者の指摘で発生）
- [x] ★ **G1 の目的を一次で確認**（README §1.1 逐語）＋ ⚠️ **「確証データ未取得」を訂正**（EP-D7 / EP-D8）
- [x] ★ **numpy 2.4.6 / scipy 1.17.1 を導入**（研究者の許可）→ `scripts/oracle_check.py`（**20 ok / 0 fail**）
- [x] ⚠️★★★ **oracle が解析式の楽観バイアスを検出** → `scripts/power_mc.py` を主経路に（EP-D9）
- [x] ★ **実測アンカーを P000 1 名 → P010–P014 の 5 名へ**（研究者がデータ所在を提供・EP-D10）
- [x] ⚠️★★★ **Phase1 の非打鍵ノイズを分離**（G1 の凍結ゲート `keydown ≥ 100` 適用・CV 1.053 → **0.502**・EP-D11）
- [x] ★ **Phase1 の現況を実測**（★ **完了済み・inconclusive・`decision_reason` = PreReg-1 通過率 0.00**）
      → ⚠️★★★ **「Phase1 完了待ち」という私の発言は誤りだった。Epic 2 系は着手可能**

## 6. 引き継ぎ
- [x] `.steering/_handoff/next-session-prompt-mhd-improvement-and-scope.md` を作成
      （★ 主題 A–D ／ Phase1 の 3 原因 ／ タスク拡張の可否を決める数字 ／ §9 の名指し警告 ／ 訂正 5 件）
