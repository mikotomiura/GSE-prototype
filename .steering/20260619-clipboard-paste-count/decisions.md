# decisions — clipboard-paste-count

## D1: ペースト検出方式 = Ctrl+V/Cmd+V フック検出 (ユーザー承認 2026-06-19)

- **判断**: OS クリップボード API を読まず、既存キーボードフックで Ctrl+V (Win) / Cmd+V (mac)
  を検出する。
- **根拠**: クリップボードの中身に一切触れない = D4 (回数のみ) + data-privacy (中身禁止) と
  最も整合。代替のクリップボード変更監視は中身アクセスの誘惑と権限増を招くため却下。
- **承認**: AskUserQuestion で「Ctrl+V/Cmd+V フック検出 (推奨)」を選択。

## D2: 記録粒度 = 1 ペースト = 1 NDJSON 行 (ユーザー承認 2026-06-19)

- **判断**: `{"type":"paste","t":<ms>}` を 1 ペーストごとに 1 行記録。回数は行数で算出、
  各ペーストの時刻も保持。中身フィールドは作らない。
- **根拠**: 既存 key 行と一貫。指標 #5 (AI 依存度) で時系列分析が可能。
- **却下案**: Atomic 集計 (N 秒ごとの合計回数) は個別タイムスタンプを失うため不採用。
- **承認**: AskUserQuestion で「1ペースト=1行 (推奨)」を選択。

## D3: Windows の Ctrl 状態取得 = GetAsyncKeyState 実状態読み (code-reviewer HIGH 対応)

- **当初案**: `CTRL_DOWN: AtomicBool` を Ctrl の WM_KEYDOWN/UP で追跡。
- **問題 (code-reviewer HIGH×2)**:
  1. WH_KEYBOARD_LL はシステムグローバルで press/release が対で届く保証がない。Ctrl 押下中に
     フォーカスが他アプリへ移り up を取りこぼすと CTRL_DOWN が true で**固着**し、以降の単独 V を
     すべて paste と誤判定する。
  2. 単一フラグのため左右 Ctrl の同時押し/片方離しで状態が壊れる (macOS の per-event flags 読みと
     セマンティクスがずれる)。
- **判断**: 判定の瞬間に `GetAsyncKeyState(VK_CONTROL=0x11)` の最上位ビットで Ctrl 実状態を読む方式に
  変更。CTRL_DOWN Atomic は撤去。
- **根拠**: 固着・左右非対称を同時解消し、macOS の `CGEvent::get_flags()` per-event 読みと検出
  セマンティクスが揃う。GetAsyncKeyState は alloc/lock/blocking を伴わない軽量カーネル読み取りで
  hook-constraints (コールバック内は非ブロッキングのみ) に抵触しない (rust-standards も windows
  crate の例として GetAsyncKeyState を提示)。OS 依存は input/ に閉じたまま (architecture-rules 準拠)。
- メモリ方針 `feedback_tech_debt_now_not_backlog` に従い HIGH を本タスクで消化 (backlog に punt しない)。

## D4: Ctrl+V の V 打鍵は通常キーとしても features に流れ続ける (意図的・据え置き)

- **事実**: Ctrl+V を押すと V(0x56) は既存どおり InputEvent として features に渡り、key 行としても
  記録される。本タスクはこれに加えて paste 行を**追加**するだけ。
- **判断**: V 打鍵を features から除外する変更は行わない (スコープ外・既存挙動維持)。
- **根拠**: 打鍵リズムの真実源 (raw key stream) を歪めない。FeatureExtractor は is_paste を読まないため
  FeatSnapshot は不変 (golden byte-equal 保持)。paste の特徴量利用は別タスク (#5 以降)。

## D5: ペースト回数の OS 間オートリピートバイアス (既知の限界・指標層 #5 で対処)

- **事実**: Ctrl+V/Cmd+V を**長押し**した場合、macOS はフック層で autorepeat を弾く (is_repeat) ため
  1 回計上、Windows は is_repeat=false 固定で全 down を送るため複数計上になる。
- **判断**: 本タスク (記録層) では補正しない。タップ操作 (長押しでない) が通常運用であり、指標 #5 は
  相対比較のため許容範囲。
- **対処**: 指標算出 (#5) 側で OS を考慮するか頻度上限を設ける余地を残す。silent に握り潰さず本書に明記。
- 参考: security-checker は本件を「プライバシー無害な精度上の論点 (LOW)」と評価。

## レビュー結果サマリ (2026-06-19)

- **security-checker**: CRITICAL/HIGH/MEDIUM なし。「クリップボード中身が一切残らない」ことを
  (1) OS クリップボード API 呼び出しゼロ (2) VK+修飾フラグのみで検出 (3) NDJSON は時刻単独
  (4) is_paste は bool でディスク非到達 (5) read-back テストで禁止フィールド非混入を自動検証、
  の 5 点で確証。LOW 2 件はいずれもプライバシー無害。
- **code-reviewer**: HIGH×2 (Windows CTRL_DOWN 固着/非対称) → D3 で解消。MEDIUM (D4/D5) → 本書に記録。
- **/cross-review (Codex)**: jq 未導入のため Codex 系統を skip し Claude 単独レビューへ縮退
  (既知制約: `project_codex_review_needs_jq`)。
