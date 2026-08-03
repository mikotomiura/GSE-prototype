# 設計 — G1 事前登録

## アプローチ

既存の設計（`README.md` / `config.json`）を**凍結可能な水準まで詰めて**別文書に固定する。
既存ファイルは削らず、**改訂点だけを追記**して整合させる（append 方針）。

| 成果物 | 役割 |
|---|---|
| `experiments/20260801-controlled-friction-task/preregistration.md` | ★ **凍結文書**（齟齬時はこれが正） |
| 同 `config.json` | 機械可読な凍結基準（本文書と一致） |
| 同 `README.md` / `notes.md` / `SEED` | 改訂点への整合（追記のみ） |
| `docs/references.md` | [P43] [P44] を append-only 登録 |
| `docs/literature/20260802-controlled-task-manipulation-prior-protocols.md` ＋ `_index.md` | 文献カード 3 枚 ＋ 索引 1 行 |

## セッション構成（改訂の中心）

```
[1] copy      5分   ← positive control ＋ 個人の転写 baseline（位置固定）
[2]…[9] G1    5分×8  ← HI4 / LO4（SEED で無作為化・強制比較の鎖はここで閉じる）
[10] copy     5分   ← positive control（疲労ドリフト測定を兼ねる・位置固定）
```

約 62 分（改訂前 48 分）。並べ替えは G1 が C(8,4)=70（最小 p≈0.014）、
positive control が C(10,2)=45（最小 p≈0.022）でいずれも 0.05 に到達可能。

## 見る順序（固定）

1. 操作チェック → 不合格なら判定を**解釈しない**
2. positive control → 不合格なら **G1 を無効**
3. FS-A / FS-B の判定

## 検証戦略

コード変更ゼロのため `cargo test` は対象外。文書側の整合を確認する。

- [x] `preregistration.md` と `config.json` の数値一致（10 ブロック / n=5 / λ=1.0 / 0.70 / 0.60 / 80%）
- [x] `preregistration-v0.3.md` 未変更（凍結契約）
- [x] `research-positioning.md §5` 未変更
- [x] 全 inline [n] が `references.md` に実在
- [x] コード（`src/` `src-tauri/`）に差分なし
- [x] PII・セッション日時・raw NDJSON なし

## リスクと緩和

| リスク | 緩和 |
|---|---|
| 凍結後に「実は先行研究があった」と分かる | ★ **凍結の直前に調査した**（判断 2）。それでも網羅性は主張しない |
| positive control 追加でセッションが伸び、被験者が離脱 | 62 分。研究者判断で採択済み。copy は認知的に軽いので末尾に置いても負担が小さい |
| positive control の位置固定による交絡 | **floor チェックに限定**し効果量を主張しないと明記（判断 4） |
| `✗/✗` が出たときに過大解釈される | §3.7 で**解釈規約を事前宣言**（「操作が細かすぎた可能性」を必ず併記） |
| 産出量差が摩擦の分離に化ける | `keys` 単独 AUC の descriptive 報告と解釈制限（判断 5） |
