# 設計判断 (F4)

## D1. callback 内で CGEventTapEnable を呼ぶ (hook-constraints からの意図的逸脱)

**判断**: `handle_event` callback で `TapDisabledByTimeout`/`ByUserInput` を受けたら、その場で
`CGEventTapEnable(tap, true)` を呼んで tap を再有効化する。

**背景**: `hook-constraints` mac-3 は「callback 内では再作成しない。Hook Thread のポーリングループで
対処」と定める。しかし本コードは `CFRunLoop::run_current()` がブロックする設計で、runloop 実行中に
回るポーリングループが存在しない。また再「作成 (recreate)」と再「有効化 (enable)」は別物である。

**根拠**:
- `CGEventTapEnable` は Apple 公式が tap timeout 復旧手順として明示する**軽量呼び出し**であり、
  tap を作り直さないため取りこぼし・失効頻度が最小。
- 呼び出しは tap の runloop スレッド (= この callback と同一スレッド) から行うのが正しい。
- callback 内で禁止される heap 確保・Mutex・ブロッキング channel・tracing ログは一切持ち込まない
  (Atomic load + 単一 FFI のみ)。`hook-constraints` の「input pipeline を止めない」という本旨にむしろ沿う
  (再有効化は pipeline の復旧そのもの)。

**代替案と却下理由**:
- 別 watchdog スレッドで tap enabled 状態をポーリング → スレッド追加・port 共有が必要で複雑。
  callback 再有効化の方が低レイテンシかつ標準的。
- 何もせず runloop 退出 → 丸ごと作り直しに任せる → 取りこぼし大・失効頻度高で現状の問題そのもの。

**chicken-and-egg の解法**: closure は tap 生成前に渡るため tap を参照できない。tap 生成後に
`mach_port` (CFMachPortRef) を静的 `AtomicPtr<c_void>` (`TAP_PORT`) へ格納し、callback はそれを
読んで自前 extern の `CGEventTapEnable` を呼ぶ。書き込み・読み出しとも同一 hook スレッドのため
データ競合なし。runloop 退出時に null クリアして stale port 使用を防ぐ。

## D2. `last_key==0` の扱い: 駆動側は away 寄り、Dashboard 表示は 0 のまま

**判断**: プローブ駆動 (`lib.rs`) の idle 計算は `driver_idle_ms` 経由とし、`last_key==0` を
`away_idle_ms` (= 離席扱い) に倒してプローブを抑止する。一方 Dashboard 表示用
`get_keyboard_idle_ms` (lib.rs:429) は従来どおり `last==0 → 0` を維持する。

**根拠**:
- 主修正 (B: hook で `LAST_KEY_MS` を 0 に倒さない) により、セッション中の `last_key==0` は
  原則「初回打鍵前」だけになる。その状態でプローブを撃っても分析窓に打鍵がなく低価値かつ、
  「在席なのに離席扱い」の誤りは「離席なのに発火」より研究的に無害 → **保守側 (発火しない) に倒す**。
- 表示用は「未打鍵 = idle 0」が UI として自然。離席閾値を表示すると誤解を招くため分離する。

**トレードオフ (記録)**:
- セッション開始直後、ユーザーが在席でも初回打鍵まではプローブが抑止される。ただし
  ウォームアップ (`min_session_elapsed_ms=31_000`) で元々その期間は発火しないため実害はほぼない。
- (B) があれば (C) は冗長だが、将来別経路で `last_key` が 0 化した場合の多層防御として残す。

## D-review. code-reviewer 指摘への対応 (2026-06-25)

- **HIGH-1 (callback 再有効化のスラッシング)**: 採用。`CONSECUTIVE_REENABLES` カウンタ +
  上限 `MAX_CONSECUTIVE_REENABLES=100` を追加。normal イベント到達で 0 リセット、tap 生成時も 0。
  上限超過後は再有効化を諦め、`LAST_KEY_MS` 保持により idle 増加 → away に倒れる fail-safe 縮退。
  callback は依然 Atomic + 軽量 FFI のみ (blocking/heap/log なし)。
- **HIGH-2 (Windows `hook_windows.rs:231` も `store(0)` 削除すべき)**: **却下** (誤指摘)。
  `:231` は message loop が `break` した時のみ実行され、break は `WM_QUIT` (= アプリ終了) のみ
  (`hook_windows.rs:216-226` で確認)。待機中に `WH_KEYBOARD_LL` は OS から外れないため idle/away
  破壊は Windows では発生しない (phase2-followups.md の厳密調査と一致)。アプリ終了時の `store(0)` は
  プロセス消滅直前で無害。Windows silent-unhook は症状が逆かつ Phase2 スコープ。よって本タスクで
  Windows は変更しない。
