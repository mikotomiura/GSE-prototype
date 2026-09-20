# review-D: 評価契約群（`.steering/20260916-gse-theory-operationalization-review/`・14 ファイル・約 2,000 行）

> Status: pre-SSOT レビュー。⚠️ 判定は**提案**であり、採否は研究者が決める。
> 読了: 2026-09-18・`design.md` / `decisions.md` / `next-task.md` / `requirement.md` / `tasklist.md` / `theory-propagation-audit.md` /
> `core-proposition-coverage-matrix.md` / `core-cs-` / `core-art-` / `bridge-dn-evaluation-contract.md` / `measurement-dictionary.md` /
> `eval-ncc-analysis-contract.md` / `eval-ncc-dag.md` / `gr-h4-h9-h11-h12-falsification-table.md` を全文通読。

## 0. 総評（D 固有）

- ★ **方法論としての完成度は高い** —— IAS（opportunity-level ITT）・post-treatment 調整の禁止・競合転帰・欠測の 5 区分・
  intersection-union の共同 gate・`negligent relinquishment` の負の対照・「帰無を棄却できないことを支持に読まない」。
  これらは SSOT 化してよい水準である。
- ⚠️★★★ **ただし「何を評価するか」の側が 3 点で既存 SSOT とずれている**:
  1. **後続転帰の語彙**（再開・再停止・外部化・離脱）が ADR-029 D5 の不採用語彙（→ D-C1）。「再停止」の定義は ADR-030 の条件 A と別物（30 秒の主課題イベント途絶）。
  2. **CORE-CS の停止対象が現行 GSE に存在しない** → positive control（`CS-C0`）が作れない（→ D-C2・J-3）。
  3. **「支援到達可能性」「応答分岐（受容・保留・拒否）」が既存の招待設計（ADR-018 / 021 / 026 / 027）の上に置けるか未検証**（→ `ssot-collision-findings.md`）。
- ⚠️ 評価対象の課題（GR-H11 の AI 助言つき判断課題・誤受容の客観正答）は、research-positioning のスコープ
  （正解も mastery 判定も無い論述作業）の**外**にある（→ D-C4・J-7）。

## 1. 主張台帳

### 1.1 構造・方法（design / decisions / coverage matrix）

| ID | 箇所 | 主張の要約 | 種別 | 根拠 | 既存 SSOT との関係 | 判定 |
|---|---|---|---|---|---|---|
| D-01 | `design.md` Workstream A | 4 構成概念（負担・第二作業化・判断品質・誤受容）の暫定測定境界 | 定義 | — | 新規 | **保持**（→ D-10〜D-17 で操作化済みのものは統合） |
| D-02 | `design.md` Workstream B | 体系的差分レビューの 7 束 | 計画 | — | 別トラック tasklist で未着手 | **保持**（段 2 と統合） |
| D-03 | `design.md` C0 / `decisions.md` 2026-09-17 | 理論と命題の階層分離（2 理論・下位・評価測定・構成・命題） | 定義 | — | A §1.1 と同一 | **統合**（A の表 1 本に） |
| D-04 | `design.md` Workstream D | 判定語 保持・統合・縮小・棄却 | 定義 | — | 本レビューも同じ語を使用 | **保持** |
| D-05 | `design.md` Workstream E / A 横断 | 測定妥当性と表現・介入妥当性の 2 軸・証拠階梯 E0〜E5 | 定義 | — | A の EH0〜EH5 と同一（記号が `E` と `EH` で揺れる） | **統合**（`EH` に一本化。⚠️ C §4.2 の `E0`〜`E4` と衝突するため） |
| D-06 | `core-proposition-coverage-matrix.md` §1-§6 | 全 GR-H1〜H12 の primary owner を 1 つに固定。競合の裁定 5 件。整合性検査 | 計画・規則 | — | 新規 | **保持**（★ 昇格時の骨格） |

