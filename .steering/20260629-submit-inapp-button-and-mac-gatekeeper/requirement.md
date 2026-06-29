# 要件: 提出のアプリ内ボタン化 ＋ mac Gatekeeper(quarantine) 対策

## 背景（Phase1 ユーザー検証のブロッカー解消の一部）
macOS 被験者がセッション後に `提出する_mac.command` を実行すると、macOS 15 (Sequoia) Gatekeeper が
「マルウェアが含まれていないことを Apple が確認できないため開けません」でブロックする。

- 原因: GSE の mac バイナリは **ad-hoc 署名 (`codesign --sign -`)・未 notarize**（tauri.conf に signingIdentity
  なし／CI `APPLE_SIGNING_IDENTITY: "-"`）。ダウンロードで付く `com.apple.quarantine` を Gatekeeper が弾く。
- **2層構造**: ①`.command` スクリプト自身が quarantine → ダブルクリックでブロック（被験者がここで停止）。
  ②仮に許可しても中で呼ぶ `gse-submit` も quarantine → SIGKILL(exit137)。
- 作業ツリーの未コミット修正 `xattr -dr com.apple.quarantine "$(dirname "$0")"` は**②しか解決しない**
  （スクリプトが起動して初めて走るため①に無力）。

## ゴール
1. **恒久対策＝提出をアプリ内ボタン化**: 被験者は**既に Gatekeeper 承認済みの GSE アプリ**から「提出する」を
   押すだけ。別スクリプト/別バイナリの Gatekeeper 発火を**根絶**する（mac の提出 quarantine 問題を消す）。
2. **即効の暫定対策**: 未コミットの `xattr -dr`（②対策）を commit ＋ 参加者ガイドに①の許可手順
   （システム設定→プライバシーとセキュリティ→「このまま開く」 / Terminal `xattr -dr` 一括）を明記。

## 最重要の設計分岐（着手前に決める）
`age` 暗号は **`package` feature で隔離**され **app 本体ビルドに載っていない**（Cargo.toml: `package=["dep:age"]`、
gse-submit/gse-package/gse-unpack は `required-features=["package"]`。理由: age を default Tauri ビルドから外す）。
よってアプリ内提出は二択:

- **案A: sidecar(externalBin) 同梱**: CI が別途ビルドする `gse-submit` を `.app` バンドル内に同梱し、
  tauri-plugin-shell の `Command::sidecar` で起動。**バンドル内バイナリは app 署名に内包され単独 quarantine が
  付かない**＝Gatekeeper 根絶＋age 隔離維持。参加者 ID は env `GSE_PARTICIPANT_ID` で渡し（submit.rs は対応済）、
  stdout/exit を UI に表示。tauri.conf `bundle.externalBin` ＋ CI のバイナリ配置（target-triple 接尾辞）が要る。
- **案B: in-process**: app ビルドに `package` feature（age）を載せ、`packaging::package_session()` を新 Tauri
  コマンドから直呼び。UX 最良（サブプロセス無し）だが **age を app 本体に載せる**＝隔離方針の撤回・バイナリ増・
  ビルド OOM 懸念（Cargo.toml の windows-sys OOM メモ参照）。

→ `/start-task` の design 段で A/B を評価（必要なら `/reimagine`）。第一候補は **案A（隔離維持＋Gatekeeper 根絶）**。

## 受け入れ条件
- [ ] mac 実機: ダウンロード→アプリ初回承認→**アプリ内「提出する」ボタンで `.age` が生成**され、
      別の Gatekeeper ダイアログが出ない（被験者が Terminal/設定を触らず提出完了）。
- [ ] 生成物は従来 CLI と同一（匿名化 VK→KeyCategory・時刻相対化・`P###_<stem>.age`・実名混入なし＝data-privacy）。
- [ ] 既存 `gse-submit` CLI（研究者/Windows 経路）と Windows 提出フローは**非回帰**。
- [ ] 暫定対策（`xattr -dr` commit ＋ ガイド許可手順）が即リリースに入る。
- [ ] 提出失敗時は fail-loud（既存のインライン error パターン同様、静かに失わない）。

## 非対象
- Apple 公証（Developer ID＋notarytool）は将来スケール時の最終解として別途検討（本タスクでは扱わない）。
- task_kind=論述ロック・P007 confirmatory 再走は別タスク（Phase1 ブロッカーの別項目）。

## 参考
- 議論の出典: 本リポ会話 2026-06-29（Phase1 実行可否レビュー）。Phase1 ブロッカーは4点:
  ①P007 M0 confirmatory 未走 ②task_kind 未ロック ③**本件=mac 提出 Gatekeeper** ④お題/進行ガイド未作成。
- コード: `src-tauri/src/packaging.rs`（提出ロジック単一情報源）/ `src/bin/submit.rs`（CLI・env ID 対応）/
  `scripts/submit/提出する_mac.command`（未コミット xattr 修正）/ `docs/participant-setup-guide.md`。
- Skill: `data-privacy`（匿名化/暗号/PII）/ `architecture-rules`（Tauri コマンド追加）/ `rust-standards` /
  `typescript-standards` / `git-workflow`。
