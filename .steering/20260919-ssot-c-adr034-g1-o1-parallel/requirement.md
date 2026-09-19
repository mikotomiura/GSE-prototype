# 単位 c: G1 / O1 の並行実施の新 ADR（ADR-034）

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **c**。

## 背景

- ADR-014 は、O1（R3）と G1 の募集の競合を**時間軸で解いた**（判断 1「同時に募集しない」・判断 4「開始 = G1 の収集完了直後」）。
- 研究者判断 J-5（2026-09-18・前段 判断 1 #13）: **並行実施へ変える**（推奨と異なる回答）。判断 1 / 4 を上書きする新 ADR が要る。
- 扱うべき論点 5 つ: (i) 募集競合の受け入れ、(ii) 追補の制約 1 との両立、(iii) P-ID の単一採番、(iv) プール分離、(v) ADR-031 M9 による律速。
- 起草前に研究者へ 3 点を確認した（親タスク 判断 1 #8・判断 2 #1 / #2）: 同一人物は草案 C §7.1 のとおり ／ T-27 は案内日を分けて検出で受ける ／ O1 は 3〜5 名を維持。

## ゴール

- 新 ADR（ADR-034）で、開始時期・募集・G1 の計器の凍結・同一人物・プール分離・同時採番の運用を決める。
- `docs/o1-roster-operations.md` に並行時の運用規則を足す（運用の SSOT）。

## スコープ

### 含むもの
- `docs/adr/ADR-034-g1-o1-parallel-conduct.md`（新規）・`docs/adr/README.md`（一覧と ADR-008 / 014 / 018 行の参照）
- `docs/o1-roster-operations.md` §5（新設）

### 含まないもの
- ⚠️ ADR-014 本文の書き換え
- ⚠️ 被験者向け文書（`docs/participant-setup-guide.md`・同意文書）の変更
- ⚠️ GAS の改修（研究者判断でコード変更ゼロ）
- ⚠️ G1 と O1 のデータの結合解析の可否（同意文書の範囲の確認が要る）

## 受け入れ条件

- [ ] 論点 (i)〜(v) がすべて決定か明示的な未決になっている
- [ ] 追補の制約 1 を緩めず、条件 2〜4 も緩めていない
- [ ] 一次（ADR-014・ADR-031 M9・GAS の採番コード・配布スクリプト・`meta` 行）で確かめた事実だけを Context に書いている
- [ ] ADR-014 判断 3（倫理審査不要の根拠 4 件）を崩していない
- [ ] `/cross-review` 2 巡

## 関連ドキュメント

- `docs/adr/ADR-014-continuous-natural-work-collection.md`（判断 1〜4・追補・Migration）
- `docs/adr/ADR-031-self-reported-activity-audit-criterion.md` §Migration M9 の追補
- `Form_G1/GSE_G1_Form_Builder.gs`・`Form_O1/GSE_O1_Form_Builder.gs`（採番・T-27）
- `experiments/20260801-controlled-friction-task/make-common-app-zip.sh`・`scripts/check-o1-release-readiness.sh`
- `.idea/20260916-gse-mitou-research-plan.md` §7.1（★ 追跡外）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 並行にするかどうかは研究者が裁定済み（J-5）で、細部も起草前に研究者へ確認した
