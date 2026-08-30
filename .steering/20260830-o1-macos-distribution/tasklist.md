# tasklist

## §0 状態の固定（★ メモを一次資料にしない）
- [x] readiness / selftest / portability / O1 ガード / 配布 selftest を**自分で走らせた**
- [x] 前提コマンド（ditto / hdiutil / codesign / zip / python3 / gh / git / pwsh）と `gh auth` を確認
- [x] macOS 26.5.2 (arm64) / bash 3.2.57 を確認

## §1-B タグ
- [x] 最新タグ `v0.1.29` と release 資産を確認（dmg は `aarch64` のみ）
- [x] ⚠️ **既定 `TAG="v0.1.24"` を書き換えていない**（G1 実施中）

## §1-C / E 配布物
- [x] 本番設定 `Form_O1/o1_submit.json` で `--mode o1 --tag v0.1.29` を実行 → **完走した**
- [x] zip 内 `g1-submit.json` が本番設定と **byte 一致**（SHA-256 一致・両 OS）
- [x] `--mode o1` が G1 の zip を作り直していないことをタイムスタンプで確認
- [x] ⚠️ **その配布物は隔離した**（→ B-2。O1 を知らないビルドだった）

## §1-D 実機通し確認
- [x] 1. zip を展開してデスクトップへ
- [x] 2. README 【1】どおりに初回セットアップ → ⚠️ **NG**（B-1）→ 修正後 **OK**（2 回とも）
- [x] 3. `.app` を起動（★ TCC は既に許可済み: `input_monitoring=true accessibility=true`）
- [x] 4. O1 モードか実体で確認 → ❌ **なっていなかった**（B-2）
- [ ] 5. 宣言 4 択 → ローテート ── ⚠️ **未実施**（O1 モードでないので意味が無い）
- [ ] 6. 「すぐ止める」→ `recording_pause` ── ⚠️ **未実施**（同上）
- [ ] 7. ⚠️★★★ 「この時間帯の記録を消す」 ── ⚠️ **未実施**（★ 全 OS でいまだ未実施のまま）
- [ ] 8. 自動起動の登録 ── ⚠️ **未実施**
- [ ] ⚠️ Gatekeeper ダイアログ ── **未再現**（★ ローカル展開なので quarantine が付かない）

## §1-E 送信
- [ ] ⚠️★★★ 送信 timeout の実測 ── **実施できなかった**
      （★ 研究者は承認したが、`gse-submit` に `--o1` が無く O1 の規則で包めない）

## §1-F README
- [ ] ⚠️ 文言の実機突き合わせ ── **未実施**（★ 通し確認に到達していないため判断材料が無い）
- [x] ★ ただし **確認文言の鎖**は機械化した（セットアップ / 配布ゲート / UI 実装の 3 点照合）

## ★ 本セッションで作った修正
- [x] `初回セットアップ_mac.sh`: マーカー自動判別 ＋ モード別文言 ＋ 対照 3 件（8→12 項目）
- [x] `初回セットアップ_mac.sh`: `xattr` / `codesign` 不在の silent pass を塞ぐ
- [x] `make-common-app-zip.sh`: **配布物そのもの**で初回セットアップを回す検査
- [x] `make-common-app-zip.sh`: タグ ＋ 実体の二重で O1 実装の有無を検査（macOS / Windows 両方）
- [x] `make-common-app-zip.sh`: `--mode o1` で `--config` の既定（G1 設定）を禁止
- [x] `make-common-app-zip.sh`: 未取得タグと「O1 が無い」を別の die に分離 / `$V` の trap / `grep -cF`
- [x] `make-common-app-zip.sh`: 確認文言 3 点鎖の selftest（17→18 件）
- [x] `check-o1-release-readiness.sh`: 「O1 を含むリリースタグの有無」を検査（＋ 対照 2 件）
- [x] `check-o1-release-readiness.sh`: 「実 secret の値の散文混入」を検査（＋ 対照 2 件）
- [x] `check-shell-portability.sh`: ⚠️ **非 ASCII 名のファイルを無言で除外していた穴**を塞ぐ

## レビュー
- [x] `code-reviewer` / `security-checker` を並列起動
- [x] CRITICAL 1 件（私が `.steering/` に実 secret を貼った）→ 削除 ＋ ゲート化 ＋ 全走査で確認
- [x] HIGH 3 件・MEDIUM 5 件・LOW 3 件を反映
- [x] `/cross-review` を起動 ── ⚠️ **Codex は secrets-filter でブロック**（誤検知・→ `decisions.md` 判断 6）
      ★ Claude 単独へ縮退。⚠️ 予算は未消費（`tokens_used=25960` のまま）
- [x] 縮退後に出た HIGH 1 / LOW 2 を反映（→ `decisions.md` 判断 7）
- [ ] ⚠️ Codex の真の第二意見 ── ★ 研究者が目視同意すれば `--ack-filtered` で再実行可能

## 最終ゲート（★ 実測値・2026-08-30）
| ゲート | 結果 |
|---|---|
| `check-o1-release-readiness.sh` | **通過 17 / 未達 2** ⚠️ 未達が 1 件**増えた** ＝ 見えていなかった赤が見えた |
| `check-o1-release-readiness.sh --selftest` | **43 / 0** |
| `check-shell-portability.sh` | **7 / 0**（★ 走査対象 56 → **58 本**） |
| `sync_session_o1_guard_test.sh` | **13 / 0**（`PS1_VERIFIED: core/7.6.5`。⚠️ Desktop 5.1 は未検証） |
| `make-common-app-zip.sh --selftest` | **19 / 0** |
| `初回セットアップ_mac.sh --selftest` | **12 項目・緑** |
| ★ `--mode o1 --tag v0.1.29` | **`build_exit=1`**（★ 正しく止まる） |
| ★ G1 の zip | **08-23 のまま**（⚠️ 作り直していない） |

## ⚠️ 未達 2 件は「直せなかった」のではなく「研究者の作業が要る」
1. O1 実装を含むリリースタグが無い → 新タグ ＋ CI（→ `blockers.md` B-2）
2. 送信 timeout が未実測 → ★ 1 の後でないと**実施しても意味が無い**（`--o1` が無いため）
