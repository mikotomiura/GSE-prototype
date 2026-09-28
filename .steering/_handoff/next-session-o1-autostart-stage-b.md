# 次セッション — O1 v0.1.38 の段階 B（本当のログイン）と残り

> 作成: 2026-09-28（`.steering/20260928-o1-resilience-g1-g2-g5/` 完了直後・O1 の配布タグ = `v0.1.38`）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す。

## §0 打ち込む用

```
.steering/_handoff/next-session-o1-autostart-stage-b.md を読んで、O1 v0.1.38 の段階 B（本当のログインでの自動起動の確認）を進めてください。
⚠️ まず git pull --ff-only。並行セッションがあれば worktree を切る。
Skill: verify-before-claiming・data-privacy。応答は日本語。
```

## §1 状態（2026-09-28）
| 何 | 値 |
|---|---|
| O1 の配布タグ | `v0.1.38`（`afe6b0d7`）。記録は `docs/o1-distribution-tag.md` v0.1.38 節 |
| 実装 | PR #246（G-1 自動起動 / G-2 6 時間ごとの再送 / G-5 32 MiB 超の隔離）・#247（版上げ）・#249（配布記録） |
| Drive | O1 の zip 2 点を研究者が差し替え、コネクタでバイト数照合済み |
| O1 ゲート | 通過 23 / 未達 1（同意文書の「未了」＝6 択 ESM 追補の採否・研究者判断待ち） |
| 同意フォーム | 研究者が `migrateO1ConsentForm()` を実行し、説明文の新しい 1 文を実物で確認済み（2026-09-28） |

## §2 やること

1. **段階 B（研究者の Mac・本当のログイン）** — `.steering/20260928-o1-resilience-g1-g2-g5/g1-mac-autostart-experiment.md` を**新しいビルドがみずから plist を書く**形に読み替える:
   - `O1_実施用_macOS.zip` を展開 → 実験用に `g1-submit.json` の endpoint を**届かない宛先**へ差し替え（⚠️ 本番の受け口に送らない）→ 初回セットアップ → 起動 → 同意確認（⚠️ 実験用の P-ID）→ `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist` と配布フォルダの `o1.autostart`・`~/.gse/o1_autostart_registered` ができるか。
   - ログアウト → ログイン → 自動で立ち上がり `gse_o1_*` に `key` 行が増えるか（⚠️ NDJSON は 8〜12 秒待つ）。
   - **一覧での表示名**（システム設定 → 一般 → ログイン項目と機能拡張 の「バックグラウンドでの実行を許可」）が README の「gse-next」と一致するか。**通知**（「バックグラウンド項目が追加されました」）が出たか。
   - そこで **オフ** → 別フォルダに展開した同じ zip を起動 → **plist が付け替えられても（Repoint）オフのまま**か（security-checker の未確認点）。
   - 片付け: plist・`~/.gse/o1_autostart_registered`・`~/.gse/o1_consent_ack`・O1 参加者 ID・実験で増えた NDJSON／`.age`・システム設定の項目。
   - 結果が README と食い違えば、README（両 OS）を直して**版を上げずに**配布物だけ作り直せるか（README は zip にだけ入る）を確かめる。
2. **Windows 実機**（研究者または Windows 側の Claude Code・収集専任: memory `windows-agent-collection-only`）: 同意確認のあと `HKCU\…\Run` に `GSE-O1`（引用符つき）ができるか・サインインで起動するか・タスクマネージャーでの表示名・無効にしたあと別フォルダで起動しても無効のままか。
3. 任意: G-3（スリープをまたいだ確認）は研究者の手順（memory `claude-code-caffeinate-blocks-sleep-tests`）。

## §3 やらないこと
- G1 の配布物（`v0.1.36` 凍結）。GAS の `doPost` の変更。同意文書の「未了」の採否。

## §4 既知の残り（決めたうえで受け入れたもの）
- ローテートスレッドへの G-2 の配線（60 秒ループ）は単体テストでは見ていない（純関数のみ）。
- ハードリンクを持たないファイルシステムでは隔離をしない（その場に残して error ＝送らないことは同じ）。
- 登録に失敗しても被験者には見えない（README の「印が出ないときは研究者に連絡」で拾う）。
