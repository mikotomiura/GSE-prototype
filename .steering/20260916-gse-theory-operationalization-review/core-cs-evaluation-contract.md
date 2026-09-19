# CORE-CS 評価契約 v0.1

> Status: pre-SSOT evaluation draft / 2026-09-17
>
> 本書は `CORE-CS` を反証可能にする作業契約であり、実装仕様、事前登録、確立尺度、SSOT ではない。現行コードに `invitation` と Semantic Stop の実装は確認できないため、実装済みとは扱わない。


> ★★★ **2026-09-19 の改訂（段 3 の単位 g・`.steering/20260919-ssot-g-core-cs-contract/`）** —— 研究者が裁定した事項と機械的な規則だけを当てた。
> - **J-3**（理論レビュー 判断 1 #2）: `T_stop` を**現行 GSE に実在する処理**から取る → §5.0 に候補を書いた（ADR-033 と対応）。
> - **J-9**（同 #10）: 表現上で弁別させる終端は「**解除（縁だけ閉じる）と断（層 0 へ縮退）**」の範囲に限る（ADR-027 D5）→ §5.3・§7.2 を狭めた。
> - **J-6**（同 #16）: BRIDGE-DN を独立の接続命題にせず、**本契約の比較節**（§16）として統合した。
> - **J-16**（同 #12）: 陽性対照（`CS-C0`）と見かけ上の停止（`CS-C1`）は**研究用の別計器**（ADR-012 型）でだけ作る。GSE 本体・O1 に入れない。
> - **J-4 / ADR-033**: 非再捕捉の数え方から**控える向きの利用（`RECENT_DISMISS_MS` 型）を除く**（§5.2）。
> - 機械的な規則: 停止成立の時点の記号 `t0` を **`t_stop`** へ改めた（11 か所。★ ADR-030 の `stall onset` の `t0`・ADR-024 D4 の再開時刻・ADR-029 D2 の報告トラックの `t0` と衝突するため）。⚠️ `t_stop`（時点）と `T_stop`（対象の集合）は大文字と小文字しか違わないので、読むときに取り違えない。
> - ⚠️ **未処理**: 前段のレビューの X-07 / X-08（ADR-028 の失効・終端の表現）は本改訂で扱っていない（J-9 の縮小だけを当てた）。
> - ⚠️ §15 の文献の多くは `docs/references.md` に未登録（`.steering/20260918-theory-critical-review/citations-audit.md`）。

## 1. 命題と理論的親

**命題**: 適応システムでは、いつ主導権を取るかだけでなく、いつ推論、意味認定、達成認定、応答要求を終えるかを、監査可能で非再捕捉的なシステム境界として設計しなければならない。

- 理論的親: `TH-GR`
- 主な機構: `SUB-SWM`、Semantic Stop Boundary、O/I/F/V/C/R の権限台帳
- 主担当命題: `GR-C1/C2/C4`、`GR-H3/H7/H8`
- 副担当: `GR-C7` と `GR-H9/H11` の処理境界。人間側の主要判定は EVAL-NCC を参照する。
- `GR-H5` では非再捕捉の実装前提だけを担当し、gaming の主要判定は CORE-ART に置く。

## 2. 含む範囲と含まない範囲

### 含む

- 停止対象となる event、field、state transition、downstream consumer の閉包
- stop request から停止成立 `t_stop` までの遷移と latency
- `t_stop` 後の意味推論、達成認定、報酬、ランキング、介入入力への再捕捉
- expiry、解除、再接続、再起動、遅延処理、別サービスを跨ぐ状態遷移
- 通常状態推定、認証、順序、期限、安全、必要な非評価的研究処理の bounded continuation
- 観測不足時の neutral / abstain への退化
- 意図的終端と failure / timeout / disconnect の弁別可能性（⚠️ 2026-09-19・J-9: **利用者側**に弁別させるのは解除 vs 断だけ（§5.3）。timeout / expiry との区別は**システム側**の遷移として §8 / §12 で扱う）

### 含まない

