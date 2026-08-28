# 要件 — O1 の配備インフラ ＋ 打鍵の実機確認

## 背景

`.steering/20260827-o1-collection-enablement/` で **O1 の計器は実装・検証済み**である。
本タスクは計器を作り直さない。残っているのは
**(A) 打鍵 `key` 行の実機確認 / (B) UI のクリック通し / (C) 外界の配備インフラ** の 3 つ。

一次記録: `.steering/_handoff/next-session-prompt-o1-infra-and-key-verification.md`

## ゴール

- **A**: `GSE_O1_MODE=1` で起動し、研究者が実際にタイプしたときに
  `gse_o1_*.ndjson` へ `"type":"key"` 行が出る／生 VK が無い／`feat.keys` が 0 でない／
  `hook_health.starved_ms` が 0 のままであることを**実測**で確かめる。
- **B**: 宣言 4 択 / すぐ止める / 時間帯削除 / 開始前ゲート の 4 経路を**実機のクリック**で通す。
- **C**: O1 の提出先 (受け口・Drive・secret)・age 鍵・`g1-submit.json`・フォーム・
  配布 zip の `o1.mode`・同意文書の連絡先・**送信済み分の削除手順 (台帳)** を配備可能な状態にする。

## スコープ外

- 計器の作り直し（実装・レビュー・検証は完了済み）
- R-15（時計の前進で猶予が消える）— 起票のみ
- 段 1 のチャネル追加 / `task_kind` の enum 追加（凍結済み）

## ★ セッション冒頭で一次資料から確かめたこと（引き継ぎメモの検算）

| 主張（引き継ぎメモ §5） | 一次資料での実測 | 判定 |
|---|---|---|
| ブランチ `feature/o1-collection-enablement` に 11 コミット未 push | `git rev-list --left-right --count origin/main...main` = `0 0`。PR #120 マージ済み | ⚠️ **古い。解消済み** |
| gse-dataset にコミット 1 本未 push (`4a02dda`) | `git -C C:/gse-dataset rev-list --count origin/main..main` = `0` | ⚠️ **古い。push 済み** |
| CI は復旧済み・main は緑 | `gh run list --branch main` 最新 run `33096214706` = **success** (2026-08-27T17:00:59Z) | ✅ 支持された |
| `scripts/make-participant-zip.sh` が配布 zip を作る (C-5 の対象) | 同スクリプトは**汎用 zip 化のみ**。`g1.mode` / `g1-submit.json` を置くのは `experiments/20260801-controlled-friction-task/make-distribution.sh:149-150,179-180` と `make-common-app-zip.sh:91-92,132-133` | ⚠️ **メモの指す先が違う** |

## ★★★ 新たに見つかった障害（C-1 の前提を変える）

**現行の受け口は O1 の提出物を 1 本も受け取れない。**

`Form_G1/GSE_G1_Submit.gs:229` の `sanitizeName_` は
`/^[A-Za-z0-9]{1,16}_block\d{2,3}_gse_\d{8}_\d{6}(_\d{1,10})?\.age$/` しか通さない。
O1 の提出物名は `submission::o1_age_file_name`（`submission.rs:267`）が作る
`<participant>_o1day<NN>_<stem>.age` で、stem は `gse_o1_<date>_<time>`（`o1.rs:263`）。

実測（`node` で当該正規表現をそのまま評価）:

```
ACCEPT  P012_block03_gse_20260807_101112.age
REJECT  P012_o1day01_gse_o1_20260828_143000.age
REJECT  P012_o1day01_gse_o1_20260828_143000_2.age
```

→ ⚠️ **`bad name` が返り、収束器は「未送信」のまま何度でも失敗を繰り返す**
（`GSE_G1_Submit.gs` 自身が「永久に届かない = 黙って壊れる経路」と警告している型）。
→ ★ **「同じ受け口をそのまま使う = 手間ゼロ」は成り立たない。** どちらを選んでも `.gs` の改修と再デプロイが要る。
