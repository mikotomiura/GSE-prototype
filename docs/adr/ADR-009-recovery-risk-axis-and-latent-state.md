# ADR-009: X 軸を `self_directed_recovery_risk` へ再定義し、潜在状態の数を決めない

- **ステータス**: **Proposed**（方向合意）。確定は実装時（Phase1 完了後）。ADR-008 と一体で読む。
- **日付**: 2026-08-01
- **関連**: `docs/architecture/personalization-and-online-learning.md §2/§3/§4/§8`・
  ADR-001（HMM を Writing baseline へ降格）/ ADR-005（additive versioning）/ ADR-006（task_kind→head）/
  **ADR-007（receptivity 分解維持・本 ADR で維持を再確認）**/ ADR-008（オンライン学習の境界）
- **昇格元**: `.idea/20260801-behavioral-context-online-latent-ml-design.md` §0/§4.1 ＋
  `.idea/20260801-architecture-signal-and-online-learning.md` §1/§7（`.idea` は追跡外・SSOT ではない）

## Context

### 実測（推測ではない）

- **旧 X 軸（Cognitive Friction）は主観摩擦を予測できていない**。最も検定力のある P010（n=103）で
  全特徴量が偶然水準（f1=0.442 / f3=0.507 / f5=0.468 / 合成 0.503）。Bonferroni 通過は到達可能な
  70/103 セルでゼロ。
- **φ 正規化は単調変換なので C-index をほぼ変えない**（実測差ほぼ ≤0.03）。
  → 「生特徴量が偶然水準」は **β に依存しない結論**であり、正規化修正では解けない。
- **産出側には弱いが一貫した信号がある**。単純な `keys`→Q2 の個人内 C-index が
  0.615/0.600/0.657/0.676（P014 のみ 0.368）で、**現行 5 特徴量のどれよりも高い**。
- **ラベルの供給が壊れた**。Phase1 は probe 枯渇・P013 の straight-lining により GATE3 = DataInsufficient。
  旧 X 軸の criterion は主観プローブ Q1 であり、**まさにそこで死んだ**。

### 提案されていた案の破綻

`.idea` doc#2 §4.1 は latent state を
`Progress / Stagnation / ExternalizationPressure / Receptivity` の 4 つに限定し、
`z_t ~ p(z_t | z_(t-1), context_t, head)` と categorical（相互排他）を主張していた。これは成立しない:

1. **相互排他でない**（Receptivity は Progress と排他でない）。1 つの潜在次元の分割になっていない。
2. **Receptivity は観測の放出元でない**。入力（cooldown / daily_cap / recent_dismiss / time-of-day）は
   システム状態と履歴であり、潜在状態からの放出ではない。**放出モデルが書けない**。
3. **ExternalizationPressure は状態でなく傾向**で、§0 の X 軸定義と機能が重複し循環する。
4. **既存 `WorkStateEstimate`（連続 proxy 5 つ）への写像が未定義**。
5. **「4」の根拠が無い**。Phase1 の 3 状態は手で選んだ状態だった。3→4 は同じ轍で、
   失敗が「ラベルの入れ替わり」から**「データ中の何にも対応しない状態」**へ移るだけである。

さらに **層跨ぎの事故**: 既存 SSOT で **Receptivity は Layer 5** の概念であり、
**ADR-007 が「分解形の維持」を Accepted** で採択済み。4 状態をそのまま昇格させると
「Layer 4 の Receptivity」と「Layer 5 の Receptivity」が並立し、**ADR-007 が静かに無効になる**。

## Decision

### D1. X 軸を `self_directed_recovery_risk` へ再定義する

> このユーザーが、この task 文脈で、**近い時間範囲（horizon H）内に自力による前進を回復できない確率**。

- Layer 4（Work-State Proxy）の**出力**とし、`WorkStateEstimate` に
  `self_directed_recovery_risk: Option<f32>` と `recovery_risk_uncertainty: Option<f32>` を
  **additive に追加**する（ADR-005 の additive 原則。既存 5 proxy は不変）。
- **採用の主要根拠は「行動から自己ラベル付けできる」こと**。criterion が主観プローブでなく
  行動（stall 後 H 分以内の自力回復の有無）であるため、**プローブを 1 件も撃たずに教師信号が生成される**。
  Phase1 で死んだ label supply の構造問題への直接の答えである。

### D1b. 旧 X 軸（Cognitive Friction）の**格を落とす** ★D1 と対で読むこと

新軸を additive に足すだけでは不十分である。それだと「旧 X も recovery risk も**どちらも確証対象**」と読めてしまう。
**旧 X 軸は明示的に降格させる**——これは ADR-001 が HMM に対して行ったこと（ontology → Writing head の baseline）の、
**軸に対する版**である。

