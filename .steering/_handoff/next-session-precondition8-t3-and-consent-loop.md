# 次セッション — 前提条件8（precondition8）＋ T3 実装 ＋ consent.md 文言更新（Loop 一括）

> 作成: 2026-09-27（前段 `.steering/20260927-o1-receipt-ledger/` の完了直後・PR #235 merge 済み・main=`a8b1234`）。
> ⚠️ **このメモを一次資料にしない。** 数字・状態は着手時に測り直す。
> ★ この 3 本（precondition8・T3・consent 文言）を **1 つの Loop バッチ**として回す方針（研究者 2026-09-27 決定）。
> ⚠️★★★ **O1 台帳の配備は前段セッションで完了済み**（`GSE_O1_ledger` プロジェクト・トリガー稼働中）。本タスクの対象外。

## §0 打ち込む用（★ まず Opus に切り替えてから開始する）

```
/model opus
```
に切り替えた後、続けて:

```
.steering/_handoff/next-session-precondition8-t3-and-consent-loop.md を読んで、次を進めてください。
  A: precondition8（validate_blocks.py の未完了マーカー対応／analyze.py:196-200 の n 未達ゲート見直し／G1 の人単位記録破棄手順の文書化）
  B: T3 人単位ライフサイクル台帳の実装（状態ログ＋導出方式・O1 参考列は手で写す・研究者裁定済み）
  C: consent.md をフォーム説明文の言い回しに合わせて更新する下書き（最終反映は研究者）
⚠️ まず git pull --ff-only。/start-task（task 名: precondition8-t3-and-consent）を実行し、
   grilling skill で残りの判断分岐を閉じてから requirement.md を確定する。
★ 確定したら issue-slicing skill（Opus）で .steering/precondition8-t3-and-consent/issues/00X.md に縦切りする。
⚠️★★★ issue 分解が終わったら **/clear して新セッション**で loop 実行を始める（分解セッションに実行を持ち込まない）。
⚠️ consent.md・participant-guide 等の被験者向け文書は契約。**最終反映は研究者承認が要る**（下書きまでは loop で作ってよい）。
Skill: verify-before-claiming・grilling・issue-slicing・subagent-delegation・data-privacy（validate_blocks.py/analyze.pyはPIIなし想定だが確認）。
応答は日本語。
```

## §1 現在の状態（2026-09-27・測り直し済み）

| 何 | 値 |
|---|---|
| main | `a8b1234`（PR #235 merge 直後 + O1 配備記録の docs commit）。push 済み・CI 発火確認済み |
| O1 台帳の配備 | ✅ **完了**（`.steering/20260927-o1-receipt-ledger/decisions.md` 末尾「配備完了」節）。第3プロジェクト `GSE_O1_ledger`・スクリプトプロパティ3件設定済み・`o1LedgerRun` トリガー稼働中（6時間ごと・エラー通知=今すぐ） |
| O1/G1 ゲート | 前段と不変（本タスクではコードを変えていない）。着手時に `bash scripts/check-o1-release-readiness.sh` / `check-g1-collection-readiness.sh` で測り直すこと |

## §2 タスク

### A. precondition8（3 サブ項目・すべてコード/文書レベル）
一次: `.steering/_handoff/next-session-g1-o1-release-and-o1-resilience.md:103`「第 20 版の規則を実行する計器（`validate_blocks.py` の未完了マーカ・`analyze.py:196-200` の n 未達ゲートの見直し）と G1 の人単位の記録破棄手順」。

**A-1. `validate_blocks.py` の未完了マーカー対応**
- 現状（一次・`validate_blocks.py:614`）: `validate_blocks.py` は**転記ミスの検出だけ**を行う設計（`README.md:614`「検証は `--selftest`。⚠️ 除外も判定も足さないこと（足した瞬間に `§3.6` に触れる）」）。
- 第 20 版（`preregistration.md` §「9 マス」(i)）が要求するのは「1 つも開始していない人」の判定基準（課題ページの開始ゲート／アプリの「開始する」を押したか。実験者の実施記録で確認）。★ **除外や判定を足すのではなく**、①既に集めている情報（ブロックファイルの有無・打鍵行数）から「未完了」「開始していない」の**状態を報告するだけの新しいチェック関数**を足す形にする（`§3.6` に触れない＝除外はしない）。
- **決めること（grill）**: 「開始していない」の判定に**実験者の実施記録**（手入力）を要求するか、機械的に判別できる範囲（開始ゲート通過のログ有無）に留めるか。

