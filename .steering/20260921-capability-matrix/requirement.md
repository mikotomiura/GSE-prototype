# capability matrix（ADR-032 M7）— 現行 schema だけで T0/T1 をどこまで offline replay できるか

## 背景

★ `ADR-032 D5` 逐語の要求:

> ★ **GSE の現行 schema だけで T0/T1 のどこまで offline replay できるか capability matrix を作る**

★ 出所は `.idea/…gap-survey.md §11-2`（逐語・2026-09-21 に一次で確認）。
⚠️ `ADR-032 D5` は **④ IME content-free 状態機械の追加の是非を「今決めない」**と裁定し、
★ **matrix を先に作れ**と命じている（理由 1: 既存ログで作れる見込みがある ／
理由 2: 特徴量の設計が動きうるのでフィールド追加を先に打つと手戻りになる）。

### ⚠️ なぜ層別が要るか（★ `ADR-032 D5` の「判定の形」逐語）

> ★ **`capability matrix` は `OS × ライブ変換設定` で層別する**（⚠️ 1 つの表に畳まない）。

★ 理由は `D6` と地続きである —— ⚠️ 起票 6 の実測（2026-09-12・実機）で
**macOS 既定の「ライブ変換」ON では `abandon` が系統的に過大**になり、
★ **確定 1 回が `放棄 1 ＋ 確定 1` の 2 行に割れる**ことが分かっている。
→ ⚠️ 「作れる見込み」は **Windows と macOS で別々に判定しなければならない**。

## ゴール

`docs/architecture/` に、**`OS × ライブ変換設定` で層別した capability matrix** を置く。
判定は **3 値**（`ADR-032 D5` 逐語）:

| 判定 | 意味 |
|---|---|
| **作れる** | 現行 schema ＋ 既存実装で出せている（★ 実測で確認した） |
| **作れない** | 現行 schema に**送出元が無い** |
| **粒度が足りない** | 行は出るが、⚠️ **意味が壊れている / 単位が合っていない** |

⚠️★★★ **合成 fixture 上の判定であることを表に明記する**（判断 5）。
★ 実データでの再判定が要る項目は「**要再判定**」と書く（⚠️ 「作れる」と断定しない）。

## スコープ

### 含むもの
- ★ 実証範囲は **判断 5 の A** に限る:
  **現行 schema の静的分析 ＋ 既存 fixture での実測 replay ＋ 起票 6 の既測結果の引用**
- ★ 対象 Tier: **T0 / T1a / T1b / T1c / T1d / Q**（`.idea/survey §6.1` の候補列）
- ★ `.idea/survey §6.3` の **IME 優先候補 9 個**の可否（⚠️ D5 の本題）

### 含まないもの
- ⚠️ **`T2`（cross-channel）** —— ★ `ADR-032 D3 / D4` が「解かない / 不採」と**裁定済み**
  （⚠️ 蒸し返さない。★ ただし matrix の欄外に「裁定済み」と書いて所在を示す）
- ⚠️ **実機での新規 fixture 取得**（★ 判断 5 が B を却下している）
- ⚠️ **schema へのフィールド追加**（★ `ADR-032 D5` が「matrix の前にフィールドを打たない」と命じている）
- ⚠️ **ADR 本文の書き換え**（★ 規約。追加は番号の大きい文書側に置く）
- ⚠️ **`HMM_VERSION` を動かす / 特徴量・推論・介入を変える**（★ `ADR-032` 切り分け表 7）

## 受け入れ条件

- [ ] AC1: `docs/architecture/` に matrix 文書がある
- [ ] AC2: ⚠️ **`OS × ライブ変換設定` で層別**されている（★ 1 つの表に畳んでいない）
- [ ] AC3: 判定が **3 値**（作れる / 作れない / 粒度が足りない）で付いている
- [ ] AC4: ⚠️★★★ **合成 fixture 上の判定であること**と、**要再判定**の項目が明記されている
- [ ] AC5: 各判定に**一次の根拠**（コード行 / 実測ログ / 起票番号）が添えてある
- [ ] AC6: `.idea/survey §6.3` の **IME 優先候補 9 個**すべてに判定が付いている
- [ ] AC7: ⚠️ 引用 `[Pn]` / `[Vn]` を使うなら `docs/references.md` に **active** で在る
      （★ `scripts/check_citations.py` が `docs/` を走査する）

## 関連ドキュメント

- `docs/adr/ADR-032-instrument-change-arbitration.md` **D5 / D6 / D2 / M7 / M11 / §Consequences**
- `.steering/20260914-mhd-feature-offline-tiers/decisions.md` **判断 4 / 判断 5 / 判断 25 #16**
- `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md` **起票 6 / 起票 7**
  （⚠️ 引継ぎメモは参照先を `20260914-instrument-change-arbitration` と書いていたが**誤り**。
   ★ 2026-09-21 に grep で一次を特定した）
- `.steering/20260914-instrument-change-arbitration/blockers.md` **起票 19 / 起票 21**
- `src-tauri/schema/current.json` ／ `src-tauri/src/analysis/feat_offline/`
- `src-tauri/src/input/ime_compose.rs`（★ OS 非対称の一次）／ `src-tauri/src/capabilities.rs`

## 運用メモ
- /reimagine 適用: **No**
- 理由: ★ 成果物の形（3 値・層別・置き場）は `ADR-032 D5` と判断 4 / 5 が**既に確定**しており、
  設計の選択肢が無い。⚠️ 中身は一次資料の読解と実測であって、案の比較ではない。
