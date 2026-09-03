# 検証テスト ランブック (回帰 + 機能 + フォーム)

開発者・研究者向けの **動作検証手順** を一箇所にまとめる。リリース前・PR マージ前・実機配布前に
ここを上から実行する。データ収集パイロットの運用は `docs/calibration-smoke-runbook.md` /
`docs/pilot-runbook.md` を、被験者スモークは `.steering/*/smoke-test-runbook.md` を参照。

- **対象**: macOS 13+ (Apple Silicon) / Windows 11。`analysis/` は OS 非依存、`input/`・overlay は OS 固有。
- **プライバシー**: 検証で生成する NDJSON にもキーストローク**内容**は含まれない (VK コード列のみ)。
  外部 LLM・外部サービスへ NDJSON 生ログを送らない (`data-privacy`)。

---

## 1. 自動検証 (OS 非依存・CI 相当・必須)

`src-tauri/` で実行する。**全部 green でなければ先に進まない。**

> ⚠️ ★ **`~/.cargo/bin/cargo` が動かない環境がある**（2026-08-06 に macOS で実測）。
> `~/.cargo/bin/*` は rustup の shim（symlink）で、`rustup` 本体が消えると**全部 dangling** になり
> `no such file or directory` で落ちる。⚠️ ★ `ls` ではリンクが見えるので**壊れていると気づきにくい**。
> → 実体は `~/.rustup/toolchains/<toolchain>/bin/cargo`。`cargo --version` が通らなければそちらを使う。
> ★ これを踏むと `run.sh` の cargo ゲート 4 本が「飛ばした」と言って**素通り**する。

```bash
cd src-tauri

# (a) 単体・統合テスト
~/.cargo/bin/cargo test --workspace
#   macOS で素早く回すなら: cargo test --lib --target aarch64-apple-darwin

# (b) リプレイ回帰 (背骨): FeatSnapshot 列が byte-equal で一致すること = HMM 不変の証明
~/.cargo/bin/cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson \
  --snapshot tests/snapshots/minimal.json
#   期待: "OK: N snapshots match ..."。差分が出たら HMM 挙動が変わっている。
#   意図的変更なら HMM_VERSION を bump → ゴールデン再生成 → .steering/ に根拠を記録。

# (c) Schema drift 検査 (gse-dataset 整合)
~/.cargo/bin/cargo run --bin emit_schema    # 出力を src-tauri/schema/current.json と byte-equal 比較

# (d) フロント型チェック
cd .. && npx tsc --noEmit

# (e) 整形・lint (任意だが推奨)
cd src-tauri && ~/.cargo/bin/cargo fmt --check && ~/.cargo/bin/cargo clippy --workspace
```

合格条件:
- [ ] `cargo test --workspace` パス
- [ ] `gse-replay --snapshot` が一致 (HMM 不変)
- [ ] `emit_schema` 出力が `schema/current.json` と一致 (drift なし)
- [ ] `tsc --noEmit` エラー 0
- [ ] `cargo fmt --check` クリーン・`clippy` 新規警告なし

---

## 2. macOS 機能検証 (実機・手動)

開発 dev ビルドを**二重 gate** で起動する (デバッグボタン + backend gate)。

```bash
VITE_GSE_DEBUG=1 GSE_DEBUG=1 npm run tauri dev
```

dev ログ NDJSON: `~/Documents/GSE-sessions/gse_*.ndjson`。記録成功は同ファイルに該当エントリが
残ることで客観確認する。

### 2.1 介入カードのクリック受理 + フォーカス非奪取 (v2.22)
1. セッション開始 → Dashboard「プローブを出す」→ 右上のプローブカードが表示される。
2. Q1/Q2 を選び「回答する」を押す → **カードが閉じる** (ボタンが効く)。
3. Dashboard「Nudge を出す」→ Nudge を閉じる → 閉じる。
4. カード表示中に**前面エディタへのタイピングフォーカスが奪われない**こと
   (カードを出したまま別アプリで文字が打てる)。

合格条件:
- [ ] プローブ/Nudge のボタンが**初回クリックで効く** (無反応でない)
- [ ] カード表示中もフォーカスを奪わない (背後アプリで入力継続できる)
- [ ] カード以外の画面領域は背後アプリへ**クリック透過**する (非ブロック)

### 2.2 記録の着地 + 窓反転バグの非回帰 (v2.22)
**起動直後 (5 秒以内)** に「プローブを出す」→「回答する」を試す (旧バグの再現条件)。

合格条件:
- [ ] dev ターミナルに `record_… FAILED` が出ない
- [ ] NDJSON に `realtime_label` が着地する。起動 5s 以内はゼロ幅窓
      (`analysis_window_start_ms == analysis_window_end_ms`)、5s 超は通常窓 (`end > start`)
- [ ] Nudge dismiss で `intervention_response` が着地する

確認例 (NDJSON):
```bash
grep -E '"type":"(realtime_label|intervention_response)"' ~/Documents/GSE-sessions/gse_*.ndjson | tail
```