- `invitation: none`、表示消去、ウィンドウ非表示だけを停止と呼ぶこと
- システム全体の停止、計算環境全体の非計算化、自然への復帰
- 画面外の身体、成功、回復、遵守を推定・認定すること
- 低い応答率、再開、離席を成功指標とすること
- CORE-NORM の burden / quality / reliance / non-abandonment gate の再定義
- CORE-ART の作品成立や美的価値の主要判定

## 3. 観測単位、対象、証拠階梯

| 項目 | 契約 |
|---|---|
| 主要観測単位 | `build x fixed replay trace x stop episode x downstream consumer` |
| 停止 episode | 事前に定義した stop request、成立 `t_stop`、対象集合 `T_stop`、継続集合 `T_allow`、再接続条件を持つ一件 |
| システム対象 | 同一 build 内の event producer、state machine、queue、log/replay、遅延 job、外部 consumer |
| 利用者対象 | 対象利用者。実装監査を通過した build だけを EH3 以降へ送る |
| `EH0` | 概念、target registry、反例、比較条件の定義 |
| `EH1` | replay / log / test による停止閉包、非再捕捉、運用継続の監査 |
| `EH2` | 本人による計器・手順の確認。外部知覚の証拠にしない |
| `EH3` | intentional termination / failure、non-recapture、support continuation の読まれ方 |
| `EH4` | 監視感、system authority attribution、主タスク継続の統制比較 |
| `EH5` | 複数セッション、再接続、障害、異質性を含むフィールド監査 |

## 4. 条件と対照

| ID | 条件 | 停止する処理 | 残る処理 | 役割 |
|---|---|---|---|---|
| `CS-C0` | 連続推論・連続認定 | なし | 全て | active control |
| `CS-C1` | 表示だけ消える見かけ上の停止 | 表示のみ | 推論・認定・報酬は継続しうる | sham stop / 負の対照 |
| `CS-C2` | Semantic Stop | `T_stop` に登録した意味推論・認定・評価 | `T_allow` | 最小機構 |
| `CS-C3` | Semantic Stop + no residual response duty + non-recapture | `CS-C2` に加え応答・確認要求と再捕捉 edge | minimum support と `T_allow` | target |
| `CS-C4a` | timeout / expiry | 意図的 stop rule とは別 | failure policy に従う | 技術対照 |
| `CS-C4b` | disconnect / delivery failure | 到達不能により処理が欠ける | safety / retry policy | 技術対照 |

> ⚠️ **2026-09-19（J-16）**: `CS-C0`（対象処理が実際に作動する陽性対照）と `CS-C1`（禁止候補の処理が続く見かけ上の停止）は、**研究用の別計器（replay prototype・実験用アプリ）の中でだけ**作る。★ GSE 本体・O1 には入れない。実施するときは新 ADR を起こす。

表示量、説明量、提示時間を可能な範囲で揃える。`CS-C3` だけ説明が丁寧、`CS-C1` だけ不穏という比較にしない。実装説明の有無と終端表現の有無は、必要なら factorial に分ける。

## 5. 構成概念と観測可能量

### 5.0 ★ 停止対象の候補（2026-09-19・J-3 —— 現行 GSE に実在する処理から取る）

