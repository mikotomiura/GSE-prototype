# 次セッション — 論文化トラックの具体的な議論（IME 論文の評価設計の確定 ＋ [P321] 2 本目の再検討）

> 作成: 2026-09-27（論文化可能性調査 → grill の直後）。同日、[P321] の再検討を追加。
> ⚠️ **このメモを一次資料にしない。** 数字・状態は着手時に測り直す。
> ★ 他の handoff（O1 リリースタグ・loop-run 修正）と触るファイルが別なので並行可能。

## §0 打ち込む用

```
.steering/_handoff/next-session-ime-paper-discussion.md を読んで、論文化トラックの議論を進めてください。
まず .steering/20260927-ime-observation-paper-eval-design/ の paper-suggest.md・decisions.md（判断 1–9）・design.md を読む。
トラック A（IME 論文）: paper-suggest.md §7 の論点を 1 つずつ閉じ、design.md の承認が取れたら /reimagine を回す。
トラック B（[P321] の 2 本目）: 本メモ §3 のサーヴェイを実施し、判断 9 を見直すかどうかを決める。
★ B のサーヴェイは A と独立なので、subagent に並列で投げてよい（subagent-delegation skill の契約で）。
Skill: verify-before-claiming・reproducibility-discipline・citation-ssot・subagent-delegation（B は literature-review / literature-card も）。
応答は日本語。
```

## §1 状態

- 作業ディレクトリ: `.steering/20260927-ime-observation-paper-eval-design/`（requirement / decisions 判断 1–9 / design v1 / tasklist / paper-suggest）
- 確定済み: BRM に 2026 年内投稿・CHI 2027 Posters は任意・合成入力のみ・参照入力欄を正解・両 OS 主要 IME・評価一式だけ先に公開・貢献 C1–C5
- 暫定: **2 本目は今は書かない**（判断 9。[P321] 再解析は原著者データの再解析なので、RENE トラックの「新しいデータへの適用」条件を満たさない）→ 本メモ §3 で再検討する
- 未確定: design.md の承認と `/reimagine`、タイトル、ライセンス、BRM 規程、CPU 値の計測法、[P321] の 2 本目
- ⚠️ 本タスクのファイル（`.steering/20260927-ime-observation-paper-eval-design/`・本メモ・`docs/glossary.md` の 2 行）は**未コミット**で、`fix/loop-run-progress-flag` ブランチの作業ツリーにある。コミットする前に専用ブランチ（例: `docs/ime-paper-eval-design`）へ分けること。

## §2 トラック A — IME 論文：着手時に一次で確かめること

- `experiments/20260903-o1-runtime-cost/` の CPU 平均 0.98% がどの計測法の値か（memory `macos-top-l2-undercounts-cpu`）
- MS-IME（TSF）から自窓へ `WM_IME_STARTCOMPOSITION` 等の IMM 互換メッセージが届くか（MS の一次文書 → 可能なら実機）
- `NSTextInputClient` の呼び出し順（Apple の一次文書）
- BRM の規程（Springer のページは WebFetch で取得できなかった → ブラウザで読む）

## §3 トラック B — [P321] 再解析を 2 本目にできるか（サーヴェイ → 再検討）

### 3.1 現状（2026-09-27）

- 解析は済み: `experiments/20260906-p321-resumption-baseline/`（既報値 12 項目を検算・R₀ = 70/89 = 0.787・分母の効果 −3.5pt に対し分子の効果 +11.2pt・放棄の混入の向きが直観と逆）
- ⚠️ 受け皿の条件（判断 9 に逐語と URL）:
  - SANER 2027 RENE: abstract **2026-10-19** / paper **10-23**・10+2 頁・double-anonymous・「新しいデータセットへの適用」が必須
  - ICPC 2027 RENE: abstract **2026-12-11** / paper **12-18**（2027 年版の規程本文は未確認。2026 年版は新データ必須・非匿名査読・10+2 頁 or 4+1 頁）
- ⚠️ 既知の弱点: 89 episode 全体は第一著者 1 名のコーディング・N = 11 名 / 15 セッション・活動数に 1 件の未解決差（`notes.md` §4 / §7）

### 3.2 サーヴェイで答える問い

1. **[P321] と同じ定義（episode の開始 = 行き詰まり / 終了 = 解決または中止・外部資源の参照の有無・結末）を当てはめられる別の公開データはあるか。**
   - 候補の方向: 開発者の画面録画 / 発話思考を人手でコーディングした公開データ、IDE の操作ログ ＋ ブラウザ履歴のデータ、Stack Overflow 参照を含む開発行動データ、LaToza 研究室の他のデータ公開
   - 各候補について: ライセンス・入手可能性（リンクが生きているか）・episode の終端（解決と放棄）が区別できるか・外部資源の参照が観測されているか・規模
2. **RENE 以外の受け皿はあるか**（原著者データの再解析と、新しい指標の提案を受ける場）。
   - 例: VL/HCC の short paper、ICSE / FSE 系のワークショップ、MSR 系、ESEM の emerging results。⚠️ 各 CFP の締切・頁数・「再解析だけでよいか」を一次で確かめる
3. **R₀ / R₀′ のような「外部資源を参照せずに終わった割合」や「解決と放棄の混入」を既に扱った先行はあるか**（新規性の確認。⚠️ 「先行が存在しない」とは書かない）

### 3.3 判断のしかた

- 研究者の基準: **accept されやすい** かつ **機が熟している（すぐ書ける）** の両方を満たすなら 2 本目を書く。
- 3.2-1 で使えるデータが見つかる → 新しいデータへの適用として ICPC 2027 RENE（12-18）を検討する。⚠️ IME 論文の BRM 投稿（12 月）と時期が重なるので、工数を見積もって研究者が判断する。
- 3.2-2 で再解析だけを受ける場が見つかる → 締切と受理の見込みを並べて研究者が判断する。
- どちらも無い → 判断 9 を維持する。
- 結論は `decisions.md` に判断 10 として記録し、`paper-suggest.md` の候補表と投稿計画を更新する。見つけた文献は `citation-ssot` の手順で `docs/references.md` に登録する。

## §4 やらないこと

- 人の打鍵データを使う（著者本人も含む）
- Phase1 / G1 / O1 のデータを IME 論文に混ぜる
- プロトコル凍結前に実測を始める
- ⚠️ [P321] の値を GSE の期待値として使う（`experiments/20260906-p321-resumption-baseline/notes.md` §4）
