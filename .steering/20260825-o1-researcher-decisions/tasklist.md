# タスクリスト — O1 の研究者判断（2026-08-25）

## 読み込み（★ ゼロから考えない）
- [x] `.steering/_handoff/next-session-prompt-o1-decisions-after-macos.md`（全 257 行）
- [x] `docs/adr/ADR-016-…md` §研究者判断 / D7
- [x] `preregistration-draft.md` §1 / §2 / §4 / §5 / §9 / §11 / §12
- [x] `consent-draft-o1.md`（全文 ＋ dev 向けメモ 7 件）
- [x] `20260823-…-prereg/decisions.md` D-10 / D-11 / D-16
- [x] `20260823-o1-instrument-r3a/decisions.md` D-A / D-J / D-M
- [x] `20260824-o1-macos-instrument/decisions.md`（T1 / 判断 5 / 見送り）
- [x] `workspace-behavior-observation.md` §2.1 / §4.3 / §9.4
- [x] `personalization-and-online-learning.md` §3.3 / §11-7
- [x] Skill `verify-before-claiming`

## 一次資料での実測（★ docs を信じない）
- [x] F1 `task_kind` は必須・enum 制約あり（schema_dto.rs / schema/current.json）
- [x] F2 `record_session_meta` は再呼び出し可（lib.rs）
- [x] F3 `run_replay` が複数宣言 / 複数 session_start で `Err`（replay.rs）
- [x] F4 非 G1 はローテートしない（g1.rs / logger.rs）
- [x] F5 `start_session` 前は入力を捨てる・自動開始は無い（lib.rs）
- [x] F6 `INTERVENTION_ENABLED` 既定 true（lib.rs:102）
- [x] F7 `HMM_VERSION = 0.5.0`（engine.rs:58）
- [x] F8 App.tsx の lock 実体（App.tsx:15-21, 223）
- [x] F9 `KeyCategory` 14 種（anonymize.rs）
- [x] F10 間の分類定数・特徴量窓 30 s（intervention.rs / features.rs）

## 研究者判断（⚠️ dev は決めない）
- [x] 判断 4 — `creative` の意味と宣言 UI に含めるか
- [x] 判断 4b-1 — 宣言の頻度
- [x] 判断 4b-2 — 宣言の粒度
- [x] 判断 4b-3 — 未宣言時の扱い
- [x] O1 の運用形態 (A) 押下あり / (B) 常時収集（★ F5 が暴いた分岐）
- [x] D-3 — O1 中の介入の既定
- [x] D-1 / D-6 — 同意文書 注 A の文言
- [x] D-4 / D-5 — ADR-014 D4 本文への注記
- [x] D-7 — flaky test の起票

## dev が候補を出す（★ 研究者が凍結）
- [x] 未凍結 1 `L_nk`
- [x] 未凍結 2 `Δ` の集合と「動いた」の基準
- [x] 未凍結 4 Decision Episode の下限
- [x] 未凍結 8 NK-6 の床 `K`

## 伝播（⚠️ D-8 の再発防止・3 か所すべて）
- [x] ADR-016（判断 4 / 4b / ステータス = Accepted）＋ `docs/adr/README.md`
- [x] `preregistration-draft.md` §2.2 / §2.5 / §7 / §8 / §9 / §11 / §12 / 改訂履歴
- [x] `consent-draft-o1.md` §2 / §3 注A・注B / §4-3 / §5 / dev メモ
- [x] `.steering/20260825-o1-researcher-decisions/decisions.md`
- [x] ⚠️ ADR-014 D6 の記述訂正 ＋ D8 の上書き ＋ D4 の注記 ＋ `workspace-behavior-observation.md` §4.3 / §9.4（★ F5 と食い違っている）

## 完了処理
- [x] 禁止語 grep（`効果があ|精度が上が|有効性`）
- [ ] §6 完了報告チェックリストを転記して報告
- [ ] やらなかったこと / 落としたものを明示