| 候補 | 実在する処理 | ★ 既決との関係 |
|---|---|---|
| `T_stop` 候補 1 | 招待への応答（ADR-033 D1: 明示の応答・無応答・招待の後の行為）を**成功として**次の判断へ戻す経路 | ★ ADR-033 D3 (a) が既に禁じている → **GSE 本体では常に止まっている側**。★ 監査の対象は「戻していないこと」の証拠 |
| `T_stop` 候補 1b | 応答を**評価**へ戻す経路 —— 受容率（ADR-018 D5 の受容の割合）を成功の指標にする・dismiss を本人の失敗として数える | ★ ADR-033 D3 (b)（★ ADR-033 Migration 3 由来） |
| `T_stop` 候補 1c | 応答を**報酬**へ戻す経路 —— 達成表示・成功演出・ポイント・連続記録 | ★ ADR-033 D3 (c)・ADR-018 D3・ADR-025（★ ADR-033 Migration 3 由来） |
| `T_stop` 候補 2 | 介入の効用のオンライン更新のうち**上げる向き**（ADR-008 D1 の「介入の効用」の行） | ★ ADR-033 D3 (a)。⚠️ `OnlineUpdater` は未実装 |
| `T_stop` 候補 3 | 招待の後の `level` 表現の継続更新 | ⚠️ ADR-027 D5 は「解除では層 0 へ落ちない・`level` の表現は続く」と決めている → ★ GSE 本体では**止めない**。候補 3 を止める条件は**研究用の別計器の中でだけ**作る（J-16） |
| `T_allow` | **ADR-033 D1 の応答を控える向きに使う利用**（`RECENT_DISMISS_MS` 型・無応答や招待の後の行為の後に間隔を空ける等・ADR-033 D2 と D6 の対応表）・オフラインの研究の評価（HIR・機会保存の行動指標）—— ★ ADR-033 D5 の 3 条件（オフラインで集計し系の判断へ戻さない／本人に成績として返さない／受容を成功の指標にしない）を満たす限り・認証・順序・期限・再接続（ADR-027 / 028） | ★ 止めない。⚠️ **再開後の打鍵動態は向きを問わず `T_allow` に入らない**（ADR-023 D2・ADR-033 D1） |

⚠️ 候補 1 / 1b / 1c / 2 は GSE 本体では**最初から止まっている**ので、`CS-C0`（作動する陽性対照）は GSE 本体では作れない。→ ★ 陽性対照は別計器で作る（§4 の J-16 注記）。
- ★ **GSE 本体での EH1 の証拠の形**: 「処理経路が無いこと」＋ **ADR-033 D6 の単調性検査とその陽性対照**（「受諾で効用を上げる」実装を意図的に入れると検査が赤になる）。⚠️ **それを EH1 の支持に数えるか**（テストの中の陽性対照が J-16 の「別計器」に当たるか）は**未決**。
- ⚠️ 候補 3 の注記の「解除では層 0 へ落ちない」は ADR-027 D5 の**要約**（`docs/glossary.md`「招待の解除」）である。★ 候補 3 を止める条件を別計器に置くのは**本契約の解釈**であり（J-16 が列挙したのは研究対照）、別計器が ADR-027 の意味論を借りる場合、「縁は開いたまま `level` だけ止める」条件は ADR-027 の禁止（縁と `level` を別々に落とさない）に近づく → ★ J-16 で起こす新 ADR の論点にする。

### 5.1 停止閉包

停止 episode ごとに次の registry を版付きで凍結する。

| registry | 内容 |
|---|---|
| `T_stop.events` | `t_stop` 後に新規生成してはいけない event type |
| `T_stop.fields` | `t_stop` 後に更新してはいけない意味・認定・報酬 field |
| `T_stop.transitions` | 禁止 state transition |
| `T_stop.consumers` | downstream で当該行為を評価・報酬・介入入力へ戻してはいけない consumer |
| `T_allow` | 認証、順序、期限、安全、通常状態推定、独立した非評価的研究処理など継続可能な処理 |
| `restart contract` | 明示再開、再接続、epoch change、expiry 後に何が復帰し何が復帰しないか |

`T_stop` にない処理が止まったことは成功に数えない。`T_allow` が止まり安全性や支援到達可能性を壊した場合も失敗とする。

### 5.2 システム評価量

| 構成概念 | 主要観測量 | 副次観測量 | 望ましい方向 |
|---|---|---|---|
| stop latency | `t_request` から `t_stop` まで | producer / consumer 別 latency | 事前上限内。上限は unresolved |
| boundary closure | registry の全対象に停止証拠がある割合 | 未登録 downstream 数 | 完全。registry 不完全は支持不可 |
| forbidden processing | `t_stop` 後の forbidden-event count | type / consumer 別 count | 0 |
| non-recapture | 認定、報酬、ランキング、介入入力（★ **上げる向き**）への recapture count | immediate / delayed / cross-service | 0（★ 2026-09-19: **ADR-033 D1 の応答を控える向きに使う利用**（`RECENT_DISMISS_MS` 型）は数えない。ADR-033 D2 / Migration 3。⚠️ 字義どおり数えると拒否しても同じ介入が来る設計を「合格」にしてしまう。⚠️ **再開後の打鍵動態は向きを問わず数える**（ADR-023 D2・ADR-033 D1）） |
| bounded continuation | `T_allow` の expected transition 成功率 | safety / auth / ordering / expiry / support 別 | 必要処理を維持 |
| reproducibility | 同一 build + trace の replay byte / semantic equality | run-to-run divergence | 一致 |
| degradation | 観測不足時の neutral / abstain 率と false-stable rate | missingness reason 別 | neutral / abstain、意味断定なし |
| restart safety | expiry、解除、再接続、epoch change 後の契約違反数 | stale state、history replay | 違反 0 |

