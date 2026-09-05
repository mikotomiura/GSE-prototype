# O1 稼働コストの再測（macOS・8 時間 1 本）と孤児回収の 2 回目検証

## 背景

★ 2026-09-04 の 1 回目（`experiments/20260903-o1-runtime-cost`）で、CPU / RSS / NDJSON は
**8 時間ぶん実測できた**（notes.md の結果表）。⚠️ しかし 2 つが埋まっていない:

- **A. エネルギー影響** —— ★ バッテリー % の対照は AC 運転で無意味になり、指標 3 を
  `top -stats power` の**プロセス単位のエネルギー影響**に置き換えた（PR #157 / main 39d59b7）。
  ⚠️ **GSE を動かした状態での実運用は未検証**（★ Finder を代役にした end-to-end までしか済んでいない）。
- **B. 起動時のコスト** —— ⚠️ 1 回目は稼働 4h15m 後から測ったので**未測定**。
  ★ 孤児回収の走査を含むので、**GSE を起動する *前* からサンプラを回す**必要がある。

★ 併せて、PR #151（孤児回収）の **2 回目の実機検証**を「強制終了 → 再起動」というより現実に近い
経路で行う（★ いま `~/Documents/GSE-sessions/` に `session_end` を持たない孤児が 1 本ある）。

## ゴール

1. ★ 8 時間 1 本を **GSE 起動前から**回し、`energy_impact` / `ref_energy_impact` に実値を得る。
2. ★ 集計 (`summarize.py`) が**エネルギー影響を参照との比で報告**する（⚠️ 閾値は置かない）。
3. ★ 孤児回収が起動時に発火したことを `gse-app.log` の逐語で確かめる。

## スコープ

### 含むもの
- macOS のみ。`with-gse` 1 本のみ（⚠️ 対照は README で廃止済み）。
- 集計スクリプトの修正（★ 8 列目まで読む・⚠️ 廃止した指標との整合）。

### 含まないもの
- ⚠️ Windows の実測（★ 別引き継ぎ `next-session-prompt-windows-runtime-cost-and-orphan-verify.md`）。
- ⚠️ CPU / RSS / NDJSON の測り直し（★ 1 回目で足りている）。
- ⚠️ 送信 timeout の実測（★ 別件・release readiness の唯一の赤）。
- ⚠️ `o1_consent_ack.bak` を戻すこと（★ §3 の研究者判断・本セッションでは触らない）。

## 受け入れ条件

- [ ] ★ 1 分スモークで **8 列すべてに実値**が出ることを確かめてから 8 時間を回す
      （⚠️ 全部 0 なら測定器が壊れている）。
- [ ] ★ サンプラを先に起こし、**1 分の起動前基線**を取ってから GSE をバイナリ直叩きで起動する。
- [ ] ★ `summarize.py` がエネルギー影響を **GSE / Finder の比**で出す（⚠️ 閾値判定はしない）。
      ★ 陽性対照（列が空/0 のとき「測れていない」と出る）と陰性対照（正常データで出ない）を置く。
- [ ] ★ 孤児回収の発火を `gse-app.log` の逐語で示す（⚠️ 陰性対照＝既に閉じたファイルが無変化）。
- [ ] ⚠️ **1 回目の結果 (`results/with-gse/samples.tsv`) を消さない**（★ git 未追跡＝ディスクにしか無い）。

## 関連ドキュメント

- `experiments/20260903-o1-runtime-cost/README.md` / `notes.md`
- `.steering/_handoff/next-session-prompt-o1-runtime-cost-round2.md`
- `.steering/20260903-o1-preflight-4/decisions.md`（PR #151）
