# tasklist

## §1 CPU% 規約
- [x] Microsoft 一次資料の逐語を取得（★ Process オブジェクトは 100 % を超えうる）
- [ ] ⚠️ **Windows 実機の busy-loop 実測**（★ 手順を研究者へ提示済み・**結果待ち**）
- [x] `sample-macos.sh` / `run.sh` / `summarize.py` に規約を meta で記録
- [x] `notes.md` の「FAIL 相当」記述を訂正
- [x] ⚠️★★★ **予定外**: macOS の計測器が約 2.08 倍過小報告していたのを発見・修正・校正

## §2 取り込み（案 B）
- [x] Windows 実測ぶんのみ取り込み（`.steering/20260904-windows-orphan-verify/` + experiments）
- [x] `check-o1-release-readiness.sh` の陰性対照
- [ ] PR

## §4 mac 側
- [x] B: 起動時の山を実測（★ 起動直後 2.08 % / 定常 1.31 %・**初めて数字にした**）
- [ ] ⚠️ A: スリープ跨ぎ検証 —— ★ **私からは実行不能**（`caffeinate` / メディア再生）。
      手順と復帰後チェックを渡した。⚠️ **陰性対照は既に崩れている**ことは記録済み
- [x] C/D: ブランチ棚卸し（★ 4 本を実物まで降りて調査。⚠️ **削除はしていない**）

## ⚠️ 残（★ 次セッションへ）
- [ ] ⚠️ Windows CPU% 規約の実機決着 → 決着したら `run.sh` の `one_core_100_unverified` を確定
- [ ] ⚠️ **macOS の 8h 再測**（★ 直した計器で。⚠️ 旧 2 本の CPU は無効）
- [ ] ⚠️ スリープ跨ぎ検証の実行
- [ ] ★ `feature/phase1-reminder-and-dashboard` の steering 記録 4 件を救出してから削除
- [ ] ★ 残り 3 系統の取り込み（ADR-023〜028 / metrics.rs / 表現層 / ツール）＝ 案 C
