# 要件: パイロット投入前 統合実機スモーク (アプリ v2.22+F4 ＋ Google Form 被験者自動化)

## 背景
パイロット (n=3-5) 投入前の最終実機スモーク。コードはすべて main にマージ済み。
残りは「本番ビルド／実フォームでの動作確認」のみ。**検証フェーズ — コードは原則変更しない。**

## ゴール
- (A) macOS/Windows アプリ v2.22(PR#37)+F4(PR#36) 修正の実機非回帰確認
- (B) Google Form 被験者管理自動化 (F1提出→P-ID自動発番→自動メール→同意/NDA→管理シート) の実フォーム動作確認

## 役割分担
- 実機操作・Apps Script 実行 = ユーザー (研究者)
- エージェント = 手順提示・ログ解析(log-analyzer)・不具合切り分け・修正提案・§1自動検証の実行

## 受け入れ条件
- §1 自動検証 (cargo test / gse-replay --snapshot / emit_schema drift / tsc) 全 green
- §2 macOS 機能検証 (クリック受理・記録着地・Wall・IME・F4 idle/プローブ) 合格
- §3 Windows 差分 合格
- §4/B Form 自動化 (buildForm冪等・trigger・適格ドライラン・冪等性・不適格スキップ・管理シート集計) 合格
- 発見した不具合は本ディレクトリに記録し follow-up を切る (このセッションでは修正しない)

## 確定事実 (起動時に git で裏取り)
- main HEAD version 0.1.21
- feature/participant-mgmt-automation は **PR#46 で main へマージ済み** (prompt の「未マージ＝要デプロイ」は解消済)
- Form_Phase1/GSE_Phase1_Form_Builder.gs 作業ツリーは clean (= main HEAD と一致 = 最新)