### 1.2 CORE-CS 契約

| ID | 箇所 | 主張の要約 | 種別 | 根拠 | 既存 SSOT との関係 | 判定 |
|---|---|---|---|---|---|---|
| D-07 | `core-cs` §3-§5 | 観測単位 `build × trace × stop episode × consumer`。`T_stop` / `T_allow` / restart contract の registry を版付きで凍結。停止閉包・forbidden event 0・recapture 0・bounded continuation | 評価量 | — | ⚠️ `T_stop` に載せる処理が**現行 GSE に無い**（画面外推論・達成認定・報酬は ADR-017 D10 / ADR-018 D1 / ADR-025 で最初から無い）。⚠️ 一方、**実在する「再捕捉」**は `intervention.rs:6` `RECENT_DISMISS_MS`（dismiss を次の判定へ戻す）と ADR-008 D1 の効用更新 | **保持（枠）**／⚠️ `T_stop` の中身は **J-3** |
| D-08 | `core-cs` §4 `CS-C0`〜`C4b` | 連続認定 / 見かけ上の停止（sham）/ SS / SS＋義務終了＋非再捕捉 / timeout / disconnect | 実験条件 | — | ⚠️ `CS-C0`（positive control: 対象処理が実際に発生する）は、J-3 で停止対象を実在処理から取らない限り**構成不能**。`CS-C4a/b` の区別は ADR-027 D5（解除 ≠ 断）/ ADR-028（失効は曝露の契機で判定・系は断を監視しない）と要照合 | **保持**（J-3 に従属） |
| D-09 | `core-cs` §6 | 時点 `W-pre` / `t_request` / `t0` / `W-drain` / `W-post-near` / `W-post-delay` / `W-restart` | 定義 | — | ⚠️ **記号 `t0` が ADR-030 の `stall onset` の `t0` と衝突**（同じレビュー対象の EVAL-NCC / T1d が ADR-030 の `t0` を使う） | **保持**（中身）＋ 記号を `t_stop` 等へ改める |
| D-10 | `core-cs` §15 | 限定サーヴェイ（Horvitz / Scerri / Fogarty / Orseau / Hadfield-Menell / NIST / Amershi / Satchell / OECD）と引用射程の裁定 | 根拠の射程 | ⚠️ 9 件中 **Horvitz 以外は未登録**、Horvitz は [P42] が別キーで登録済み（`citations-audit.md`） | 新規 | **保持**（射程の書き方）＋ 登録 |

### 1.3 CORE-ART 契約

| ID | 箇所 | 主張の要約 | 種別 | 根拠 | 既存 SSOT との関係 | 判定 |
|---|---|---|---|---|---|---|
| D-11 | `core-art` §4 `ART-C0`〜`C6`・経路操作 | widget / 装飾 / Portrait / Aperture / 見かけ上の終了 / SS / failure。同終点異経路・異終点類似経路・endpoint-only | 実験条件 | — | 整合（A-26 の replay prototype） | **保持** |
| D-12 | `core-art` §5 | 構成概念 13（path distinguishability … self-quantification reading）を合算しない | 評価量 | — | ⚠️ `self-relatedness`（本人が当該セッションの実践との関係を認める）は**本人のトレースを要する** —— 同契約 §4「初期 artifact は合成 fixture を正とする」とは両立しない（合成 fixture で測れるのは外部観察者の読みだけ） | **保持** ＋ ⚠️ self-relatedness は「本人トレースを使う段（EH2/EH3）でのみ測る」と明記 |
| D-13 | `core-art` §5 `termination-as-form` / §7 Termination family | 終端が故障でなく形式として読まれる（forced choice: termination / failure） | 評価量 | — | ⚠️ **ADR-027 D4**（解除の理由を載せない・受諾 / 本人の失効 / 時間切れを区別する値も文言も置かない）＋ **ADR-021 D9**（本人が検証できない区別を表示しない）と緊張。★ ただし ADR-027 **D5** は解除（縁だけ閉じる）と断（層 0 へ縮退）を**見た目で分けている**ので、「意図的終端 vs 断」の弁別は SSOT 内に足場がある | **保持**（「意図的終端 vs 断」に限定）／「意図的終端 vs 時間切れ」の表示上の弁別は **J-9** |
| D-14 | `core-art` §7.2 codebook 14 コード | 二重 coding・一致度・negative case | 評価量（手続き） | — | 新規 | **保持** |
| D-15 | `core-art` §15 | 限定サーヴェイ（Boden & Edmonds / Eco / Data Portraits / Offenhuber / Gaver / Sengers / Höök / Etkin / UbiFit / de Montjoye / Cage・Hsieh・Lozano） | 根拠の射程 | ⚠️ 過半が未登録・Offenhuber / Eco は草案間で版が不一致 | 新規 | **保持**（射程の書き方）＋ 登録 |

