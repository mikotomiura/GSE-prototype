# 重要な設計判断

## 判断 1: Loop Engineering は Wave 0 にのみ適用し、Wave 1 には適用しない

- **判断日時**: 2026-09-11
- **背景**: `.idea/` の SSOT 化を issue 単位の自律ループで回せるかを判定する必要があった。
  当初は「文書タスクなので AC を exit code で言えない → Loop Engineering 不適」と判断したが、
  取り込み（intake）と新規裁定（promotion）で性質が異なることが調査で判明した。
- **選択肢**:
  - A: 全体を Loop Engineering で回す（モード C の無人実行を含む）
  - B: 全体を通常タスクとして回す（Loop Engineering を使わない）
  - C: Wave 0（取り込み）のみ Loop Engineering、Wave 1（新規裁定）は人が承認する
- **採用**: C
- **理由**:
  - `issue-slicing` 基準 4 は「AC は exit code か test 名で言える。AC↔test マッピングが空の
    issue は issue ではない」と規定する。
  - **Wave 0 は満たす**。取り込みは「既に書かれたものを移す」作業であり、
    `cargo test` / `gse-replay --snapshot` / `emit_schema` parity / `check_doc_lexicon.py` /
    `check_citations.py` / `secrets-filter-test.sh` で全系統の AC を機械回収できる。
  - **Wave 1 は満たさない**。「ADR-029 の裁定内容が正しい」を検証する手段が存在しない。
    `docs/loop-engineering.md` が言うモード C の客観性は「verify の exit code から events を作る」
    ことに依存しており、ここに文書裁定を流すと**中身が空でも緑になる**ループを量産する。
- **トレードオフ**: Wave 1 では自動化の恩恵を捨て、人のレビューがボトルネックになる。
  代わりに `check_doc_lexicon.py` / `check_citations.py` を**衛生条件**としてのみ AC に載せ、
  「正しさ」は `/cross-review`（Codex + code-reviewer の独立レビュー）で担保する。
- **影響範囲**: `_issue-plan.md` の verify_level 割当。Wave 0 の issue は `recheck` を含むが、
  Wave 1 の issue は機械 AC が衛生条件に限られるため、人の承認を Done 条件に明記する。
- **見直しタイミング**: Wave 1 の裁定を機械検証できる仕組み（例: ADR の Decision 節と
  実装の対応を検査する lint）が生まれたら再検討する。

## 判断 2: 取り込みは案 C（系統ごとに PR を割る）を採る

- **判断日時**: 2026-09-11
- **背景**: 未マージブランチ `feat/resumption-outcome-arbitration` が 200 files / +26,924 / −1,707 と
  巨大で、`.steering/_handoff/next-session-prompt-intake-windows-and-continue.md §2` が
  「研究者に諮ること」として案 A/B/C を用意していた。案 B（Windows 実測ぶん）は既に完了済み。
- **選択肢**:
  - A: PR 1 本で丸ごとマージ
  - B: Windows 実測ぶんだけ cherry-pick（**完了済み**）
  - C: 系統ごとに PR を割る（ADR / metrics / 表現層 / ツール / 実測）
- **採用**: C
- **理由**:
  - handoff 自身が案 A を「28k 行を 1 度に入れる。**レビューの粒度がゼロになる**」と警告している。
  - `metrics.rs` の識別子改名（`recovery` → `pflow_exit`）は `HMM_VERSION` bump の要否と
    ゴールデン再生成の判断を伴うため、**コード変更とドキュメントを同一 PR に混ぜるべきでない**。
  - 系統ごとに AC が異なる（`cargo test` / `check_doc_lexicon` / `check_citations` /
    `secrets-filter-test`）ので、系統分割がそのまま縦切り issue になる。
- **トレードオフ**: 手間が大きく、依存順序を解く必要がある。
  → 調査で依存関係は判明済み（ADR-023 → 024 が上書き、025 は 023 M9 の分割、
    026 は 021 由来の `PS-Q7` と 025 D1 の取りこぼし、027 は 022 D1 が前提、028 は 027 D6 の `W-3`）。
- **影響範囲**: `docs/adr/README.md` が ADR-023〜028 の全行を含むため 001 と 002 で交差する。
  → **README は 002 が一括で担当し、001 は触らない**（001 単独 merge 時に README が
    不完全になるが、main は壊れない）。
- **見直しタイミング**: 001 の取り込みで golden が割れた場合、`HMM_VERSION` bump の判断が
  必要になり分割方針を見直す（ADR-024 は bump 不要と実測確認済みだが、main 側の変化で崩れうる）。

## 判断 3: 転帰定義の一本化を Wave 1 の最優先に置く

- **判断日時**: 2026-09-11
- **背景**: 転帰の定義が 3 つ並立し（ADR-009 / `metrics.rs` / ADR-024）、
  ADR-009 と ADR-024 で**主従が反転**している（ADR-009 では paste は回復を妨げる競合イベント、
  ADR-024 では paste 自体が主イベント）。両者の関係がどの文書にも書かれていない。
- **選択肢**:
  - A: Wave 1 の最優先に置き、新規 ADR で関係を確定する
  - B: 取り込み後に「番号の大きい方が正」という既存規約で自然に決まるとみなす
  - C: O1 配布直前まで保留する
