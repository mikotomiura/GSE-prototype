# 引き継ぎ: O1 の導入識別子（`o1_install_id`）の実装と v0.1.40 の配布

> 作成 2026-10-07。⚠️ 新セッションは先に `/clear` 済みであること。最初に `CLAUDE.md` の行動規範（`/start-task` → docs 先読み → Skill 参照）を踏む。
> 研究者の目標: **複数端末でも O1 を走らせられるようにして、今日中に配布できる状態にする**。

## 0. 何をするか（1 行）
O1 モードの `meta`(session_start) 行に、導入ごとにランダム生成した 16 桁 hex `o1_install_id` を刻み、新タグ `v0.1.40` で配布する。

## 1. 研究者が決めたこと（2026-10-07）
| 項目 | 決定 |
|---|---|
| O1 の計測期間 | **3 週間/人**（暫定）。下限・解析は最初の 3 週間に揃える／暦日 21 日＋有効日に下限（数値は未決） |
| 複数端末 | **許す。解析で分けるため端末識別子を足す** |
| 開始時期 | **識別子を入れた新タグを切ってから開始する**（v0.1.39 では開始しない） |
| 陳腐化したタスクラベル | **限界として明記・計器は変えない**（ADR-016 4b-3） |
| G2 の「介入判断」 | Nudge 発火可否の割れ方。`p_stuck`(HMM 出力) を既存の発火判定への**読み出しとして**通す。ADR-014 D4b は「新しい非打鍵チャネルを推論へ流さない」の意味と**読む**（解釈であり ADR 改訂ではない・凍結時に再確認） |

## 2. 作業場所と現在の状態
- **worktree**: `/Users/johnd/GSE-prototype-o1-device-id`（ブランチ `feature/o1-install-id`・基点 `origin/main@428a13bd`）。⚠️ **未コミット・未ビルド・未テスト**。
- 実装済み（コンパイルしていない。まず `cargo build` / `cargo test` で通す）:
  - `src-tauri/src/o1.rs`: `INSTALL_ID_LEN` / `is_valid_install_id` / `install_id_from_bytes` / `set_install_id` / `install_id()`（OnceLock）＋単体テスト 2 本
  - `src-tauri/src/submission.rs`: `O1_INSTALL_ID_FILE_NAME`（`~/.gse/o1_install_id`）/ `read_or_create_install_id_at` / `read_or_create_o1_install_id` ＋テスト 4 本（`rand::random::<[u8;8]>()` を使用）
  - `src-tauri/src/lib.rs`: `set_mode` の直後に O1 のときだけ `set_install_id(...)`
  - `src-tauri/src/logger.rs`: `o1_mode_fragment` → 純関数 `o1_meta_fragment(mode, install_id)`。O1 のとき `,"o1_mode":"..","o1_install_id":".."`。⚠️ **この関数のテストはまだ無い**
  - `src-tauri/src/schema_dto.rs`: `o1_install_id: Option<String>`（`skip_serializing_if`）
  - `.steering/20261007-o1-install-id/`（requirement / design / tasklist / decisions。`/start-task` 相当は済んでいる）
- 設計: `.steering/20261007-o1-install-id/design.md`（保存先 `~/.gse/o1_install_id`・ハードウェア由来の値を使わない・非 O1 は byte 不変）。

