# requirement — Phase1 完了前の凍結非接触・前倒し準備 (Epic2 安全網 + 集計再現性 + RQ-2 gate)

## 背景
`.steering/_handoff/next-session-prompt-phase1-prep.md` に基づく前倒しラウンド。Phase1 完了/凍結解除
前でも凍結対象に触れずに価値を出せる 3 トラックを調査し (別セッション)、その成果のうち
**additive・凍結非接触**な準備をユーザー承認のうえ実装する。

- 凍結対象 (不触): `schema_dto.rs` / `schema/current.json` / `analysis/engine.rs` (HMM_VERSION) /
  `analysis/intervention.rs` の閾値 / `analysis/probe_scheduler.rs` / `src/App.tsx` argumentative lock /
  `docs/preregistration-v0.3.md`。
- ベース: `origin/main @713c395`。ブランチ `chore/phase1-verdict-and-epic2-prep`。

## ゴール (承認済み recommend = ③ + A + B + D を 1 PR、C は別 PR)
- **③**: RQ-2 (Epic4 gate) deep-research 成果を落合カード + references SSOT に登録 (additive doc)。
- **A**: Epic2 の受け入れゲート (`replay --snapshot` byte-equal) を手動 CLI から **cargo `#[test]`** に格上げ。
- **B**: 未ガードの現行挙動を golden 化 (`phase1_ime_heavy` = IME/沈黙, `category_coverage` = 量子化)。
- **D**: `scripts/repro.sh` = 較正コホート 1 本の来歴固定 + 1 コマンド再現 (reproducibility-discipline)。

## 受け入れ条件
- [ ] 凍結対象ファイルに変更ゼロ (git status で検証)。
- [ ] `cargo test --bin gse-replay` 全パス (新規 golden 回帰含む)。
- [ ] golden は決定論的 (2 回生成で同一)・round-trip exit 0。
- [ ] `repro.sh` が dry-run / 実走ともに動作し verdict と provenance を生成。
- [ ] references.md は append-only (renumber なし・[V45]-[V53])・dedup 済。

## 非スコープ
- C (deep-silence fixture 新規 + golden) は別 PR。
- Epic2 以降のコード実装・HMM_VERSION bump。
