# pc-invitation-surface — PS-Q7 を閉じる（PC 側の招待面の視覚設計要件）

> 2026-09-07 開始 / ブランチ: `feat/resumption-outcome-arbitration`
> ★ 入口: `.steering/_handoff/next-session-after-adr025.md` §B-0（第一候補）

## 背景

★ **一次で確認済み**（`docs/architecture/expression-channel.md` §8 の `PS-Q7` 行・2026-09-07 起票）:

- ⚠️★★★ **招待を差し出す面（PC 側）に、視覚設計の要件が 1 つも存在しない。**
- ★ **A-1〜A-8**（§3.5.2）も **受け入れ観点 A11–A14**（§7.5）も、すべて **層 A ＝ スマホ** 向けである。
- ★ **§6.2 は「PC に置く *理由*」しか書いていない**（観測可能性 / 境界の一方向性 / 役割分離）。
- → ★ **PC 側の面は「要件が緩い」のではなく「書かれていない」。**

⚠️ **層 A の要件をそのまま流用できない** —— ★ **曝露の性質が違う**:
層 A ＝ アンロック動作に埋め込まれた *強制* 曝露 ／ PC ＝ **主課題と同じ面**。

★ この穴は `.idea/20260907-resumption-outcome-and-attention-sensitive-expression.md` §2 と §6 の
設計問い 5 本に対応する（⚠️ **三次資料。根拠にしない**）。

## ゴール

★ **PS-Q7 を裁定として閉じる。**具体的には:

1. **PC 側の要件表**（層 A の A-1〜A-8 に対応するもの）を `expression-channel.md` に起こす。
2. **§7.5 に PC 側の受け入れ観点**を足す。
3. **ADR-026** として裁定を残し、`docs/adr/README.md` の index を更新する。
4. 裏付けとして **文献サーヴェイを 1 ラウンド**回し、`docs/references.md` に append-only で登録する。

## スコープ

### 含むもの
- ★ `expression-channel.md` §3.5 系に **PC 側の要件表**を新設（層 A の A-n と混ざらない採番）
- ★ `expression-channel.md` §7.5 に **PC 側の受け入れ観点**を追加
- ★ `expression-channel.md` §8 の **`PS-Q7` 行を閉じた状態へ更新**
- ★ **ADR-026** の新規作成（`Accepted`）＋ `docs/adr/README.md` index 追記
- ★ **文献サーヴェイ 1 ラウンド**（`literature-review` ＋ サブエージェント並列）
  - ⚠️ `.idea` メモの **未登録引用 3 件**の一次検算を含む:
    Fukasawa & Shimomura (2021) `10.5100/jje.57.119` /
    Hodgetts & Jones (2014) `10.1080/00140139.2014.952680` /
    Brumby et al. (2013) PMID `23795978`
  - ★ `docs/references.md` への append はメインが直列で行う
  - ★ カードを書くなら `docs/literature/` ＋ `_index.md`
- ★ 既存一次 **[P267] / [P256] / [P85]** の **逐語検算**（★ §8 の記述は SSOT で裏を取る）

### 含まないもの
- ⚠️★★★ **W-2 を閉じない**（★ 発火条件 / 初期同期 / 解除の区別 —— ★ **PS-Q7 とは独立**。
  ★ PC 側の招待表現は **ローカル**で境界イベントを通らない）
- ⚠️ **既存 ADR（017/018/020/021/022/023/024/025）の本文を書き換えない**（★ 番号の大きい ADR が上書きする）
- ⚠️ **凍結済み `docs/preregistration-v0.3.md` を書き換えない**
- ⚠️ **実装しない**（★ `src-tauri/src/` / `src/` に `invitation` は 0 件のまま）
- ⚠️ **具体的な造形・色・アニメーション仕様を決めない**（★ `.idea` §7 の「決めていないこと」に従う）
- ⚠️ **試視を回さない**（★ PS-Q5 / E-7 / M-3 は別タスク）
- ⚠️ **試視ハーネスの設計・機械検査を変えない**（★ ADR-023 M6・selftest 41/41 が基線）
- ⚠️ **`scripts/secrets-filter.sh` を触らない**（★ 引き継ぎ C-1 は別タスク）
- ⚠️★★★ **却下リスト #1–#21 に触れる書き方をしない**（★ ADR-023 9 項 / ADR-024 #10–14 / ADR-025 #15–21）

## 受け入れ条件

- [ ] `expression-channel.md` に **PC 側の要件表**が存在し、各行が **一次の逐語**に紐づく
      （⚠️ 一次の無い行は「未決」と明示する）
- [ ] `expression-channel.md` §7.5 に **PC 側の受け入れ観点**が追加されている
- [ ] `expression-channel.md` §8 の `PS-Q7` 行が **閉じた**（★ 残った未決は別行として立っている）
- [ ] `docs/adr/ADR-026-*.md` が存在し `Accepted` で、`docs/adr/README.md` の index に載っている
- [ ] サーヴェイで採った出典が `docs/references.md` に **append-only** で登録されている
      （★ 番号は末尾の次番号・再利用なし）
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が **「違反なし」まで**通る
- [ ] `code-reviewer` ＋ `security-checker` 並列 → HIGH 指摘を **本タスクで消化**
- [ ] `/cross-review` を **コミット後・パス限定**で回す（★ 2 巡）

## 関連ドキュメント

- `docs/architecture/expression-channel.md` §3.5 / §3.5.2 / §6.2 / §7.5 / §8
- `docs/adr/ADR-017` / `ADR-021` / `ADR-022` / `ADR-023` / `ADR-025`
  （⚠️★★★ **ADR-017 単独で読むと古い契約を掴む。必ず番号の大きい方まで読む**）
- `docs/references.md`（★ 引用 SSOT）/ `docs/literature/_index.md`
- `.idea/20260907-resumption-outcome-and-attention-sensitive-expression.md`（⚠️ 三次資料）

## 運用メモ
- /reimagine 適用: **Yes**
- 理由: ★ **設計判断そのものが成果物**（PC 側の要件を「何本・どの粒度・どの根拠で」立てるかは
  複数案があり最良案が自明でない）。★ ADR-025 の教訓 5「`/reimagine` は *案を選ぶ* より
  *射程を切る* ために効いた」を踏まえ、要件表の**射程**（PC 面のどこまでを縛るか）を切るのに使う。
