# 通知メールのレスポンシブHTML化（スマホ/PC両対応）

## 背景・要件
F1 適格提出時に自動送信される通知メール（`f1EmailBody_`）はプレーンテキスト＋スペースインデントで、
スマホのプロポーショナルフォントでは崩れて見える。スマホ/PC 両方で綺麗に表示したい（ユーザー指示）。

## 実装
- `f1EmailHtml_(pid, formUrls)` を新規追加。
  - **max-width:600px + インライン CSS のみ**（メールクライアントは `<style>`/外部CSS/メディアクエリを
    制限するため）。スマホは画面幅に追従、PC は中央600px。
  - 濃紺ヘッダ / P-ID 強調ボックス / アンケートはカード+青ボタン / コマンドは折り返しコードブロック
    (`white-space:pre-wrap;word-break:break-all`) / Dropbox・リンク集もボタン化 / フッタ。
  - `esc()` で HTML エスケープ。`APP_DOWNLOAD_INFO` は各行 trim して `<br>` 連結。
- `f1EmailBody_`（プレーンテキスト）は **`{htmlBody:}` 未対応クライアント向けフォールバック**として維持。
- `onF1Submit`: `urls` を変数化し、`MailApp.sendEmail`/`GmailApp.createDraft` に
  `body`(text) + `{ htmlBody: html }` を渡す。

## 統合（旧 PR #52 を包含）
F2/F4 配布短縮URLを正本フォームを指す新URL（`x.gd/m3q89`/`x.gd/3qba4`）に更新。これにより本PR1つで
「メールHTML化＋新URL」が揃うため、URL差し替えのみの PR #52 はクローズする。

## 検証
- `node --check` 構文 parse 成功。
- scratchpad に P001 展開のプレビューHTML生成（ブラウザ確認）。
- 実レンダリングの最終確認は `AUTO_SEND=false` で下書きを作り Gmail スマホ/PC で確認（推奨）。
