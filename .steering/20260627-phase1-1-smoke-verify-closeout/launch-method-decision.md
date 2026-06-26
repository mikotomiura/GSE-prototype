# 被験者の起動方法（advice.md issue 2）

## 問題
キーストローク動態を OS フックで取得する Tauri アプリを、技術レベル不明の
パイロット被験者 2-3 名に確実に起動させたい。**Apple Developer 証明書なし**、
CI は ad-hoc 署名（`APPLE_SIGNING_IDENTITY="-"`、ci.yml:133）のみ。

## 候補
| 案 | 内容 | 摩擦 | 外的妥当性 |
|---|---|---|---|
| A | CI 本番バイナリ配布（macOS=ad-hoc dmg / Win=nsis） | 中（Gatekeeper/SmartScreen 回避＋権限付与） | 高（release ＝本番と同一の TCC/パス文脈） |
| B | git clone + `npm run tauri dev` | 高（Rust/Node/Xcode CLT 導入） | 低（dev は release 固有の TCC/権限を検証できない） |
| C | 研究者が初回セットアップ（権限付与・ログ確認まで）を同席/遠隔で代行 | 低（被験者は以後起動のみ） | 高 |

## 推奨: **A ＋ C を標準運用**（codex consult と一致・2026-06-25）
- 配布も本番検証も **A（CI 本番バイナリ）**。理由: #1 最有力原因（macOS Documents/TCC で
  `File::create` 失敗）は **本番 .app でこそ顕在化**するため、本番で fail-loud の効果を検証できる。
  盲検は `VITE_GSE_DEBUG` 既定 OFF で起動方法に依存せず守られる（バイナリに焼かれない）。
- 被験者 2-3 名と小規模なので **初回だけ研究者同席（C）** が現実解。Gatekeeper 回避・
  Input Monitoring 付与・再起動・**fail-loud バナーが OK であることの確認**まで研究者が見届ける。
  C は A の代替ではなく **A のリスク軽減策**として使う。
- **B はデバッグ用に限定**。被験者起動の本線にはしない（環境構築の敷居＋外的妥当性が低い）。

## codex が指摘した盲点（follow-up 候補・本タスクでは未実装）
1. **初回起動セルフチェック**: 「権限OK / hook 受信OK / ログ書込OK / 残容量OK」を一括判定し、
   失敗時は研究者に送れる診断コードを表示。← A の真のリスクは「インストール成功」ではなく
   「権限付与後に正しく動いている証明」。
2. **ログ全損対策は `File::create` だけでは不足**: ディスク満杯・権限変更・スリープ復帰・
   ローテーション失敗・書込途中クラッシュ・排他競合。追記成功カウンタ / flush・fsync 方針 /
   heartbeat / 最終書込時刻の UI 表示 / 起動時の前回異常終了検出 を検討。
3. **盲検の非 env 漏洩経路**: UI 文言・ログファイル名・通知・メニュー・プロセス名・設定ファイル・
   配布ファイル名から条件が推測されうる。Week1/2 を同一バイナリ・同一起動導線にする。
4. **検討外オプション**: 研究用 Mac 貸与 / 事前セットアップ済み端末 / 短期 Apple Developer 証明書取得 /
   Windows 先行パイロット。

## 決定（ユーザー確定・2026-06-25）
- **起動方法 = A＋C で確定**。CI 本番バイナリ配布＋初回研究者同席。
- **codex の follow-up（#1 self-check / #2 fsync・heartbeat・異常終了検出）= Phase2 送り**（記録のみ）。
  → `phase2-followups.md` 参照。Phase1 配布は現状の fail-loud 修正で進める。
- macOS Gatekeeper 回避は初回研究者同席（C）で完結させる方針（被験者に xattr 操作を強いない）。