| 対象 | 現在 | 降格後 |
|---|---|---|
| **主張上の格** | **確証の核**（H-X1 / GATE3 = PreReg-4 の対象。`research-positioning §1`「反証可能な確証核」） | **比較用 baseline・歴史的説明**。新しい確証主張の対象にしない |
| `friction_score` フィールド | Layer 4 の主要出力 | **削除しない**（`WorkStateEstimate` に残す）。ただし主役ではない |
| 合成式 `0.30φ(F3)+0.25φ(F6)+0.25φ(F1)+0.20φ(F5)` | 手決めの重みが本番経路 | **凍結のまま維持**。新軸側では重みは学習され、手決め式は継承しない |
| `p_stuck` → Need 層 | 介入トリガの唯一の供給元 | **Phase 2b までは現行のまま**。置換は recovery risk が G2/G4 を通ってから |
| 外部説明・UI の語り | 「摩擦を推定する」 | 主要な語りにしない（ADR-001 の三状態表示の降格と同じ扱い） |

**なぜ削除ではなく降格か**: (i) Phase1 の確証トラックとの連続性を切らない、(ii) 新軸の**比較対象**として必要
（新軸が旧軸を上回らなければ、軸を変えた意味が無いことになる）、(iii) `p_stuck` は現に介入を駆動しており、
代替が G2/G4 を通る前に外すと介入機能そのものが止まる。

> ⚠️ **降格は「X の測定に失敗したから」ではなく「X には現行の観測空間で信号が無いことが実測で示されたから」**である。
> 統制タスク実験（D7 / G1）で分離できれば、旧 X が復権する余地は残る。降格は不可逆な棄却ではない。

### D2. 目的変数の operational definition を先に閉じる

- `progress_proxy` = 個人×task_kind×phase 基準で正規化した**純産出の持続**
  （窓内の 挿入−削除 打鍵数を個人基準で正規化し、T 秒以内に取り消されないこと）。content-free。
- `self_directed_recovery` = stall onset から H 分以内に、**観測された外部化（paste）を挟まずに**
  `progress_proxy` が個人基準を超えて回復すること。H は事前宣言して凍結する。
- **打ち切り（censoring）**: content-free 制約下では検索・別デバイス・口頭相談は観測できない。
  focus 喪失・アプリ切替（**回数のみ**・識別子もタイトルも保存しない）を打ち切り指標として別に記録し、
  「自力回復」と「観測外で解決して戻った」を区別できないことを明示する。

### D3. 潜在状態の層を ontology から head の実装詳細へ降格し、**状態数を今決めない**

```text
Layer 4 の出力（固定）
    WorkStateEstimate + self_directed_recovery_risk (+ uncertainty)

推定器（未確定・競合させる）
    ★正   baseline : p_recovery = sigmoid(bias_user_task_phase + (w_head + δ_user_task)·context)
                     潜在状態を持たない
      候補 A       : 相互排他な作業モードの状態フィルタ（例 Progressing / Stalled / Externalizing）
      候補 B       : online EM による潜在構造学習（→ D6）
```

- **stateless baseline を「正」とする**。
- `ExternalizationPressure` は**状態でなく `recovery_risk` の構成要素（特徴）**として扱う。
- **`Receptivity` は Layer 5 に戻す**。ADR-007（分解維持）を**維持**する。

### D4. 潜在状態モデルの採用ゲートを事前に宣言する

候補 A / B は次を**両方**満たしたときにだけ baseline を置き換えられる:

| ゲート | 内容 |
|---|---|
| **勝ち幅** | held-out（subject-level / task-level / session-level split 必須）の recovery 予測で、stateless baseline を**事前宣言した幅**だけ上回る |
| **退化検出** | ① 状態占有エントロピーが下限超 ② 各状態の**最小占有率**が下限超（使われない状態が無い） ③ 初期値・seed を変えても**状態ラベルが安定**（label switching が起きない） |

**この退化検出の追加こそが §Context の破綻点 5 への実質的な回答**であり、状態数を変えることではない。

### D5. 旧仮説 H-X1 を新軸へ流用しない

`research-positioning.md §5` の **H-X1 は旧 X 軸（Cognitive Friction ↔ Q1）に対する仮説**であり、
GATE3 の判定（DataInsufficient）も旧軸に対するものである。
**新軸には新しい仮説番号が要る**。本 ADR は **H-X1d（案）** を提案する:

> `self_directed_recovery_risk` は、行動由来 criterion（stall 後 H 分以内の自力回復の有無）を
> 個人内で偶然を超えて予測する。

