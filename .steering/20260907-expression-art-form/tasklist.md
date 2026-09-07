# タスクリスト — expression-art-form

## 0. 準備
- [x] ハンドオフ (`.steering/_handoff/next-session-after-adr024.md`) を読み、§D を一次で検証
- [x] ★ **D-2（`architecture-rules` SKILL ルール 5 が古い）は `e50bfe4` で既に解消済み**と実測
- [x] ★ **D-1（`out.txt` が未追跡かつ `.gitignore` 対象外）は未処理**と実測
- [x] `/start-task` → grill（判断 1–3 / 6 を `decisions.md` に記録）
- [x] ADR-024 / ADR-023 D3 / D3-c / D3-d / M6 / M9 / ADR-021 D4 / `expression-channel.md` §3.5 / §4 / §7 / §8 を読む
- [x] `file-finder` で「合否」表現と「数値」言及を横断探索

## 1. 設計
- [x] `design.md` v1（局所裁定）
- [x] `/reimagine` → `design-v1.md` へ退避、v2（横断規則）を生成
- [x] `design-comparison.md` で 2 案比較
- [x] ★ 研究者判断: **ハイブリッド採用** ／ **裁定は「添えない」で確定**（判断 4 / 5）
- [x] `design.md` を確定版へ

## 2. 実装（★ 文書のみ・コード変更ゼロ）
- [x] `docs/adr/ADR-025-no-self-quantification-return.md` を起票
- [x] `docs/adr/README.md` に登録（★ 表題は本文 H1 と一致させる）
- [x] `expression-channel.md` §7 冒頭 / §7.1 の位置づけを「合否」→「**事前の操作チェック**」へ（ADR-023 M9）
- [x] `expression-channel.md` §7.5 に **A17** を追加（⚠️ **A16 は ADR-023 M5 が予約済み**）
- [x] `expression-channel.md` §8 に **(a) 決着 / (b) 未決 / (c) 射程外の未決** を立てる
- [x] `expression-channel.md` §4.1 ・ §2.1(`:72`) ・ §7.5 A2(`:712`) に **ADR-025 参照**を足す（★ ねじれ解消）
- [x] `experiments/20260902-expression-layerA-visual/notes.md` の位置づけのみ更新（ADR-023 M6）
- [x] `docs/glossary.md` に **`操作チェック`** を追記
- [x] `docs/glossary.md` `抽象状態イベント` を ADR-021 D4（3 値 ＋ `invitation` ＋ `epoch`）へ是正

## 3. 検証（★ `design.md` テスト戦略 T1–T8）
- [x] **T1** `PYTHONUTF8=1 python scripts/check_citations.py` を**「違反なし」まで**繰り返す
- [x] **T2** `git status --porcelain` に本タスク由来の `src-tauri/` / `src/` / `scripts/` が無い
- [x] **T3** `git diff --stat experiments/` が `notes.md` のみ
- [x] **T4** 新規 ADR に禁止用語が規範文として無い
- [x] **T5** `docs/adr/README.md` の ADR-025 行と本文 H1 が一致
- [x] **T6** `A17` が存在し `A16` と衝突していない
- [x] **T7** `cd src-tauri && cargo test --workspace` が緑
- [x] **T8** `python experiments/20260902-expression-layerA-visual/scripts/selftest.py` が緑

## 4. レビュー・完了
- [x] `code-reviewer` ＋ `security-checker` を**並列**起動
- [x] ⚠️ **HIGH 指摘は backlog へ punt せず本タスクで消化**（★ HIGH 8 件・全件一次で検算して消化。→ `decisions.md` 判断 7）
- [x] コミット（★ パス限定 `git add` —— ⚠️ **未踏スライド作業を巻き込まない**）
- [x] `/cross-review`（★ **2 巡実施**。1 巡目 HIGH 3 件 / 2 巡目 HIGH 3 件のうち 1 件は偽陽性と実測。→ `decisions.md` 判断 8）
- [x] `/finish-task`（★ schema parity は skip —— ⚠️ `schema_dto.rs` / `schema/current.json` を touch していない・実測）

## 5. 引き継ぎ
- [x] 次セッション用プロンプトを `.steering/_handoff/next-session-after-adr025.md` に作成
