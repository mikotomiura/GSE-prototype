# タスクリスト

## Step 1 — 読む（★ 引き継ぎ §2 の順で）

- [x] `.idea/20260819-user-validation-workspace-behavior-and-mhd.md` 全文（190 行）
- [x] `docs/adr/ADR-012-nonkeystroke-observation-formative-track.md` D1〜D12 ＋ Alternatives / Consequences / Migration
- [x] `docs/adr/ADR-008-online-learning-boundary.md` D1〜D8 全文
- [x] `docs/adr/ADR-010-task-scope-gating.md` 全文
- [x] `docs/adr/ADR-006-task-kind-beta-wiring.md`（⚠️ 引き継ぎのファイル名は誤り・D-14）Decision / 下位決定 / 実施記録
- [x] `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md` D2 / D7（★ G2 落下時の入口表を含む）
- [x] `docs/adr/ADR-013-collection-self-description.md` D6 / Alternatives
- [x] `docs/architecture/personalization-and-online-learning.md` §1.3 / §3.6 / §4.2–§4.6 / §5.2 / §10 / §11
- [x] `docs/architecture/domain-adapter-boundary.md` §Adapter A/B/C / §Layer 2
- [x] `.steering/20260819-nonkeystroke-observation-space/requirement.md` / `decisions.md`（D-0〜D-13）
- [x] 既存引き継ぎ 2 本（別計測器 / Stage 0）
- [x] `docs/research-positioning.md §5`（★ **読むだけ・変更しない**）
- [x] `experiments/20260801-controlled-friction-task/consent.md`（★ 同意の粒度を裁くために追加で読んだ）

## Step 2 — 突き合わせ表（★ 一次成果物）

- [x] メモ §0〜§9 の**全節**を 4 列で表にする（`triage.md §A`・全 42 行）
- [x] 4 値（既決=一致 / 既決=却下 / ⚠️ 衝突 / 空）で仕分ける
- [x] 集計を出す（★ 既決=一致 27 / 既決=却下 2 / 衝突 6 / 空 9）

## Step 3 — 引き継ぎ §3 の表を検証

- [x] 12 行すべてを一次資料（ADR 本文）に当てる
- [x] ⚠️ **誤り 2 件**（B-13 存在しないファイル名 / B-14「どの ADR も扱っていない」）
- [x] ⚠️ **不正確 3 件**（B-5 理由が古い / B-7 要約が不完全 / B-9 参照番号 D2→D3）
- [x] ★ **補正 4 件**を足す（常時収集は衝突 / 役割カテゴリは順序 / §5 層表は 6 行とも既決 / 分割条件の差分は「日」1 つ）

## Step 4 — 空いている所だけ議論

- [x] **論点 1（常時収集レジーム）** → ★ **3/4 閉じた**。⚠️ 同意の粒度は研究者判断
- [x] **論点 2（L-d）** → ⚠️ **閉じない**（★ 後半は既決だった。前半は Stage 0 が律速）
- [x] **論点 3（`z_shared` / 評価 6 段階）** → ★ **2/3 閉じた**（(c) ablation の事前宣言は A-Q3 が掛かる）
- [x] **論点 4（`domain_posterior` / `externalization_likelihood`）** → ★ **閉じた**（3 件とも既決へ吸収）
- [x] **論点 5（§9 の残り）** → ★ **解消**（独立の論点ではなかった）

## Step 5 — 出口

- [x] `triage.md` を確定（⚠️ 必須の出口）
- [x] `docs/adr/ADR-014-continuous-natural-work-collection.md` を **Proposed** で起草
- [x] `docs/adr/README.md` に索引行 ＋ 一体で読む注記
- [x] `docs/glossary.md` に 3 語（収集レジーム / 常時収集 (R3) / 参照チャネル）
- [x] `.idea` 末尾に「2026-08-21 追記」（★ **本文は書き換えない**）
- [x] `.steering/` に requirement / design / tasklist / decisions

## Step 6 — 検証（★ 「変えていないこと」の証明）

- [x] `git status --short` に `src-tauri/` が出ない
- [x] 禁止語 grep（`効果があ` / `精度が上が` / `有効性`）が利得の意味で 0 件
- [x] `docs/research-positioning.md` の差分ゼロ
- [x] ADR-009 / 010 / 012 / 013 の差分ゼロ
- [x] ADR-014 が参照するファイル名がすべて実在する

## ⚠️ やらなかったこと（★ 意図的）

- [ ] ~~`src-tauri/` の実装~~ → ⚠️ **計器は 2026-08-21 に凍結**
- [ ] ~~別計測器の実装~~ → ★ `_handoff/next-session-prompt-nonkeystroke-instrument-build.md` の担当
- [ ] ~~`data-privacy` Skill の改訂~~ → ★ **必要性の確認に留めた**（ADR-012 §Consequences「改訂は別タスク」）
- [ ] ~~ADR-009 / 010 / 012 への追記~~ → ★ **既決に吸収されたので参照で足りる**（D-13）
- [ ] ~~`docs/research-positioning.md §5` の変更~~ → ⚠️ **研究者確認が要る節**

## Step 7 — ⚠️ 追加（研究者指摘 2026-08-21/22）

### 7a. 非打鍵チャネルの要否（D-15）
- [x] 実測で確認（NDJSON 行種 / `left_observation` 実装 / WinEventHook の購読範囲 / `starved_ms` のマウス込み）
- [x] ADR-014 D4 を撤回・改訂（D4 / D4b / D4c / D4d）
- [x] `triage.md §C-1` / `decisions.md` D-15 / `.idea` / `glossary` / `README` を追随

### 7b. 打鍵の「内容」の扱い（D-16）
- [x] 実測で確認（`logger.rs:1382` が全打鍵 VK を記録 / `is_typing_key` が修飾キーを除外）
- [x] `boundary keys` が **★★★ 採用（弁別の前提条件）** であることを確認（[P121]）
- [x] ADR-014 **D4e** を追加（★ R3 は logger 境界で VK をカテゴリへ量子化）
- [x] ⚠️ `consent.md` の文言と実装粒度のずれを **研究者判断 6** として申し送り

### 7c. ★ Rust で取れる入力信号のサーヴェイ（★ 研究者が subagent 活用を明示指示）
- [x] repo 側の確定事実を先に固める（`survey-input-channels.md §1`）—— 既取得 / 未取得 / **feature フラグの現状**
- [x] Windows: ポインタ・打鍵・スクロール（subagent）
- [x] Windows: フォーカス・システム状態・クリップボード・境界（subagent）
- [x] macOS: ポインタ・打鍵・スクロール（subagent）
- [x] macOS: フォーカス・システム状態・クリップボード・配布制約（subagent）
- [x] ⚠️ 両 OS の差を `§4` にまとめ、**対のテストが要る箇所**を特定する（★ 8 件）
- [x] ★ 結果を **ADR-014 D4 の候補表（R3 の段 1）** に反映（⚠️ **凍結は研究者承認後**・Migration 3）
- [x] ⚠️★★★ サーヴェイ中に見つかった**既存計器の欠陥 2 件**を `findings-instrument-defects.md` に記録

⚠️★★★ **サーヴェイが答えるべきは 3 問**（`survey-input-channels.md §0`）:
**(1) 識別子なしで遷移時刻だけ取れるか / (2) 座標なしでポインタ量だけ取れるか /
(3) アイドル時間をキーボードとマウスで分離できるか。**
