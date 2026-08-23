# タスクリスト

## 調査（★ 一次資料まで降りる）

- [x] `docs/architecture/workspace-behavior-observation.md` 全文
- [x] ADR-014（D4 / D4b / D4c / D4d / D9 / Alternatives / Consequences / 判断 1〜6 / Migration）
- [x] ADR-012（D1 / D2 / D4 / D5 / D6 / D7 / D8 / D9 / D10 / D11）
- [x] ADR-009（D2 / D3 / D4）・ADR-010（D1〜D6）・ADR-013 D1
- [x] `personalization-and-online-learning.md` §3.1 / §3.2 / §3.3 / §3.4 / §11-7
- [x] `research-positioning.md` §8 段別表 T0–T3 / §9 A-Q3
- [x] `domain-adapter-boundary.md` §Adapter C
- [x] `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §3.6 / §4
- [x] `.steering/20260823-r3-accept-and-role-category/decisions.md` D-11 / D-20
- [x] `experiments/20260819-nonkeystroke-silence-coverage/preregistration.md`（★ 様式の先例）

## 検証（⚠️ 断定の前に一次へ降りる）

- [x] `grep -rn "left_observation\|still_stalled" src-tauri/src/ src/` → **0 件**（★ 実装は無い）
- [x] `progress_proxy` が打鍵ベースであることを `personalization §3.2` 逐語で確認
- [x] **ADR-016 の採番が repo 全域で未使用**（`target/` 除く・**0 件**）
- [x] **判定量の接頭辞 `NK-` が repo 全域で未使用**（**0 件**。⚠️ `N-1`〜`N-3` は `.steering/20260821-precollection-close-and-x-axis/blockers.md` が使用中）
- [x] **ADR-012 D7 制約 4 の逐語**を確認 → ★ **別計測器の稼働条件のみを拘束**している
- [x] Windows 昇格プロセスの穴が **既記録**であることを確認（★ 新発見として報告しない）

## 成果物

- [x] `docs/architecture/workspace-behavior-observation.md` §9.4 / §9.5 / §9.6 を追記
- [x] `§8` 表の 7 行目と `§9.2` に到達点のポインタを追記
- [x] `docs/adr/ADR-016-nonkeystroke-interval-handling-in-o1.md`（**Proposed**）
- [x] `docs/adr/README.md` の一覧と「一体で読む」注記
- [x] `docs/agent-shared.md` のリンクハブ（ADR-001〜014 → 001〜016）
- [x] `.steering/20260823-o1-nonkeystroke-gap-and-prereg/preregistration-draft.md`（⚠️ **未凍結**）
- [x] `requirement.md` / `design.md` / `decisions.md`

## 検査

- [x] ⚠️ **実装していない**（`src-tauri/` / `src/` / schema / `HMM_VERSION` に触れていない）
- [x] ⚠️ **凍結物を 1 文字も変えていない**
- [x] ⚠️ **禁止語 grep** の結果を記録

## 追加実施（★ 研究者の指示により本タスク内で実施）

- [x] ★ 研究者判断 **1 / 2 / 3 / 5** を確定（ADR-016）
- [x] ★ **前提 1**: 同時稼働の実機確認 —— ✅ **Windows 実測**（2 プロセスで計数完全一致）／⚠️ **macOS 未確認**
- [x] ★ **前提 2 / 3**: 同意文書ドラフト（二重記録・録画の重なりを明示）
- [x] ★ 3D / 動画編集への「適応」= **head を足さず宣言経路だけ確保**（ADR-016 D7）
- [x] ★ **計測器のゲート分割**の設計（ADR-016 D8）
- [x] ⚠️ **G1 の「変えられない」の線を訂正**（配布形なので repo 変更は届かない・D-16）
- [x] ★ O1 全体の完了状況・問題・残タスクを棚卸し（★ すべて実測で確認）
- [x] ★ **次セッションの引き継ぎを作成** → `.steering/_handoff/next-session-prompt-o1-instrument-and-deletion-ui.md`

## ⚠️ 残（★ 本タスクの外 = 次セッション）

> ★ 引き継ぎ: `.steering/_handoff/next-session-prompt-o1-instrument-and-deletion-ui.md`

- [ ] ⚠️★★★ **研究者判断 4 のみ未確定**（`creative` の意味と宣言 UI の文言）→ 埋まるまで ADR-016 は **Proposed**
- [ ] ⚠️★★★ **区間指定削除 UI の実装** —— ★ **無いまま収集を始めると倫理審査を不要とした根拠 3 が崩れる**
- [ ] ⚠️ **`data-privacy` Skill の拡張**（区間指定削除 ＋ 非打鍵チャネル）—— ★ 同意文書の配布前提
- [ ] ⚠️ **同意文書の研究者レビュー・承認**（⚠️ 承認まで配布しない）
- [ ] ⚠️ 事前登録ドラフトの **未凍結 5 項目**（`preregistration-draft.md §12`）
- [ ] ⚠️★★★ **計器の実装（R3-a）＋ ゲート分割** —— ⚠️ **着手前に ADR-014 判断 4 へ「配布境界」を追記する**
      （★ **D-16 により「G1 の収集完了待ち」の前提が変わった**。⚠️ 記録せずに実装を始めない）
- [ ] ⚠️★★★ **macOS の同時稼働 probe**（実機が要る）／⚠️ **実入力 probe の取り直し**
- [ ] ⚠️ **Windows 昇格プロセスの実機確認**を O1 の開始前チェックに載せる
- [ ] ⚠️ **`is_typing_key` の両 OS 対テスト**（★ 現在 0 件）
- [ ] ⚠️ 6 段階 ablation の事前宣言 —— ★ **n と検出力の算術が未了**
- [ ] ⚠️ **G1 の募集・収集**（★ 確証標本 **0/3 名**・`results/` 空）—— ★ **O1 の *開始* はここが律速**