### 1.4 BRIDGE-DN 契約

| ID | 箇所 | 主張の要約 | 種別 | 根拠 | 既存 SSOT との関係 | 判定 |
|---|---|---|---|---|---|---|
| D-16 | `bridge-dn` 全体 | 計算機自然の内部での局所的非認定という狭い接続命題。借用範囲マトリクス・反例・主張禁止線 | 接続命題 | Ochiai 2018/2026・Weiser ほか（全件未登録。Digital Nature は書籍一次未読と自認） | 新規 | **統合候補** —— 同契約 §9 の統合条件（「差分が CORE-CS の停止可能性を別語で述べるだけなら統合」）に現状該当する。⚠️ 残す理由が未踏の文脈（PM との接続）にあるなら研究者判断 **J-6** |

### 1.5 EVAL-NCC 契約（測定辞書・分析契約・DAG・反証表）

| ID | 箇所 | 主張の要約 | 種別 | 根拠 | 既存 SSOT との関係 | 判定 |
|---|---|---|---|---|---|---|
| D-17 | `measurement-dictionary` §2-§4 | 判断品質 `DQ`・誤受容 `EA_cond`・無検証依存 `UVR_risk` の定義と許容幅の決め方（標本サイズから逆算しない） | 評価量 | [P127]/[V37]・[P366] | ⚠️ **客観正答を持つ判断課題が前提** —— research-positioning のスコープ（正解も mastery 判定も無い論述作業・RP:638 / RP:1449）の外 | **保持**（GR-H9/H11 用）＋ スコープの拡張は **J-7** |
| D-18 | `measurement-dictionary` §5 | 支援到達可能性 `SA_success`（最大手順数・時間内に支援へ到達できた割合）。利用率の低さは失敗としない | 評価量 | — | ★ ADR-026 PC-4（「必要時には届く」を要件にしない）とは**別の構成概念**（PC-4 = 系 → 人の push、SA = 人 → 支援の pull）で衝突しない。⚠️ ただし **GSE に支援機能は存在しない** —— 支援を担うのは課題環境（GSE の外）だと明記しないと、GSE に機能を足す話になる。⚠️ 「支援利用」を媒介として調整禁止にしているが、**ADR-024 では外部から答えを受け取ること（受領 = paste）が主イベント**であり役割がずれる | **保持**（別構成概念と明記・支援の担い手を課題環境に置く） |
| D-19 | `measurement-dictionary` §6-§9 | 罪悪感・応答義務・不利益予期・放置不安を各 2 項目で測る（7 件法・独自候補・認知インタビュー前） | 評価量 | 無し（既存尺度未選定と自認） | 新規 | **保持**（候補として）＋ **要サーヴェイ**（S6b: 既存尺度 —— falsification-table §9 の限定調査 1 と同じ） |
| D-20 | `measurement-dictionary` §10-§11 | 欠測 5 区分（STR / TECH / OBS / SEL / ADMIN）と共同判定規則 | 規則 | — | 整合（PreReg-7 の MNAR 上下限・ADR-013 D4 の「信号が無い／計器が無い」） | **保持** |
| D-21 | `eval-ncc-analysis-contract` §2 C0〜C4 | 無招待 / 命令＋receipt / SS＋残存義務 / SS＋義務なし＋最小支援 / negligent relinquishment（低リスク模擬課題・短窓・事後説明） | 実験条件 | — | ⚠️ C1「命令＋完了確認」・C4「支援経路を意図的に欠く」を製品の禁止（ADR-018 D1 完了判定なし）とどう切り分けるかは `ssot-collision-findings.md`。★ 倫理面は **研究倫理審査の対象**（C4 は事後説明必須） | **保持**（研究条件として）＋ 倫理手続きを明記 |
| D-22 | `eval-ncc-analysis-contract` §3 | 最小支援義務 6 項目 | 定義 | — | 新規 | **保持** |
| D-23 | `eval-ncc-analysis-contract` §4-§5 | IAS（全割付機会）・副次集団の禁止事項・6 分岐（受容 / 保留 / 拒否 / 見逃し / 意図的無応答 / 判別不能）。見逃しと意図的無応答はログから推定せずブロック末 probe | 定義・規則 | — | ⚠️★★★ **「受容」の二重定義（X-04）** —— SSOT（ADR-018 `:117`）の受容は「提示に対して**離席が起きたか**」（行動）であり、`expression-channel.md` PC-9 / A20 は「**受諾を記録する経路はコードに 0 件**・受諾率を直接測れると書かない・その非対称を評価設計に明記せよ」。★ PC-12 は受諾・拒否の**操作 UI** を要求しているので UI は既定路線、崩れるのは「受諾を記録しない」側。⚠️ 「保留（later）」は SSOT に規定も禁止も無い（新規）。⚠️ ブロック末 probe は反復設計では ADR-023 `:344` の反応性（X-18） | **保持**（方法論）／ 「受容」の語と記録の可否は **J-13**・実施場所は **J-16** |
| D-24 | `eval-ncc-analysis-contract` §6 | 後続転帰: 再開（主課題チャネルの最初の有効作業イベント）/ **再停止（再開後に主課題イベントが連続 30 秒以上途切れる最初の時点）**/ 外部化 / 離脱。first-event の CIF、再停止は multi-state 副次 | 評価量 | — | ⚠️★★★ **衝突** —— (a) 語彙は ADR-029 D5 が採らなかった第三語彙（「離脱」は `left_observation` と打ち切りを混ぜる）、(b) 「再停止」は ADR-030 の条件 A（純産出）と別の定義 → **定義が 2 つになる**（研究者判断 25 #9 が禁じた状態） | **縮小** —— 語彙を ADR-009 D2 / ADR-029 D2 へ戻し、再開・再停止を ADR-030 の条件 A の辺から一意に定義（→ `definitions-restop-t1d-t1c.md`） |
| D-25 | `eval-ncc-analysis-contract` §7 | 主要 estimand `τ = E[Y(C3)] − E[Y(C2)]`、4 gate の階層、GR-H4 は C3 対 C1、分岐別は記述的、principal stratification は感度分析のみ | 評価量 | 方法論 | 新規 | **保持** |
| D-26 | `eval-ncc-analysis-contract` §8-§11 | 推定モデル・非劣性マージンの決め方（blind vignette・EH3 pilot は分布確認のみ）・欠測処理・調整禁止 | 規則 | 方法論 | 整合（preregistration の forking paths 排除） | **保持**（★ SSOT 化の価値が高い） |
| D-27 | `eval-ncc-dag` 全体 | ノード 14・主 DAG・調整禁止ノード・無応答の DAG・競合転帰の状態図・媒介の境界・負の対照の役割・脅威 6 | 規則 | 方法論 | 整合 | **保持**。⚠️ 状態図の `Restopped` / `Externalized` / `Exited` は D-24 の語彙修正に従う |
| D-28 | `falsification-table` §1-§3 | GR-H4 / H9 の判定表と二重台帳の操作（C2/C3/C4） | 実証予測の判定規則 | — | 整合（D-25 と一致） | **保持** |
| D-29 | `falsification-table` §4 | GR-H11 独立ミニ実験（zero / light / heavy friction・客観正答・AI 提案の正誤を固定比率で混ぜる） | 実験計画 | [P127]/[V37] | ⚠️ 中身は Buçinca 2021 の cognitive forcing の**追試・拡張**。GSE 本体（AI 助言系ではない）の検証ではない | **縮小** —— TH-GR の境界条件の検証として保留（**J-7**） |
| D-30 | `falsification-table` §5 | GR-H12: AFS の許可用途・禁止用途、予測研究の手順（基準モデル先行・holdout・校正・群別誤差）。失敗時は派生仮説だけを棄却 | 規則 | [P362] | 整合 | **保持** |
| D-31 | `falsification-table` §6-§7 | マージン決定表（全 unresolved）・敵対的レビュー 8 攻撃 | 規則 | — | 整合 | **保持** |
| D-32 | `theory-propagation-audit.md` | 三文書間で主張反転なし・概念整合は高い・実証操作化は未完・[P361]-[P367] を登録 | 監査（自己評価） | gpt-5.5 の独立監査 2 本 | ⚠️ 「主張反転なし」は草案**間**の照合であり、**SSOT との照合をしていない**（本レビューで衝突が複数出た） | **縮小** —— 「草案間の伝播監査」と明記 |

