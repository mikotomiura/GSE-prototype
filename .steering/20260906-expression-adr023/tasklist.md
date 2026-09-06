# タスクリスト — expression-adr023

## 段 0: 準備
- [x] `CLAUDE.md` / `docs/agent-shared.md` を読む（★ セッション開始時に自動）
- [x] `/start-task` で `.steering/20260906-expression-adr023/` を作成
- [x] `citation-ssot` / `verify-before-claiming` / `literature-card` Skill を Read
- [x] SSOT を読む: `expression-channel.md` §5/§7/§8 ＋ ADR-017/018/020/021/022 README
- [x] 前タスクの判断 (i) ＋ 精緻化 ＋ §RQ-A〜E を Read
- [x] ★ **一次で裏取り**: `metrics.rs` / `intervention.rs` / `observe.rs` / 技術設計書 / `research-positioning.md`
      → ★ **訂正 1 件 ＋ 発見 2 件**（`decisions.md`）

## 段 1: サーヴェイ 1 ラウンド
- [x] サブエージェント 5 系統を並列起動（RQ α/β/γ/δ ＋ 一次取得）
- [x] RQ α 完了（★ 理解度 × 行動変化の個人内関連）
- [x] RQ β 完了（★ `self_recovery_without_paste` の粒度）
- [x] RQ γ 完了（★ 純アンビエント × 行動指標・Kluckner 2013）
- [x] RQ δ 完了（★ 触覚を含む三感覚統合 / A16）
- [x] 一次取得 5 件 完了（Tiefenbeck 2019 / Buçinca 2021 / [P307][P310][P311] の DOI）
- [x] ★★★ **メインが直列で照合**: 全候補の key を `references.md` の既存行と突合（★ 重複検出）
- [x] ★★★ **メインが直列で採番・append**: `[P317]-` / `[V137]-`（⚠️ **subagent に編集させない**）
- [x] `docs/literature/20260906-*.md` にカード（落合 6 項目）
- [x] `docs/literature/_index.md` に 1 行追記
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` を **「違反なし」まで**繰り返す
- [ ] ★ サーヴェイを **1 コミット**にする（⚠️ 複数ラウンド同居を避ける）

## 段 2: ADR-023 の起票
- [x] `docs/adr/ADR-023-*.md` を新規作成（Context / Decision / Alternatives / Consequences / Migration）
- [x] D1–D12 を記述（★ サーヴェイ結果で増減）
- [x] ⚠️★★★ **留保 9 件**を漏れなく書く
- [x] ⚠️★★★ **「主張してはいけないこと」9 件**を「却下した主張」節に書く
- [x] ★ 各断定に **一次の典拠 `[Pn]`/`[Vn]` か repo の `file:line`** を付ける
- [x] `docs/adr/README.md` の一覧に 1 行追記
- [x] ⚠️ SSOT の訂正（★ **一次で裏が取れたものに限る**）—— ★ **4 件実施**:
      **[P307]**（⚠️ URL が *別論文* を指していた → `hdl.handle.net` で実測確認して訂正）／
      **[P310]**（⚠️ 同上 ＋ DOI `10.21785/icad2019.048` を Crossref で確定）／
      **[P311]**（DOI `10.1117/12.587254`・vol.5669・pp.146–157 を確定）／
      **[P127]**（★ 一次全文を再取得して数値を精密化）
      ⚠️★★★ **加えて [P334] / [P335] を `active` → `provisional` へ降格**（★ 本文未取得・`code-reviewer` 指摘）

## 段 3: 検証とレビュー
- [x] `git status` で `src-tauri/` を触っていないことを確認（★ 予測しない）
- [x] `cargo test --workspace`（★ **実際に走らせた** —— ⚠️ 予測していない）
      ★ **結果（2026-09-06・`src-tauri/` から実行）**:
      | 検査 | 結果 |
      |---|---|
      | `cargo test --workspace` | ★ **583 テスト / 0 失敗**（36.31 秒） |
      | `gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` | ★ **15 snapshots match** |
      | `emit_schema` → `schema/current.json` の byte-equal 比較 | ★ **差分なし** |
      ★ ドキュメントのみの変更なので想定どおりだが、⚠️ **走らせて確認した**（`verify-before-claiming` ルール 5）。
- [ ] `code-reviewer` + `security-checker` を **並列**起動
- [ ] `/cross-review`（⚠️ **パス限定**: `bash scripts/run-codex-review.sh -- docs/adr/ADR-023-*.md .steering/20260906-expression-adr023/`）
- [ ] ⚠️★★★ **HIGH 指摘を本タスクで消化**（backlog へ punt しない）
- [ ] `/finish-task`

## ⚠️ サーヴェイ後に判断すること（★ 段 1 の結果を見てから）
- [ ] RQ α の結果を受けて **判断 (i) の立て方を維持するか / 但し書きを足すか**
- [ ] RQ β の結果を受けて **`self_recovery_without_paste` の新しい指標名**を決める
- [ ] RQ γ の結果を受けて **[P314] への留保**を強めるか
- [ ] RQ δ の結果を受けて **A16（媒体不変性）を受け入れ観点に足すか**
- [ ] ⚠️★★★ **「招待を届ける媒体 = 最悪の代替課題」の温度**（★ 現状 `PLAUSIBLE BUT UNPROVEN`）

## ⚠️ 次セッションへ送るもの（★ 本タスクではやらない）
- [ ] ★★★ **中断 → 再開の観測を `experiments/` として設計**（★ 既存 O1 データで回せる・WoZ 不要）
      ⚠️ **設計時に必ず**: 離席候補と `FOCUS_TX` を別アームにする
- [ ] ★ **Writing / Coding 間の一般化テスト**（判断 (h)・新規データ収集ゼロ）
- [ ] ⚠️ **「慣れているか（習慣化）」を扱うか**（★ 扱うなら ADR-020 に当たる）
- [ ] ★ `experiments/20260902-expression-layerA-visual/notes.md` に位置づけの変更を書く
      （★ 設計は不変・「合否」→「操作チェック」）
- [ ] ⚠️★★★ **機会保存指標の `p_flow` 依存の是正**（★ コード変更を伴うので別タスク）
