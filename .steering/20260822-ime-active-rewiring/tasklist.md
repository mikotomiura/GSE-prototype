# タスクリスト

## 準備
- [x] git merge 状態の確認 (main = f8f2b90 = PR #110、origin と 0/0、未マージ無し)
- [x] handoff §1.3「済んでいること」3 件を実ファイルで検証 (記憶ではなく一次資料)
- [x] `hook-constraints` Skill を参照 (Win-1: コールバック内は Atomic + try_send のみ)
- [x] 配線の非対称をソースで確認
      (`hook_windows.rs:219/260` だけが `IME_ACTIVE` を書く / `:512` が nav の唯一の入口)

## §A 計測 (★ §B を gate する)
- [x] `is_ime_candidate_window_visible` を `pub` へ (可視性のみ・`input/ime.rs` から再エクスポート)
- [x] プローブに問い 3 (EnumWindows 経路) を追加 — 25ms 実測 + 100ms 本番相当の間引き
- [x] プローブに診断用クラス名センサスを追加 (⚠️ クラス名のみ・タイトル/PID は取らない)
- [x] `cargo build --example ime_winevent_probe` 緑 (exit 0)
- [x] ⚠️★★★ **実機で 60 秒 × 2 回走らせた** (2 回目は候補リストを意図的に開く手順)
- [x] 追加計測: 絞り込み無しの可視窓センサス + 窓レベル CREATE/SHOW/HIDE のクラス名
- [x] ⚠️★★★ **判定: 立ち上がり 0/600 (本番相当) → B は不成立**
- [x] ⚠️★★★ **自己訂正: UIA 経路を測っていなかった** → プローブに本番の完全な述語
      `is_candidate_window_open()` を追加し 3 回目を実測
- [x] ★★★ **UIA の寄与 = 0** (「本番 true かつ EnumWindows false」が 0 回)
      → ⚠️ **3 経路すべて閉じ、B 不成立が確定**
- [x] ⚠️ 3 回目で初出の一過性窓 (`Xaml_WindowedPopupClass` 5/600) を評価
      → ★ 滞在 500ms で候補窓の滞在を表さず、かつクラス名が IME 固有でない (誤検知源) → **結論不変**

## §B 配線 — ⚠️★★★ **実施しない (§A で gate が閉じた)**
- [x] ~~`lib.rs` IME Monitor の配線~~ → ⚠️ **不成立**。handoff §2.1 の gate に従い着手しない
- [x] `capabilities` の `ime_shadow` 区分 → ★ **`config_gated` 据え置き** (PR #110 の判断を追認)
- [x] `capabilities.rs` の doc に EnumWindows 追試の結果を追記 (★ 再試行を防ぐ)

## テスト
- [x] `cargo test --workspace` 緑 — **exit 0** / 441 + 29 + 1 passed, 0 failed
- [x] ゴールデン byte-equal — **exit 0** / `OK: 15 snapshots match`
- [x] `emit_schema` == `schema/current.json` — **byte-equal** / parity **exit 0**
- [x] ⚠️ ~~実起動ログの `ime_shadow` 行~~ → ★ **該当なし** (配線しないので 0 行のまま。これが正しい状態)

## レビュー
- [x] code-reviewer + security-checker を**並列起動** (2026-08-22)
- [x] **HIGH 2 件を修正**:
  - [x] `cargo fmt --all -- --check` が 4 ハンクで落ちていた → `cargo fmt --all` 適用・**exit 0**
  - [x] `capabilities.rs` の doc が実測より強い断定 (`verify-before-claiming` 違反)
        → ★ cloak/uncloak の対立仮説を明記し、**両説で結論が変わらない**形へ書き直し
- [x] **MEDIUM 4 件を修正**:
  - [x] ⚠️ クラス名が**プロセス名を含みうる** (WPF `HwndWrapper[<exe>;;<GUID>]` / WinForms)
        → `normalize_class_name()` を追加し、doc の前提を訂正
  - [x] `SetWinEventHook` 失敗時に exit 0 で返していた → **成功分を unhook し `Err` を返す**
        (★ null 結果を根拠にするツールで「測れなかった」と「測って 0」を終了コードで分ける)
  - [x] `GetClassNameW` の失敗を**無言で捨てていた** → `N_CLASS_UNAVAIL` を追加して結果に出す
  - [x] センサスが窓単位で数え凡例と矛盾 (`Chrome_WidgetWin_1 4800/600`) → **1 ポーリング内で重複排除**
- [x] **LOW**: clippy `is_multiple_of` / 診断B の `looks_ime_like` をタグ付きキーに掛けていた不具合 /
      Mutex 中毒と空の出し分け / ポーリング滑りの検出 / 限界の明記 / `ime.rs` 再エクスポートの誤用警告
- [x] ⚠️ **`anyhow::Result` への変更提案は却下** —— ★ 本 repo は **anyhow を依存に持たない**
      (`overlay_panel.rs:40` / `bin/replay.rs:323` 逐語)。`std::io::Error::other` で代替
- [x] **`/cross-review` (Codex 独立レビュー) を実施** — exit 0
      (⚠️ `run-codex-review.sh -- <paths>` でソース 4 ファイルに限定。
      ★ `findings-*.md` は**端末環境の実データ**なので外部 LLM へ渡していない)
- [x] **Codex が単独で見つけた指摘 4 件を修正** (★ 他 2 レビューアは見つけていない):
  - [x] ⚠️★★★ **高**: `N_CLASS_UNAVAIL` を診断A/診断B で**共用**しており意味が混ざっていた
        → `N_EVENT_CLASS_UNAVAIL` / `N_CENSUS_CLASS_UNAVAIL` へ分離
  - [x] ⚠️ **高**: 「取りこぼし無し / 必ず捕まる」が過剰主張 → 「取りこぼしにくい」＋限界を明記
  - [x] **中**: 正規化は WPF/WinForms 限定で万能ではない
        → ★ **出力はローカル専用**であり共有前にレビューする旨を doc に明記
  - [x] **テスト不足**: `normalize_class_name` の単体テスト 4 件を追加
        (`cargo test --example ime_winevent_probe` で **4 passed**)
  - [x] ⚠️ **中 (MSRV)** は**該当なし**と判定 —— ★ repo に MSRV 宣言は無く
        (`rust-toolchain*` / `rust-version` とも不在)、toolchain は **1.94.1**。
        ★ `is_multiple_of` が既に ≥1.87 を要求しており `Error::other` (1.74) は制約にならない
  - [x] **低**: `#[doc(hidden)]` を再エクスポートに付与 (★ 公開 API ではなく診断用の出口と示す)

## 最終ゲート (★ 全部実測 exit code)
- [x] `cargo fmt --all -- --check` — **0**
- [x] `cargo test --workspace` — **0** / 441 passed, 0 failed
- [x] `cargo test --example ime_winevent_probe` — **0** / 4 passed
- [x] `cargo clippy --all-targets` — **0** / ⚠️ 変更 4 ファイルの警告 **0 件**
- [x] ゴールデン byte-equal — **0** / `OK: 15 snapshots match`
- [x] `emit_schema` vs `schema/current.json` — **byte-equal**
- [x] `check_schema_parity.py --dataset /c/gse-dataset` — **0**

## 0x8030 (ConversionTargetChanged) — ★ **見送り確定**
- [x] `accevent.exe` を試すも ⚠️ **UIA イベント側の設定**で MSAA WinEvent を見ておらず不成立
- [x] ★ プローブを **UIA クライアントへ格上げ** (`ElementFromHandle` + Text/TextEdit パターン要求)
- [x] ⚠️ 自己訂正 2 件: パターンを**フレームで数えていた** / **入力の有無を出力していなかった**
- [x] ★ 入力の証拠を **`WH_KEYBOARD_LL` の打鍵計数**へ変更 (⚠️ UIA イベントはアプリ依存で誤判定した)
- [x] ★★★ **有効計測: 打鍵 282 / TextEdit 240/240 / CONV_TARGET = 0** → ⚠️ **見送り確定**
- [x] ★ `capabilities` は**変更しない** (記録仕様は 1 バイトも変わらない)

## §C 議論 (★ B の後)
- [ ] `triage.md` / ADR-014 / `survey-input-channels.md` / `decisions.md` を読む
- [ ] ADR-014 の研究者判断 6 件
- [ ] R3 の段 1 凍結 (ADR-014 Migration 3)
- [ ] `triage.md §D` の閉じなかった 4 件

## ドキュメント
- [x] ⚠️★★★ ~~意味が変わったこと~~ → ★ **該当なし** (配線しないので意味は変わっていない)
- [x] `findings-enumwindows-probe.md` に実測を記録 (★ 自分の誤読の訂正も含む)
- [x] decisions.md に判断 3 件を記録

## 完了処理
- [ ] design.md の最終化
- [ ] git commit (⚠️ `.claude/settings.json` / `.gitignore` は**含めない**)
