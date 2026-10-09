# notes — EH1 of the portrait

> ⚠️ EH0 の実験である。結果は「検査した範囲で見つからなかった」までで、「状態の情報が無い」の証明ではない（親タスク判断 8 E1-3）。合成した「停滞」は打鍵の統計の型であり、認知の状態ではない。「GSE が示した」と書かない。

## 接続

- **検証する仮説**: `docs/research-positioning.md` §5 の仮説には対応しない（肖像は EH0・RP の主張ではない）。問いは `.idea/20261005-motivation-fatigue-reentry-surface.md` §8.5 の EH1 と、親タスク `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 5・8（E1-1〜E1-8）。
- **X/Y**: MhD の X/Y も検証の X/Y も扱わない。`p_stuck` は陽性対照 PC2 の材料と、合成の記録の妥当性の確認にだけ使う（L0 の検証対象ではない）。
- **事前登録に当たるもの**: `.steering/20261009-portrait-eh1-eh2/design.md` §3（合否の基準・結果の前に `abfb2c45` で固定）。固定の後の逸脱は同 §8。
- **借用した手法**: 攻撃者の最大を取る漏れの検査の組み立て（`papers/ime-observation/experiment/preregistration.md` §6.8）。セッション単位の交差検証とブートストラップは標準の手法。

## 実行の記録

| 日時 | 機械 | world | 計器のコミット | 所要 | selftest |
|---|---|---|---|---|---|
| 2026-10-09 | Windows 11・16 論理コア・Python 3.11.9 | v1 | `7c29fd8a`（`experiment_dir_dirty` / `src_tauri_dirty` とも false） | 840 s | 0 failed（変異 3 本とも PASS） |
| 2026-10-09 | 同上 | v2 | 同上 | 857 s | 0 failed（変異 3 本とも PASS） |

## 結果（基準は design §3・値は `results/<world>/*.json`）

### world v1（主の記録・固定した設計どおり）

`summary.json` の判定（主の 6 組 = raw/ordinal/keyed × none/diffuse。jit・cap1 の派生 18 組は E1-6・E1-4・E1-7 のみ）。

| 検査 | 結果 |
|---|---|
| E1-3 | 6 組とも**判定不能**。陽性対照 PC1 は検出器が働かず（`positive_controls_ok=false`・PC1 の上乗せ hgb ≈ 0・lr +0.0008。モデル A の AUC が 0.997 で上限が 0.003 しかない）。上乗せの上限はいずれも 0.0004 付近 |
| 順序の感度 | raw 2 組が緑（比 4.47）、ordinal 2 組（比 1.18）・keyed 2 組（比 1.42〜1.43）は赤 |
| E1-6 | 24 組すべて赤（招待時の変化の中央値に対し、それ以外の中央値が 0。比は inf） |
| E1-4 | 主の 6 組と jit の 6 組は緑、cap1 の 12 組は判定不能。PC2 は赤（陽性対照として働いた） |
| E1-7 | 24 組すべて緑（違反 0） |
| 帰無 | E1-3 の並べ替え 95 パーセンタイルは raw-none で 0.00096（`null_ok=true`） |

### world v2（逸脱・design §8）

| 検査 | 結果 |
|---|---|
| E1-3 | 6 組とも**判定不能**。ただし PC1 は検出器が働いた（上乗せ hgb +0.157・lr +0.200）。PC2 は働かず（hgb −0.018・lr −0.002）。実際の組の上乗せは hgb −0.017・lr +0.0008（raw-none。上限 0.0039、並べ替えの 95 パーセンタイル 0.0016）。`positive_controls_ok=false` が判定不能の理由 |
| 順序の感度 | 6 組すべて赤（raw 比 2.71・ordinal 1.39・keyed 1.21） |
| E1-6 | 24 組すべて赤（raw-none の比 8.3・ci90 下限 4.0 で、基準を満たさない側） |
| E1-4 | v1 と同じ（主 6 組・jit 6 組が緑、cap1 12 組が判定不能、PC2 は赤） |
| E1-7 | 24 組すべて緑 |

### 探索（固定の外）: scheduler `recent`

（`exploratory_recent.json`。合否を付けない）

### 記述: E1-2・戻ったときの変化と不在の長さの順位相関・D の組の距離

（`e12.json`・`describe.json`）

### E1-8 の候補

`results/<world>/e18/synth-*.png`（基準なし）。見本の画像は `results/<world>/samples/synth-*.png`。

## 逸脱・気づいたこと

（引き継ぎ先のセッションが気づいたことはここに書く。design §8 への反映は本体のセッションが行う）

- **判断 W1（実行）**: Windows では `run.sh` の最後の provenance 書き出しが `…/release/gse-replay`（`.exe` なし）を開いて `FileNotFoundError` で落ちた（スモーク 1 回目。解析本体は終わっていた）。計器は変えず、`run.sh` の冒頭に書かれた環境変数 `GSE_REPLAY` に ビルド済みの `gse-replay.exe` を指定して回し直した。スモーク 2 回目と本番 v1・v2 はこの指定で実行（`provenance.json` の `experiment_dir_dirty` は false）。`run.sh` が Windows で `.exe` を補わない点は本体のセッションで直すか判断してほしい。
- 結果は Mac 版（作った機械）のスモークで見えた傾向（design §8: v1 の E1-3 は全組判定不能、v2 は PC1 が働く）と同じ向きだった。
- E1-3 は両 world で判定不能のため、「形に停滞の情報が残らない」とは言えない。見つからなかったのではなく検査器が基準に届いていない（v1: 構成上、v2: PC2 が働かない）。
- **判断 W2（Surface Pro 8 での試み・止めた）**: 2026-10-09 13:30〜13:57、Surface Pro 8（Windows 11・8 論理コア・RAM 8 GB）でも EH1 を回し始めたが、止めて結果は残していない（本番の結果のファイルは開かずに消した）。計器は変えていない。
  - スモーク（v1）は selftest `0 failed`。`.exe` の件は判断 W1 と同じ症状で、同じ回避（`GSE_REPLAY` に `.exe` を渡す）で通った。
  - 本番（v1）は selftest `0 failed`（変異 `random levels` も PASS）の後、`checks.py` が **`MemoryError`** で落ちた（開始から約 3 分半・runs の段）。`checks.py` の並列は `--jobs` の既定値 16 で、`run.sh` は渡さない。RAM 8 GB の機械に 16 プロセスは載らない。並列 3 で回し直しかけたが、研究者の判断で止め、EH1 は G-GEAR の結果（判断 W1）を使う。Surface では EH2 だけを回した（`experiments/20261009-portrait-eh2/notes-windows.md`）。
  - 本体のセッションへ: RAM の少ない機械でも回せるよう、`run.sh` から `checks.py` に `--jobs` を渡せるようにするか判断してほしい。乱数は `SEED` とセッションから派生させているので、並列数で結果は変わらないはず（コードを読んだ範囲・実測で比べてはいない）。

## 限界

- E1-3 はセッションをまたいで学ぶ攻撃者を想定している。本人が 1 セッションの中で自分の写像を覚えることは検査しない（`keyed` の守りはこの想定に頼る）→ EH3 の M-4。
- 結果は合成の記録の仮定（区間の型・遷移・打鍵の分布）に条件づけられる。world v1 では打鍵の有無だけで停滞がほぼ決まり、v2 では停滞が修正・打鍵の間隔・まとまりの打鍵数にだけ出る。実際の打鍵はその間のどこかにある（未確認）。
- 生成器は仮の文法で、製品の候補ではない。見た目の美しさは測っていない。
- EH1 は Windows の機器の解析で回した。`analysis/` で OS により違うのはキーリピートの判定だけで（Windows は同じキーを離す前の再度の押下を除く・macOS は hook で autorepeat を捨てる）、合成の記録ではその重なりは押下の 0.069%。EH1 は入力層を通らないので、OS ごとの入力の違い（IME・観測するキー）は検査していない（decisions 判断 5 の補記）。
