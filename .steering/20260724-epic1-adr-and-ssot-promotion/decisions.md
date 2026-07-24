# decisions — Epic 1

## D1: worktree で main ベースの branch を作った（GAS 作業の温存）
現在地 `feature/phase1-reminder-and-dashboard` は未コミットの GAS フォーム作業が乗り main より 11 遅れ。
tracked 3 ファイルが main と差分 = `checkout -b origin/main` は "would be overwritten" で失敗する。
→ `git worktree add -b docs/post-phase1-epic1 <path> origin/main` で clean な main ベース branch を作成し、
現作業ツリー（18 未コミットエントリ）を一切触れず温存。Epic 1 は docs のみでこの分離が最も安全。

## D2: Phase1 未完だが Epic 1 に着手（研究者承認済み）
Phase1 はデータ収集未完（pilot GATE2 FAIL・リマインド未デプロイ）。roadmap は「Phase1 完了+承認」を課すが、
Epic 1 はコード変更ゼロ・凍結対象非接触で物理干渉しない。研究者（ユーザー）が 2026-07-24 に着手承認。

## D3: 改善設計書は「コピー」でなく「昇格」— Epic0 実態を刻む
設計書 v0.1 の思想を保ちつつ、Epic 0 で確定した実装状況（◎/○/△/記録/✗）と「エビデンスの温度」を各 docs に反映。
特に Need/Opportunity 分離・none/defer・cooldown 群・Monk Mode=介入拒否は**既に実装済み**であることを明記
（「新規実装でなく整理が主」）。

## D4: ★ADR-006 = Alternative C（分離）を研究者採択（2026-07-24）
現行 β 選択は `ime_open` 切替で task_kind 非配線（engine.rs で実測確認・task_kind は analysis/ に 0 件）。
IME 状態は β 選択だけでなく backspace ペナルティも gate（engine.rs:367）＝ within-writing の意味を持つ。
→ 二者択一（配線 A / 現状維持 B）でなく **C: task_kind→head 選択・β は head 所有・IME→within-writing 信号の分離**を
**研究者が採択**（2026-07-24・"Cにしますか"）。A/B は単一 HMM 内の β 切替入力を変えるだけで Phase2 混在時に交絡が戻るのに対し、
C は宣言(task_kind)と観測(IME)を直交させ Phase1 挙動を包含。日本語 IME 信号は Writing head 内に温存＝dataset 公開と両立。
- **実装は Phase1 完了後**（凍結 HMM_VERSION・task_kind 定数で検証データ無し）。抽出(2a・no bump)/配線(2b・bump)の 2 段階。
- **下位2点は未決**（Epic 2 Phase 2b 直前で決めれば足りる）: #2 IME off 日本語論述の β 扱い、#3 Creative/VibeCoding の baseline。
- ADR-006 に具体化（match ルーティング・β_coding 移行論点・2a/2b 境界）を追記済み。ステータス Deferred→Accepted(枠組み C)。

## D5: エビデンス過大主張の防止を各 docs に構造化
- 実証支持: none/defer 第一級 [V43]・Motivation Generator 非標準実装 [P21][V40]・Gate D は prior [V41][V42]。
- 未検証（効果主張しない）: Session Context（[V43] は自己申告が受容性を予測しない逆風）・Accountability・
  Agentic 過信 proxy。→ covariate / 倫理ゲート / feasibility の枠に限定。
- 機会保存 vs 学習効果の分離: [P12]Kapur は「守るべき困難の存在根拠」に限定（[P27][P28]）。
引用は既存 [Pn]/[Vn] を指すのみ（citation-ssot の append-only を守り新規登録しない）。

## D6: ステータス設計
決定可 = ADR-001/004/007（Accepted）。方向合意 = ADR-002/005（Proposed）。
境界のみ合意・採否保留 = ADR-003（Proposed・採否 Deferred）。最優先論点 = ADR-006（Deferred・研究者判断）。

## D7: 既存 docs は書き換えず新規追加のみ
architecture.md / research-positioning.md / functional-design.md 本体は不変。旧技術設計の置換は「方針」として
overview/ADR に記し、README・本体書き換えは研究者承認後の別タスク（Phase1 完了後）。