## 3. 残りの作業（上から順）
1. `cd /Users/johnd/GSE-prototype-o1-device-id/src-tauri && ~/.cargo/bin/cargo build` → 型・import のエラーを直す（`rand` は Cargo.toml に `rand = "0.8"` あり）。
2. **テスト追加**: `logger.rs` に `o1_meta_fragment` の 3 ケース（非 O1 → 空文字列 / O1＋妥当な id → `o1_mode` の直後に `o1_install_id` / O1＋不正な id → `o1_mode` のみ）。`anonymize.rs` に meta の `o1_install_id` が保たれるテスト（既存 `anonymize.rs:454` の隣）。⚠️ 非 O1 の meta 行が従来と byte 一致することの確認（既存ゴールデン・`gse-replay --snapshot`）。
3. **schema**: `cargo run --bin emit_schema` → `src-tauri/schema/current.json` と byte 比較して更新。`scripts/check_schema_parity.py`。⚠️ gse-dataset 側（private・別 repo）の schema 更新が要るか確認（`/finish-task` Step 3）。optional フィールドの additive 追加なので旧ログは通る。
4. `cargo fmt` / `cargo clippy --all-targets` / `cargo test --workspace` を緑に。macOS 手元だけでは Windows の `hook_windows.rs` が検査されない → **CI の両 OS ジョブが本番の検査**（memory: windows-only-code-needs-ci）。
5. **Skill を参照してから確認**: `data-privacy`（識別子の追加。ハードウェア由来でないこと・ADR-013 D6）、`architecture-rules`、`rust-standards`。`/review-changes`（code-reviewer + security-checker 並列）。**`/cross-review` は完了時に必須**（CLAUDE.md・Codex が安全ゲートで止まったら縮退して理由を完了報告に明記）。
6. **ADR-038 を起票**（`docs/adr/`・append-only）: 論点 = (a) ADR-013 D6 は「マシン GUID はフィンガープリント」として禁止 → 乱数由来で導入ごと・`~/.gse` 削除で別値、は D6 に抵触しないという根拠 (b) 限界: `~/.gse` のコピーで同値／OS ユーザーが違うと別値／再導入で別値＝**導入単位であって端末ではない** (c) 複数端末を許す根拠 = G2 の入力汚染（端末 A を離れて B で作業 → A 側で離脱に見える）(d) v0.1.39 以前のログには無い（旧ログは端末を分けられない）。`docs/adr/README.md` に行を足す。`citation-ssot`（ADR も対象）。
7. **同意文書の改訂案**（反映は研究者）: `Form_O1/GSE_O1_Form_Builder.gs` の「▼ 記録するもの」（`o1ConsentFormDescription_`・約 575 行）に「**この端末の導入ごとに作った乱数の識別子（端末や個人を特定する情報ではありません）**」を足す案と、必要なら同意項目（`o1ConsentItemTitles_`）。`.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md` とも揃える。⚠️ **被験者向け文書は契約**。`checkO1Form` 系・`o1_form_builder_test.cjs`・変異テストが緑であること。
8. **版を 0.1.39 → 0.1.40**（`package.json` / `src-tauri/Cargo.toml` / `src-tauri/Cargo.lock` / `src-tauri/tauri.conf.json`。先例コミット `2e1fa0ee`）。G1 は `app_version = 0.1.36` で見分ける契約なので**番号を再利用しない**。
9. コミット → push → PR → CI 緑 → merge（`git-workflow` ルール 6。⚠️ push 拒否時は settings.json の permissions を先に読む）。
10. **タグ `v0.1.40` を切る**（研究者承認のうえ push）→ CI の `build-macos` / `build-windows` / `release` 成功を確認。
11. **配布物を作る**: `cd experiments/20260801-controlled-friction-task && bash make-common-app-zip.sh --mode o1 --tag v0.1.40 --config "$REPO/Form_O1/o1_submit.json"`（⚠️ `--tag` と `--config` は必ず明示）。SHA-256・サイズ・byte 一致（Release の資産と `cmp`）を `docs/o1-distribution-tag.md` に **v0.1.40 の節として追記**（過去の節は書き換えない）。
12. **研究者の作業**（私はできない・または承認が要る）: Drive の `O1_実施用_*.zip` を v0.1.40 に差し替え（置き先フォルダは v0.1.39 と同じ・旧版は残さない）／O1 の Apps Script に `GSE_O1_Form_Builder.gs` を貼って `migrateO1ConsentForm()` を実行（⚠️ **zip の差し替えと同時かその後**）／O1 事前登録の凍結。
13. **実機で確かめる**（可能なら）: O1 モードで起動して `~/Documents/GSE-sessions/gse_o1_*.ndjson` の 1 行目に `"o1_install_id":"<16桁hex>"` が出ること、再起動で同じ値、`~/.gse/o1_install_id` を消すと別の値になること。**NDJSON は 8〜12 秒待たないと 0 件に見える**（memory）。非 O1（G1/通常）では出ないこと（陰性対照）。

