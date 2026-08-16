# physical-anchor Skill を既決 D10/D11 と [P77] に整合させる

> ⚠️★★★ **本ディレクトリは 2026-08-15 に「切り出し」だけを行った。未着手である。**
> ★ 着手は別セッションで行う（★ CLAUDE.md のタスク境界: `/clear` → 実装フロー）。
> ★ 出所: `.steering/20260814-expression-place-and-modality/decisions.md` **PM-D5 / PM-D11 / PM-D12**

## 背景

`physical-anchor` Skill は CLAUDE.md が **Lv3/Lv4 設計時の必須参照**に指定している。
⚠️ しかし **Skill の内容が、後から確定した既決 D10/D11 および出典 [P77] と矛盾している。**
★ **放置すると、次に Lv3 を触る者（人でもエージェントでも）が Skill の指示どおりに D11 違反を実装する。**

### 矛盾 1: 完了条件が「量」で本人の解放を決めている

| 出所 | 内容 |
|---|---|
| `.claude/skills/physical-anchor/SKILL.md`（介入レベル定義） | **Lv3 完了条件 = 歩数達成**（室内歩行 50〜100 歩）／ **Lv4 完了条件 = 距離達成**（屋外 500m 以上） |
| 同 ルール 1 | 歩数 / 移動距離 / 歩行速度を `pedometer` / `geolocator` で計測すると規定 |
| ⚠️★★★ **既決 D11**（`.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md:217-220`・逐語） | **「歩数・距離・MET 等の量を算出して本人に向けない。使ってよいのは『歩いた / 歩かなかった』の二値のみ」** |
| ★ D19 の「不変」行（同 `:459`） | **D10（歩行を MhD の観測に入れない）・D11 は変更しない** |
| ★ [P77]（`docs/references.md`・一次逐語照合済み） | **計測してよいのは打鍵（作業＝害の減衰条件）／計測してはいけないのは歩行（回復・楽しい活動＝害が最大）** |
| ★ [P99]（`docs/references.md`・一次全文確認） | **performance-contingent で「最大報酬に届かなかった」群の毀損が全群中最大 `d = −0.88`** |

⚠️ **`physical-anchor` Skill は D11 より前の設計であり、[P77] / [P99] を織り込んでいない。**

### 矛盾 2: 参照先が空である

`SKILL.md:171` は関連 Skill として
> `data-privacy` — **位置情報・歩数データのプライバシー扱い**

と書いているが、⚠️★★★ **`.claude/skills/data-privacy/SKILL.md` に位置情報の規定は 1 行も無い。**
★ **実測**: `grep -n "位置\|GPS\|location\|歩数\|pedometer\|加速度"` の該当は
**キーボードのスキャンコードに関する 1 行のみ**（`pub scan_code` のコメント）。

## ゴール

★ **Lv3/Lv4 を実装しようとする者が Skill だけを読んでも、D10/D11 に反する設計に到達しないこと。**

## スコープ

### 含むもの
- `.claude/skills/physical-anchor/SKILL.md` の**介入レベル定義**と**ルール 1（計測指標）**の改訂
- `.claude/skills/data-privacy/SKILL.md` への**位置情報・歩数データの規定の追加**（★ 参照先の空を埋める）
- ★ 改訂根拠を `.steering/` に記録し、D10/D11/[P77]/[P99] へのリンクを Skill 本文に埋める

### 含まないもの
- ⚠️ **Lv3/Lv4 の実装そのもの**（★ 現行の最高介入は Lv2 Wall。Skill 冒頭が明記）
- ⚠️ **既決 D10 / D11 / D19 の改訂**（★ D19 が「不変」と明記している。変えるなら別の判断が要る）
- ⚠️ **Phase 1 のスコープ変更**（★ 既決 D8: 散歩は WoZ ＋ 自己申告で受容性のみ。★ 事前登録に影響する）
- `docs/functional-design.md` の Lv3/Lv4 記述（★ 影響調査の結果 必要なら別途）

## 受け入れ条件

- [ ] **Lv3/Lv4 の完了条件が「量」でなくなっている**
      （★ 採る形の候補: **時間**（Lv2 Zen Timer と同型・経過であって成績ではない）／**往復の二値**）
- [ ] **Skill 本文に D10 / D11 / D19 / [P77] / [P99] への明示リンクがある**
- [ ] **`pedometer` と `geolocator` が別扱い**になっており、**GPS 位置履歴の扱いが明記**されている
- [ ] **`data-privacy` Skill に位置情報・歩数データの規定が追加**され、`physical-anchor:171` の参照が実体を持つ
- [ ] ★ **「量を測ってよいが本人に向けない」と「量を測らない」のどちらを採ったかが書かれている**
      （⚠️ PM-D11 の結論は**前者**: D11 は計測自体を禁じていない）
- [ ] ★ **検査を一緒に置く**（`verify-before-claiming` ルール 6）——
      例: Skill 内に「歩数達成」「距離達成」が完了条件として再出現しないことを検査する grep
- [ ] `empirical-prompt-tuning` で改訂後の Skill を検証したか、**しなかった理由が書かれている**

## 関連ドキュメント

- `.steering/20260814-expression-place-and-modality/decisions.md` **PM-D5 / PM-D11 / PM-D12**
- `.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md` **D10 / D11 / D19**
- `docs/references.md` **[P77] / [P99] / [P101] / [P107]**
- `docs/literature/20260815-portable-ambient-object-and-activity-coupling.md` カード 2・カード 3
- `.claude/skills/intervention-design/SKILL.md`（★ Lv1/Lv2 の既存段階設計・Zen Timer の形）
