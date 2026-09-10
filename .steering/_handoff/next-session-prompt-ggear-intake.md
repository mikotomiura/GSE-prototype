# 次セッション開始プロンプト — **G-GEAR 取り込み ＋ 残雑務**

> ★ 「===」以下をコピペして開始する。⚠️ 前セッションから `/clear` すること。
> ★ 実行マシン: **mac**（★ `analysis/` は OS 非依存だが、⚠️ 両 OS の検証は CI がやる）。
> ★ モデル: ⚠️ **取り込みの切り方は Opus**（★ 誤ると全部やり直しになる）。実装は Sonnet。

---

===

## §0 ⚠️★★★ このメモを一次資料にしない

★ 2026-09-10〜11 のセッションで **自分の測定器・検査を 6 回壊した**。
→ ⚠️ **このメモも同じ確率で間違っている。** ★ 数字は自分で引き直すこと。

```bash
cd /Users/johnd/GSE-prototype
git fetch --all --prune && git checkout main && git pull --ff-only
git log --oneline -1 && git tag --sort=-v:refname | head -1
bash scripts/check-o1-release-readiness.sh | tail -3
bash scripts/check-measurement-binary.sh | tail -2
gh pr list --state open
```

## §1 ✅ 前セッションで**決着したもの**（⚠️ 蒸し返さない）

| 項目 | ★ 結論 |
|---|---|
| ⚠️★★★ **macOS の SIGSEGV** | ★ **原因特定・修正・merge 済み**（PR #175）。★ `core-graphics` 0.24 に `Drop` が無く、`remove_source` も呼んでいなかった → **UAF**。★ v0.1.33 は 37 分/10 分で落ちたが、⚠️ **v0.1.34 は 9h51m 落ちなかった** |
| ★ 稼働コスト | ★ 両 OS 同一基準 `one_core_100` で **Win 2.06 % / mac 2.19 %**（★ どちらも作業中の 8h）。⚠️ 深夜の 60 分は **1.62 %** ＝ **活動量に依る** |
| ★ スリープ跨ぎ | ★ **成立**（3 度目）。⚠️ 1・2 回目は `SleepDisabled = 1` で寝ていなかった。★ 6 項目すべて健全 |
| ★ リリース | ★ **v0.1.34 を CI が公開済み**（Win exe ＋ mac dmg）。★ dmg を実物マウントして版・署名・修正の痕跡まで検算済み |
| ★ 配布可否ゲート | ★ **20 件 / 0 件 = 配布してよい状態** |
| ⚠️ 起動時の山 | ⚠️ **再現しなかった**（v0.1.31 は +0.77 pt / v0.1.34 は 2 本とも **負**）。★ ただし「山は無い」とは断定していない |

## §2 ★★★ 本題: G-GEAR ブランチの取り込み（★ 案 C）

★ 対象: `origin/feat/resumption-outcome-arbitration`
★ 規模（★ 実測）: **246 ファイル / +26,681 行 / −4,870 行**

| 系統 | ファイル数 | ⚠️ 取り込み前に見るもの |
|---|---|---|
| ★ steering | **125** | ★ 記録なので衝突しにくい。⚠️ **まずここだけ出すのが安全** |
| ★ experiments | **52** | ★ `reproducibility-discipline` Skill。⚠️ seed / lockfile / HMM_VERSION の刻印 |
| ★ その他 docs | **28** | ⚠️ `citation-ssot` の**採番衝突**を先に見る |
| ★ scripts | **12** | ⚠️ `md2pptx.py` +1313 行 / `svg2png.py` / `secrets-filter.sh` の穴 4 件 → ★ `secrets-filter-test.sh` を**走らせる** |
| ★ **ADR** | **7** | ★ **番号衝突なし**（main は 001–022 / ブランチ新規は **023–028**）。⚠️ 既存本文は書き換えない規約 |
| ⚠️★★★ **Rust** | **6** | ★ 本丸。下記 §2-1 |
| ★ architecture docs | 2 | ⚠️ ADR-021 / ADR-022 まで読む（★ ADR-017 単独では古い契約を掴む） |

### §2-1 ⚠️ Rust の取り込み（★ `analysis/metrics.rs` +909 行）

★ 中身は **`recovery` → `pflow_exit` の改名**。★ 前セッションの**下調べ（⚠️ 見立て・実測していない）**:

- ★ `src-tauri/src/analysis/engine.rs` の差分 **無し**
- ★ `src-tauri/src/schema_dto.rs` の差分 **無し**
- ★ 改名は `--metrics` 経路であって ⚠️ **`--snapshot`（`FeatSnapshot` byte-equal）ではない**

