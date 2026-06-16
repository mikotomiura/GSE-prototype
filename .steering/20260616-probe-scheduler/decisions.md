# decisions.md — Task B「backend プローブ scheduler」

## DB-1 スケジューリングは A1「同次 Poisson + rolling thinning」(2026-06-16 ユーザー承認)
- **判断**: 指数間隔(逆変換 `-ln(1-u)/λ`)で次候補を抽選し、gap<8分 / cap≥2件/30分 /
  away(idle≥180s)違反は棄却(thin)して再抽選する。窓ごと一様2点(A2)は採らない。
- **根拠**: 同次 Poisson は count 条件付きで時刻が一様 = 一様ランダムの教科書的生成法で、
  `probe_assignment.scheduled_ts` の実現分布から一様性を監査証明しやすい(D-14 核心要件)。
  idle 除外が「離席中は候補棄却→再抽選」で自然に表現できる。A2 は固定窓境界の comb 構造で
  全体一様性が崩れ、idle 除外を絶対時刻の事前抽選へ組込むとモデル非依存性の監査が濁る。
- **参照**: design.md §設計判断A、handoff「rolling thinning / Poisson 指数間隔」。

## DB-2 スケジューラ駆動は専用ポーリングスレッド(1Hz 解析ループ非干渉)
- **判断**: IME Polling(`ime_windows.rs:205`)と同型の専用スレッドを `setup()` で spawn し、
  `recv_timeout(1000ms)` + sender drop の Disconnected で shutdown。1Hz Analysis Thread には触れない。
- **根拠**: プローブ駆動は emit(AppHandle)と logger 送信(tx)の両方が必要。1Hz Analysis Thread は
  レイテンシ要件があり AppHandle も持たない。責務分離を維持(architecture.md スレッドモデル)。

## DB-3 probe_id は内部生成 newtype(外部 String を受けない)
- **判断**: `ProbeId(String)` を probe_scheduler 内に閉じ、唯一のコンストラクタ
  `ProbeId::generate(&mut rng)` が seeded RNG から `[A-Za-z0-9_-]` 16文字を生成。`uuid` crate は不使用。
- **根拠**: Task A security-checker 申し送り(本文/タイトル由来 ID 混入を型で排除)。seeded RNG なら
  決定論テスト可能。base64url 風アルファベットで data-privacy ルール1(escape 残留)を構造的に回避。

## DB-4 B↔C イベント契約: B が窓を確定し emit に含める
- **判断**: `probe_triggered` payload に `analysis_window_start_ms/end_ms` を含め、C は受領して
  `realtime_label` へ転記する。窓計算(random t−31s..t−1s / self t−35s..t−5s)は B が所有。
- **根拠**: v0.3 §14 の `realtime_label` が窓フィールドを持ち Task A の `realtime_label_answered` も
  窓を引数に取る。窓確定を B に集約するのが schema と整合(handoff base)。

## DB-6 RNG seed を tracing に記録する(一様性監査の再現性・code-reviewer MEDIUM 対応)
- **判断**: 本番スケジューラは `from_entropy` 直挿しでなく、entropy から `u64` seed を引いて
  `from_seed(seed)` で初期化し、seed を `tracing::info!("probe scheduler seed=... session_start=...")`
  に記録する。
- **根拠**: backend が probe 生成を所有する理由は D-14「一様ランダム・モデル非依存を監査証明」する
  ためだが、`from_entropy` だと seed が残らず「この seed でこの scheduled_ts 系列が出た」ことを後から
  再現・検証できない。seed を残せば本番の非決定論と監査再現性を両立できる。
- **scope**: NDJSON schema は Task A で凍結のため seed は **trace ログにのみ** 残す(schema 不変=DB-5 維持)。
  durable な seed 記録(NDJSON へ載せる)が必要なら schema 拡張として Task A 系列で別途扱う。

## DB-7 away 除外は process-global キーボード idle を意図的に使う(code-reviewer MEDIUM 整理)
- **判断**: `idle` は既存 `input::hook::last_key_ms()`(プロセス全体で永続・セッションでリセットしない)
  から計算する。`start_session` で `LAST_KEY_MS` をリセットする変更は **しない**。
