# design

## アプローチ

### §1 CPU% 規約（★ 3 系統の証拠を揃える）

| 系統 | 手段 | 状態 |
|---|---|---|
| 一次資料 | Microsoft *Examining Processor Time Data* の逐語 | ★ 取得済 |
| 実機実測 | Windows で busy-loop を 1 個作り `Get-Counter` を読む | ★ 研究者に依頼 |
| 内部整合 | Windows 実測 809/903 行の p99 が 7.75 %（×16 = 124 %）である蓋然性 | ★ 参考 |

⚠️ **どちらに転んでも**「どちらの規約で記録したか」を `meta.json` に残す。

### §2 取り込み（案 B）

Windows 実測に関係するパスだけを別ブランチへ持ってくる:
`experiments/20260903-o1-runtime-cost/**` / `.steering/20260904-windows-orphan-verify/**`

⚠️ `scripts/build_analysis_db.py` / `secrets-filter.sh` / `md2pptx.py` / `metrics.rs` /
ADR-023〜028 / 表現層は **この PR に入れない**（後続 C）。

### §4 mac 側

- B: `GSE_COST_DURATION_S=300 GSE_COST_INTERVAL_S=1`。⚠️ サンプラを先に起こしてから GSE 起動。
- A: スリープ跨ぎ。手順は `_handoff/next-session-prompt-post-windows.md §2-1`。
  ⚠️ 陰性対照（スリープさせない同尺の区間）を置く。
- C/D: 4 ブランチの棚卸し。⚠️ 消す前に「先」の中身が main にあるか `git cherry` で確かめる。

## テスト戦略

- ★ `summarize.py` を変えたら **既存 results（macOS 2 本・Windows 1 本）で再集計**し、
  ⚠️ 数値が変わらないこと（陰性対照）を確かめる。
- ★ 規約列の追加は **不在（旧 results）** でも壊れないこと（3 状態: 正常 / 不在 / 壊れ）。
