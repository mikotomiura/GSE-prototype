# tasklist

## 完了

- [x] `.age` 31 本を repo 外で復号（`gse-unpack --identity ~/.gse/age-identity.txt`）
- [x] `analyze.py --verify-blocks` を 3 名分（ラベルを読まない客観検証）
- [x] 計器の健全性を実測（壊れた行 0 / `dropped` 0 / `hook_health` alive /
      `paste` 0 / probe・realtime_label 0 行 / `session_start` 重複 0 /
      全ブロック 301.0s・`feat` 300 行 / 適格性ゲート 30/30）
- [x] 実施 OS をログの `capabilities` から判定（+ 独立な傍証 2 つ）
- [x] P014 の「1 つずれ」を G1-M の回答時刻で裏取り
- [x] Drive から G1-M / G1-S / 実施トラッキングを取得
- [x] `blocks/{P007,P009,P014}.json` に `file` / `execution_mode` / `manipulation_check_answers` を投入
      （強制比較は `forms_to_blocks.py` で機械変換・手転記なし）
- [x] `validate_blocks.py --dataset ~/gse-dataset` が 3 名とも緑
- [x] 復号済み NDJSON を `~/gse-dataset/raw/` へ staging（コミット対象外）
- [x] `data.md` B-4 の G1 明示マニフェストを作成し、**gitignore し忘れを塞いだ**
- [x] `config.json` の `sample_roster` を修正（★ 第 17 版の未反映も同時に直った）
- [x] ★ **3 人目が揃うまで `analyze.py` が止まることを実測**（`[NG] 確証標本が 2 名で…`）
- [x] `env.md` / `data.md` / `notes.md §11` に記録

## 完了（2026-08-27 追加分）

- [x] P016（3 人目）を復号・客観検証（11 本／★ 先頭は 2026-08-22 の練習・g1_mode=env）
- [x] P016 の「1 つずれ」を G1-M 回答時刻で裏取り（7 問すべて）
- [x] 管理シート xlsx から G1-M / G1-S / 実施トラッキングを読み出し
- [x] ★ `analyze.py` に `structurally_missing_features` を実装（P007 の案 b）
- [x] ★ **変異 2 種で selftest が赤になることを実測**（緑を信用しない）
- [x] 潰しが実データで効いたことを確認（P007 block1–9 = 1618〜4365 ms → 全 0.0）
- [x] `sample_roster` を 3/3 に確定（`CONFIRMATORY_COLLECTION_COMPLETE_3_OF_3`）
- [x] ★ **判定前の宣言を `notes.md §12` に書いた**（★ その時点で `results/` は空）
- [x] `analyze.py` を実行 → **`MANIPULATION_CHECK_FAILED`**（`notes.md §13`）
- [x] 出力にプライバシー漏れが無いことを実測（日時 0 件・ファイル名なし）
- [x] ⚠️ `§12-2` の過剰な主張（`degenerate_features` に必ず出る）を `§13-3` で訂正

## 未着手（★ 研究者の行為・別タスク）

- [ ] ★★ **課題設計のやり直し**（`§3.4-1` の指示）。⚠️ P016 が **5/5 で逆向き**だった点を起点に
- [ ] ★★ **到達可能性を上げる**（`§5.2`）。⚠️ P007 は **AUC=1.0 でも p<0.05 に届かない**
- [ ] ⚠️ **`--unseal` は使わない**（使うと再実施が確証的でなくなる）
- [ ] `preregistration.md` 第 18 版の起票（P009 の `§2.4-3` 適用／課題設計の改訂）
- [ ] 管理シート「G1 実施トラッキング」の更新（P016 の実施形態/OS 欄が空・P009 行が 8/8 のまま）
- [ ] `~/gse-dataset` の `.gitignore` 変更を commit（他 repo なので研究者が行う）
- [ ] ⚠️ P010 を dataset へ staging（`blockers.md` D-2・ADR-012 Stage 0 の入力）

## 完了（2026-08-27 サーヴェイ＋引き継ぎ）

- [x] `/literature-review` 1 ラウンド（用途=判定 gate / 予算=angle 4 既定）
- [x] ★ **前ラウンド最優先のやり残し [P44] 本文を取得**（一次全文・Table 4 の内訳）
- [x] ⚠️ **参照クラスの誤対応を発見し [P43]/[P44] と `_index.md` 2026-08-02 行に訂正を追記**
- [x] 反証 angle を含め、**GSE に有利な主張 [P133] を否決**（対称性の担保）
- [x] `references.md` に **P133 / P134 / V87** を append（`check_citations.py` = 違反なし）
- [x] `research-positioning.md` への還元判定 = **還元不要**（理由は `decisions.md` D-6）
- [x] `notes.md §14` で実験側へ接続
- [x] ★ **引き継ぎ `_handoff/next-session-prompt-friction-survey-round2.md` を作成**
      （★ subagent の割り方・G-GEAR トラックの取り込み・リベース手順を含む）
- [x] ⚠️ **引き継ぎの事実主張 5 件を検算**（採番 P135/V88・O1 引き継ぎ実在・
      finish-task Step 5・観測台帳・ADR-016 Accepted）

## ⚠️ 引き継ぎで訂正した、私の誤った説明

- ⚠️★★★ 2026-08-27 の対話で「**O1 の判断 4/4b・事前登録 5 件・同意文書が未確定**」と説明したが、
  ★ **PR #118（2026-08-26 merged）で全件確定済み**だった。ローカル main が 12 コミット遅れていた。
  → ★ 引き継ぎ §3-1 に訂正を明記した。