## 2. SSOT との衝突（D）

| # | 重大度 | 草案 | SSOT（一次） | 内容 |
|---|---|---|---|---|
| D-C1 | HIGH | `eval-ncc-analysis-contract` §6・`eval-ncc-dag` §6（D-24, D-27） | ADR-029 D5 / ADR-009 D2 / ADR-030 D3 | 語彙の衝突と「再停止」の二重定義 |
| D-C2 | HIGH | `core-cs` §4-§5（D-07, D-08） | ADR-017 D10 / ADR-018 D1 / ADR-025 ／ ADR-008 D1・`RECENT_DISMISS_MS` | 停止対象が空、positive control が作れない。実在する再捕捉は SSOT 内にある |
| D-C3 | MEDIUM | `core-art` Termination family（D-13） | ADR-027 D4 / ADR-021 D9 | 終端の種類を本人に弁別させる設計と「理由を載せない・検証できない区別を表示しない」の緊張 |
| D-C4 | MEDIUM | `measurement-dictionary` §2-§4・`falsification-table` §4（D-17, D-29） | research-positioning のスコープ（RP:638 / RP:1449） | 客観正答つき判断課題は現行の研究スコープ外 |
| D-C5 | MEDIUM | `core-cs` §6 の `t0`（D-09） | ADR-030 D2 の `t0` | 記号衝突 |
| D-C6 | LOW | `theory-propagation-audit`（D-32） | — | SSOT 照合なしの「整合」判定 |