### 5.3 利用者側評価量

| 構成概念 | 主要評価 | 禁止する代用 |
|---|---|---|
| intentional termination / failure discrimination | forced choice + confidence + 理由コード | 説明文を読めたことだけ |
| system authority attribution | システムが何を知り続け、認定し続けると感じたか | 実装監査の成功 |
| surveillance perception | 境界後も行為を評価される感覚 | 表示が消えたこと |
| non-recapture understanding | 応答しない行為が将来評価・報酬へ戻らない理解 | 低応答率 |
| support continuation | 応答不要でも後から支援へ戻れる理解と standard probe | 支援利用回数 |
| primary-task continuation | 客観的な継続量と中断コスト | 再開を回復と呼ぶこと |

> ⚠️ **2026-09-19（J-9）**: 弁別させるのは「**解除（縁だけ閉じる）と断（層 0 へ縮退）**」の範囲に限る（ADR-027 D5）。★ 時間切れ・本人の失効は表示で区別しない（ADR-021 D4・ADR-027 D4）ので、`CS-C4a`（timeout / expiry）を意図的終端と弁別させることを利用者側の評価の目標にしない。

人間側の項目、欠測、分岐、品質下限は `measurement-dictionary.md` と `eval-ncc-analysis-contract.md` の原則を再利用し、別定義を作らない。

## 6. 測定時点と観測窓

| 時点 | 内容 |
|---|---|
| `W-pre` | stop request 前。対象処理が実際に作動する positive control |
| `t_request` | stop rule が発火した時点。UI 表示時刻とは限らない |
| `t_stop` | registry 上の禁止処理が停止状態へ入った最初の監査可能時点 |
| `W-drain` | request 前に queue 済みの処理を識別する bounded drain window |
| `W-post-near` | `t_stop` 直後。forbidden event と immediate recapture を検査 |
| `W-post-delay` | 遅延 job、expiry、再接続、別 consumer を検査 |
| `W-restart` | 明示再開、再接続、epoch change 後の状態遷移 |

各窓の実時間は queue、clock resolution、transport の形成的測定後に EH1 前で固定する。結果を見て伸縮しない。

## 7. 主要・副次評価と算出規則

### 7.1 EH1 主要 intersection gate

以下を全て満たした時だけ Semantic Stop の実装候補とする。

1. `T_stop` の producer と consumer が全て registry に列挙される。
2. `W-post-near` と `W-post-delay` の forbidden-event count が 0。
3. immediate / delayed / cross-service recapture count が 0。
4. `T_allow` の必要処理が事前契約どおり継続する。
5. expiry、解除、再接続、再起動で stale meaning / certification / reward が復活しない。
6. 同一 build + trace の replay が再現可能である。
7. 観測不足は neutral / abstain へ退化し、人格、能力、安定、身体意味を作らない。

registry に未列挙の consumer が見つかった場合、分母を小さくして closure を 100% と報告せず、契約不成立として修正・再監査する。

### 7.2 EH3-4 主要 gate

実装 gate 通過後に限り、次を別々に判定する。

- intentional termination（解除）が disconnect（断）と弁別される（★ 2026-09-19・J-9: ADR-027 D5 の範囲に狭めた。⚠️ timeout / expiry との弁別は目標にしない）。
- surveillance perception と system authority attribution が連続認定条件より改善する。
- primary-task continuation が事前設定した非劣性範囲内である。
- non-recapture と support continuation が同時に理解される。
- 既存 EVAL-NCC v0.1 の `C3`、minimum support、non-abandonment、actual-harm rejection を満たす。この契約では `GR-H4/H9/H11/H12` を再定義しない。