## 4. 並行して残っているもの（別トラック・同じ日でなくてよい）
- **O1 の事前登録の草案**: `/Users/johnd/GSE-prototype/.steering/20261007-o1-preregistration-draft/preregistration-draft.md`（第 0 版・未コミット・主チェックアウト `docs/ime-m12-mac-conditions` ブランチ上）。残る【決】: 3-c（有効日の定義と下限・`left_observation` 本数の下限）/ 3-d / 6-b（ε・全員一致）/ 2-a（Δ の候補値）/ 8-a / 10-a / 1-a / **12-a（v0.1.39 で複数台が走った人の扱い。今回 v0.1.40 から開始なら不要になる見込み）**。✅ 草案 §12 に「複数端末は識別子で分ける・v0.1.39 には無い」と書いてある → v0.1.40 開始に合わせて**書き換える**（識別子で分ける前提・欠損時の規則）。§4 の必須検査に「`o1_install_id` が全 meta にあること／無ければ停止か警告か」を足す案。
- `docs/o1-distribution-tag.md`（主チェックアウトで追記済み・未コミット）: v0.1.39 の Drive 配置の確認（サイズ一致・SHA 未照合）。
- 主チェックアウトの未コミット: 上記 2 ファイル + `.steering/20260926-g1-o1-mac-collection-prep/drafts/03-o1-preregistration-skeleton.md`（§9 に「3 週間」追記）+ `.steering/20261007-o1-preregistration-draft/`。コミット前に `git branch --show-current`（memory: parallel-sessions-share-checkout）。
- G1 は別軌道（収集開始ゲート 26/26 通過・3 人目の登録と `status` 表記の整合が残る）。**G1 の配布物は v0.1.36 固定のまま**（ADR-034 D3）。v0.1.40 は `--mode o1` のみ。

## 5. 注意（踏みやすい穴）
- ⚠️ **`--mode o1` のタグは `docs/o1-distribution-tag.md` の最新節以外を使わない**。
- ⚠️ 識別子を足したことで `schema/current.json` が変わる → **gse-dataset 側の schema 同期が要るか**を確認（`CLAUDE.md` の data repo 連携節）。
- ⚠️ **ハードウェア由来の値を使わない**（ADR-013 D6）。乱数・`~/.gse`・O1 のときだけ作る（G1 / 通常運用の端末に何も残さない）。
- ⚠️ 2 台を許す運用でも、**参加者 ID は人単位のまま**（削除台帳 `docs/o1-deletion-ledger.md` は P-ID 単位）。端末ごとの削除要求の経路は未設計 → ADR-038 に「P-ID 単位で全端末ぶん」と書く案。
- ⚠️ 受け口は同名・同サイズでも重複を保存する（`GSE_O1_Submit.gs:343-351`）。2 台の `.age` がファイル名で衝突しないかを `reconcile.rs` / `packaging.rs` で確認（ブロック番号は端末ごとのディスクの最大値＋1 なので**端末間で同番号になりうる**。⚠️ 要確認・未確認）。
- 研究者への質問は `AskUserQuestion` で行う（本セッションの依頼）。

## 6. 一次資料
`docs/adr/ADR-014`（D4b / D4c / D9）/ `ADR-013`（D1 / D6）/ `ADR-016`（4b-3）/ `ADR-034`（D3 / D4 / D5 / Migration 6）/ `ADR-037` / `docs/o1-distribution-tag.md` / `docs/o1-roster-operations.md` / `src-tauri/src/analysis/intervention.rs:252-253`（`need_score = p_stuck`）/ `Form_O1/GSE_O1_Form_Builder.gs`（`o1ConsentFormDescription_`・`buildO1PostSurveyForm` の「別の端末」設問）。
