# 次セッション開始プロンプト — Phase A2: 介入応答 (Wall) の NDJSON 捕捉

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> 親ロードマップ: `roadmap-xy.md` §3 Phase A (A2) + §2 支配原則 (捕捉の不可逆性)。
> 先行タスク: capture-schema-freeze (PR #18, CD3 で Wall 応答配線を本タスクに後置) /
> outcome-metrics (PR #19)。両者 main マージ済。
> **新規 `/start-task` で着手。main 基点で別ブランチ・別 PR。main 直コミット禁止。**

## なぜ Phase A2 が次か

`roadmap-xy.md` §2 の支配原則 = **「捕捉(capture) は 算出(analysis) より前」**。パイロットで録り
損ねた信号は永久に失われる。現状を code で確認した結果:

- **Wall の応答が NDJSON に記録されていない**。`wall_server.rs:185` の `/unlock` ハンドラは
  `tracing::info!("unlock signal received")` のみで、`LogEntry` を logger に送っていない。
- Nudge の dismiss は capture-schema-freeze で捕捉済 (`InterventionResponse` + `DismissReason`)。
  しかし **Wall の早期解除 (⏸/early-unlock) / Zen タイマー完走 (順守) / タイマー満了** は未捕捉。
- 設計書は **⏸押下数を「GSE 思想の実証データ」= 独立指標**と明記 (`roadmap-xy.md` A2)。
  これを録らずにパイロットを回すと Y 受容の主要行動指標が不可逆に失われる。

`intervention_decision` (action=wall) で **Wall 提示**は既に捕捉済。本タスクは **応答**を閉じる。

## スコープ

### 含むもの — Wall 応答の NDJSON 捕捉
- `wall_server.rs` の `/unlock` 経路で **介入応答イベントを logger に送る** (現状 tracing のみ)。
  - **早期解除** (タイマー 0:00 前に押下) / **通常解除** (2分完走後) / **タイマー満了**(自動) を区別。
  - これにより「順守 (2分やり切った)」vs「早期離脱」が後段で算出可能になる。
- 既存 `InterventionResponse` variant を **action=wall に拡張**して使うか、新 variant を足すか (要承認①)。
  内容・キーストロークは含めず、**カテゴリ + タイムスタンプ + 経過時間 (ms) のみ** (content-free)。
- schema 同期: `schema_dto.rs` を変えるため **`emit_schema` 再生成 + gse-dataset parity** が必須
  (capture-schema-freeze と同手順)。`HMM_VERSION` は不変 (features 不触)。

### 含まないもの
- (a)(b) 指標算出への組み込み (outcome-metrics 側の別タスク。本タスクは捕捉のみ)。
- Zen Timer / Monk Mode / Early Unlock の**挙動変更** (記録の追加のみ・UX は不変)。
- Nudge dismiss の再設計 (capture-freeze で完了済)。`silent` 自動送出 (CD7 で将来送り)。
- Physical Anchor / 散歩 (Phase E)。anonymize/package パイプライン (Phase C)。
- features/HMM・engine の変更 (`--snapshot` byte-equal を保つ)。

## 要承認の設計判断 (会話承認 — 着手前に詰める)

1. **イベント表現 (新 variant vs 既存拡張・複数案 → `/reimagine` 推奨)**:
   - (i) 既存 `InterventionResponse { action, reason }` を **action=wall** で再利用し、`reason` に
     `early_unlock` / `completed` / `timer_expired` を足す (capture-freeze CD3 の汎用化方針の延長)。
   - (ii) 専用 `WallResponse { kind, elapsed_ms, .. }` を新設し Wall 固有情報 (経過時間等) を持たせる。
   - **トレードオフ**: (i) は schema 追加が enum 値のみで最小・既存解析と一貫。(ii) は経過時間など
     Wall 固有メトリクスを構造化できるが variant 増。**初期推奨は (i) + 経過時間フィールド検討**。
2. **wall_server → logger の配線 (アーキテクチャ・要 `architecture-rules`)**:
   - `wall_server` は HTTP サーバスレッドで現状 logger の `Sender` を持たない。`WallServer` 構築時に
     `mpsc::Sender<LogEntry>` (または既存の送信ハンドル) を渡す設計。`lib.rs` の起動配線を変更。
     **フックコールバックではない**ので I/O 制約は緩いが、ハンドラ内ブロッキングは避ける (try_send)。
3. **「順守」の定義**: 2分タイマー完走 = 順守 / 早期解除 = 非順守、の二値で十分か。タイマー満了後の
   通常解除と早期解除の境界 (0:00 ちょうど) の扱い。
4. **後方互換**: 新フィールド/variant は `Option`/新 enum 値 (capture-freeze CD4 と同方針)。旧 NDJSON・
   旧 fixture のパースを壊さない。`emit_schema` parity 緑。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. `/start-task` で `.steering/[今日]-intervention-response-capture/` 作成 → (variant 設計が重いので
   `/reimagine` 検討) → `/add-feature`。
2. **docs 先読み**: `roadmap-xy.md` §2/§3(A2) / `capture-schema-freeze/decisions.md` (CD3 Wall 後置・
   CD4 後方互換・CD7 silent・CD9 IPC 純粋関数化) / `development-guidelines §3`(Replay-as-Truth)・
   §9(schema drift)・§10(data repo) / `functional-design.md` (介入 UC)。
3. **Skill 参照 (必須)**: `intervention-design` (Wall/Zen/early-unlock の正準仕様) /
   `data-privacy` (記録は数値・カテゴリのみ・本文禁止) / `architecture-rules` (wall_server↔logger 配線・
   レイヤー) / `rust-standards` / schema を変えるので `hook-constraints` は該当箇所のみ。
4. **サブエージェント委譲**: `file-finder`/`impact-analyzer` で `wall_server.rs` の `/unlock` 経路・
   `lib.rs` の WallServer 起動配線・`logger.rs` の `LogEntry`/`InterventionResponse`/送信ハンドル・
   `schema_dto.rs` の `LogEntryDto`/`InterventionResponse`/`DismissReason`・既存 NDJSON fixture を調査。
5. **実装後 `code-reviewer` + `security-checker` を並列** (焦点 = Wall 応答に**本文・キーストローク内容が
   出ず数値/カテゴリのみ**・wall_server の token 認証を壊さない・try_send でブロックしない・後方互換)。
6. **`/cross-review` (Claude ∥ Codex)**: jq 導入済 (`~/.local/bin/jq.exe`) で両系統可。予算/機密ゲートのみ確認。
7. **`/finish-task`**: schema parity check (tier-3 guard) が `schema_dto.rs`/`current.json` 変更を検知し
   gse-dataset との JSON 意味同値を検証する。**drift 検出時は commit せず停止**し修復。

## 前提 (ブランチ — 重要)

- **main は PR #18 (capture-schema-freeze) + #19 (outcome-metrics) マージ済**。更新後 main から
  `feature/intervention-response-capture` 等を切る。**main 直コミットしない・別 PR**。
- 未コミットの `.codex/budget.json` / `MEMO` / `wbs_検証用docs/` はステージしない (作業ツリー据え置き)。

## 検証ゲート

- `cargo test --workspace` 緑 (新 NDJSON variant/フィールドの純粋関数テスト: format_*_line 生成・
  パース後方互換・カテゴリ検証。`wall_server` の応答→LogEntry 変換の単体テスト)。
- **schema parity**: `emit_schema` 出力を `schema/current.json` と byte-equal、gse-dataset parity 緑
  (capture-freeze と同手順)。**今回は schema が変わるので parity は実走必須** (前回の Phase B と違う)。
- **Replay-as-Truth**: `--snapshot` (FeatSnapshot) は features 不触で **byte-equal 不変**のはず。
  新 variant を含む golden fixture を gse-replay が panic せずパースできること (旧 fixture 互換も)。
- 旧 NDJSON (新 variant/フィールド欠落) で gse-replay が panic しない (`#[serde(default)]`/新 enum 値)。
- code-reviewer / security-checker CRITICAL/HIGH なし。`/cross-review` 両系統で HIGH なし。

## 制約

- `tracing`/`anyhow`/`any` 禁止・`winapi` 禁止・`analysis/` は OS 非依存・記録変換は logger 側。
- **NDJSON に介入応答の本文・キーストローク・成果物テキストを一切入れない** (カテゴリ/数値のみ・data-privacy)。
- wall_server の **ランダムトークン認証を壊さない** (data-privacy ルール4)。ハンドラ内は try_send で非ブロッキング。
- `.steering/` 記録を省略しない。`/finish-task` まで完遂。別 PR・main 基点。

## 受け入れ条件

- Wall の早期解除 / 通常解除 / タイマー満了が NDJSON に**カテゴリ + タイムスタンプ (+経過時間)** で記録される。
- `gse-replay` が新 NDJSON をパースでき、旧 NDJSON でも panic しない。`--snapshot` byte-equal。
- `emit_schema` parity 緑 (schema 同期完了)。`cargo test --workspace` 緑。
- NDJSON に数値/カテゴリのみ・本文非混入。code-reviewer/security-checker/cross-review で CRITICAL/HIGH なし。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-phaseA2-intervention-response-capture.md
に従い、Phase A2 (介入応答=Wall の NDJSON 捕捉) を実装してください。capture の不可逆性 (roadmap-xy §2)
により、パイロット前に閉じるべき最後の捕捉ギャップです。

現状: wall_server.rs:185 の /unlock は tracing のみで LogEntry を送っておらず、Wall の早期解除/通常解除/
タイマー満了 (= ⏸/順守、設計書で「GSE 思想の実証データ」) が NDJSON に残っていない。Nudge dismiss は
capture-schema-freeze で捕捉済 (CD3 で Wall 応答配線を本タスクに後置)。

着手前に: main は PR #18 + #19 マージ済。更新後 main から feature/intervention-response-capture を切る
(main 直コミット不可)。/start-task で .steering/[今日]-intervention-response-capture/ を作成 → variant
設計が重いので /reimagine 検討 → /add-feature。roadmap-xy §2/§3(A2)、capture-schema-freeze/decisions.md
(CD3/CD4/CD7/CD9)、development-guidelines §3/§9/§10、functional-design.md(介入 UC) を読む。Skill は
intervention-design / data-privacy / architecture-rules / rust-standards を参照。

スコープ (捕捉のみ): wall_server.rs の /unlock 経路から介入応答 (早期解除/通常解除/タイマー満了) を
logger に送り NDJSON 記録。WallServer 構築時に LogEntry の Sender を渡す配線 (lib.rs)。記録はカテゴリ+
タイムスタンプ(+経過時間 ms)のみ・content-free。schema_dto.rs を変えるため emit_schema 再生成 + gse-dataset
parity 必須。
スコープ外: (a)(b)指標への組込み・Wall/Zen の挙動変更・Physical Anchor/散歩・anonymize/package パイプライン・
features/HMM 変更。

要承認の設計 (会話で承認、①は /reimagine 推奨): ①イベント表現 = 既存 InterventionResponse を action=wall
+ reason(early_unlock/completed/timer_expired) で拡張 か 専用 WallResponse 新設か ②wall_server→logger の
Sender 配線 (HTTP スレッドにブロッキングを持ち込まない try_send) ③「順守」の二値定義 ④新 variant/フィールドは
Option/新 enum 値で後方互換。

CLAUDE.md 準拠で: /start-task → (/reimagine) → /add-feature → 上記 Skill 参照 →
file-finder/impact-analyzer で wall_server.rs(/unlock)・lib.rs(WallServer 起動)・logger.rs(LogEntry/
InterventionResponse/送信ハンドル)・schema_dto.rs(LogEntryDto)・NDJSON fixture を調査 → 実装 →
code-reviewer + security-checker 並列 (焦点=本文非混入・token 認証維持・非ブロッキング・後方互換) →
/cross-review (jq 導入済で Claude∥Codex 両系統可) → finish-task (schema parity 実走必須・drift で停止)。

検証: cargo test --workspace 緑・emit_schema parity 緑 (今回は schema 変更ありで parity 実走必須)・
--snapshot byte-equal (features 不触)・旧 NDJSON(新フィールド欠落)で panic しない・新 variant を含む golden
を gse-replay がパース。制約: tracing/anyhow/any禁止/winapi禁止・wall_server token 認証を壊さない・
NDJSON に本文を入れない(カテゴリ/数値のみ)・.steering 記録必須・別PR・main 基点。
```
