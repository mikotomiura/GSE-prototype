# タスクリスト

## 【A】macOS でレシート UI を目視する

- [x] v0.1.25 の dmg を取得し、配布 zip を展開して確認対象にする
- [x] `g1.mode` が効いて G1 モードになる (`G1 モードで動作しています（marker）`)
- [x] 入力監視の権限を付与し、`CGEventTap installed via Input Monitoring` を実測
- [x] ★ `開始する` の前に AX API で参加者 ID の実体値 `P999` を確認
- [x] 【1】確認カード
- [x] 【2】`記録を送信しています…`
- [x] 【3】`✅ この回の記録を送信しました（13:27・2 件）`
- [x] 【4】文字が読める (背景と同色の文字なし)
- [x] 【5】`✅ 送信を待っている記録はありません。`
- [x] Drive 側の到着 2 件を実体で確認 (レシートの件数と一致)

## 【B】配布 zip の生成

- [x] `make-common-app-zip.sh --tag v0.1.25` を実行
- [x] `G1_実施用_macOS.zip` / `G1_実施用_Windows.zip` を生成
- [x] ★ スクリプトの自己申告と独立に中身を検算 (エントリ / 版 / 秘密鍵混入)
- [x] ⚠️ `gse-unpack` が `.app` 内に同梱されている事実を記録 (v0.1.23 から不変・鍵は埋まっていない)
- [ ] ⚠️ **Drive へのアップロードは未実施** (研究者が行う)

## 【C】テスト送信の後片づけ

- [x] `P009_block01_gse_20260808_060459.age` の素性を確定 (= この Mac のテスト)
- [ ] ⚠️ Drive で `(windows_test)` / `(macos_test)` を前置 (**人が UI から**)
- [ ] ⚠️ Windows 機ローカルの 8/10 分の後片づけ
- [ ] ⚠️ 本セッションで増えた `P999` 2 件の後片づけ

## 積み残し (別タスク)

- [ ] ⚠️★★ **ブロック未開始のセッションが提出される** (`verification.md` 参照)。
      macOS の初回起動経路でほぼ必ず踏む
- [ ] ⚠️★ macOS でフック生存検知が動かない (`liveness.rs:141`)
- [ ] ⚠️ `Input Monitoring denied but Accessibility granted` と出るのに
      `CGEventTap creation failed` が続く経路がある (実測。フォールバックの判定が実態とずれる)
- [ ] ⚠️ レシート UI に `code-reviewer` / `security-checker` / `/cross-review` は**未実施のまま**
- [ ] ⚠️★ `f1` の凍結 (`.steering/20260809-g1-hook-liveness-detection/measurements.md §7-2`)
