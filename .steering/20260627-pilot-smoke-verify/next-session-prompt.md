# 次セッション用 開始プロンプト（パイロット投入前 統合実機スモーク：アプリ v2.22+F4 ＋ Google Form 被験者自動化）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> **実装ではなく検証フェーズ**。コード修正は原則しない（バグが出たら別途 follow-up を切る）。
> `.steering/20260627-pilot-smoke-verify/` に合否と発見した不具合を記録する。実機操作はユーザー（研究者）。
> エージェントは手順提示・ログ解析（log-analyzer）・不具合切り分け・修正提案を担う。

## 0. 一言ゴール
パイロット (n=3-5) 投入前の **最終実機スモーク**。対象は (A) macOS/Windows アプリの v2.22+F4 修正、
(B) Google Form の被験者管理自動化（F1 提出→P-ID 自動発番→自動メール→同意/NDA→管理シート）。
すべて**コードはマージ/実装済み**。残りは「本番ビルド／実フォームでの動作確認」だけ。

## 1. ここまでの確定事実（git で裏取り済み・触らない）
現 main HEAD は version **0.1.21**。以下は **すべて main にマージ済み**：
- **PR #37**（overlay クリック受理 NSPanel 化＋capability＋窓反転=記録失敗 修正, v2.22）
- **PR #36**（macOS CGEventTap 失効時の idle/away 誤リセット＋ランダムプローブ誤発火 修正, F4）
- **PR #39**（v2.22 検証ランブック＋`buildForm` の clearForm 冪等修正）
- **PR #40-45**（F3 廃止／F5 出典／管理シート／Dropbox 配線／P-ID 連番採番／version 0.1.21）

★ **未マージ＝今回検証で要デプロイ**: ブランチ `feature/participant-mgmt-automation`（5コミット）。
  F1 提出トリガでの **P-ID 自動発番＋通知メール自動送信(AUTO_SEND=true)**、**F1 同意拡充＋F1内NDA記名署名**、
  通知メールの**アンケート手順＋公開リンク集**、管理シートの **NDA署名列／進捗ダッシュボード／refreshRosterStatus**。
  → **このブランチを main へマージ（or レビュー後 PR）し、最新 `Form_Phase1/GSE_Phase1_Form_Builder.gs` を
     Apps Script エディタへ貼り直してから** Form スモークを行うこと。

## 2. ★今回やること（検証のみ）

### A. アプリ実機スモーク（macOS 主・Windows 差分）
単一起点 = `docs/verification-runbook.md`（§1 自動 / §2 macOS / §3 Windows / §4 Form / §5 trouble）と
`.steering/20260627-phase1-1-smoke-verify-closeout/smoke-test-runbook.md`。
- 本番ビルドで起動（`open` は env を渡さないのでバイナリ直起動）:
  ```bash
  VITE_GSE_DEBUG=1 npm run tauri build
  GSE_DEBUG=1 "src-tauri/target/release/bundle/macos/<App>.app/Contents/MacOS/<bin>"
  ```
- v2.22（PR#37）重点: §2.3 Wall 全画面ブロック→QR→Zen Timer→unlock の full flow（NSPanel 化で
  maximize 禁止 D8、setSize/setPosition で全画面・クラッシュ無）／§2.4 日本語 IME 合成非回帰（panel level=Floating）／
  §2.2 起動 5s 以内・以降の両方で プローブ→回答→`realtime_label` 着地（5s 以内はゼロ幅窓 start==end）。
- F4（PR#36）重点: **長時間 Idle で idle カウンタが 0 に戻らない**こと、離席（3分以上 idle）中に
  **ランダムプローブが誤発火しない**こと、`hook_macos.rs` の "CGEventTap CFRunLoop exited" warn が減ること。
  （デバッグは時間がかかるので、必要なら `away_idle_ms` を一時短縮した検証ビルドで確認し本番値へ戻す）。
- Windows 差分: overlay は `set_ignore_cursor_events` 経路（NSPanel は macOS gate）。クリック・記録着地・Wall・IMM 非回帰。

