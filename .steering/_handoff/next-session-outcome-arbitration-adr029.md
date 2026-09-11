# 次セッション開始プロンプト — **転帰定義の一本化（issue 007 / 新規 ADR-029）**

> 作成: 2026-09-11 / ⚠️★★★ **このメモを一次資料にしない。**
> 実体は `.steering/20260911-outcome-arbitration-and-o1-preflight/issues/007.md` にある。
> *issue ファイルだけを読んで実行が成立しないなら、分解が失敗している。*

## §0 ⚠️★★★ まずこれを実行する（★ 省略しない）

```bash
cd /c/GSE-prototype        # Windows は git-bash 必須
git switch main && git pull
git status && git branch --show-current
ls docs/adr/ | tail -8      # ★ ADR-028 まで在ることを確認する
```

⚠️★★★ **モデルは Opus。** `issue-slicing` ではなく**裁定**であり、切り方を誤ると
O1 の全収集が無駄になる（`CLAUDE.md` のモデル選択ルール）。

⚠️★★★ **`/reimagine` を設計段階で必ず起動する**（`requirement.md` の運用メモで **Yes** と決定済み）。
初回案を破棄して再生成した案と比較してから ADR を書く。★ **実装着手前専用**なので、
ADR 本文を書き始める**前**に回すこと。

## §1 ★ やること = issue 007 だけ

`.steering/20260911-outcome-arbitration-and-o1-preflight/` を開き、この順に読む:

1. `requirement.md` — 背景（⚠️ 転帰定義が **3 つ並立**している表）
2. **`issues/007.md`** — ★ **これが SSOT**
3. `decisions.md` 判断 3（★ なぜ最優先なのか）/ 判断 7〜11（★ issue 008 で確定した事項）
4. `blockers.md` 起票 1〜8

### ★ ゴール

**O1 の主解析が予測する「未来転帰」の定義を 1 つに確定する新規 ADR を書く。**
⚠️ 具体的には **ADR-009 と ADR-024 の関係**を明文化する ——
**上書きか / 別トラックとして並存か / 第三の統合か**を、理由付きで。

## §2 ⚠️★★★ 前提の現況（★ 2026-09-11 に実測した。古い記述を掴まないこと）

| 項目 | 実測した現況 |
|---|---|
| **新 ADR の番号** | ★ **ADR-029**（`docs/adr/` の最大は **ADR-028**。実測済み） |
| **ADR-024** | ✅ **main に在る**（`docs/adr/ADR-024-resumption-outcome-without-estimator.md`・**Accepted 2026-09-07**） |
| **ADR-009** | ⚠️ **Proposed のまま**（★ Accepted にしない。⚠️ ADR-009 自身が「最大の未決は G1 が `n = 0/3`」と書いている） |
| **`metrics.rs` の改名** | ✅ **取り込み済み**（`pflow_exit_window_ms` / `pflow_exit_manual_gain_rate` などが実在） |
| **issue 007 の Dependencies (001 / 002)** | ✅ **両方とも解消済み**（★ mac 側が取り込みを完了した） |
| **O1 の収集** | ⚠️★★★ **まだ開始していない**（★ だからラベル定義を今のうちに確定する） |
| **配布物の版** | ⚠️ **`v0.1.35`**（2026-09-11 11:02 UTC リリース。★ 古いメモの `v0.1.34` は**失効**） |

### ⚠️ issue 007 の AC 8 にパス誤りがある

逐語: 「`.steering/20260911-idea-to-ssot-intake-and-promotion/_codex-review-007.md` が存在する」
→ ⚠️ **そのディレクトリは存在しない。** 正しくは
`.steering/20260911-outcome-arbitration-and-o1-preflight/_codex-review-007.md`。
★ 分解時の書き間違いなので、**そちらに出力して実行結果に記録する**。

## §3 ⚠️★★★ 裁定の核心（★ ここを外すと ADR が空になる）

**ADR-009 と ADR-024 は主従が反転している。**

| | ADR-009 | ADR-024 |
|---|---|---|
| 時間原点 | stall onset | ★ 離席候補ギャップ（≥180s）明けの**初打鍵** |
| **主イベント** | `recovery`（自力前進の回復） | ★ **`receipt`（external paste）の発生** |
| **`paste` の役割** | ⚠️ **回復を妨げる競合イベント** | ⚠️ **主イベントそのもの** |
| 構造 | 4 択・離散時間 hazard | Aalen–Johansen 競合リスク CIF |
| 状態 | Proposed・凍結中・着手ゼロ | **Accepted** |

⚠️★★★ **両者の関係はどの文書にも書かれていない。**
★ ADR-024 は ADR-009 の「stuck エピソード終端を原点にする案」を**明示的に却下**している
（5/10 分の地平では大半が打ち切りになる。実測 gap 中央値 263.6s / p90 764.0s）が、
⚠️ **ADR-009 の Phase C そのものを置き換えるとは書いていない。**

★ さらに `.idea/20260910` と `.idea/20260911`（⚠️ **ADR-024 の Accepted 日より後**）が
なお ADR-009 の 4 択語彙を使っている。→ ⚠️ **どちらが生きているのかが現場で分かれている。**