### 統合表（`ssot-collision-findings.md`）から D に当たる行

| X-ID | 重大度 | D の行 | 一言 |
|---|---|---|---|
| X-01 / X-02 | HIGH | D-24, D-27 | 語彙・「再停止」の定義（D-C1） |
| X-03 | HIGH | D-25（主要 estimand） | 「coupling as primary outcome」の中身が ADR-023/024 と別物 —— 契約は ADR-023/024/025/026/029 を**一度も参照していない**（grep 実測・◻） |
| X-04 | HIGH | D-23 | 「受容」の二重定義 |
| X-07 | HIGH | D-08（gate 7・restart safety） | ADR-028 D4「失効まで最後の組を描き続ける」等、Accepted の設計が引き受けた代償と正面衝突 |
| X-08 | HIGH | D-08（CS-C4b の retry・failure code）、D-13 | 生存信号を作らない・断を監視しない・理由を載せない（ADR-028 / ADR-027） |
| X-17 / X-18 | MEDIUM | D-21, D-19, D-23 | 研究対照・probe・自由記述の**実施場所**（本体か別計器か） |
| X-20 | MEDIUM | D-09 | `t0` の三義 |
| X-27 | LOW | `measurement-dictionary` §1 の W0 expiry | glossary「チャネルの失効」と二義・未決の PS-Q10② を暗黙に決める |
| X-29 | LOW | D-23 | 評価量「拒否理由」と Gate H が分岐体系から消えている |