### B. Google Form 被験者自動化スモーク（★今回の主眼・新規）
**前提**: 上記 feature ブランチを反映した最新 .gs を Apps Script に貼り済みにする。
1. **既存フォーム修正の非回帰**（A の旧 §C）: `buildForm` を 2 回連続実行して `Invalid data updating form`
   が出ない（clearForm 効果）。`buildF5` 単独実行で事後アンケート生成。F2-B/F5 の GSE-10 と F2-C/F5 の
   `TSE_ITEMS` が pre/post で byte 一致（matched 再測定の前提）。
2. **トリガ設定**: `installF1Trigger()` を実行 → トリガが **「フォームから・フォーム送信時」** で付く
   （時間ベースは NG。`e` が無く即 return する）。初回は Gmail 送信＋Spreadsheet＋Forms スコープを承認。
3. **適格ドライラン（自分のメールで F1 提出）**: 自動で
   (a) ロスターに新規行＋P-ID、(b) condition=baseline、(c) **NDA署名=署名済(F1)**（F1 内記名署名）、
   (d) 本人へ**自動メール送信**（P-ID＋アプリ手順＋F2/F4/F5 回答 URL＋公開リンク集）が届く、を確認。
4. **冪等性**: 同じメールで再提出 → 発番・メールされずスキップ（実行ログ `♻️ 既発番のためスキップ`）。
5. **不適格スキップ**: IME「いいえ」or OS「その他」or 同意未チェックで提出 → 発番されない（`⛔ 適格外`）。
6. **管理シート集計**: F2/F4/F5 にテスト回答 → `refreshRosterStatus()` → ロスターの F2事前/セッション数/
   F4回答(計)/F5事後 と「進捗ダッシュボード」（NDA署名済率・MNAR 無回答フラグ）が更新される。
7. **メール本文の配布情報**: `APP_DOWNLOAD_INFO` を実配布先に書き換え済みか。**公開リンク集
   (`PUBLIC_LINKS_URL`) は PII（実名↔P-ID 対応表）を含まず閲覧専用**であることを最終確認（管理シートとは別物）。

## 3. 参照（先に読む）
- `docs/verification-runbook.md` … アプリ検証の単一起点。
- `.steering/20260627-phase1-1-smoke-verify-closeout/smoke-test-runbook.md` … 本番ビルド起動・F4 観点。
- `.steering/20260627-participant-mgmt-automation/decisions.md` … 今回の Form 自動化の設計判断（D1〜D10）。
- `docs/pilot-runbook.md` … 受領→metrics→cross_section と §0/§7 プライバシー。
- メモリ `macos-tap-idle-away-probe-bug.md` / `macos-overlay-clickthrough-bug.md` … 解決済みの単一真実源。

## 4. 制約（厳守）
- 検証フェーズ。コードは原則変更しない。バグは `.steering/` に記録し follow-up を切る。
- 非ブロック維持＋フォーカス非奪取（D12）、panel level=Floating 固定、NSPanel 化窓で maximize/fullscreen 禁止（D8）。
- HMM / `schema_dto.rs` 不変。`winapi`/`println!`/`eprintln!`/`any` 禁止。既存テスト無断削除しない。
- **PII**: 実名/メール↔P-ID 対応表（管理シート/ロスター）は repo 外・研究者のみ・被験者へ共有しない。
  NDJSON 生ログ・キーストローク内容を外部 LLM/クラウドに送らない。公開リンク集はフォーム＋Dropbox URL のみ。
- diff に無関係な未ステージ変更（`.codex/budget.json` 等）を混ぜない（コミットは対象ファイル列挙・`-A` 禁止）。

## 5. 起動時の行動（CLAUDE.md 準拠）
1. このプロンプト＋`docs/verification-runbook.md` を読む。
2. `.steering/20260627-pilot-smoke-verify/` に検証記録（合否・発見不具合）を残す（requirement/tasklist 軽量で可）。
3. まず feature ブランチのマージ要否をユーザーに確認 → 最新 .gs を Apps Script へ反映 → A/B を実施。
4. 実機操作はユーザー。エージェントは手順提示・ログ解析（log-analyzer）・切り分け・修正提案。
