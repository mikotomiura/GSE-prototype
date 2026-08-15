# タスクリスト

> ⚠️★★★ **未着手（2026-08-15 に切り出しのみ）。** ★ 着手は別セッションで `/clear` してから。
> ★ 出所: `.steering/20260814-expression-place-and-modality/decisions.md` PM-D5 / PM-D11 / PM-D12

## 準備
- [ ] `.steering/20260814-expression-place-and-modality/decisions.md` の **PM-D5 / PM-D11** を読む
- [ ] 既決 **D10 / D11 / D19** を一次で読む（`.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md:217-220, :459`）
- [ ] `docs/references.md` の **[P77] / [P99] / [P101] / [P107]** を読む
- [ ] `.claude/skills/intervention-design/SKILL.md` で **Lv2 Zen Timer の形**を確認する
- [ ] `impact-analyzer` で影響範囲を実測する（★ `docs/functional-design.md` / `docs/glossary.md` を含む）

## 実装
- [ ] `physical-anchor/SKILL.md` の**介入レベル定義**を改訂（★ Lv3/Lv4 の完了条件を**量から時間・往復の二値へ**）
- [ ] 同 **ルール 1（計測指標）**を改訂（★ 「測ってよいが**量を本人に向けない**」を明記）
- [ ] 同に **D10 / D11 / D19 / [P77] / [P99] への明示リンク**を追加
- [ ] ⚠️ **`geolocator` の扱いを決める** —— ★ Lv4 の 500m 判定は GPS を要求するので、**Lv4 の再設計が要るか判断**
- [ ] `data-privacy/SKILL.md` に**位置情報・歩数データの規定を新設**（★ 参照先の空を埋める）
- [ ] `physical-anchor/SKILL.md:171` の参照が**実体を持つ**ようにする

## テスト
- [ ] 静的検査を追加（★ **完了条件セル**に「歩数達成 / 距離達成」が出ないこと。⚠️ **語の言及禁止にしない**）
- [ ] 相互参照検査を追加（★ 参照先の節が実在すること）
- [ ] ⚠️ **検査を 3 状態で試す**（正常 / 不在 / 壊れている・`verify-before-claiming` ルール 5b）
- [ ] ⚠️ **`src-tauri/` に触れた場合のみ** `cd src-tauri && cargo test --workspace`
      （★ `Cargo.toml` は repo 直下に無い）
- [ ] `empirical-prompt-tuning` で改訂後の Skill を実測する（★ **やらないなら理由を書く**）

## レビュー
- [ ] `code-reviewer` + `security-checker` を**並列**起動
- [ ] `/cross-review`（★ **必須**。⚠️ 安全ゲートでブロックされた場合は **skip 理由を完了報告に明記**）
- [ ] HIGH 指摘への対応

## ドキュメント
- [ ] `docs/functional-design.md` の Lv3/Lv4 記述を同じ版に揃える（★ 影響調査の結果次第）
- [ ] `docs/glossary.md`（★ 「Physical Anchor」の定義に量が入っていれば直す）
- [ ] `decisions.md` に**採った形と却下した形**を記録する

## 完了処理
- [ ] `/finish-task`
- [ ] ⚠️ **`git push` は deny されている** —— ★ 研究者に `! git push` を依頼する

---

## ⚠️ 着手前に必ず確認すること

1. ⚠️★★★ **既決 D10 / D11 / D19 を改訂しない**（★ D19 が「不変」と明記している）。
   ★ 本タスクが直すのは **Skill が既決と食い違っている点**であって、既決そのものではない。
2. ⚠️ **Lv3/Lv4 の実装には入らない**（★ 現行の最高介入は Lv2 Wall）。
3. ⚠️ **Phase 1 のスコープを広げない**（★ 既決 D8: 散歩は WoZ ＋ 自己申告で受容性のみ・事前登録に影響する）。
