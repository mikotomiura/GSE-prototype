# 次セッション開始プロンプト — PreReg-1 の残り（施行計画 / 再凍結 / 反応性の点検）

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-17 に `.steering/20260817-prereg1-scale-instructions/` で
**PreReg-1 の器（教示文・8 ビネット・採点・記録）を初回施行できる状態にした**。
⚠️ **施行はしていない。GATE1 は依然として未発効。**

---

===

## §0 ⚠️★★★ まず、この 2 つを疑ってかかること

1. ⚠️★★★ **「〜と引き継ぎに書いてあった」を根拠にしない。**
   前回の引き継ぎ（`next-session-prompt-prereg1-scale-instructions.md`）は
   **§0 の前提そのものが誤っていた**。「通過率 0.00 ＝ 1 人も通っていない」と書いてあったが、
   一次資料では **5 名全員が一度も受けていない**（`vignette.total == 0`）だった。
   `decision_reason` の逐語だけを転記したことが原因で、**一次まで降りていれば防げた**。
   → ★ 本ファイルの記述も**仮説として扱い、一次で確かめてから使うこと**（`verify-before-claiming`）。
2. ⚠️★★ **前回のタスクは「施行できる状態にした」であって「施行した」ではない。**
   完了報告をそう読まないこと。

## §1 ★ 最初に読むもの（この順で）

1. `.steering/20260817-prereg1-scale-instructions/decisions.md` — D-1〜D-13（★ 特に **D-3 / D-4 / D-10**）
2. 同 `tuning-log.md` — ★ **実測ログ。§5「収束基準は未達」と §6「この実測が保証しないこと」を必ず読む**
3. 同 `tasklist.md` §8「未完了・引き継ぐもの」
4. `docs/preregistration-v0.3.md` §1 PreReg-1 — ★ **凍結された合否条件（6/8・80%）**
5. `experiments/20260731-phase1-calibration-analysis/notes.md` §4・§6.2

## §2 ★★★ このセッションでやること（★ 研究者の承認を得てから動く）

### A. ⚠️★★★ D-10 の採否を確定する（★ **最初にこれ**）

前回、`passed` に **完了ガード `total >= 8`** を新設した。
★ 「8 問そろわなければ、6 問一致でも合格にしない」。

- ★ 根拠: PreReg-1 逐語「**8 ビネット中** 6 問以上」は 8 問の実施を前提にしている
- ⚠️ ただし **旧実装より厳しい方向の変更**である。研究者は「合格条件は据え置き」と指示していた
- ★ 外すなら `calibration_eval.rs` の `total >= VIGNETTE_TOTAL &&` を削るだけ（1 行）

→ ★ **研究者に採否を確認し、`decisions.md` D-10 に結論を追記する。**

### B. ★ 施行計画を決める（D-4 で先送りしたもの）

| 決めること | 材料 |
|---|---|
| 既存 P010–P014 に**遡って**当てるか | ⚠️ 当てると L5（計測それ自体が行動を変える）を負う。⚠️ P012 は F2/F5 とも未回答＝離脱済み |
| 次コホートでいつ当てるか | ★ セッション開始前の 1 回。★ 所要は 8 問 |
| 何人に当てるか | ⚠️ **プール倍率の実数が未確定**（`_handoff` §5 B-a・研究者「現時点では分からない」） |

### C. ⚠️★★★ GATE1 を**発効**させるなら PreReg v0.4 を切る

★ 前回の変更は「**GATE1 が一度も発効していないから forking paths に当たらない**」という
整理の上に立っている（D-3）。★ **発効させた瞬間にこの整理は使えなくなる。**

→ ★ `docs/preregistration-v0.3.md` の改訂方針どおり **v0.4 を切り、
変更点（採点関数・入力 UI・完了ガード・記録項目）と理由を明記して再凍結する**。
⚠️ **合格条件 6/8・80% は v0.4 でも動かさない。**

### D. ⚠️★★ 反応性（L5）の残余を点検する設計を入れる