## §4 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **ADR-009 を Accepted にしない**（★ G1 が `n = 0/3` で反証ゲートが動いていない）
2. ⚠️★★★ **ADR 本文を書き換えない**。関係は**新 ADR 側**に書き、README の重ね書き注記で追跡する
3. ⚠️ **却下した案を消さない** —— `Alternatives` 節に**なぜ採らないか**とともに残す（AC 3）
4. ⚠️ **`metrics.rs` を触らない**（★ 取り込み済みのものを使う。issue 007 の Out）
5. ⚠️ **O1 回収後に凍結すべき項目を今決めない**（期の幅 Δ / split 定義 / 勝ち幅の数値 / G-next・O-holdout）
6. ⚠️ **`git add -A` / `git add <dir>` を使わない** —— 作業ツリーに別ブランチの未コミット作業がある
7. ⚠️ **キーストローク内容・NDJSON 生ログを Codex（外部 LLM）へ送らない**
8. ⚠️ **`.idea/20260910` `20260911` の本文を書き換えない**（`.idea` は追跡外。必要なら末尾に無効化の表を足す）

## §5 ⚠️ 決められないときは止まる（★ Stop Conditions）

- ⚠️ **どちらを主解析にするか決められない** → **推測で埋めない。研究者にエスカレートする**
- ⚠️★★★ **第三の統合案が新しい観測を要求すると判明した場合**
  → ★ **O1 配布前でなければ手遅れ**なので**即座にエスカレートする**
  （⚠️ ただし issue 008 の調査で「`key` 行の `category` から事後再構成できる」ことが分かったので、
  ★ **何が本当に復元不能かは `decisions.md` 判断 7 を読んでから判断する**）
- ⚠️ ADR-009 の本文を書き換えないと整合が取れない → 規約違反なので止まる

## §6 ★ 受け入れ条件（⚠️ 機械 AC は衛生条件にすぎない）

⚠️★★★ **この issue の「正しさ」は機械検証できない。**
`docs/loop-engineering.md` の無人ループ（モード C）に**載せない**。

| # | AC | 検証 |
|---|---|---|
| 1 | ADR-009 と ADR-024 の関係が**理由付きで**本文に明記 | ★ 人が承認 |
| 2 | **時間原点 / 主イベント / 競合イベント / 打ち切り** の 4 つが明記 | ★ 人が承認 |
| 3 | 却下した案が `Alternatives` 節に理由付きで残っている | ★ 人が承認 |
| 4 | 禁止用語違反なし | `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0 |
| 5 | 引用の整合 | `PYTHONUTF8=1 python scripts/check_citations.py` が exit 0 |
| 6 | `docs/adr/README.md` のテーブルに ADR-029 の行があり、ファイルが実在 | grep |
| 7 | ヘッダに `昇格元: .idea/...` がある（ADR-008/009 と同じ形式） | grep |
| 8 | `/cross-review` を通している | `_codex-review-007.md` が存在（⚠️ §2 のパス訂正を参照） |

⚠️ **`check_citations.py` は違反を 1 回で全件出さない。**「違反なし」まで是正 → 再実行を繰り返す。

## §7 ⚠️ 実行時に効く前提（忘れると空振りする）

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。**
  `cd src-tauri` するか `--manifest-path src-tauri/Cargo.toml` を付ける
- ⚠️ Hook はすべて bash 前提。Windows では **git-bash 必須**
- ⚠️ `/cross-review` は無関係な未コミット変更で BLOCKED になるので
  `bash scripts/run-codex-review.sh -- <paths>` で**パス限定**して回す
- ⚠️★★★ **Codex は `--sandbox read-only` だと Windows のエラー 1312 でシェルが起動できず repo を読めない。**
  ★ 資料はプロンプトに貼り、「シェルは使えない」と明記する
- コミット: `[type]([scope]): [説明]` + 本文 + `Refs: .steering/20260911-outcome-arbitration-and-o1-preflight/`
- 応答は**日本語**で

## §8 ★ この issue が終わったら

1. **issue 009（修飾キー同時押下フラグ）の要否がここで決まる。**
   ⚠️ `revision topology` を主要アウトカムに据えないなら**要らない**。
   → ★ 要否を **issue 009 の Execution Result に明記**してから閉じる（⚠️ 記録せず放置しない）
2. ⚠️ issue 009 を実施するなら、**PR #182（issue 008）のマージ後**に着手する
   （★ `hook_macos.rs` / `hook_windows.rs` / `schema_dto.rs` で交差する）
3. ★ 残る T3 / T4 は **issue 未分解**。`_survey-*.md` を読んで `issue-slicing` で分解する
   （⚠️ 分解と実行は**別セッション**）

## §9 ★ 併走している未了事項（⚠️ このセッションでは触らない）

| 何 | どこ | 状態 |
|---|---|---|
| **PR #182**（issue 008・macOS の IME 確定/放棄） | GitHub | ⚠️ **CI 全緑 / MERGEABLE**。★ マージは研究者判断 |
| **PR #183**（`check_schema_parity` の Windows 落ち） | GitHub | ⚠️ レビュー待ち |
| **mac 側の実機検証 3 件** | `.steering/_handoff/next-session-mac-ime-shadow-verification.md` | ⚠️ **mac セッションへ委託済み** |