→ ⚠️ **見立て**: `HMM_VERSION` bump 不要・ゴールデン不割れ。
⚠️★★★ **必ず `gse-replay --snapshot` を実際に走らせて確かめること**（★ 6 本ある）。

★ 改名の**下流の消費者**（⚠️ 一緒に直す）:
`scripts/build_analysis_db.py` / `scripts/fixtures/analysis_join/metrics/**.metrics.json` **4 本**
（★ ブランチ側で更新済み）／⚠️ **docs 14 本**が旧名を書いている
（★ うち `ADR-018,019,020` は**本文を書き換えない規約**なので**そのまま残す**）。

### §2-2 ★ 切り方の提案（⚠️ 1 PR に全部入れない）

★ 依存の弱い順に **5 本**へ割るのが素直:
1. ★ steering（125）＋ その他 docs（28）— ⚠️ `citation-ssot` の採番を先に見る
2. ★ ADR 023–028（7）— ★ 番号衝突なし
3. ★ experiments（52）
4. ⚠️★★★ **Rust（6）＋ 下流の消費者** — ★ `gse-replay --snapshot` を走らせる
5. ★ scripts（12）— ⚠️ `secrets-filter-test.sh` を走らせる

⚠️ `scripts/build_analysis_db.py` を入れるなら ★ **schema parity**
（`emit_schema` ↔ `schema/current.json`）を通すこと。

## §3 ★ 残雑務

- [ ] ⚠️ **PR #176**（★ 起動時コストの記録）が open なら CI 確認 → merge
- [ ] ★ **ブランチ掃除**: `feat/measurement-binary-gate`（merged）/ `chore/startup-cost-v0134`（merge 後）
      ★ `docs/handoff-post-pr132` は **削除可**と調査済み。
      ★ `feature/phase1-reminder-and-dashboard` は ⚠️ **救出不要**と確認済み（★ 記録は main に差分ゼロで存在）
      → ★ どちらも**削除は研究者判断**
- [ ] ⚠️ `feat/phase1-cindex-attainability`（遅れ 191）/ `docs/g1-verdict-and-friction-survey`（遅れ 261）
      → ★ cherry-pick か作り直し。⚠️ 文献カードは `citation-ssot` の採番衝突を先に見る
- [ ] ⚠️★★ **Windows の blockers #3**（★ 測定窓直後のフック飢餓クラスタ・**原因未特定**）
      → ★ `.steering/20260904-windows-orphan-verify/blockers.md`
- [ ] ⚠️ **被験者への配り直し**: ★ Release v0.1.34 を配る。⚠️ **初回セットアップのやり直し**が要る
      （★ 新しい .app なので quarantine が付く）。⚠️ `~/Desktop/O1_配布_v0.1.34/` の zip は
      **使わない**（★ CI 製に置き換わった。印を付けてある）

## §4 ⚠️ **やっていないこと**（★ 「問題なし」と書かないため）

- ⚠️★★★ **SIGSEGV を意図的に再現していない。** ★ 「9h51m 落ちなかった」は**観察**であって
  機序が塞がれた**証明ではない**。→ ★ 決定的にするには **tap 失効を繰り返す陽性対照**が要る。
- ⚠️ **v0.1.30（旧配布版）で同じ頻度で落ちるか未確認。**
- ⚠️ **長時間 / 複数回 / 深いスリープ**は未検証（★ 成立したのは 5 分 12 秒の 1 回）。
- ⚠️ **落ちても被験者が気づかない**問題は**未解決**
  （★ 案は `.steering/20260910-measurement-binary-rebuild/distribution-gap.md` に 4 つ）。
- ⚠️ NDJSON が 8h で **23.19 MB/日**と上振れした原因は**特定していない**（★ 活動量説は未実測）。

## §5 ⚠️ 触らないもの / 気をつけること

- ⚠️ 事前登録の凍結節 / `Form_G1/` / `Form_O1/` / `docs/adr/` の既存本文
- ⚠️★★★ **main に直接コミットしない**（★ 前セッションで**踏んだ**。ブランチへ退避して PR にした）
- ⚠️ **走っている bash script を編集しない**（★ bash は逐次読みするので壊れうる。★ 踏んだ）
- ⚠️ **`$VAR` の直後に多バイト文字を置かない**（★ bash 3.2 が食う。★ CI に捕まった）
- ⚠️ **注意書きに「悪い例」を逐語で書かない**（★ 検査が自分のコメントを捕まえる。★ 踏んだ）
- ⚠️ **crate のソースを引く前に `Cargo.lock` で版を確かめる**（★ 0.25 を読んで誤った）
- ⚠️ **`SleepDisabled` は現在 1**（★ 元の状態）。⚠️ スリープ検証をするなら 0 にしてから、
  ★ 終わったら 1 に戻す（★ さもないと 8h 計測が寝落ちする）