- **根拠**: away 除外の目的は「実際にキーボードが無活動な間はプローブを発火しない」こと。process-global
  last_key はまさに実キーボード無活動を表すため、セッション境界をまたいでも除外判定として正しい
  (セッション開始直後に長時間タイプしていなければ、それは実際に idle でありプローブ抑止が妥当)。
  共有 primitive を Task B 都合でリセットすると intervention / dashboard の idle 意味論まで変わり、
  scope 外の cross-subsystem 影響が出る(handoff「新規 idle 検出を作らない・既存再利用」とも整合)。
  `scheduled_ts` / 分析窓 / `session_elapsed_ms` は実時刻ベースで idle に汚染されない。

## DB-8 ウォームアップ guard: 窓がセッション内に収まるまで発火しない(厳密ジャッジ追補)
- **判断**: `ProbeConfig.min_session_elapsed_ms`(既定 31_000ms)を追加し、`session_elapsed < 31s`
  の候補を thinning する。これで分析窓 `[t−31s, t−1s]` の始端が必ず `session_start` 以降になる。
- **根拠**: guard が無いと、セッション開始 31s 以内に発火したプローブの窓が `session_start` を
  下回り、**開始前(drain/idle 期間)の打鍵データが窓に混入**する。較正の核は「クリーンな測定窓」
  であり、混入は Task D の C-index を静かに汚染する。発生確率 ≈ 1−e^(−31/900) ≈ 3.4%/session で
  30–50 session 規模のスモークでは無視できない(各人 ~16–20 件しか要らないため相対的に大きい)。
- **影響**: 既定挙動の変更は「最初の 31s はプローブを出さない」のみで望ましい方向。gap/cap/away の
  既存テストには影響なし(warm-up は冒頭 31s のみ)。新規テスト `no_probe_until_window_fits_in_session`。

## DB-9 self_marker 窓も session_start でクランプ(cross-review: Claude HIGH)
- **判断**: `self_marker_window_clamped(t, session_start)` を追加し、hotkey 経路でも窓始端を
  `session_start` でクランプする(セッション外 `==0` は非クランプ)。
- **根拠**: DB-8 のウォームアップは scheduler(random_probe)にのみ適用され、self_marker hotkey は
  ノーガードだった。開始 35s 以内に M を押すと窓 `[t−35s, t−5s]` が `session_start` を下回り、
  random_probe と同じ混入が起きる。Claude/Codex cross-review で Claude が指摘(Codex は未検出)。
- **テスト**: `self_marker_window_clamped_to_session_start`。

## DB-10 ProbeConfig 健全性 debug_assert(cross-review: Codex MEDIUM)
- **判断**: `ProbeScheduler::new` に `lambda_per_ms` 有限正値・`cap_count≥1` の `debug_assert` を追加。
- **根拠**: 不正設定(0/負/NaN lambda, cap_count=0)で指数間隔が inf/NaN になる、または永久に
  発火しない。本番は `default()` 固定で安全だが、将来の設定注入に対する debug 早期検出。Codex 指摘。

## DB-11 cross-review の不採用/受容判断(根拠付き)
- **post-session firing / SESSION_START_MS 非リセット(両者 HIGH)**: 本アプリに stop_session は無く、
  セッション終了は quit(プロセス終了)のみ→スレッドも die するため発火継続は起こらない。同一 ms 再開始は
  UI 上ほぼ不可能。**現モデルでは実害なし**として受容(将来 stop を足すなら 0 リセット必須と明記)。
- **poll の長時間ギャップ catch-up(Codex HIGH)**: スリープ等の長欠落中の候補は idle≥180s で
  どのみち away thinning される。away 解除直後の候補も away で棄却→再抽選。**away 除外が包含**するため受容。
- **ProbeAssignment に shown_ts が無い(Codex MEDIUM)**: shown/answered は Task C の `realtime_label.ts`
  (probe_id で join)で追える設計。schema は Task A 凍結。**設計どおり**として受容。
- **Task A 不変条件が pub variant で迂回可(Codex HIGH)**: Task A decisions TA-2 で既知・受容済み
  (構築子経由運用 + debug_assert)。merged 範囲につき本タスクでは変更しない。
- **vignette_id の String 受容(Codex MEDIUM)**: Task C の責務(受領 ID を再検証)。申し送り。
- **is_none_or MSRV(Codex LOW)**: 現ツールチェインでコンパイル済(clippy も is_none_or を提案)。
  `rust-version` 未固定。MSRV を固定するなら別途。

## DB-5 schema_dto.rs / current.json は touch しない
- **判断**: logger は Task A で `ProbeAssignment` を既にハンドル済(`logger.rs:780`)。B は producer 配線のみ。
- **根拠**: schema は A で確定。B での schema 変更は不要 → finish-task の tier-3 parity guard に当たらない。
