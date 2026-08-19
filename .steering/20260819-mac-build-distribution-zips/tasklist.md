# タスクリスト — v0.1.27 配布 zip

## §1 事前確認

- [x] `main` が `origin/main` と一致 (`501ef88`)、`v0.1.27` が main の祖先
- [x] 道具: `hdiutil` / `codesign` / `ditto` (macOS 標準)、`python3` 3.14.4、`gh` 認証済み
- [x] `g1-submit.json` を確認 (endpoint 112 文字 `/exec`・secret 33 文字 ≥ 24)
- [x] リリース資産の存在: `gse-next.exe` / `gse-submit.exe` / `gse-next_0.1.27_aarch64.dmg`

## §2 実行

- [x] `./make-common-app-zip.sh --tag v0.1.27` (⚠️ `--tag` を付けた。既定の `v0.1.24` ではない)
- [x] スクリプトの機械検査が全て緑
  - [x] タグに `reconcile.rs` あり (自動送信が入ったビルド)
  - [x] dmg マウント → 署名検証 → `.app` 取り出し → フォルダ配置後に再度署名検証
  - [x] `初回セットアップ_mac.sh --selftest` を zip 化の前と展開後の 2 回
  - [x] README の 4 文言 grep (「壊れていません」「ゴミ箱に入れないで」「研究者と一緒に」
        「ターミナルの窓へドラッグ」)／旧版「右クリック」「開発元を確認できません」の不在
  - [x] Windows zip: UTF-8 フラグ (bit 11) ／ `__MACOSX` `.DS_Store` 無し (7 エントリ)
  - [x] `gse-submit.exe` の実体に `reconcile` (6 箇所)
  - [x] 共通配布物に `block*.html` が無い

## §3 実測 (人が見る)

- [x] §3-1 `G1_実施用_macOS.zip` に `gse-next.app` (39 エントリ)・`.dmg` 0 件
- [x] §3-2 `app_version = 0.1.27` を実起動の NDJSON `meta` 行で確認
- [x] §3-3 G-1 二度押しで前ファイルが閉じ、新ファイルができる
- [x] §3-4 `starve_window` の発火条件を実装で確認 (今回は条件を満たさず未発火＝仕様どおり)

## §5 後処理

- [x] `.steering/20260819-mac-build-distribution-zips/` に結果を記録
- [x] ⚠️ Drive へのアップロード (**研究者が 2026-08-19 に実施**。私は上げていない)
- [x] Drive 上の実体を検算 (バイト数一致 / 置き場所 / 旧版と余計な物の不在 / 共有範囲)
- [ ] ⚠️ 電子同意フォームの実物への反映と突合 (収集開始ゲートは**まだ閉じていない**)
      → `_handoff/next-session-prompt-post-reboot-collection-gate.md`

## 積み残し (研究者判断待ち)

- [ ] `experiments/*/dist/` が `.gitignore` の対象外 (詳細は `decisions.md` 所見 3)
- [ ] テストで生じた `P999_block05_gse_20260811_042646.age` の扱い (未承認・未送信)