### ~~2.3 Wall 全画面ブロック (非回帰)~~ — ⚠️★★★ **2026-09-01 削除**

⚠️★★★ **この手順は実行不能である。** Wall・Zen Timer・`wall_server.rs` は
**ADR-015 (2026-08-23) D1 / D2 で全削除**され、`InterventionAction` は
`None / Nudge / Defer` の 3 値になった (実測: `src-tauri/src/analysis/intervention.rs:16-20`)。
★ **発火させる経路が無いので、この節は「必ず落ちる非回帰テスト」として残っていた。**

★ **現行で確認すべき介入は Nudge のみ**であり、§2.2 でカバーされている。
⚠️ **代替の手順を新設していない** —— Physical Anchor は未実装であり、
ADR-018 D1 で完了条件を持たない「方向づけ」に改められたため、
**「解除できるか」という形の検証項目自体が存在しない**。

### 2.4 日本語 IME 合成 (非回帰)
1. 日本語入力でローマ字 → 変換 → 確定を数回行う。
2. 候補ウィンドウ表示中は HMM がポーズする (中間 feat が出ない)。

合格条件:
- [ ] 変換・確定が壊れない (overlay の NSPanel level=Floating が IME をブロックしない)
- [ ] 候補表示中に `force_flow_state` 等のポーズが効く (`hmm-analysis` / メモリ参照)

---

## 3. Windows 機能検証 (実機・手動・差分のみ)

overlay の NSPanel 化は **macOS 限定 gate**。Windows は従来の `set_ignore_cursor_events` 経路。

合格条件:
- [ ] プローブ/Nudge のクリックが効く (`accept_first_mouse` 既定経路)
- [ ] §2.2 と同じく起動直後のプローブ記録が着地する (窓 clamp 修正は OS 非依存)
- [ ] IME (IMM) 合成が非回帰 (⚠️ **旧文の「Wall 全画面ブロック・」は ADR-015 の削除により失効・2026-09-01**)

---

## 4. アンケートフォーム検証 (Google Apps Script)

`Form_Phase1/GSE_Phase1_Form_Builder.gs` を Apps Script エディタに貼り、各関数を実行する。

- `buildForm` … F1 同意・スクリーニング (固定フォーム `FORM_ID`)
- `buildF2` / `buildF3` / `buildF4` … F2-F4 (毎回 `FormApp.create` で新規)
- `buildF5` … F5 事後アンケート (固定フォーム `F5_FORM_ID`)

合格条件:
- [ ] `buildForm` を**2 回以上連続実行**しても `Invalid data updating form` が出ない
      (分岐ナビゲーションを `clearForm` が先に解除してから削除するため)
- [ ] `buildF5` を**単独実行**して事後アンケートが生成される (一括実行で実行時間/クォータに
      当たる場合は単独で回す)
- [ ] F2-B / F5 の GSE-10 項目、F2-C / F5 の `TSE_ITEMS` が pre/post で**完全一致**
      (matched 再測定の前提)
- [ ] 実行ログの編集 URL / 回答 URL を控える

> 注: `buildF2`/`F3`/`F4` は実行ごとに別フォームを量産する設計 (`FormApp.create`)。再実行時は
> 旧フォームを手動で破棄するか、固定 ID 再利用へ寄せる (F1/F5 と同方式)。

---

## 5. トラブルシュート

| 症状 | 切り分け |
|---|---|
| プローブ「記録に失敗」 | dev ターミナルの実 Err を見る。`window_end_ms must be >= window_start_ms` は窓 clamp の回帰 (v2.22 で修正済)。`log channel ...` は logger 経路。 |
| カードのボタン無反応 (macOS) | `capabilities/default.json` の `allow-set-size`/`allow-set-position` を確認。NSPanel 化と Rust 権威 `set_ignore_mouse_events` (overlay_panel.rs)。 |
| 起動時クラッシュ (macOS) | NSPanel 化窓で `maximize()`/`unmaximize()` 禁止 (NSRangeException)。全画面化は明示 `setSize`/`setPosition`。 |
| `Invalid data updating form` | `buildForm` 再実行時の分岐 orphan。`clearForm` 経由で削除しているか確認。 |
| リプレイ snapshot 不一致 | HMM 挙動変更。意図的なら `HMM_VERSION` bump + ゴールデン再生成 + `.steering/` 記録。 |

---

## 関連ドキュメント

- `docs/calibration-smoke-runbook.md` — v0.3 較正スモーク (データ収集・3-5 名)
- `docs/pilot-runbook.md` — M1 パイロット (収集 → 暗号化 → 分析パイプライン)
- `docs/development-guidelines.md` §3 — テスト方針 (Replay-as-Truth)
- `.steering/20260625-macos-overlay-clickthrough-fix/runbook.md` — overlay クリック修正の実機検証
- `.steering/20260627-phase1-1-smoke-verify-closeout/smoke-test-runbook.md` — スモーク検証
