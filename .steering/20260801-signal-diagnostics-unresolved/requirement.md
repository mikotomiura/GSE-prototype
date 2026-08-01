# 信号診断で未解決に残した 3 件の原因特定

引き継ぎ元: `.steering/_handoff/next-session-prompt-signal-diagnostics-unresolved.md`
前タスク: `.steering/20260801-phase1-signal-diagnostics-repro/`
対象実験: `experiments/20260801-signal-diagnostics/`

## 背景

前セッションは `.idea/20260801-architecture-signal-and-online-learning.md` §1 の記載値を
再現可能な実験に落とし込んだが、**3 件を「原因不明」のまま残した**。
`.idea` 側に式・前処理が書かれていないことを理由にしたが、**候補定義は有限で総当たりできる**。
この 3 件は ADR-008/009 の根拠に直結するので、曖昧なまま SSOT へ昇格させたくない。

前セッションでは「不一致」と報告したうち 1 件が**自分のバグ**だった (paste 比を丸め後に
計算していた。生値なら 96.6 で `.idea` の 97 倍と一致)。→ **まず自分の実装を疑う**。

## ゴール

`notes.md` §1 突合表の ⚠️ / ◯ が付いた 3 行を、**✅ (原因特定) か「追跡不能 (総当たり済み)」**
のどちらかに閉じる。決着の根拠は再現可能な形 (`results/probe_variants.txt`) で残す。

### 対象 3 件

| # | 項目 | `.idea` | 再現 | 優先度 |
|---|---|---|---|---|
| ① | 並べ替え検定の件数 (notes §2-A1) | 68 件 | 既存特徴量セル 63/70 | 低 (結論に影響なし) |
| ② | 実 X と 0.25·φ(F1) の相関 (notes §1 表) | r=0.78 | 0.763 / 0.761 | 中 |
| ③ | ICC (notes §2-C) | f1=0.060 f3=0.055 f4=0.159 f5=0.156 | 0.080 / 0.073 / 0.204 / 0.200 | **高 (ADR の主張に直結)** |

③ が最重要な理由: 「個人適応すべきは β でなく写像係数」という設計判断は
**「平均水準の個人差が小さい」**ことを根拠にしており、ICC の絶対値が動くと主張の強さが変わる。

## スコープ

### 含むもの

- 候補定義の総当たり (`probe_variants.py` → `results/probe_variants.txt`)
- 決着に応じた `diagnostics.py` 本体 / `notes.md` / `metrics.json` の更新
- `acceptance.sh` の新設 (`experiments/` を触っても `cargo test` / lint は無条件に緑になるため)
- `.idea` 該当節への結果追記 (gitignore・コミットには乗らない)

### 含まないもの

- ADR-008/009 の起票 (本タスクの結論が出てから別タスク)
- `engine.rs` / `features.rs` など凍結対象の変更 (診断は Python 側で完結)
- 新規データ収集 (既存 40 セッション・P010–P014 のみ)
- `notes.md` §4 の統計上の限界 3 件の解消 (設計上の限界として明示済み)
- Loop Engineering 自体の改修

## 受け入れ条件

- [ ] `acceptance.sh` が exit 0。中身:
      - `GSE_DATASET=... ./experiments/20260801-signal-diagnostics/run.sh` が exit 0
      - 同一 seed で 2 回実行し `results/diagnostics.json` が **byte-equal** (決定性)
      - φ 等価性検査が PASS のまま (r≥0.999 / 残差中央値≤1e-3 / >0.01 が≤0.5%)
      - `notes.md` の数値 ⇔ `results/diagnostics.json` の整合 (機械確認)
      - 出力の PII 検査 (`assert_no_pii`) が通る
- [ ] `results/probe_variants.txt` に候補定義の総当たり結果が出力されている
- [ ] `notes.md` §1 の該当 3 行が ✅ / 「追跡不能 (総当たり済み)」に確定している
- [ ] `decisions.md` に「何が原因だったか / どちらを正としたか」が記録されている
- [ ] `metrics.json` が結果と整合している

## 運用メモ

- **/reimagine 適用: No**
  - 理由: 実装案の選択ではなく、**有限の候補定義を総当たりして事実を特定する**調査。
    「複数案から最良を選ぶ」構造ではない。総当たり自体が候補の網羅にあたる。
- **Loop Engineering 適用: No** (判断根拠は `decisions.md` D1・ユーザー承認済み)

## 関連ドキュメント

- `docs/loop-engineering.md` — loop 判断の根拠 (§0)
- `experiments/20260801-signal-diagnostics/notes.md` — 突合表と未解決点の SSOT
- `.steering/20260801-phase1-signal-diagnostics-repro/decisions.md` — D4/D5 (`.idea` を正としない)
- Skill: `reproducibility-discipline` / `git-workflow`
</content>
