# 次セッション開始プロンプト — Phase2 較正プロトコルの凍結（タスク適応の設計は完了済み）

このファイルの「===」以下をコピペして開始する。

**前提**: 本トラックは**コード変更ゼロ**を維持している。凍結対象には触れない。

---

===

## §0 前セッションで完了済み（**やり直さない**）

`.steering/20260802-task-adaptation-design/`（requirement / design / decisions / tasklist）。
成果物はすべて設計文書で、**コード変更ゼロ**・凍結対象は無改変。

| 成果物 | 内容 |
|---|---|
| ★ `docs/architecture/task-adaptation-and-scope-gating.md` | **設計本体**（§2 較正プロトコル → §3 統合設計 → §4 検出器の構造） |
| ★ `docs/adr/ADR-010-task-scope-gating.md` | 決定 **D1〜D6**。ADR-006 は**拡張であって改訂ではない** |
| 追記のみ | ADR README / ADR-006 の関連欄 / `personalization…md §11-11`・§11-1 / `domain-adapter-boundary.md` |

### ★ 確定した決定（前提として読むだけ）

1. **out-of-scope は head でなくフラグ**（head 相対の `scope_fit`）。`NullHead` を作らない。
   `evidence_quality` を下げ `uncertainty` を上げるだけ ＝ 既存原則がそのまま発火し、**新機構が要らない**。
2. **宣言は routing のみ・観測は割引のみ。食い違っても re-route しない**（閉ループと非対称コストが理由）。
3. **推定は streaming 窓・読み出しは Decision Episode**。検証は **block** 単位（推定量が変わる点に注意）。
4. **検出器の構造を凍結**: `(個人内逸脱 OR コホート逸脱) AND 絶対ゲート` ＋ 尺度 floor ＋ 中心の縮約 ＋
   ★ **到達不能性（`unreachable`）の出力**。**定数は書かない**。
5. **定数は in-scope 側だけから決める**（正例を使わない ＝ 感度を推定量として残す）。
6. **Phase2 で較正するのは Writing head のみ**。Coding は未較正のまま運用、Creative は baseline を作らない。
7. `phase` は Phase2 では**意味づけしない**（暫定・研究者判断待ち）。

---

## §1 このセッションの候補（優先順）

### ★ 候補 1: Phase2 較正プロトコルの**事前登録文書**を書く（設計本体 §2.9 が要求）

設計本体 §2 は**設計であって凍結ではない**。データ収集前に別文書として凍結する必要がある
（`preregistration-v0.3.md` は Phase1 の契約であり**変更しない**）。凍結すべき最小項目:
**block 構成 / counterbalance 規則 / 正例の種類 / 除外基準 / §4.5 の定数推定手続き / 報告要件**。
⚠️ ただし下記 §2 の研究者判断が閉じないと block 構成が決まらない。**先に §2 を確認すること。**

### 候補 2: 検出器の再設計を**実験トラック**で事前登録する

別トラックの引き継ぎ `.steering/_handoff/next-session-prompt-task-scope-ground-truth.md` を参照。
⚠️ **本データ（38 セッション）では検証できない**（外的正解ラベル 1 件）。
設計本体 §4.5 の禁止事項（38 セッションで定数を決めない）を破らないこと。

### 候補 3: マスキング／尺度過敏の**出典を確認して `[Pn]` 登録**

ロバスト統計の教科書的事象と思われるが**未確認**。`literature-card` で精読 → `citation-ssot` で登録。
`docs/references.md` の次番号は **`[P36]` / `[V66]`**（前セッションでは追記していない）。

### 候補 4: 単峰性の帰無に対する正しい検定（dip 検定等）

前々ラウンドの設計ミス（凍結した主検定が意図した仮説を検定していなかった）への直接の対処。
`requirements.txt` の追加が要る（`env.md` の方針に従う）。

---

## §2 ★ 研究者判断が要る 3 点（これが閉じないと候補 1 に進めない）

1. **G1（統制タスク実験）に scope block を相乗りさせるか**（設計本体 §2.8）。
   セッション骨格が同型なので相乗りを推奨したが、被験者負荷・セッション長・謝金設計に依存する。
   ⚠️ 摩擦条件 × scope 条件を**完全交叉させない**（block 数が倍になる）。
2. **`phase` を Phase2 では意味づけしない**という暫定案の可否（設計本体 §3.6）。
3. **out-of-scope 正例の 2 種類目**を何にするか（設計本体 §2.4。1 種類だとその種類の検出器になる）。

---

## §3 制約（厳守）

- **コード変更ゼロ**（設計文書のみ）
- **凍結対象に触れない**: `schema_dto.rs` / `schema/current.json` / `engine.rs` HMM_VERSION /
  `loop_step.rs` / `intervention.rs` 定数 / `probe_scheduler.rs` /
  `App.tsx` の argumentative ロック（読むのは可）/ `preregistration-v0.3.md`
- **`research-positioning.md §5` を変更しない**
- **PII**: 氏名・メール・所属を出力もコミットもしない。**raw NDJSON をコミットしない**。
  ★ **セッション日時を成果物に出さない**（本 repo は一時 public にする運用がある）
- **過大主張の禁止**: 「外れ値であること ≠ 対象外作業をしていたこと」
  「**フラグされないこと ≠ 対象作業だったこと**」を維持する。
  ★ 設計本体 §4.2 の 4 例の表は **retrodiction であって性能の証拠ではない**（導出集合 = 検定集合）
- ★ **事前登録を結果を見た後で差し替えない。** 無効な検定を凍結したら**無効だったと記録**し、
  修正版は探索的として併記する

## §4 まず読むもの（この順）

1. `docs/architecture/task-adaptation-and-scope-gating.md`（設計本体・§0 の要約 → §2 → §3 → §4）
2. `docs/adr/ADR-010-task-scope-gating.md`（D1〜D6 と Migration）
3. `.steering/20260802-task-adaptation-design/decisions.md`（判断 0〜12 の根拠）
4. `docs/architecture/personalization-and-online-learning.md §8.2`（G1/G2 の反証ゲート）