### 禁止用語（機械検査）

- 実検査: **違反 0 件**。「回復」13 行はすべて否定形（「回復と呼ばない」「認定しない」）。
  `next-task.md:40` の「完了条件」・`coverage-matrix:24` の「completed」は Physical Anchor の文脈でなく、規則 2 の射程外。

## 3. サーヴェイが要る箇所

| ID | 対象 | 問い | 優先 |
|---|---|---|---|
| S6b | D-19 | 罪悪感・応答義務・不利益予期・放置不安・支援到達可能性の既存尺度（日本語版の有無・弁別妥当性） | 中（EH3 前まで） |
| S1 | D-07（CORE-CS §15 の続き） | mixed initiative / adjustable autonomy / handover の体系的レビュー | 高（A/B と共通） |
| — | D-16 | Digital Nature の書籍一次（J-6 で残すと決めた場合のみ） | 低 |

## 4. 研究者判断が要る箇所

- **J-3** CORE-CS の `T_stop` を現行 GSE のどの処理から取るか（D-C2）
- **J-6** BRIDGE-DN の扱い（D-16）
- **J-7** GR-H11 と客観正答つき課題を研究スコープへ入れるか（D-C4）
- **J-9** 「意図的終端 vs 時間切れ・本人の失効」を表現上で弁別させる設計を、ADR-027 D4 を上書きしてまで採るか（D-C3）
- **J-10**「再停止」の定義（D-C1）→ `definitions-restop-t1d-t1c.md`

## 5. 別トラックの未チェック受け入れ条件の判定（`requirement.md` §受け入れ条件）

