# 設計

## 実施アプローチ

- 冒頭（Status の直後）に「2026-09-19 の改訂」の一覧を置き、本文の該当箇所に日付つきの注記を足した。本文の既存の文は消していない。
- **J-3**: §5.0 を新設し、`T_stop` の候補を 3 つ（応答を成功として戻す経路 ／ 効用の上げる向きの更新 ／ 招待の後の `level` 表現の継続更新）と `T_allow` を、既決（ADR-033 D2 / D3 / D5・ADR-008 D1・ADR-027 D5）との関係つきで書いた。★ 候補 1 / 2 は GSE 本体では最初から止まっており、候補 3 は ADR-027 D5 が続けると決めている → **陽性対照は GSE 本体では作れず、別計器で作る**（J-16）と明記した。
- **J-9**: §5.3 と §7.2 の「intentional termination / failure の弁別」を「解除 vs 断」に狭めた（timeout / expiry との弁別を目標にしない）。
- **ADR-033**: §5.2 の non-recapture の数え方から控える向きの利用を除いた。
- **J-6**: §16 に Digital Nature の比較節を足した（DN カードの要点・書いてよいこと / いけないこと）。旧 BRIDGE-DN 契約と命題カバレッジ行列に「統合した・数えない」の注記。
- **機械的な規則**: `t0` → `t_stop`（11 か所・正規表現で置換し、残りが無いことを確認）。

## 変更対象

- `.steering/20260916-gse-theory-operationalization-review/core-cs-evaluation-contract.md`・`bridge-dn-evaluation-contract.md`・`core-proposition-coverage-matrix.md`

## テスト戦略

- `check_citations.py` 違反なし。`/cross-review` 2 巡。

## ロールバック計画

- コミットを `git revert` する。