- **採用**: A
- **理由**:
  - ⚠️ **O1 はまだ開始していない**。ラベル定義が未確定のまま収集を始めると、
    後から定義を選ぶことになり**事後選択**になる。
  - B は成立しない。ADR-009 は Proposed のままであり、ADR-024 が Proposed を上書きしたのか
    別トラックとして並存するのかは番号順では決まらない。
  - C は「先に準備される分析パイプラインがどちらの定義を前提にするか」が死角になる。
- **トレードオフ**: 裁定には研究上の重い判断が要るため、次セッションで `/reimagine` を使う前提とする。
- **影響範囲**: O1 のラベル定義、`metrics.rs` の主指標、分析パイプライン（`gse-replay` の
  セッション横断プール = ADR-024 が `N6: 未実装` と認める残課題）。
- **見直しタイミング**: G1（統制タスク実験・`n = 0/3`）が実施され ADR-009 の反証ゲートが動いたとき。

## 判断 4: O1 配布前に手遅れになる実装 2 件を本タスクに含める

- **判断日時**: 2026-09-11
- **背景**: 調査で「配布後は原理的に復元できない観測」が 4 点見つかった（P1〜P4）。
  当初 `KeyCategory` の `Punctuation` 追加を典型例と想定したが、
  **これは既に main にマージ済み**（`feat/r3-accept-and-punctuation` = `e14b6bd` PR #113）で解消済みだった。
- **選択肢**:
  - A: P1（macOS IME 確定/放棄判別）と P3（修飾キー同時押下フラグ）を本タスクに含める
  - B: P1 のみ
  - C: 調査・起票のみで実装は別タスク
- **採用**: A
- **理由**:
  - P1: `ime_shadow`（変換セッション 1 回分の `dwell_ms` / `nav` / `abandon` 要約）は
    **Windows にしか存在しない**。macOS は `ime_state` の on/active 2 値ポーリングのみで、
    変換が確定で終わったか ESC で放棄されたかを**後から永久に復元できない**。
  - P3: 各キーが独立イベントで「同時押下」フラグが無く、通常打鍵と `Ctrl+Z` を区別できない。
    `revision topology` を主要アウトカムに据えるなら配布前にフラグ追加が要る。
  - どちらも SSOT 化ではなく実装だが、**O1 配布という不可逆な締切**があるため本タスクに含める。
- **トレードオフ**: SSOT 化タスクにコード変更が混ざる。
  → issue を分けて Allowed Files を交差させないことで分離する。
- **影響範囲**: `schema_dto.rs` を変えるなら `emit_schema` parity と `schema/current.json` の
  意図的再生成が要る。両 OS に対のテストを置く（`docs/development-guidelines.md §3`）。
- **見直しタイミング**: O1 の配布スケジュールが確定し、実装が間に合わないと判明したとき
  （その場合は「macOS では IME 確定/放棄を判別しない」ことを**明示的に記録**して配布する）。

## 判断 5: P4（macOS `secure_input` の実送出状況）は blockers へ起票し、本タスクでは実装しない

- **判断日時**: 2026-09-11
- **背景**: `schema_dto.rs` の doc は「2026-08-23 時点で送出元なし（スタブ）」と書くが、
  `observe_macos.rs` は `SECURE_INPUT_AVAILABLE=true` になっている。
- **選択肢**: A: 本タスクに含める / B: blockers に起票して別途処理
- **採用**: B
- **理由**: 確認作業は 5 分程度で、issue の粒度（変更 ≤ 5 ファイル / AC 3〜7 項目）に満たない。
  ただし放置すると「打鍵ゼロ」と「打鍵が見えない」が混ざったデータが本番に紛れ込む。
- **トレードオフ**: 忘れるリスク。→ `blockers.md` に起票し、Wave 0 完了時のチェック項目に入れる。
- **影響範囲**: O1 の macOS データの解釈。
- **見直しタイミング**: O1 配布前の最終確認時。

## 判断 6: 本 grill では `docs/glossary.md` への用語追記を行わない

- **判断日時**: 2026-09-11
- **背景**: `grilling` skill は「確定したドメイン用語はその場で `docs/glossary.md` に inline 追記する
  （揮発させない）」を終了条件に挙げている。
- **選択肢**: A: 今回使った作業語（Wave 0 / Wave 1 等）を追記する / B: 追記しない
- **採用**: B
- **理由**:
  - 本 grill で確定したのは**作業の進め方**であり、ドメイン用語ではない。
    `Wave 0` / `Wave 1` は本タスク限定の作業語で、SSOT に載せるとかえって用語体系を汚す。
  - `Practice Portrait` / `内在的開口` / `計測終端` / `イデオフォン的実践体` などは
    **Wave 1 で SSOT 化する対象**であって、この grill で確定した用語ではない。
    先に glossary へ入れると、裁定前の語を既定事実にしてしまう。
- **トレードオフ**: grill の終了条件を形式的には満たさない。→ 本判断として明示的に記録する。
- **影響範囲**: なし（Wave 1 の該当 issue が glossary 追記を担当する）。
- **見直しタイミング**: Wave 1 の用語整理 issue 実行時。
