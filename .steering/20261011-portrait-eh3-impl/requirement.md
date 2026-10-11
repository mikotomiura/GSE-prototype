# portrait-eh3-impl — EH3 の実装（招待の PC 面・肖像の壁紙・記録・配布）

## 背景

EH3 の外枠は研究者が決めた（`.steering/20261011-portrait-eh3-prereg/decisions.md` 判断 1・2）。
参加者の PC で、空・D・A の 3 ブロック × 5 稼働日、A の中で none と seed を日ごとに交互にし、
招待は全ブロックで同じ規則（契機は推定の停滞）で出し、Nudge は出さない。肖像は壁紙だけ。

事前登録の稿（`experiments/20261011-portrait-eh3/preregistration-draft.md`）は、招待の PC 面と肖像の実装で
決まる値（招待の値・seed の畳み方・セッション境界など）が空欄のままで、凍結の前提が欠けている。
招待（`invitation`）と肖像・壁紙の実装は `src-tauri/src` と `src` に 0 件である。

## ゴール

EH3 の参加者に配れるビルドを作る。すなわち、EH3 のモードで起動すると、

1. 推定の停滞を契機に、文字の無い招待の図像を overlay 窓に出し、T で失効させる（Nudge は出さない）。
2. その日の条件（空 / D / A-none / A-seed）に従って壁紙を差し替え、元の壁紙を必ず戻す。
3. 条件の割り当てと招待の提示の時刻を content-free の NDJSON に記録し、肖像への本人の操作は
   どの出力にも写さない。

あわせて、実装で決めた値を稿の §10（F 項）へ戻せる形で `decisions.md` に残す。

## スコープ

### 含むもの
- 招待の PC 面（要件 R-I1〜R-I15）: 状態機械（`analysis/` 側・OS 非依存）、overlay の図像、説明と設定の窓、
  ADR-026 M11 の検査（招待面の最初のコードと同じコミット）、ADR-035 D1〜D6 の acceptance。
- 肖像（R-P1〜R-P10）: `raw` / `lattice` の生成器と D の地模様の Rust 実装（F-1 の選択は研究者が後で行うので両方を持ち、
  配布の設定で 1 つに固定する）、更新の予定（U-4 型）、seed / none、壁紙の差し替えと復元（Windows・macOS）。
- 記録（R-L1〜R-L6）: schema の追加（additive・`Option`）、`meta` の EH3 モード、capabilities、parity。
- 配布（R-D1〜R-D3）: EH3 のモード（Nudge 無効・招待有効）、O1・G1 と分けたタグの手順。
- ADR-035 の見直し（Proposed → Accepted 候補。R-1 の読み方の注記）。⚠️ 本文は書き換えず、見直しの結果を記録する。

### 含まないもの
- 事前登録の凍結、attack-me（凍結の直前に別に回す）。
- 罪悪感・反発の尺度のサーヴェイ（F-6・別タスク）。
- 同意文書・participant-guide の本文の確定（項目の案は作るが、本文は研究者が確定する）。
- `raw` / `lattice` の選択そのもの（研究者が見本で選ぶ・F-1）。
- macOS の実機での確認（Mac 用の引き継ぎに分ける。本機は Windows の G-GEAR）。
- EH3 の後の ADR（判断 1 #4）。
- Nudge の時期の統制（ADR-035 Consequences の未決）。

## 受け入れ条件

- [ ] 招待: ADR-026 M11 の 4 つの失敗条件の検査が CI で走り、陽性対照で赤になることを確かめた
- [ ] 招待: ADR-035 Migration 1 の経路独立性（①②③）を陽性対照つきのテストで固定した
- [ ] 招待: ADR-033 の単調性（応答の列だけを変えても頻度と強度の上限が上がらない）のテストがある
- [ ] 招待: 失効のタイマーが招待 1 回ごとに結び付き、古い失効が新しい招待を消さないテストがある
- [ ] 肖像: 同じ入力の列を肖像への操作の有無だけ変えて流したとき、NDJSON・applog・提出物が byte-equal になるテストがある
- [ ] 肖像: Windows の実機で、差し替え → 復元（OS からの読み戻しのパスと SHA-256 の両方）、異常終了・再起動・スリープ復帰・
      複数モニタ・本人が自分で替えた場合を確かめた（macOS は引き継ぎ）
- [ ] 記録: EH3 のモードでないとき NDJSON が byte 同一（既存のゴールデン・`gse-replay` の snapshot が緑）
- [ ] 記録: `emit_schema` の出力と `schema/current.json` が一致し、parity・capabilities_gate が緑
- [ ] `cargo test --workspace`・clippy・tsc が緑。両 OS の CI が緑
- [ ] 実装で決めた値（R-2〜R-9）を根拠つきで `decisions.md` に書き、稿の F 項との対応を残した
- [ ] `/cross-review`（2 巡）と code-reviewer・security-checker を通した

## 関連ドキュメント

- `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`（要件の SSOT）
- `.steering/20261011-portrait-eh3-prereg/decisions.md` 判断 1〜4、`.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 1〜16
- `experiments/20261011-portrait-eh3/preregistration-draft.md`
- ADR-026（Accepted）・ADR-033（Proposed）・ADR-035（Proposed）・ADR-013・ADR-021 D4・ADR-024・ADR-027 D4
- `experiments/20261010-portrait-eh1-round5/scripts/portrait.py`、`experiments/20261009-portrait-eh2/`

## 運用メモ
- /reimagine 適用: No
- 理由: 外枠と要件は前タスクで研究者が決め、`/cross-review` 2 巡を通している。残る判断は値と配置で、本タスクの grill（decisions.md 判断 1〜2）で分岐を閉じた。PR を層ごとに分けて進める（判断 1 #4）。
