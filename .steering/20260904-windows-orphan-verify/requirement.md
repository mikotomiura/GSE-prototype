# Windows 実機検証 — O1 孤児回収 (PR #151) / 稼働コスト / overlay クリック透過

## 背景

`.steering/_handoff/next-session-prompt-windows-runtime-cost-and-orphan-verify.md` の引き継ぎに従う。
`o1::close_orphaned_sessions`（★ アプリが正常終了できなかったとき、次回起動でセッションを
閉じ直す）は Windows の `WM_ENDSESSION` → `CloseRequested` 翻訳がコードから決められないため、
実機（Windows）でしか検証できない。稼働コスト実測・overlay のクリック透過も未実測。

⚠️ 引き継ぎメモ自体が「前回の引き継ぎで 1 件誤り・1 件見積もり甘すぎ」と自己申告しているので、
本タスクでも一次資料（コード・実測ログ）を必ず自分で確かめ直す（`verify-before-claiming`）。

## ゴール

- [ ] §1: 孤児回収を A(正常終了)/B(強制終了)/C(OS 再起動) の 3 状態で実機検証し、
      それぞれの `gse-app.log` / NDJSON の実際の挙動を記録する
- [ ] §2: 稼働コスト（CPU/RSS/NDJSON サイズ、起動コスト込み）を 8 時間 1 本実測する
      （★ `0-1b` により対照 without-gse は廃止済み。2本ではなく 1 本でよい）
- [ ] §3: overlay の透明窓がクリックを奪わないか、非侵襲的 hit-test で確認する

## スコープ

### 含むもの
- 現在のブランチ (`feat/resumption-outcome-arbitration`) HEAD からのリリースビルドでの実機検証
  （★ main ではなく現ブランチを使う判断は decisions.md に記録する）
- `experiments/20260903-o1-runtime-cost/` の実測（器は既存、実測データを追加するのみ）
- 検証用に生成した NDJSON / ログの後始末

### 含まないもの
- コード変更（本タスクは検証のみ。欠陥が見つかった場合は起票のみ行い、別タスクで直す）
- `Form_G1/` / `Form_O1/`（GAS）・事前登録凍結節・`gse-dataset` 履歴には触れない
- macOS 側の検証（別セッション・別マシン）

## 受け入れ条件

- [ ] A/B/C 各状態の生ログ（`gse-app.log` 該当行 + NDJSON の `session_end` 有無）を本ディレクトリに残す
- [ ] §2 のスモーク（8列出るか）と本番 8 時間 1 本の結果を記録する
- [ ] §3 の hit-test 結果（押せる/押せない座標）を記録する
- [ ] `~/.gse/o1_consent_ack` の状態（検証前後）を明記する
- [ ] 検証で生成した NDJSON の後始末を明記する
- [ ] 未検証が残る場合は「N 件中 M 件実測、未検証 K 件」の形で明記する（「問題なし」と断定しない）

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-windows-runtime-cost-and-orphan-verify.md`
- `.steering/20260903-o1-preflight-4/decisions.md`（判断 2 / 判断 6）
- `experiments/20260903-o1-runtime-cost/README.md`
- `src-tauri/src/o1.rs`（`close_orphaned_sessions` の doc コメント）
