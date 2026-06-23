# intervention-response-capture (Phase A2: Wall 介入応答の NDJSON 捕捉)

## 背景

`roadmap-xy.md` §2 の支配原則 = **「捕捉(capture) は 算出(analysis) より前」**。
パイロットで録り損ねた信号は永久に失われる (捕捉の不可逆性)。

現状コードで確認したギャップ:
- **Wall の応答が NDJSON に記録されていない**。`wall_server.rs` の `/unlock` ハンドラは
  `tracing::info!` のみで `LogEntry` を logger に送っていない。
- Nudge dismiss は capture-schema-freeze (PR #18) で捕捉済 (`InterventionResponse` + `DismissReason`)。
  しかし **Wall の早期解除 (⏸/early-unlock) / 通常解除 (2分完走=順守) / タイマー満了** は未捕捉。
- 設計書は **⏸押下数を「GSE 思想の実証データ」= 独立指標**と明記 (`roadmap-xy.md` A2)。
  これを録らずにパイロットを回すと Y 受容の主要行動指標が不可逆に失われる。

`intervention_decision` (action=wall) で **Wall 提示**は既に捕捉済。本タスクは **応答**を閉じる。

## ゴール

Wall の **早期解除 / 通常解除 / タイマー満了** が NDJSON に
**カテゴリ + タイムスタンプ (+経過時間 ms)** で content-free に記録され、
後段で「順守 (2分やり切った) vs 早期離脱」が算出可能になること。

## スコープ

### 含むもの — Wall 応答の NDJSON 捕捉
- `wall_server.rs` の `/unlock` 経路で介入応答イベントを logger に送る (現状 tracing のみ)。
  - 早期解除 / 通常解除 / タイマー満了 (自動) を区別。
- `InterventionResponse` を action=wall に拡張 or 新 variant (要承認①, /reimagine 検討)。
  記録は **カテゴリ + タイムスタンプ + 経過時間 (ms) のみ** (content-free)。
- schema 同期: `schema_dto.rs` 変更 → `emit_schema` 再生成 + gse-dataset parity 必須。
  `HMM_VERSION` は不変 (features 不触)。

### 含まないもの
- (a)(b) 指標算出への組み込み (outcome-metrics 側の別タスク。本タスクは捕捉のみ)。
- Zen Timer / Monk Mode / Early Unlock の挙動変更 (記録の追加のみ・UX 不変)。
- Nudge dismiss の再設計 (capture-freeze で完了済)。`silent` 自動送出 (CD7 で将来)。
- Physical Anchor / 散歩 (Phase E)。anonymize/package パイプライン (Phase C)。
- features/HMM・engine の変更 (`--snapshot` byte-equal を保つ)。

## 受け入れ条件

- [ ] Wall の早期解除 / 通常解除 / タイマー満了が NDJSON にカテゴリ+タイムスタンプ(+経過時間)で記録される
- [ ] `gse-replay` が新 NDJSON をパースでき、旧 NDJSON でも panic しない。`--snapshot` byte-equal
- [ ] `emit_schema` parity 緑 (schema 同期完了)。`cargo test --workspace` 緑
- [ ] NDJSON に数値/カテゴリのみ・本文非混入。code-reviewer/security-checker/cross-review で CRITICAL/HIGH なし

## 関連ドキュメント

- `roadmap-xy.md` §2 (支配原則) / §3 Phase A (A2)
- `.steering/20260623-capture-schema-freeze/decisions.md` (CD3 Wall 後置 / CD4 後方互換 / CD7 silent / CD9 IPC 純粋関数化)
- `docs/development-guidelines.md` §3 (Replay-as-Truth) / §9 (schema drift) / §10 (data repo)
- `docs/functional-design.md` (介入 UC)
- Skill: `intervention-design` / `data-privacy` / `architecture-rules` / `rust-standards`

## 運用メモ
- /reimagine 適用: Yes (イベント表現の設計判断①が複数案・公開 schema を定義するため)
- 理由: handoff §「要承認の設計判断」①が (i) 既存 InterventionResponse 拡張 vs (ii) 専用 WallResponse 新設の
  2案で最良案が自明でなく、NDJSON schema = 外部インターフェースを定義するため。