**A-2. `analyze.py:196-200` の n 未達ゲート見直し**
- 現状（一次・`analyze.py:196-200`）: `len(conf) < n_subjects` が真なら**無条件で** `[NG]`（optional stopping 防止のため）。
- 第 20 版 `§3.9`（`preregistration.md:1397` 他）: 削除・やめる等で確証標本が **n=1 に縮んでも解析は成立する**（Fisher 統合はしない・個人内 p を報告）。**完了者 0 名なら確証解析は行えない**（NG のまま）。
- ⚠️★★★ **区別が必要**: 「まだ集まっていない」（n=3 凍結・現在 2 名収集済み → 収集完了まで見ない、が正しい＝NG のまま）と「収集は完了したが離脱で n が縮んだ」（→ n=1 でも解析してよい）を、**どう機械的に見分けるか**が本サブ項目の核心。一次に既にある手掛かり: 第 20 版 (i) 例外は「名簿から外す判断は研究者が行う」としている → 研究者が名簿から外した（config.json 更新）ことを「収集完了とみなす」トリガーにする案が有力（`t3-person-ledger-design.md` の「名簿から外す判断の記録書式」と接続する）。
- **決めること（grill）**: 「収集完了」を判定する具体的なシグナル（config.json の版・別フラグ・ロスターの状態列）。

**A-3. G1 の人単位の記録破棄手順**
- 現状: `docs/o1-deletion-ledger.md` は O1 専用。**G1 には対になる文書が無い**（`grep -rl "破棄手順"` で確認済み・2026-09-27）。
- consent.md §5「後からデータの削除を求められます」の約束を G1 でどう履行するか（対象ファイル: 個人別 block NDJSON・`sample_roster` の該当行・`Form_G1` 側の登録ログ）を文書化する。**`docs/o1-deletion-ledger.md` を型として流用**してよい（tombstone 規則・A-1〜A-14 形式の踏襲）。
- **スコープ外**: 実装（自動化）は不要。まず**手順の文書化**（研究者が手で実行できる形）。

### B. T3 人単位ライフサイクル台帳（実装）
一次: `.steering/20260927-o1-receipt-ledger/t3-person-ledger-design.md`。**研究者裁定済み（2026-09-27）**:
- 方式 = **状態ログ＋導出**（§2.2 のとおり実装する）。
- O1 参考列（最終受領日・受領本数）= **手で写す**（結合ゼロ・IMPORTRANGE は不採用）。

**まだ未決（design.md §3 に残る点。着手時に grill で閉じるか、display-only のまま進めるか判断）**:
1. 未実施のまま長期の期限の日数（第 20 版で未決）→ 設計は「決まるまで経過日数の表示だけ・判定はしない」としているので、**この値が無くても実装は進められる**。
2. G1 の受領も台帳化するか → 設計は「本設計では自動化しない」としているので、**スコープ外のまま進めてよい**。
3. 名簿から外す判断の記録書式 → A-2 の「収集完了トリガー」と関係するので、**A-2 と一緒に grill で決める**（同じ判断が両方に効く可能性が高い）。

**成果物**: 別スプレッドシートのテンプレート（研究者のみ閲覧・共有しない・数式のみ・スクリプトなし。設計文書 §2.2-2.4 のとおり）。★ **実データは研究者が入れる**（ダミー P-ID で矛盾検知（設計 §2.4）を赤・黄・緑の3状態で確かめてから引き渡す）。

### C. consent.md の文言更新（下書きまで）
一次: `.steering/20260927-o1-receipt-ledger/t2-record-a-draft.md`「consent.md ⇔ コード（別に確かめたこと）」の表。**研究者裁定済み（2026-09-27）**: consent.md をフォームの文言に合わせる方向。

具体的な差異（一次）:
1. 「短い中断」の限定表現: consent.md=「30秒未満・**中断が0回の分は記録しません**」／フォーム=「30秒より短いもの・**計測中のみ**」。
2. 同意第8項目: consent.md=「上記に同意して参加する」／フォーム=「打鍵の記録（本文を除く）と、その研究利用に同意します。」（内容が異なる・フォームのほうが具体的）。
3. ⚠️ `consent.md:178` の状態表「配布済み G1-C の8項目目の文言更新は未実施」は**実フォームと食い違っている**（実フォームは既にコードと完全一致・2026-09-27 `checkConsentFormParity` で確認済み）。この行自体を直すか、意味が別物か研究者に確認。