| 受け入れ条件 | 判定 | 根拠 |
|---|---|---|
| 四構成概念について、定義・非該当例・観測指標・主要/副次評価量・交絡・失敗条件が表になっている | ⚠️ **部分充足** | 判断品質・誤受容は `measurement-dictionary` §2-§3 で充足。⚠️ **負担**（interaction / verification burden）と**第二作業化**は項目・算出式が無い（`design.md` の境界文と CORE-ART の `interpretation burden` に名前があるだけ） |
| 負担低減と判断品質維持を別々に判定でき、誤受容とのトレードオフが明示 | ✅ **充足** | analysis-contract §7.1 の 4 gate・falsification-table |
| 第二作業化が所要時間・主観的不快感と区別 | ⚠️ **未充足** | 境界文（`design.md`）のみ。操作的定義・項目が無い |
| 検索式・採否基準・検索日・DB・抽出表を第三者が再実行できる | ❌ **未充足** | 限定サーヴェイの検索日と検索式はあるが、DB・採否基準・抽出表・除外理由が無い（自認: tasklist「体系的レビューと呼べる再現性があるか監査する」が未チェック） |
| 類似概念ごとに既知要素・結合差分・残る衝突・縮小条件 | ⚠️ **部分充足** | B §6 と各契約 §15 の表。⚠️ ironies of automation / moral crumple zone / handover / nudge 倫理が欠落（S1/S2） |
| CS・芸術・規範命題がそれぞれ一つの中核命題と複数の反証・反例条件に縮約 | ✅ **充足**（CS / 芸術）／ ⚠️ **部分**（規範） | CORE-CS / CORE-ART 契約は反証・反例表を持つ。CORE-NORM は EVAL-NCC に委ねられ、**CORE-NORM 固有の反例表（父権的介入・放置的返還・負担転嫁・再捕捉の 4 判別）は無い** |
| 規範命題が父権的介入・放置的返還・負担転嫁・再捕捉を別々に判定できる | ⚠️ **部分充足** | 放置的返還（C4 対照）・負担転嫁（C2 対照）・父権的介入（C1 対照）は条件として分離済み。⚠️ **再捕捉**は CORE-CS の実装監査にあるが**規範命題の判定表に入っていない** |
| 「非支配的協調」を共和主義的非支配と同一視しない、依拠と差分を明示 | ⚠️ **部分充足** | 同一視しないは明記（B L27・A L168）。⚠️ **依拠と差分は未記述**（サーヴェイ S2 が要る） |
| Digital Nature との接続が停止可能性として境界づけ | ✅ **充足** | BRIDGE-DN 契約 §2・§10 |
| 横断中核・DN 接続・構成命題・実証予測が別系列で番号づけ | ✅ **充足** | A §1.2・coverage matrix |
| 下位理論・評価測定モデルの整理 | ✅ **充足** | A §1.1 |
| 既存三文書の用語・研究ゲート・論文計画が更新結果と一致 | ⚠️ **部分充足** | 草案間は一致（theory-propagation-audit）。⚠️ C の記号衝突（`E1`〜`E4` の二重使用・`O1`）と Q の完了が未反映 |
| 未実証の因果・新規性・一般化・ジャンル成立を断定していない | ⚠️ **ほぼ充足** | 断定は無い。⚠️ A L178-180 の一般化（「一般化しうる」）と A §0 の「概念的成立: 高い」は格が高すぎる（A-01 / A-11） |
| AI 実装を受容・介入効果の証拠として扱っていない | ✅ **充足** | EH 階梯・各契約の主張禁止線 |
| 本人の自己使用を実行可能性・計器監査の段階に位置づけ | ✅ **充足** | EH2 |
| Mh-D の測定妥当性と受容性を別の研究質問とゲートで検証 | ✅ **充足** | `design.md` Workstream E・C の RG-3 / RG-4 / RG-5 |

## 6. ★ S2 サーヴェイの結果による更新（2026-09-19・`docs/literature/20260919-non-domination-and-autonomy-norms.md`）

| 受け入れ条件 | 旧判定 | ★ 新判定 | 根拠 |
|---|---|---|---|
| 「非支配的協調」を共和主義的非支配と同一視せず、**依拠と差分**を明示 | ⚠️ 部分充足（依拠と差分は未記述） | ★ **依拠と差分を記述できた（段 3 で草案へ反映待ち）** | 依拠: 統制された介入の条件（継続的統制・事後の透明性・choices over choices [P380]）・罰を付けない選択肢・自律 ≠ 独立 [P382]。⚠️ 非支配は能力を問い放置を問わない → **語の誤読の危険**（改名を推奨）。差分の候補: 見逃し可能性・非再捕捉性・意味認定と応答要求の終了（主流と逆向き・今回の範囲で 0 件） |
| 規範命題が父権的介入・放置的返還・負担転嫁・再捕捉を別々に判定できる | ⚠️ 部分充足 | ⚠️ **部分充足（変わらず）** | ★ ただし「父権 / 放置 / その間」の三項構図は SDT circumplex [P390]・医療倫理 [P391] に既出 → CORE-NORM は構図を**借りた**と書く |

★ **GSE 本体への含意（研究者判断の候補）**: [P380] の基準では、招待を出す時期・有無を系が決め本人が統制できない限り「非支配」とは言えない。⚠️ 状態に合わせた働きかけは操作として非難されうる [P386]（Stuck 推定時の Nudge と同じ構造）。
