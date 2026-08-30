# 表現チャネル / 計測なき身体回帰 — 議論・全体アーキ再構築・理論構築 → SSOT 昇格

> 入口: `.steering/_handoff/next-session-prompt-expression-channel-ssot.md`（2026-08-30）
> 入力: 同日のサーヴェイ 4 ラウンド（[P133]–[P191] / [V87]–[V88]・`docs/literature/20260830-*.md` 4 枚）

## 背景

`.idea/20260819-smartphone-computational-media-channel.md`（347 行・⚠️ `.gitignore` で追跡外＝ SSOT ではない）は、
表現媒体としてのスマートフォンと「計測なき身体連動」を記録した個人設計メモである。
2026-08-23 に **Physical Anchor がこのメモへ合流**した（ADR-015 D4 で `wall_server.rs` が消え、
PM-D11 が前提にしていた「既存の Wall Server の 1 ビット経路がそのまま使える」が覆ったため）。

2026-08-30 のサーヴェイ 4 ラウンドで、このメモが依拠していた前提が 3 つ崩れた:

1. ⚠️ **「スマホ表現面は未探索」は誤り** —— [P101] UbiFit の glanceable display は *携帯電話の壁紙* であり
   （逐語 *"resides on the background screen, or 'wallpaper,' of the individual's mobile phone"*）、
   [P102] も lock / home 画面。GSE は既にスマホ表現面の一次証拠を 2 本持ち、それを
   「可搬な物理オブジェクト」の根拠として読み替えていた。
   かつ **「常在面に置くこと自体」に効能は無い**（事前登録 cross-over・N=60・確証 6 アウトカム全 null・
   BF₁₀ 0.066–0.433 [P147]）。
2. ⚠️ **「打鍵は work だから測ってよい」に条件が付いた** —— [P77] 実験 4 の一次全文で、
   仕事枠付けによる減衰は *無計測時の楽しさを先に d ≈ 0.60 下げて* 買っていた（t(159)=−3.06, p=.003）。
   保護は「ユーザーが自作業を work と感じている限り」でしか働かず、GSE の目標状態 Flow は
   定義上その条件から外れる（fun-frame セル d ≈ −0.48）。
3. ⚠️ **「不便益 HCI である」が現行実装で支えられない** —— 不便益の認定条件 1（益は不便だからこそ）は
   **労力**を要求するが、ADR-015 後に稼働するのは Lv1 Nudge のみで労力を課さない [P170]。

さらに **メモ自身が内部矛盾している** —— §5 は常時ストリームを想定するが、§7 は
「状態が安定したとき、または介入レベルが変化したときだけ更新する」＝イベント駆動と書いている。
PM-D4 は「状態を常時流し続けるのは一段大きい」と判定済みで、この衝突は 2026-08-23 の追記が
論点 2 として自認していたが裁かれていなかった。

## ゴール

`.idea` の議論を裁き、**表現チャネルの設計判断と研究の主張を SSOT へ昇格させる**。

1. 論点 1〜6（引き継ぎ §3）を、閉じたもの / 閉じなかったものに分けて決着させる
2. **ADR を新設**して境界クラスと媒体分離を確定する
3. **`docs/architecture/` に表現チャネルの文書を新設**する（現在 SSOT が `.steering/` にしかない）
4. `docs/research-positioning.md` の主張の温度を一次に合わせる
5. `docs/glossary.md` に用語を確定する
6. 引き継ぎ §5 の「放置すると事故になる」5 件を裁くか切り出す

## スコープ

### 含むもの
- `docs/adr/ADR-017-*`（新設）／`docs/adr/README.md` 一覧への追記
- `docs/architecture/expression-channel.md`（新設）
- `docs/research-positioning.md` **§1 / §4 / §7 / §8 / §9**（★ 研究者承認済み・2026-08-30）
- `docs/glossary.md`（表現チャネル関連の用語追加・禁止用語の ADR-015 追随）
- `docs/architecture.md`（ADR-015 未追随の 3 箇所）
- `docs/agent-shared.md` のリンクハブ
- `.claude/skills/physical-anchor/SKILL.md` の D11 違反是正（★ 研究者承認済み・2026-08-30）
- `.idea/20260819-smartphone-computational-media-channel.md` への追記（閉じなかった論点）

### 含まないもの
- ⚠️ **実装を一切しない** —— Flutter / スマホ側のコードも `src-tauri/` の配線も書かない
- ⚠️ **`docs/research-positioning.md` §5 の適用**（★ 研究者判断で「案提示のみ」。改訂案は本ディレクトリに置く）
- ⚠️ **`src-tauri/` の記録仕様**（2026-08-21 に凍結）／**凍結済み `docs/preregistration-v0.3.md` / G1 事前登録**
  （ADR-015 D5）／**ADR-009 の X 軸**
- ⚠️ **`data-privacy` SKILL への位置情報節の新設** → 別タスクへ切り出す
- ⚠️ **[P6] の書誌確定 / [P170] 図 1 の Objective・Subjective 分類** → サーヴェイの次ラウンドへ

## 受け入れ条件

- [ ] 論点 1〜6 それぞれについて「閉じた / 閉じない（何が埋まれば閉じるか）」が `decisions.md` にある
- [ ] ADR-017 が Accepted で存在し、`docs/adr/README.md` の一覧に載っている
- [ ] `docs/architecture/expression-channel.md` が存在し、`docs/agent-shared.md` のリンクハブから辿れる
- [ ] `research-positioning.md` §1 / §4 / §7 / §8 / §9 が一次の温度に合っている
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が違反ゼロ
- [ ] 引き継ぎ §5 の 5 件が「裁いた / 切り出した」のどちらかに分類されている
- [ ] 実装ファイル（`src-tauri/**` / `src/**`）の差分がゼロ

## 関連ドキュメント

- `docs/adr/ADR-015-wall-removal.md`（D4 が本タスクを開いた）
- `docs/architecture/gse-v2-overview.md` / `docs/architecture/intervention-decision-engine.md`
- `docs/literature/20260830-{smartphone-ambient-surface,auto-onset-acceptance-and-wearing-detection,unmeasured-embodied-return,theory-scaffold-inconvenience-sdt-reflection}.md`
- `.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md`（D8–D11・D21）
- `.steering/20260814-expression-place-and-modality/decisions.md`（PM-D4 / PM-D11 / PM-D13）
- `.steering/20260815-public-space-and-media-art/decisions.md`（PS-Q1 / PS-Q3 / PS-Q5 は保留）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 本タスクは実装着手前の**設計判断そのもの**であり、初回案の破棄・再生成ではなく、
  4 ラウンドのサーヴェイが出した一次証拠に対して既決を突き合わせる作業である。
  代替案の比較は各論点の中で行い（`decisions.md` の「却下案」欄）、ADR の Alternatives に残す。