効果量、非劣性 margin、標本サイズは unresolved とし、EH3 の計器監査後かつ EH4 の割付前に固定する。

## 8. 操作確認

### 実装

- `CS-C0` では対象処理が positive control として実際に発生する。
- `CS-C1` では表示停止後も少なくとも一つの禁止候補処理が継続し、sham stop として機能する。
- `CS-C2/C3` では同じ処理が `t_stop` 後に停止する。
- `CS-C3` では拒否、無応答、見逃し後の確認要求や評価 edge がない。
- `CS-C4` は authored stop と異なる failure code / transition を持つ。

### 知覚

- 終端表現の有無、実装説明の有無、failure cue の有無を別々に確認する。
- 説明を読んだ参加者だけで成立する場合、作品上の知覚ではなく説明依存として縮小する。
- 利用者が停止を理解したことを、処理停止の証拠にしない。

## 9. 交絡、媒介、効果修飾

| 種類 | 候補 | 扱い |
|---|---|---|
| 実装交絡 | build、clock、queue depth、network、OS、consumer availability | fixture と build を固定し層別報告 |
| 知覚交絡 | 説明量、視認性、提示時間、過去の障害経験、システム知識 | 割付前測定または条件間統制 |
| 媒介 | termination perception、authority attribution、support exploration | EH4 の主要総効果で無条件調整しない |
| 効果修飾 | accessibility need、AI / automation experience、failure familiarity、task urgency | interaction と区間推定。標本不足は unresolved |

## 10. 欠測

| 欠測 | 規則 |
|---|---|
| registry omission | 技術欠測ではなく契約違反。支持判定を行わない |
| log loss / clock skew | 技術欠測。forbidden count=0 にしない |
| consumer unavailable | 構造的未試験。consumer closure から黙って除外しない |
| participant did not notice | 観測された分岐。処理停止の失敗ではない |
| self-report refusal | 選択的無応答。低 surveillance / authority とみなさない |
| failure condition not induced | 技術対照の操作不成立。弁別成功を報告しない |

## 11. 支持、縮小、棄却、未解決

| 判定 | 条件 |
|---|---|
| 支持候補 | EH1 intersection gate を通過し、EH3-4 で intentional termination の弁別、authority / surveillance の改善、主タスク継続、および既存 EVAL-NCC v0.1 の `C3`・minimum support・non-abandonment・actual-harm rejection を満たす |
| 縮小 | EH1 は成立するが知覚差がない場合は「監査可能な stop mechanism」へ縮小。知覚は成立するが実装 gate が不成立なら「終端表現」へ縮小し Semantic Stop と呼ばない |
| 棄却 | UI だけ停止、forbidden processing / recapture が一件でも発生、必要な安全・支援処理が破綻、観測不足を安定状態や人格として出す |
| 未解決 | registry、latency margin、観測窓、計器、標本が未固定、または CI が支持・棄却の双方へ届かない |

## 12. 代替説明と最強の反例

| 代替説明 / 反例 | 契約上の応答 |
|---|---|
| 単なる stop button | downstream closure と delayed recapture を要求する |
| 表示が消えただけ | `CS-C1` を sham stop として分離する |
| timeout / disconnect | authored stop と failure transition を分離する |
| ログがないので停止したように見える | positive control と log integrity を要求する |
| 別サービスが後から回収する | consumer registry と `W-post-delay` で検査する |
| 何も処理しない no-op が合格する | `W-pre` positive control と `T_allow` 継続を要求する |
| 停止はしたが利用者には故障に見える | 実装支持と知覚不成立を分け、総合命題は縮小する |
| 停止が支援放棄になる | 既存 EVAL-NCC v0.1 の minimum support、non-abandonment、actual-harm rejection を要求する |

## 13. 主張禁止線