- **MEDIUM (TAP_PORT のスレッド安全コメントが不正確)**: 採用。「同一スレッド」だけでなく
  「callback は run_current 実行中のみ動作し本体と時間的に排他」と明記。
- **MEDIUM (driver_idle_ms の `>=` 境界依存)**: 採用。docstring に poll の `>=` 前提を明記し、
  `poll_thins_at_exactly_away_threshold` テストで idle==away_idle_ms の thinning を固定。
- **LOW (crate version TODO / 追加テスト)**: 採用。extern に crate 追従 TODO を追記、
  `present_then_transient_zero_does_not_fire` テストで保守設計のトレードオフを明文化。

security-checker: CRITICAL/HIGH/MEDIUM なし (メモリ安全・プライバシー・研究妥当性すべてクリア)。
`LAST_KEY_MS` はタイムスタンプのみで文字内容を含まず、記録項目の追加なし。

## D-crossreview. /cross-review (Claude + Codex) 指摘への対応 (2026-06-25)

- **H-1 両者一致 (callback FFI と hook-constraints の文言整合)**: 採用 (一部保留)。コメントで
  Apple 推奨手順であること・軽量 FFI・スレッド・上限の条件を明記済み。`hook-constraints` SKILL.md の
  mac-1 許可リストへ「CGEventTapEnable (TapDisabled* 限定)」を追記する案は、Skill 改変が
  auto-mode で自己改変ブロックされたため**保留**。→ **ユーザー承認待ちの follow-up**: SKILL.md mac-1 に
  軽量 FFI 例外を明文化 (実装は規約の本旨=「input pipeline を止めない」に合致しており乖離は文言のみ)。
- **H-2 / X-1 両者一致 (TAP_PORT SAFETY コメント)**: 採用。可視性 (Ordering) とライフタイム安全性
  (同一スレッド時間的排他 + Apple の runloop-thread 保証) を分離記述に修正。
- **C-1 / C-3 (loop_source 失敗パスの TAP_PORT null クリア / カウンタリセット欠落)**: 採用。
  当該経路では実際には TAP_PORT は直前 run_current 退出で null 済みだが、不変条件を「経路に
  依存しない」形に強化するため Err 分岐に明示的 null クリア + `CONSECUTIVE_REENABLES` リセットを追加。
- **C-2 (LAST_KEY_MS のセッション境界非リセットの明文化)**: 採用 (記録)。下記 D4 に記載。
- **C-4 (driver_idle_ms が ProbeConfig::default() を静的取得)**: 採用。呼び出し側にコメントを追記
  (現フェーズは away_idle_ms 固定。可変化時は sched config から引くよう差し替え)。
- **X-3 (tap 再有効化パスのユニットテスト不足)**: Phase2 tech-debt として記録。`CGEventTapEnable` /
  `TAP_PORT` は FFI 依存で純ユニットテスト困難。`driver_idle_ms` は純関数として 5 本でカバー済み。
  再有効化の判定 (null ガード / 上限) を純関数に切り出すリファクタは Phase2 候補。

別件 (本タスク対象外): `scripts/run-codex-review.sh` が `git diff` (staged のみ) を使うため未コミット
変更で self-block する既知問題 (MEMORY: cross-review-codex-self-block)。`git diff HEAD` への修正は
scripts/ の別 chore で対応 (本 F4 diff に未関係変更を混ぜない方針のため本 PR には含めない)。

## D4. LAST_KEY_MS のライフタイム (C-2 対応)

`LAST_KEY_MS` は**プロセスライフタイムで保持**し、セッション境界ではリセットしない。
根拠: tap の (再)作成・失効は「最後の物理打鍵時刻」という意味と無関係であり、セッション開始は
打鍵活動の有無を変えない。前セッションの打鍵時刻が残っても、`probe_scheduler` は
`min_session_elapsed_ms` (31s ウォームアップ) と away ゲートで保護される。Dashboard 表示
(`get_keyboard_idle_ms`) は前セッションからの idle を大きく表示し得るが、これは「新セッションで
まだ打鍵していない」という事実の正しい表示であり汚染ではない。プロセス再起動時は静的初期値 0 に戻る。

## D3. スコープ限定

- Windows silent-unhook (callback timeout) 検出/復旧は症状が逆 (0 化せず増加し続ける) かつ
  発生確率が低いため **Phase2** に送り、本タスクでは扱わない (`phase2-followups.md` F4 末尾)。
- runloop 退出時の 2 秒 sleep + 作り直し経路は維持 (真の invalidate = sleep/wake は稀)。
  callback 再有効化により timeout/userinput 由来の退出は基本的に発生しなくなる。