> ⚠️ `research-positioning.md §5` は「研究者による確認が必要な節」である。
> **本 ADR は提案に留め、§5 は変更しない**。採択は研究者判断。

### D6. online EM は Phase 4 へ降格する（理由を明文化する）

降格の理由は「重い」でも「難しい」でもなく、**3 つの前提が揃っていないため現時点で評価不能**だからである:

1. **目的変数が未確定だった**（D2 で今回閉じた）。何に対して「良い潜在状態」かが定義されていなければ
   当たり外れを判定できない。
2. **比較対象（baseline）が無かった**（D3 で置いた）。
3. **識別可能性が未解決**。教師なし EM はクラスタを作るが Stuck は作らない。
   半教師ありアンカーに使う予定だったラベルは **Phase1 でまさに枯渇した**。

→ 「本命を降格した」のではなく「前提が揃うまで評価できないので順序を後ろに置いた」。
D4 のゲートを通れば Phase 4 で復活しうる。

### D7. 軸を書き換えても統制タスク実験は免除されない

「打鍵由来の content-free イベントで作業状態を分離できるか」という**測定可能性の問いは未検証のまま**である。
高摩擦を誘発する短い統制タスクを作り同一人物内で低/高条件を交互に取る実験を、
**新軸に対しても必要な反証ゲート**として設計に組み込む（`personalization-and-online-learning.md §8.2` G1）。
凍結解除後の最初のタスクに置く。

## Alternatives

- **旧 X 軸を維持し、正規化と重み付けを直す**: φ が単調変換である以上 C-index はほぼ動かない（実測）。
  正規化修正は衛生管理としては実施すべきだが、**決定的実験ではない**。却下。
- **doc#2 の 4 状態をそのまま採る**: §Context の 5 点で破綻し、ADR-007 を静かに無効化する。却下。
- **3 モード（Progressing / Stalled / Externalizing）を今確定する**: 破綻点 1〜4 は解けるが、
  **破綻点 5（状態数を手で選ぶこと自体）を 4→3 の向きで繰り返す**。
  「なぜ 3 か」に答えられないまま SSOT に入る。却下（ただし D3 の**候補 A** として残す）。
- **潜在状態を完全に廃し、連続 proxy のみとする**: 現時点の「正」は実質これ（stateless baseline）だが、
  **将来の状態モデルを構造的に排除しない**ために候補として残す枠を用意する。D3 は両者の中間ではなく、
  「正は stateless、状態モデルは昇格候補」という**明確な非対称**である。
- **`self_directed_recovery_risk` を既存 `stuck_likelihood` に統合する**: `stuck_likelihood` は
  凍結対象（`engine.rs` HMM 出力）であり、意味も違う（今詰まっているか vs 戻れるか）。
  additive な別フィールドにする。

## Consequences

- **`WorkStateEstimate` に additive 拡張が入る**（Epic 2/5）。既存 5 proxy・`uncertainty`・
  `evidence_quality` は不変。`emit_schema` の diff を意図的に確認する（Phase1 完了後）。
- **「GSE の潜在状態は何か」に現時点で答えを持たない文書になる**。外部説明では「4 状態です」より
  弱く聞こえうる。→ これは弱さでなく **採用ゲートを事前宣言した反証可能な設計**として提示する。
- ADR-001（HMM を Writing head の baseline へ降格）と整合する。HMM は候補 A の一実装であり、
  D4 のゲートに服する。**現行 HMM の内部挙動・`HMM_VERSION` は本 ADR では変えない**。
- ADR-007 は**維持**（Receptivity は Layer 5・分解形）。本 ADR はこれを再確認するだけで変更しない。
- 打ち切り（D2）が支配的な場合、新軸のラベルは成立しない。
  → 反証ゲート G2（`personalization-and-online-learning.md §8.2`）として事前宣言する。
- **コード変更ゼロ**。凍結対象に一切触れない。

## Migration

1. Phase1 完了 + 研究者承認まで**着手しない**（凍結）。
2. 凍結解除後の**最初のタスク = G1 統制タスク実験**（D7）。ここで分離できなければ、
   パイプラインを作る前に軸そのものを疑う。
3. **P1**: `progress_proxy` / `self_directed_recovery` ラベルが実際に取れるかを確認（G2）。
   現行 X を置換せず並走。
4. **P2**: stateless baseline を実装し H-X1d（案）を個人内で評価。
5. **P4**: 候補 A / B を D4 のゲートにかける。通らなければ採用しない。
6. `research-positioning.md §5` への H-X1d 追記は**研究者採択後**に別タスクで行う。
