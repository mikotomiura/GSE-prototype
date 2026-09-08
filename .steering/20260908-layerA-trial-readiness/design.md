# 設計

> ⚠️★★★ **未着手である**（★ 2026-09-08 は起票のみで中断した）。
> ★ **設計を書く前に、`requirement.md` の「含めるか未確定」を裁くこと** ——
> ★ **`E-12` の二重課題を「層 A のハーネス」と「PC 面の別実験」のどちらへ置くか。**
> ⚠️ **決めずに設計すると、測った物と閉じたい未決が食い違う。**

## 実装アプローチ

★ **次セッションで書く。**★ 入口は `.steering/_handoff/next-session-layerA-trial-readiness.md` §A。

## 変更対象（★ 見込み・確定していない）

### 修正するファイル
- `experiments/20260902-expression-layerA-visual/player/layerA.html` — 周辺視ブロック / 中止ボタン / `1b'` の DOM 分離
- `experiments/20260902-expression-layerA-visual/layerA.config.json` — ⚠️ **周辺視の枠が既にある**（★ 値を埋める）
- `experiments/20260902-expression-layerA-visual/scripts/selftest.py` — 機械検査の追随
- `experiments/20260902-expression-layerA-visual/notes.md` — §現況 / §5 の更新

## テスト戦略

- ★ **機械検査を追随させる**（★ Python / ページ内の両方）
- ⚠️★★★ **検査を「正常 / 不在 / 壊れている」の 3 状態で試す**（`verify-before-claiming` ルール 5b）
  —— ★ **本ハーネスは「機械検査 42 項目が緑のまま HIGH 5 件を見逃した」実績がある。**
- ★ **ブラウザ実測**（`browser-verification` —— ⚠️ **機械検査が緑でも読めるかは何も分からない**）

## ロールバック計画

★ **`experiments/` 配下のみなので `git revert` で戻る。**
⚠️ ただし **`SEED` を再固定した場合は、過去の結果と比較できなくなる**ので `data.md` に境界を書くこと。
