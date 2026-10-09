# notes — EH1 round 2 of the portrait

> ⚠️ EH0 の実験である。結果は「検査した範囲で見つからなかった」までで、「状態の情報が無い」の証明ではない（親タスク判断 8 E1-3）。合成した「停滞」は打鍵の統計の型であり、認知の状態ではない。「GSE が示した」と書かない。

## 接続

- **検証する仮説**: `docs/research-positioning.md` §5 の仮説には対応しない（肖像は EH0・RP の主張ではない）。問いは親タスク `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 5・8（E1-1〜E1-8）と、第 1 回の結果（`.steering/20261009-portrait-eh1-eh2/decisions.md` 判断 9）。
- **X/Y**: MhD の X/Y も検証の X/Y も扱わない。`p_stuck` は陽性対照 PC2 の材料と、材料の情報量の記述にだけ使う（L0 の検証対象ではない）。
- **事前登録に当たるもの**: `.steering/20261009-portrait-eh1-round2/design.md` §3（合否の基準・どの結果よりも前に `ea02e557` で固定）。固定の後の逸脱は同 §8。
- **第 1 回との関係**: 合成の記録は第 1 回と同じ（同じ生成器・同じ seed）。第 1 回の結果は `experiments/20261009-portrait-eh1/notes.md`。
- **借用した手法**: 攻撃者の最大を取る漏れの検査の組み立て（`papers/ime-observation/experiment/preregistration.md` §6.8）。セッション単位の交差検証とブートストラップは標準の手法。

## 実行の記録

| 日時 | 機械 | 何を | 計器のコミット | 所要 | selftest |
|---|---|---|---|---|---|
| 2026-10-09 17:42〜18:14 | G-GEAR | 本番 v2・`--jobs 16`。E1-3 の途中で止められた（結果なし・逸脱 1） | `0429e3aa` | — | 0 failed |
| 2026-10-09 18:22〜19:34 | G-GEAR | **本番 v2**・`--jobs 8` → `results/v2/` | `0429e3aa` | 71 分（`checks.py` 4174 s） | 0 failed |
| 2026-10-09 19:34〜19:49 ごろ | G-GEAR | 本番 v1・`--jobs 8`。E1-3 の途中で止められた（結果なし・逸脱 1） | `0429e3aa` | — | 0 failed |
| 2026-10-09 21:54〜23:10 | G-GEAR | **本番 v1**・`--jobs 8` → `results/v1/` | `0429e3aa` | 77 分（`checks.py` 4487 s） | 0 failed |

- 機械: G-GEAR（Windows 11・provenance の `platform` は `Windows-10-10.0.26300-SP0`・16 コア・メモリ 31 GB）。Python 3.11.9（実験のディレクトリの `.venv`）。
- 計器: HEAD `0429e3aa`。計器の最後のコミット `eb5034a3` との差は `.steering/` の 2 ファイル（tasklist と引き継ぎ）だけ。
- `gse-replay`: 第 1 回と同じビルド（`GSE_REPLAY` で渡した・`gse_replay_sha256` = `71d09dab…986`・`hmm_version` 0.5.0）。
- provenance（両 world）: `experiment_dir_dirty` false・`src_tauri_dirty` false・`seed` 20261009・`jobs` 8。
- selftest（両 world で PASS 35 行・`0 failed`）。変異 4 本はどちらも PASS:

| 変異 | v2 | v1 |
|---|---|---|
| 不在の中で薄れる → E1-4 が赤 | violations=11 | violations=9 |
| 直近の入力が少ないと中立 → E1-7 が赤 | violations=46 | violations=24 |
| 水準を乱数にすると E1-3 の上乗せが余裕の下 | hgb −0.012・lr −0.010（60 セッション） | hgb +0.000・lr −0.001 |
| `lattice` の水準を乱数にすると L300 の上乗せが余裕の下 | full/hgb −0.032・small/hgb −0.034・full/lr −0.008・small/lr −0.006 | −0.000・+0.000・−0.001・−0.001 |

- `lattice` の揺らしの INFO（±50 ms で区分が保たれた描いた更新）: v2 70/107・v1 76/107（どちらも 40 組）。
- 段ごとの時刻（`checks.py` の開始から）: v2 は runs 16600 本 134 s・E1-3 L300 2216 s・L60 4111 s・材料の情報量 4134 s・全体 4174 s。v1 は 154 s・2489 s・4424 s・4448 s・4487 s。

## 結果（基準は design §3・値は `results/<world>/*.json`）

（本番の後のセッションが書く）

## 逸脱・気づいたこと

（本番を回したセッションが気づいたことはここに書く。design §8 への反映は本体のセッションが行う）

1. **`--jobs 16` ではなく `--jobs 8` で回した**（引き継ぎ §3 は 16）。v2 を 16 で回していた 18:14 ごろ、機械全体の空きメモリが尽きかけ（空き 1.1 GB / 31 GB）、Claude Code が裏で走らせていた `run.sh` を止めた。計器の例外（`MemoryError` 等）ではない。そのときの `checks.py` の親は約 4.2 GB、ワーカーは 1 本 0.2 GB ほどで、残りは同じ機械の他のセッション・アプリが使っていた。研究者の決定で `--jobs 8` に下げて v2 を回し直し、v1 も 8 で回した。結果は並列の数に依らない設計（design §3.9）。両 world の provenance の `jobs` は 8。
2. **v1 も 1 回止められた**（19:34 に `--jobs 8` で始め、19:49 までに E1-3 の途中で同じ理由で止められた）。研究者の決定で 21:54 に同じ指定で回し直し、最後まで通った。
3. 止められた 2 回とも、`run.sh` だけが止まり `checks.py` の木が孤児として残ったので、手で止めた（provenance と結果の置き換えの段が走らないため、残しても結果にならない）。`run.sh` は始めに `work-<world>/` と `results/.partial-<world>/` を消すので、回し直しは前の回の残りに依らない。止められた回のログは worktree の外に残した（コミットしない）。
4. 所要: 引き継ぎの見積もり（16 並列で 1 world 2〜4 時間）より短く、8 並列で v2 71 分・v1 77 分。
5. `.venv` に requirements.txt に無い `pyflakes` 4.0.3 が入った（`pip install -r requirements.txt` の後の `pip freeze` で確認・入った理由は調べていない）。`scripts/`・`run.sh` に `pyflakes` の参照は無い（grep で確認）。provenance の `packages` には出ない。

## 限界

- 第 1 回の限界（`experiments/20261009-portrait-eh1/notes.md` §限界）はそのまま残る: 本人が 1 セッションの中で自分の写像を覚えることは検査しない・結果は合成の記録の仮定に条件づけられる・生成器は仮の文法・EH1 は Windows の解析（キーリピートの判定あり）で回す。
- L300 は「直近 300 s の過半が停滞か」を当てる攻撃者で、更新の間隔（I = 5 分）に揃えた。もっと長い尺（「この 30 分は苦しんでいたか」）は検査していない。
- world v1 の E1-3 は、結果の前に「問いが立たない」と宣言した（design §3.1）。
- 合成の記録の性質（第 1 回から引き継ぐ・記録を同じにするため直さない・判断 4 R3・R4）: world v2 でも、次のまとまりの始まりは前のまとまりの最後の打鍵から数えないので、打鍵の速さに依る残りが打鍵の有無に残りうる。J の揺らしで、終わりの直前の打鍵がセッションの外に出うる（`active` からは外れ、`presses` には残る）。
