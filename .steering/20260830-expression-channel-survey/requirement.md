# スマホ表現チャネル / 計測なき身体回帰 — SSOT 昇格前のサーヴェイ 4 ラウンド

## 背景

`.idea/20260819-smartphone-computational-media-channel.md`（★ `.gitignore:58` で追跡外・SSOT ではない）は、
**スマートフォンを表現媒体とする案（§1–§11）**と**「計測なき身体連動 / 身体回帰」（§12）**、および
2026-08-23 追記で **Physical Anchor の合流**を扱っている。

⚠️★★★ **このメモの本格議論は一度も実行されていない。**
- 引き継ぎ `_handoff/next-session-prompt-smartphone-expression-channel.md`（2026-08-21）は存在するが、
  冒頭で「後回し」と明記され、以降 `20260823-r3-accept-and-role-category/tasklist.md:49` 等で
  「次セッション」として繰り返し先送りされた。**対応する `.steering/` ディレクトリが存在しない。**
- ★ **実測**: `docs/` に `Expression Channel` / `表現チャネル` / `計測なき身体連動` / `身体回帰` は
  **1 件もヒットしない**。ADR も無い。

★ 研究者判断（2026-08-30）: **新セッションで議論と全体アーキ再構築・理論構築を行い、SSOT へ昇格させる。**
**その前段として、サーヴェイを本セッションで回す。**

### ★ 既存サーヴェイの棚卸しで判明した「一度も探索していない穴」

| # | 穴 | 出所 |
|---|---|---|
| 1 | **スマホを表現面にする系そのもの**（ロック画面 / AOD / ライブ壁紙 / ウィジェット）。既存の先行は例外なく専用オブジェクト・据置・ウェアラブル | メモ §1–§4 の中核。**該当ラウンドが存在しない** |
| 2 | **自動再生・自動前面化の受容**。イヤホン接続 ≠ 装着 の実証も無し | メモ §3.3 / §6 / §9-3 |
| 3 | **遅延・非同期フィードバック** | `20260807-self-state-externalization-and-ambient-media.md` やり残し #9 が名指しして**未着手のまま** |
| 4 | **[P77] 実験4の減衰の大きさ / 認知作業文脈での再現 / 「量でなく有無」が回避になるかの直接証拠** | `20260810-auditory-*` 追補5 やり残し #2・#3・#4（**#4 は現状ただの演繹**） |
| 5 | **理論骨格が空**: 不便益 [P6] は URL 無しの 1 行のみ / **SDT は references に 0 件** / Slow Technology・Reflective Design 0 件 / informative art [P113] 一次未取得 | ★ **本日 grep で実測** |
| 6 | generative art / 非表象的可視化の受容 | 追補5 やり残し #5 |
| 7 | 未取得の最有力: arXiv 2307.05986 / [P111] Bell 2013 / Wilson 2015 | third-place やり残し #2、parsimony やり残し #1・#2 |

## ゴール

★ **次セッションが「議論と再設計」だけに集中できる状態を作る。**
すなわち、メモ §1–§12 と 08-23 追記の 5 論点を裁くのに必要な**文献側の材料が揃っている**こと。

## スコープ

### 含むもの
- **R-1** スマホをアンビエント表現面にする（穴 1・7）
- **R-2** 自動開始の受容と安全条件（穴 2）
- **R-3** 計測なき身体回帰の支柱（穴 3・4）
- **R-4** 研究コンセプトの理論骨格（穴 5）
- 各ラウンドの `docs/literature/<date>-<slug>.md` 生成 / `docs/references.md` への append-only 登録 /
  `docs/literature/_index.md` 追記 / `docs/research-positioning.md` **§3** への還元
- ★ 次セッション用の引き継ぎプロンプトを `.steering/_handoff/` に作成する

### 含まないもの
- ⚠️ **メモの ADR 化・SSOT 昇格そのもの**（★ 次セッションの研究者判断）
- ⚠️ **`docs/research-positioning.md` §4（差分）・§5（仮説）の書き換え**
  （★ §5 は研究者確認が要る節。§4 は概念そのものなので次セッションで裁く）
- ⚠️ **`src-tauri/` の変更**（★ 計器は 2026-08-21 に凍結）
- ⚠️ **凍結済み `docs/preregistration-v0.3.md` / G1 事前登録の書き換え**（ADR-015 D5）
- ⚠️ **実装**（Flutter / スマホ側 / 配線）

## 受け入れ条件

- [ ] R-1〜R-4 の 4 カードが `docs/literature/` に生成されている
- [ ] 各ラウンドが**反証 angle を含み**、**否決リストを持ち**、**下位問いごとに温度が分かれている**
- [ ] `docs/references.md` に append-only 登録され、`python scripts/check_citations.py` が**違反なし**
- [ ] `docs/literature/_index.md` に 4 行追記され、「やり残し」が次ラウンドの入口の粒度になっている
- [ ] `research-positioning.md` §3 への還元（または「還元不要」の判断）が明示されている
- [ ] ★ **ラウンドごとに分離コミット**されている（★ 同居させると `git add -p` で分離できない）
- [ ] ★ 次セッション用引き継ぎが `.steering/_handoff/` にあり、**裁くべき論点と既決の制約が埋め込まれている**

## 関連ドキュメント

- `.idea/20260819-smartphone-computational-media-channel.md`（★ 追跡外。議題の本体）
- `.steering/_handoff/next-session-prompt-smartphone-expression-channel.md`（★ 2026-08-21 の未実行引き継ぎ）
- `.steering/20260814-expression-place-and-modality/decisions.md` **PM-D4 / PM-D5 / PM-D11 / PM-D13**
- `.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md` **D8 / D9 / D10 / D11 / D19**
- `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md`（★ 表現層の既存仕様）
- `.steering/20260815-public-space-and-media-art/decisions.md` **PS-Q1 / PS-Q3 / PS-Q5 は未決**
- `.steering/20260815-physical-anchor-d11-alignment/`（⚠️ **未着手**。Skill が D11 違反のまま）
- `docs/adr/ADR-015-wall-removal.md` **D4**（⚠️ Physical Anchor は運搬路を失った）
- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md`（★ `self_directed_recovery_risk` は**コード未実装**）
