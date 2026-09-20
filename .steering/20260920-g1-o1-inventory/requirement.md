# G1 / O1 の残タスクの棚卸し

> 前段: `.steering/20260920-decision4-reflection/`（判断 4 の反映・完了）。
> 入口: `.steering/_handoff/next-session-g1-o1-inventory.md`。
> ブランチ: `docs/adr-030-stall-onset-definition`（main へ switch しない）。

## 背景

判断 4 の反映が終わり、次は **G1（統制タスク実験）と O1（継続的自然作業収集）の
「配布・収集を始める前に残っていること」が何本あるのか**が分からなくなっている。

既存の引き継ぎ（`g1-o1-precollection-findings.md` = 2026-09-01、
`next-session-post-adr032-approvals-and-parallel-tracks.md` = 2026-09-14、
`next-session-o1-consent-secondary-use.md` = 2026-09-13）は **どれも段 3 より古く**、
書かれている「状態」が今も真かどうかは保証されない。
加えて ADR-034（G1 と O1 の並行）が募集ゲートと配布ゲートを分けたため、
**何がどちらのゲートに載るか**が文書に散っている。

したがって本タスクは「残っているものを推測で並べ直す」のではなく、
**一次資料（コード・スクリプトの実行・ADR・事前登録・被験者向け文書）で状態を確かめ直し、
1 枚の台帳に落とす**ことを目的とする。

## ゴール

1. G1 / O1 / 共通（マージ・schema）の残項目を、**一次で確かめた状態つきで** 1 つの台帳
   （`inventory.md`）にする。各行に「根拠（ファイル:行 / 実行コマンドと終了コード）」を持たせる。
2. 各項目を **3 つの区分**に分ける。
   - **[研究者]** 研究者の判断が要る（＝ agent が埋めてはいけない）
   - **[機械]** 判断が要らず機械的に片づく
   - **[ゲート]** 配布・収集の前に必ず止めるもの（律速）
3. 研究者への質問 Q1〜Q4（引き継ぎ §1）に **この場で答えを得て** `decisions.md` に記録する。
4. 選ばれた 3 つを実施する（範囲の確定は grill 済み・下記スコープ）。

## スコープ

### 含むもの
- 一次確認と台帳化（上記ゴール 1〜3）。
- **機械的な不具合の修正**: `run.sh` / `check_g1_emails.py` の cp932 問題など、
  研究者の判断が要らないもの。
- **main へのマージ計画の作成**（計画書のみ。★ マージの実行はしない）。
  ブランチ 140 先行・main 2 先行の分岐、schema parity の drift（`activity_label`）を含む。
- **検査の追加**: ADR-034 D6（案内日の分離）など、機械検査に落とせるものを検査へ足す。
  置き場の判断を含む。

### 含まないもの
- ⚠️ **ADR 本文の書き換え**・**事前登録 §3 の書き換え**（規約で禁止）。
- ⚠️ **被験者向け文書**（同意文書・`participant-setup-guide.md`・募集文面）の改訂。
  必要が出たら研究者へ返す（契約であるため）。
- ⚠️ **配布の実行**（`make-distribution.sh` / `make-common-app-zip.sh` / タグ push）。
- ⚠️ **main へのマージの実行**（計画までで止める）。
- G1 / O1 の収集開始そのもの。
- 文献ラウンド・SSOT 本体の Codex 1 巡（引き継ぎ §3 の「その後」= 次タスク）。

## 受け入れ条件

- [ ] `inventory.md` の全行に根拠（ファイル:行 / コマンド＋終了コード）が付いている
- [ ] 全行が [研究者] / [機械] / [ゲート] のいずれかに分類されている
- [ ] Q1〜Q4 の回答が `decisions.md` に「決定 / 理由 / 却下案」で記録されている
- [ ] cp932 問題: `run.sh` が `PYTHONUTF8` 無しの Windows 既定環境で緑になる
      （＝ 修正後に実際に実行して終了コード 0 を確認する）
- [ ] 追加した検査が、**わざと壊した入力で赤**・**正常な入力で緑**の両方を実測している
      （★ `feedback_acceptance_self_test`: 検査スクリプトは通しで回すまで未検証）
- [ ] `merge-plan.md` に、衝突予測・schema drift の扱い・タグとの順序が書かれている
- [ ] `/cross-review` 2 巡（パス限定）を通している

## 関連ドキュメント

- `.steering/_handoff/next-session-g1-o1-inventory.md`（入口・未検証メモ）
- `.steering/20260920-decision4-reflection/decisions.md` 判断 8（Q1〜Q4 の一次）
- `docs/adr/` ADR-031 / ADR-032 / ADR-034 / ADR-035
- `experiments/20260801-controlled-friction-task/preregistration.md`（前提条件 1〜7）
- `docs/o1-deletion-ledger.md` / `docs/verification-runbook.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 本タスクは「一次確認と台帳化」＋「機械的な修正」＋「計画書」であり、
  アーキテクチャ選択や複数案の比較を伴わない。ただし **検査の置き場**（どのスクリプトに
  D6 検査を足すか）は設計判断を含むため、`decisions.md` に判断として残す。