★ 教示文は「8 つの場面は…高い側か低い側かがはっきりするように書いてあります」と言っており、
⚠️ **本番プローブへ「端に寄せる」癖を持ち越しうる**。
★ 完了画面に打ち消し文（「本番では『どちらとも言えない』も正当」）を置いたが、
⚠️★★★ **その打ち消しが効くかは測っていない**（LLM では測れない）。

→ ★ **施行群と非施行群で Q1/Q2 の回答分布を比較する**項目を、
`experiments/` の分析設計に入れる。★ 決めるのは「何をもって反応性ありと言うか」。

## §3 ⚠️ 未着手のまま残っているもの（★ 前回タスクの射程外）

| # | 項目 | 状態 |
|---|---|---|
| 1 | ⚠️★★★ **`gse-dataset` の `schema/current.json` が未コミット** | ★ 前回 `elapsed_ms`/`changes` を追加して同期したが、**別 repo なのでコミットしていない**。★ `git push` は deny のため研究者が押す |
| 2 | ⚠️ `scripts/check_citations.py` が **CI にもフックにも未接続** | ★ `check_vignettes.py` は前回 CI に載せた。★ 同型の負債が citations 側に残っている |
| 3 | ⚠️ **プローブ負荷の個人適応** | ★★★ **straight-lining の真因はこちら**（`notes.md` §6.2: P012 は 11 件中 10 件で「多すぎた」）。⚠️ `probe_scheduler` は Phase1 凍結対象なので Phase1 完了後 |
| 4 | ⚠️ P011 で **Wall が一度も発火しなかった**原因調査 | ★ `notes.md` §5④-5。⚠️ 先に `intervention_enabled` を確認（memory: idle は Wall トリガーではない） |
| 5 | ⚠️ **PM-Q1〜Q7（表現層）が 700 行の議論のまま承認待ち** | ★ 前々回からの持ち越し |
| 6 | ⚠️ Codex 監査 pass1 / pass2 #3・#4 が未実施 | ★ `_handoff` §6 の手順（⚠️ **資料はプロンプトに貼る。シェルは起動しない**） |

## §4 ★ 落とし穴（★ 前回セッションの実測）

1. ⚠️★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）。`cd src-tauri` してから叩く
2. ★ ゴールデンは **4 本**（`minimal` / `phase1_ime_heavy` / `category_coverage` / `deep_silence`）。
   ★ 前回は特徴量に触れていないので **byte-equal のまま通った**（`HMM_VERSION` bump 不要を実測）
3. ⚠️★★ **Windows コンソールは cp932** → Python は `PYTHONUTF8=1` を必ず付ける
4. ⚠️★★ **`git push` は deny**。押すなら研究者に `! git push` を依頼する
5. ★ schema を変えたら `cd src-tauri && cargo run --bin emit_schema > schema/current.json` →
   `python scripts/check_schema_parity.py --dataset /c/gse-dataset` → ★ **gse-dataset 側にも cp する**
6. ⚠️★★★ **教示文の文言を変えたら必ず測り直す**（`tuning-log.md` の手順）。
   ★ 特に **「合否条件を教示文に書く」と被験者が出題構成を推測し始める**（D-11・実測済み）

## §5 ★ 前回の検証結果（★ 実測・引き継ぐ事実）

| 検査 | 結果 |
|---|---|
| `cargo test --workspace` | ★ **366 passed / 0 failed** |
| `gse-replay` ゴールデン 4 本 | ★ 全て byte-equal（15 / 6 / 2 / 51 snapshots） |
| `npx tsc --noEmit` | ★ exit 0 |
| `check_vignettes.py` ＋ `--self-test` | ★ 両方 OK |
| `check_schema_parity.py --dataset` | ★ OK（21332 bytes canonical） |
| `check_citations.py` | ★ 違反なし |
| 凍結値 | ★ `VIGNETTE_PASS_MIN = 6` / `VIGNETTE_COHORT_PASS_FRACTION = 0.80` **不変** |
| 実測（`empirical-prompt-tuning`） | ★ 誠実ペルソナ **22/22 回が ≥6/8**、straight-lining **5/5 回が <6/8**（最大 2/8） |