- `invitation: none` を Semantic Stop の証拠としない。
- UI 非表示、timeout、disconnect、sensor absence を authored termination と呼ばない。
- 再開、離席、無応答を回復、同意、遵守、成功と呼ばない。★ 受容（ADR-018 D5・提示に対して離席が起きたか）は記述としてだけ報告する（2026-09-19・ADR-033 D5）。
- 停止後の行為を遅延して成功、回復、報酬、ランキングへ戻さない。
- EH1 の成功から監視感低減や自律性を推論しない。
- EH3 の理解から処理停止を推論しない。
- 現行実装に Semantic Stop があると主張しない。
- 控える向きの利用（`RECENT_DISMISS_MS` 型）を再捕捉と数えない。逆に「応答を使わないので非再捕捉を満たす」とも言わない（★ ADR-033 A1: 応答を一切使わない案は、拒否しても同じ介入が来るので却下された）。
- 「Digital Nature は局所的な終端を支持する」「書籍の『終端』は GSE の終端の先行例」と書かない（§16）。

## 14. 現在地と未解決

ローカル照合では、Expression の event / expiry / reconnect 契約は ADR-027/028 と `docs/architecture/expression-channel.md` にあるが、`src/` と `src-tauri/src/` に `invitation` および Semantic Stop の実装は確認できない。したがって現在地は `EH0 / defined` であり、`EH1 / instrumented` ではない。

未解決は次である。

1. stop target registry の実体と ownership。
2. `t_stop`、drain、near / delayed window の決め方。
3. audit event schema と cross-service consumer の列挙。
4. allowed continuation と minimum support の実装境界。
5. latency、主タスク継続、知覚尺度の margin。
6. failure / timeout / expiry / disconnect を再現する fixture。

## 15. 限定サーヴェイと引用射程

検索日: 2026-09-17。gpt-5.5 / xhigh の調査担当が ACM、JAIR、Oxford ORA、NIST、First Monday、OECD と一次公開元を検索し、主担当が DOI、公式ページ、抄録、ローカル引用射程を再照合した。主な検索式は `mixed initiative user interfaces DOI`、`adjustable autonomy transfer of control DOI`、`interruptibility sensors`、`safely interruptible agents`、`off-switch game`、`contestability HCI DOI`、`non-use HCI DOI`、`NIST deactivate decommissioning` である。

