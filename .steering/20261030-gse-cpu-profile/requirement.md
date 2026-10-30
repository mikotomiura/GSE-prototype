# gse-cpu-profile — GSE の CPU の内訳を測り、軽くする設計の出発点を作る

## 背景

logger の空回りの修正（`.steering/20261030-logger-flush-busy-loop/`・枝 `fix/logger-flush-busy-loop`・push 済み・PR 未作成）の判断 1 で、「CPU の内訳と軽くする設計は別タスク」と分けた。空回りを除いた後に何がどれだけ CPU を使っているかは、まだ測っていない。
引き継ぎ: `.steering/_handoff/next-session-gse-cpu-profile.md`（一次資料にはしない。数字と挙動はコードと実測で確かめ直す）。

## ゴール

空回りの修正が入った版について、状態ごとの CPU とスレッドごとの内訳を実測で出し、軽くする候補を効きの見込みの大きい順に並べる。直すかどうか・どれからやるかは研究者が決める。

## スコープ

### 含むもの（2026-10-30 に研究者が「1〜4 すべて」と回答）
1. 状態ごとの本体の CPU（累積の CPU 時間の差で測る）: 開始前の停止中・記録中で打鍵あり・記録中で打鍵なし・一時停止中
2. スレッドごとの内訳（`sample`。WebKit の子は責任者の pid で拾う）
3. 重い処理の間にトレイから前面に出られなかった件が CPU と関係するか（全画面の中かどうかと分けて確かめる）
4. 試作の枝の run7 で、開始前に `feat` が出ていなかった理由

### 含まないもの
- コードの修正（直すなら別タスク）
- PR の作成（G-GEAR の処理中のため。push までで止める）
- O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`）を止める・起動すること
- G-GEAR での作業
- NDJSON の生ログ・キーストロークの内容を外部 LLM に送ること

## 受け入れ条件

- [ ] `results.md` に状態ごとの CPU の表（4 状態・測り方と窓の長さつき）がある
- [ ] `results.md` にスレッドごとの内訳の表がある（WebKit の子を含む）
- [ ] 前面に出られない件について、CPU との関係を確かめた結果（または確かめられなかった理由）がある
- [ ] run7 で開始前に `feat` が出なかった理由を、コードと記録で示している
- [ ] 軽くする候補の一覧（効きの見込みの大きい順・根拠つき）がある
- [ ] 次に O1 の版を切るときの実機確認の手順（一時停止中の CPU を含む）が、`docs/o1-distribution-tag.md` の v0.1.40 の注意とつながって書かれている

## 関連ドキュメント

- `.steering/20261030-logger-flush-busy-loop/`（修正の枝の worktree `/Users/johnd/GSE-prototype-logger-flush`）
- `docs/architecture.md`（スレッドモデル）
- `docs/o1-distribution-tag.md`（v0.1.40 の注意）
- 記憶 `macos-top-l2-undercounts-cpu`

## 運用メモ
- /reimagine 適用: No
- 理由: 実測と内訳の報告で、設計判断や実装を伴わない（軽くする設計は候補を並べるまで）
- 作業場所: worktree `/Users/johnd/GSE-prototype-cpu-profile`・枝 `chore/gse-cpu-profile`（`fix/logger-flush-busy-loop` の 140b376b から）
