# 入力データの固定（未実施・実施時に埋める）

> ⚠️ **本実験は設計のみで未実施**。被験者募集も行っていない。

## 規約（`docs/development-guidelines.md` §10 / `data-privacy` Skill）

- **セッション NDJSON は本リポジトリにコミットしない。**
- 共有アーティファクトは `gse-replay --metrics --json` の出力（`metrics.json`）のみ。
- 生ログは [mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset)（private）の
  `metrics/P*/<os>/` に置き、**本ディレクトリからは commit hash で参照する**。

## 実施時に記入する

| 項目 | 値 |
|---|---|
| gse-dataset commit hash | TBD |
| 被験者 ID（P0xx） | TBD |
| セッション数 / ブロック数 | TBD（設計上は 1 人 8 ブロック） |
| NDJSON の hash | TBD |
| 課題文セット ID | TBD（課題文は未作成・README §5-1） |

## 課題文について

LO 用資料（1 本）と HI 用資料（相互に矛盾する 3 本）は**未作成**である。
セッション間で使い回さないだけのセット数が必要（README §5-1）。
課題文自体は被験者の産出物ではないためリポジトリ内に置いてよいが、
**被験者が書いた本文は保存しない**（content-free 原則）。
