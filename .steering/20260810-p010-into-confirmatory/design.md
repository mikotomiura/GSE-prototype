# 設計

## 実装アプローチ

第 15 版で作った仕組み（`sample_roster` による強制）は**そのまま使う**。
★ 変えるのは **roster の中身と、それに伴う文書の記録**だけである。

| | 第 15 版 | ★ 第 16 版 |
|---|---|---|
| `sample_roster.confirmatory` | `[]` | **`["P010"]`** |
| `sample_roster.shakedown` | `["P010"]` | `[]`（条項は残す） |
| `design.n_subjects` | 3 | **3**（変えない） |
| `status` | `SHAKEDOWN_DONE_CONFIRMATORY_NOT_STARTED` | `CONFIRMATORY_IN_PROGRESS_1_OF_3` |

★ **コードは 1 行も変えない**（`PREREG_REVISION` の 15→16 を除く）。
⚠️ 第 15 版で入れた境界 6 種・`resolve_sample`・`check_subject_matches_filename` は無変更。

## 変更対象

### 修正するファイル

- `config.json` — roster の移動 / `status` / `revision` 16 / `v16_changes`
  （★ `v16_changes` は **違反を先に、緩和を後に**の順で書く）
- `preregistration.md` 第 16 版 —
  - ⚠️ 冒頭で **`§2.4-2` 違反**を書く（言い換えない）
  - ★ その**後で**「実質的保護は残る（`results/` が空）」
  - ★ 実施条件は満たされていた（承認は実施前）と第 15 版の記述を訂正
  - ⚠️ **block07 が主判定に載る**代償
  - 第 15 版の該当 3 箇所に**撤回/訂正の印**（★ 本文は消さない）
- `analyze.py` — `PREREG_REVISION` を 16 に（★ 版一致検査 3 本が守る）
- `notes.md` / `data.md` — 実態反映
- `.steering/_handoff/next-session-prompt-p010-shakedown-closeout.md` — ★ 前提が変わったので**書き直す**

### 新規作成 / 削除

なし（引き継ぎファイルは既存を置換）。

## 影響範囲

- ★ `src-tauri/` / `src/` はゼロ → ⚠️ **zip 再配布は不要**
- ★ `analyze.py` の停止理由が「確証標本 0 名」→「**1 名で n=3 に達していない**」に変わる
  ＝ P010 が確証標本として数えられている証拠
- ⚠️ 3 名揃った時点で `--last-session-on-restart` が**必須**になる（block07・`§3.10`）

## テスト戦略

1. `analyze.py --selftest` / `validate_blocks.py --selftest` — ★ 第 15 版の境界検査が**無傷**であること
2. 版 3 点一致（`config.json` / `analyze.py` / `preregistration.md` = 16）
3. ★ **実データ**: 「確証標本が **1 名**で n=3 に達していない」で止まる
   （⚠️ 第 15 版は「0 名」だった。★ この差分が P010 の算入を示す）
4. ⚠️★ **壊して赤を見る**: `n_subjects` を 1 にすると roster ゲートを**通過**し、
   次のゲート（`§3.10` の block07）で止まる ＝ P010 が確かに解析対象に入っている
5. `bash run.sh` が GREEN

## ロールバック計画

- `git revert` で戻せる。⚠️ ただし `preregistration.md` は凍結文書なので、
  戻す場合も**改訂履歴に「第 16 版を撤回した」と残す**（履歴を消さない）