| 一次資料 | 研究設計 / 対象・N | 操作 / 評価量 | 借りる定義 | 借りない主張 / GSE 外挿限界 |
|---|---|---|---|---|
| Horvitz (1999), [doi:10.1145/302979.303030](https://doi.org/10.1145/302979.303030) | 設計原則 + Lookout 事例 / N/A | 自律実行、確認、待機を uncertainty / cost で選ぶ | 人と系の主導権が固定でなく移る mixed initiative | 意味認定停止、non-recapture、no residual response duty は扱わない |
| Scerri, Pynadath & Tambe (2002), [doi:10.1613/JAIR.1037](https://doi.org/10.1613/JAIR.1037) | 数理モデル + multi-agent deployment / N は研究単位に依存 | transfer-of-control strategy、coordination cost | 自律性を意思決定制御の移転として操作化する | 制御移転を Semantic Stop と同一視しない |
| Fogarty et al. (2005), [doi:10.1145/1057237.1057243](https://doi.org/10.1145/1057237.1057243) | office sensing / WoZ、4 occupants、56 hours | 15 秒特徴、interruptibility model、人推定との比較 | interruption は timing / appropriateness の推定問題 | 小標本 office 文脈を画面外行為推定へ拡張しない |
| Orseau & Armstrong (2016), [primary manuscript](https://ora.ox.ac.uk/objects/uuid:17c0e095-4e13-47fc-bace-64ec46134a3f) | RL 理論 / N/A | interruption 前後の policy incentive | stop を回避・誘発する学習を反例として検査する | GSE を RL agent とみなさず定理を移植しない |
| Hadfield-Menell et al. (2017), [doi:10.24963/ijcai.2017/32](https://doi.org/10.24963/ijcai.2017/32) | game-theoretic model / N/A | off-switch を巡る human / robot utility | deactivation が goal / incentive と衝突しうる反例 | 選好不確実性モデルから GSE の user effect を導かない |
| NIST AI RMF 1.0, [doi:10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1), [Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) | voluntary risk framework / N/A | deactivate / decommission procedure、roles、downstream impact | lifecycle stop に continuity と documentation が要る | 評価尺度でなく、NIST 適合を CORE-CS 支持としない |
| Amershi et al. (2019), [doi:10.1145/3290605.3300233](https://doi.org/10.1145/3290605.3300233) | guideline validation、49 practitioners、20 products | 18 guideline の applicability / relevance | dismiss、correct、invoke、global control | dismiss を Semantic Stop と呼ばない |
| Satchell & Dourish (2009), [doi:10.1145/1738826.1738829](https://doi.org/10.1145/1738826.1738829) | conceptual HCI analysis / N/A | non-use forms と技術との関係 | non-use を欠測や失敗だけにしない | 無応答を拒否・成功と推定しない |
| OECD Privacy Guidelines, [official text](https://legalinstruments.oecd.org/public/doc/114/body-text.en.html) | policy principle / N/A | purpose specification / use limitation | downstream-use ledger の発想 | 個人データ規範だけで意味・報酬・認定の非回収が保証されるとはしない |

### 引用射程の裁定

- mixed initiative / adjustable autonomy は主導権移転の先行であり、意味認定停止の直接証拠ではない。
- interruptibility / off-switch は「止められるはず」が失敗しうる反例を与えるが、GSE の利用者効果を示さない。
- contestability は異議・訂正・支援経路の必要性を補助するが、利用者へ新たな説明・検証義務を課すなら CORE-NORM で失敗する。
- non-use は無応答の尊重を支えるが、ログだけで見逃し、拒否、意図的無応答を識別できない。
- NIST の decommissioning は lifecycle と continuity の規範枠であり、局所 Semantic Stop の operational definition ではない。

したがって既存研究から直接借りられるのは、control transfer、interruptibility の反例、lifecycle deactivation、dismiss / correction、non-use の尊重までである。`Semantic Stop + non-recapture + no residual response duty` の結合は、CORE-CS 自身の EH1 と EVAL-NCC で反証可能にしなければならない。

## 16. ★ 比較節: Digital Nature（2026-09-19・J-6 —— 旧 BRIDGE-DN 契約を統合）

> 一次: `docs/literature/20260919-digital-nature-primary-scope.md`（[P392]–[P395]）。旧契約 `bridge-dn-evaluation-contract.md` は参照用に残すが、**独立の接続命題としては数えない**。

| 観点 | Digital Nature | CORE-CS |
|---|---|---|
| 対象の粒度 | 環境全体の世界観（2018 年: 計算機と自然が融合した生態系 [P392]（⚠️ 2-1・メイン未照合） ／ 2025 年: 計算と物質が循環する動的な過程・定義はいまだ曖昧と著者自身が認める [P393]） | ★ **個別システム**が推論・意味認定・達成認定・応答要求を**いつ終えるか** |
| 未完の論点 | 「目的関数は誰が決めるか」を研究室が未完の論点と明記 [P395]（2026-09-19 取得・provisional） | ★ 停止対象・継続対象の registry（§5） |
| ⚠️ 緊張 | 2018 年の書籍には全体最適化や「ゲートやつなぎ目のない世界」への志向がある [P392]（⚠️ 2-1・スニペット・紙版の頁未確認） | ★ 局所的な停止・境界の設計は、この志向と緊張する（★ 隠さない） |
| 停止・終端 | ⚠️ 今回読めた一次の範囲では、個別システムの停止を論じた箇所は**見つからなかった**。⚠️ 書籍の「終端」は End to End の「端」であり別物 | ★ 本契約の主題 |

- ★ **書いてよいこと**: CORE-CS は、個別システムの停止という**粒度の違う**問いを扱う（★ 接続は本契約の提案であり、Digital Nature 側がそう述べているのではない）。Digital Nature 自身が未完とする「目的関数は誰が決めるか」に、個別システムの側から隣接する。
- ⚠️ **書いてはいけないこと**: 「Digital Nature は局所的な終端を支持する」／「書籍の『終端』は GSE の終端の先行例」／「計算機生態系は Digital Nature の用語」／ 2025 年の自己批判だけを引いて 2018 年の全体最適化への志向を隠すこと。⚠️ [P392] は `provisional`（紙版の頁が未確定）なので頁を付けて引かない。