**やること**: consent.md の該当箇所の**差分案**を作る（`Form_G1/README.md`・`protocol.md §4.1-1` も同時に直す規約・`consent.md` 冒頭の注記どおり）。⚠️ **配布済みの実フォームには反映しない**（フォームの書き換えは別承認・`migrateConsentForm()` は実行しない）。consent.md 側の記述をフォームに合わせるだけであり、フォームを consent.md に合わせるのではない（研究者裁定の向き）。

## §3 Loop Engineering の適用方針

- **grill は Opus で行う**（`docs/loop-engineering.md` モデル割当ポリシー）。A-2・A-3・B の残り判断はここで閉じる。
- **issue-slicing も Opus**（7 基準・`docs/loop-engineering.md`）。縦切りの目安:
  - issue 1: `validate_blocks.py` の未完了マーカー検出関数 + テスト（A-1）
  - issue 2: `analyze.py` の n 未達ゲート改修 + テスト（A-2・§3.9 の n=1 個人内p報告を含む）
  - issue 3: G1 削除保証台帳の文書作成（A-3・コード変更なし）
  - issue 4: T3 テンプレートの数式・矛盾検知（B）
  - issue 5: consent.md 文言差分案（C・被験者向け文書なので `verify_level: recheck` 相当の慎重さ。実際の反映は研究者が行うため、issue の AC は「差分案の提示」までにする）
  - ⚠️ issue 1 と issue 2 は **同じファイル（analyze.py の周辺）を触らない**よう Allowed Files を分ける（`validate_blocks.py` vs `analyze.py`は別ファイルなので基準3は満たしやすい）。
- **verify_level**: A-2（データ判定ロジック）と C（被験者向け文書）は `recheck`。他は `parse` でよい。
- `/clear` 後の実行モードは、C（1〜2 issue の小規模）なので **モード B（orchestrator + subagent）** が過不足なさそう（モード C の無人運用ほどの規模ではない）。

## §4 ⚠️ 見落としやすい点
1. **`analyze.py` / `validate_blocks.py` は凍結された `preregistration.md §3.6` に触れない**（除外・判定を機械が決めない）。A-1・A-2 とも「報告するだけ」「研究者の判断を反映するだけ」の実装にする。
2. **`consent.md` は被験者向け文書＝契約**。差分案の作成までは Loop でよいが、**最終反映（コミット・ましてやフォームへの反映）は研究者承認**。
3. T3 のスプレッドシートは**研究者のみ閲覧**。共有設定・URL は repo に書かない。
4. `.codex/budget.json` は台帳（`git checkout --` で戻さない）。
5. **`git add -A` / `git add <dir>` は使わない**（明示パス指定）。
6. 作業ブランチを先に切ること（★ 前段セッションで main に直接コミットしてしまった事故がある。`git switch -c` を最初に行う）。

## §5 やらないこと
- O1 台帳の配備（完了済み）・G1/O1 の受け口（`doPost`）の変更。
- consent.md・フォームの**最終反映**（下書きまで）。`migrateConsentForm()` の実行。
- `preregistration.md §3.6` の除外規則自体の変更。
- T3 テンプレートへの実 P-ID の入力。
- G1 の削除保証の**自動化実装**（今回は文書化のみ）。

## §6 一次資料（読む順）
1. `.steering/20260927-o1-receipt-ledger/decisions.md`（前段の判断・O1 配備完了の記録）
2. `.steering/_handoff/next-session-g1-o1-release-and-o1-resilience.md:37,103`（precondition8 の出所）
3. `experiments/20260801-controlled-friction-task/preregistration.md`「9 マス」の表・§3.9・「公表物の書き方」
4. `experiments/20260801-controlled-friction-task/validate_blocks.py`・`analyze.py:180-210`
5. `docs/o1-deletion-ledger.md`（G1 版の文書化の型）
6. `.steering/20260927-o1-receipt-ledger/{t3-person-ledger-design.md, t2-record-a-draft.md}`
7. `experiments/20260801-controlled-friction-task/consent.md`（§5・記録項目表・同意チェック欄）・`Form_G1/GSE_G1_Form_Builder.gs:238-241,297-308`（`consentItemTitles_` / フォーム説明文）
8. `docs/loop-engineering.md`（実行前に必ず）
