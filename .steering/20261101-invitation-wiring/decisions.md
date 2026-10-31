# 設計判断

## 判断 1: 研究者の決定（2026-11-01・AskUserQuestion）

- 通常のモードの第 2 週だけ招待を出す（第 1 週は出さない・10-31 の決定）。
- 契機は研究者の設定ファイルで選ぶ。既定は今の挙動。
- 無作為の頻度は値を注入する。既定値を置かない。

## 判断 2: 実装の後の研究者の決定（2026-11-01・AskUserQuestion）

- 通常のモードで本人が招待を止めた後に戻す道: 招待が許されたセッション（第 2 週）の間だけ、トレイに「印の説明と設定」を出す。
- `invitation_condition` 行は区間削除で消さない（`session_meta` と同じ・ADR-031 D6 決定 3）。参加者向けの文書と data-privacy Skill には「消しても残る行」の一覧が無く、足していない。同意文書に一覧があるなら足すかは研究者が決める。
- 無作為の契機の seed: 設定の seed とセッションの開始時刻から導き、乱数は秒の番号から引く（全員・全セッションで同じ予定表にならないように・記録から立つ時刻を再現できるように）。設定の seed と導いた seed の両方を記録する。

## 判断 3: 未決として残すもの（研究者の決定・2026-11-01）

- 説明と設定の窓（`InvitationSettings.tsx`）は「作業が進みにくくなっているかもしれない時間がしばらく続いたとき」と説明している。既定の契機（推定器）では事実と合うが、無作為・なし・上がりの契機では合わず、そのまま使うと説明の偽りになる。今は変えない。無作為・なしを実際に使う前に、説明の文と同意の扱い（盲検にするか）を事前登録と合流で決める。
- 通常のモードの同意文書に `invitation_present`・`invitation_condition` が載っているかは repo で確かめられていない。
- gse-dataset の schema parity（`invitation_condition` の追加）は別作業。

## 判断 4: レビューへの対応（code-reviewer・security-checker・/cross-review・2026-11-01）

- HIGH なし。EH3 の挙動は変わっていない（3 本とも確認）。
- 採った: セッションの終了で許可と提示を下ろす（Claude と Codex が同じ事実）／NaN で上がりの履歴を捨てる（Codex）／`window_ms`・`hold_ms` の上限（Codex・security-checker）／無作為の seed と秒の引き方（code-reviewer・Codex・研究者の決定は判断 2）／設定ファイルと replay の入力の上限（security-checker）／設定の保存を O1・G1 以外で常に受ける（security-checker・本人の統制）／トレイの差し込みの失敗の警告・replay の欠けた p_stuck を Err・複数行の doc（code-reviewer）。
- 採らない: 設定ファイルが無いとき推定器の既定で第 2 週に招待が出るのは、10-31 の決定（契機の既定は今の挙動）どおり。通常のモードで設定の窓を常に作るのは design §3 のまま（WebView が 1 枚増える点は CPU の計測の課題に渡す）。
- Codex の消費は 34,806（1 回）。Codex に送ったのは Rust の主対象 5 本で、replay.rs・logger.rs・schema は Claude の 2 本だけが見た。

## 判断 5: /cross-review 2 巡目への対応（修正の範囲 `3fc908cf..HEAD`・2026-11-01）

- HIGH なし。EH3 の後始末は EH3 を変えない（`close_normal_invitation` は EH3 で先に戻る）。本人の設定を越えて出す経路は無い。
- 採った: M1（両者一致・MEDIUM）許可を立てる前に世代を進める順に直した（`lib.rs` の `record_session_meta`）。
- doc で限った: replay は最初の宣言以降だけ実機と一致する（再宣言の作り直しは再現しない・Codex C2）／`feat` 行の欠けが離席候補からの再開をまたぐと、無作為の引く秒の数が実機と違いうる（Claude L1）／遡った区間の当たりは最初の 1 つだけ（Codex C1）。`invitation_trigger.rs` の `replay_recorded` の doc に書いた。
- 採らない: 設定ファイルの差し替えの競合（Codex C3）は、`~/.gse` に書ける主体がファイルそのものを書き換えられるので脅威の外。G1 の自動終了で `SESSION_START_MS` が 0 に戻る点（L2）は通常のモードを通らない。
- 検証（メインが回した）: `cargo test --workspace` 1054 passed・0 failed、clippy `-D warnings` 0。
- Codex の消費: 2 巡目で worktree の台帳の今日が 69,660 / 2 回（1 巡目 34,806 と 2 巡目 34,854）。
