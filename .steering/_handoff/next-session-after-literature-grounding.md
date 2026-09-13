# 次セッション開始プロンプト — ⚠️★★★ **起票 11（ESM）の ⓪〜④ が締切を持っている** ／ 文献の残件

> 作成: 2026-09-13 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md`（**起票 11**）/
> `.steering/20260913-mhd-inference-ssot/blockers.md`（**起票 15〜18**）/
> `.steering/20260913-mhd-literature-grounding/`（★ 前セッションの記録）/
> `docs/adr/ADR-030-stall-onset-and-decision-episode.md` / `docs/references.md` /
> `docs/literature/_index.md`（★ **2026-09-13 行のやり残し欄が次ラウンドの入口**）。

## §0 ⚠️★★★ まずこれを実行する

```bash
cd /c/GSE-prototype        # Windows は git-bash 必須
git switch main && git pull
git log --oneline main..docs/adr-030-stall-onset-definition | cat   # ★ 前セッションで 8 コミット増えた
ls docs/adr/ | tail -4      # ⚠️ ADR-029 / ADR-030 が main に在るか
PYTHONUTF8=1 python scripts/check_citations.py | tail -2   # ★ 着手前ベースラインを取る
```

⚠️★★★ **モデルは Opus**（★ 裁定が入る）。⚠️ **応答は日本語で。**

## §1 ★ 前セッションで何が済んだか（★ 8 コミット）

| # | 何 | 状態 |
|---|---|---|
| **順序 0** | **起票 11 の研究者判断** = ★★★ **「(a) 6 択フルを O1 で取る」** | ✅ **判断のみ**（⚠️ **⓪〜④ 未着手**） |
| **順序 1** | 文献接地 1 ラウンド —— **[P357]–[P360] / [V146]–[V150]** を登録 | ✅ |
| **順序 2** | ADR-030 `Context-3b` / `D2` / `Consequences` へ接地（⚠️ **D1〜D11 は 1 文字も変えていない**） | ✅ |
| — | `research-positioning` / `[P273]` / **未踏提出 2 文書**の主張を 1 段下げた | ✅ |
| — | レビュー 4 本（`code-reviewer` / `security-checker` / `/cross-review` 2 巡）を反映 | ✅ |

### ⚠️★★★ 前セッションが **自分で 3 回間違えて 3 回直した**もの（★ 同じ轍を踏まない）

| # | 何を間違えたか | ★ どう直したか |
|---|---|---|
| 1 | ⚠️ **起票 17 の前提**（「GSE も沈黙で窓が薄くなる」） | ★ **コードで実測**して撤回。`features.rs:102-104` は `cutoff = last_ts - 30_000` で、**窓の右端は「今」ではなくバッファ最後のイベント時刻**。→ **沈黙中は凍結する** |
| 2 | ⚠️ **カードの集計**（17/11/5/1 が合わない） | ★ **claim 台帳**を置いて 21/13/7/1 に |
| 3 | ⚠️★★★ **残件数を 3 回書いて 2 回間違えた**（17 → 14 → **15**） | ★ **key 列だけを対象に**数え直した。⚠️ 「19 登録済み」は `L16-1635` が **[P273] の gloss にヒットしただけ** |

> ### ★ 運用の教訓（★ 次も効く）
> 1. ⚠️★★★ **`references.md` を数えるときは *key 列だけ* を対象にする**（★ gloss の言及を数えない）。
> 2. ⚠️★★★ **還元の消費者は `grep` で機械的に洗う。**★ ⚠️ **`docs/mitou_submission/**` まで含める**
>    （★ 前セッションは外部提出 2 文書を取りこぼし、`code-reviewer` に HIGH で拾われた）。
> 3. ⚠️★★★ **SSOT（`references.md`）を最後に確認する。**★ ADR / カード / `_index` の 4 箇所を直して
>    **SSOT だけ取りこぼした**（★ `/cross-review` 1 巡目が拾った。⚠️ grep パターンが括弧違いで外れた）。

## §2 ★★★ 本セッションでやること（★ 優先順）

### ⚠️★★★ 順序 A —— **起票 11 の ⓪〜④**（★ **これだけが締切を持つ**）

★ **`.steering/20260911-.../blockers.md` の起票 11 を読む**（⚠️ 状態は `⏳ 判断済 / 未着手`）。

| 段 | 何 | ⚠️ 置き場 |
|---|---|---|
| **⓪** | **ESM 行の提出猶予と第三者の扱いを裁く** | ★ **新 ADR**（⚠️ ADR-014 D8 制約 1 の上書きに触れる） |
| **①** | `data-privacy` **ルール 7** に「自己申告による行動カテゴリ」を明文化 | Skill ＋ **新 ADR** |
| **②** | **同意文書の改訂** | ★ **破れる逐語は特定済み**: `participant-setup-guide.md:105` / `:185-186` の「**だけ**」節 |
| **③** | **`capabilities` 粒度の決定** | ★ **新 ADR**（⚠️ `schema_dto.rs` を触る前） |
| **④** | `schema_dto.rs` へ additive 追加 ＋ parity ＋ `gse-dataset` 同期 ＋ 再ビルド | ★ ここで初めてコードに触る |

⚠️★★★ **④ から始めてはならない。**⚠️ 締切は「O1 配布前」ではなく **「O1 の収集が本格化する前」**。
★ **打鍵ログは後から再解析できるが、その場の自己申告は後から生成できない**＋**出したら消せない**。

### ★ 順序 B —— ⚠️★★★ **未踏提出 `.docx` の再生成**（★ 前セッションが `.md` だけ直した）

★ **`*.docx.md` が正本で `.docx` は生成物**。→ ⚠️ **`.md` を直しただけでは `.docx` に反映されていない。**

```bash
MD=docs/mitou_submission/mitou_docs
f="$MD/[提案プロジェクト詳細資料]GSE_proposal.docx.md"
PYTHONUTF8=1 python scripts/md2docx.py "$f" "${f%.md}" --unescape --compact   # ⚠️ 詳細資料だけ --compact
f="$MD/[提案プロジェクト補足資料]GSE技術設計書.docx.md"
PYTHONUTF8=1 python scripts/md2docx.py "$f" "${f%.md}" --unescape             # ⚠️ 補足資料は --compact なし
```

⚠️★★★ **詳細資料には 10 ページ規約がある。**★ 前セッションは長さを増やさずに直したが、
**再生成後に Google ドキュメントで測り直すこと**（★ 手順は `docs/mitou_submission/README.md`）。

### ★ 順序 C —— 文献の残件（★ 起票 15 が最優先）

| 優先 | 何 | ⚠️ 注意 |
|---|---|---|
| **1** | ⚠️★★★ **起票 15: [V5] 全文 21 頁 と [P273] APTIF 本文 11 頁を *同じラウンドで* 読む** | ★ **片方だけ読むとまた片側だけの裁定になる**（★ [P273] の「IME を 1 語も書いていない」は**まだ未検証で active**） |
| **2** | ⚠️ **起票 18: 「反復エピソード × 競合リスク」の同時作法** | ★ [V147] にも [V148] にも無い。⚠️ 無ければ **事前登録に「未決」と書く**（隠さない） |
| **3** | ★ **[V150] Therneau (1993) の書誌特定** ＋ **[V148] Fine & Gray の本文 PDF** | ★ どちらも `provisional`。⚠️ **[V148] の定義を逐語引用してはならない** |
| **4** | ★ `.idea/survey §13` の**残り 15 件** | ★ 次点は **Putter (2024)** / **Coman & Sillitti 原典** / **Conijn (2021)** / **Parnin & Rugaber (2009)** |
| **5** | ★ **[P360] の SVN リビジョン固定** ＋ 残り 225 セッションの確認 | ⚠️ 計数はスナップショットに紐づく |

## §3 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **起票 11 を「再決定」しない。**★ 研究者判断 **(a)** は 2026-09-13 に出ている。
2. ⚠️★★★ **ADR 本文の *決定* を書き換えない。** ★ 改訂は番号の大きい新 ADR へ。
3. ⚠️★★★ **`docs/preregistration-v0.3.md` を書き換えない** / **`HMM_VERSION` を bump しない** /
   **`.idea` の本文を書き換えない**（★ 追跡外）/ **`.steering/` の過去記録を書き換えない**（★ 書かれた時点の事実）。
4. ⚠️★★★ **ADR-009 を Accepted にしない**（★ G1 が `n = 0/3`）。
5. ⚠️★★★ **`git add -A` / `git add <dir>` を使わない**（★ 作業ツリーに常に別ブランチの未コミット作業がある）。
6. ⚠️★★★ **Codex へ送る前に `P0\d\d` を目視する。**★ ⚠️ **`docs/mitou_submission/**` は拡張子を問わず送信禁止。**
   ★ 前セッションは `docs/external-skills.md` を除外して送った（★ 規約の例示文に `P012` が出るため）。
7. ⚠️ **一節だけ読んで裁定しない**（★ `verify-before-claiming` ルール 7）。

## §4 ★ ブランチとマージの状態（⚠️ 律速は変わっていない）

| 何 | 状態 |
|---|---|
| **ADR-029** | ⚠️ ブランチ `docs/adr-029-outcome-role-arbitration`・**未 push / 未 PR**。**AC 1〜3 は研究者承認待ち** |
| **ADR-030** | ⚠️ ブランチ `docs/adr-030-stall-onset-definition`（★ ADR-029 から分岐）・**未 push / 未 PR**。**16 コミット** |

→ ⚠️★★★ **マージ順序は ADR-029 → ADR-030 に固定。**★ **ADR-029 の承認が律速。**
★ **研究者判断 2026-09-13 = 承認は保留**（★ 文献接地を先に済ませた）。
→ ★ **セッション冒頭で「ADR-029 / ADR-030 の承認をどうするか」を再度確認する。**

## §5 ★ 全体順序（★ 更新版）

| # | タスク | 計器 | 状態 |
|---|---|---|---|
| 0 | O1 同意へ二次利用の任意項目 | 不要 | ★ `next-session-o1-consent-secondary-use.md` |
| 1 | `stall onset` / `Decision Episode` の操作的定義 | 不要 | ✅ **ADR-030**（⚠️ 承認待ち） |
| **1b** | ⚠️★★★ **起票 11 の ⓪〜④** | ⚠️ **要**（④） | ⚠️★★★ **本セッションの順序 A**（★ **締切あり**） |
| 1c | 文献接地 1 ラウンド | 不要 | ✅ **2026-09-13** |
| **1d** | ★ **未踏 `.docx` 再生成** | 不要 | ⚠️ **本セッションの順序 B** |
| 2 | **計器を変えずに作れる特徴群を `gse-replay` へ** | 不要 | ★ 1b の後。⚠️ `issue-slicing` で分解（**別セッション**）。★ Loop モード C の初回 |
| 2z | ⚠️ **Loop 基盤整備** | 不要 | ⚠️ タスク 2 の前。★ 実体は `next-session-mhd-feature-redesign-ssot.md` **§8c** |
| 3 | leakage 防止・split 規律の SSOT 化 | 不要 | ★ 2 と並行可 |
| 4 | ⚠️ **計器を変える一式**（`T1c` の `undo`/`redo` / `T2` / `T3`） | **要** | ⚠️ **費用の裁定ではなく *禁止の再審***（ADR-030 D11）。★ **ESM は本行から外れた**（1b へ） |
| 5 | T4（Practice Portrait） | — | ⚠️ 後（★ ADR-020 D3 の 6 条件と照合） |

## §6 ⚠️ 実行時に効く前提（★ 忘れると空振りする）

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。**
- ⚠️ Hook はすべて bash 前提。Windows では **git-bash 必須**。
- ⚠️★★★ **`check_doc_lexicon.py` は ADR を検査していない**（★ 対象は `docs/mitou_submission/**` ＋
  `glossary.md` ＋ `physical-anchor/SKILL.md`）。→ ★ **緑を「検査された」と読まない。**
- ⚠️ **`check_citations.py` は 1 回で全件出ない** → ★ 「違反なし」まで繰り返す。
  ⚠️★★★ **かつ「相互リンクの無い同一 key」しか見ない** —— ★ **key が違う drift（[P273] ⇄ [P360]）は検出できない。**
- ⚠️ `/cross-review` は `bash scripts/run-codex-review.sh <range> -- <paths>`。
  ⚠️★★★ **引数なしだとコミット済みの変更はレビューされない。**
  ★ 予算は `.codex/budget.json`（日次 300k・2026-09-13 は 4 回で消費）。
- ⚠️★★★ **Codex は `--sandbox read-only` だと Windows 1312 で repo を読めない。**★ 資料はプロンプトに貼る。
- ⚠️ **`WebFetch` は PDF を読めない**が原本をローカル保存する → ★ **pypdf** で開く。
  ★ **スキャン PDF は `PyMuPDF (fitz)` で PNG 化して視読**（⚠️ tesseract / pdftoppm は本機に無い）。
  ★ **Springer は curl + UA なら 200**（⚠️ WebFetch は `idp.springer.com` へ 303）。
  ★ **MDPI は `mdpi-res.com` の CDN 直リンク**（⚠️ `www.mdpi.com` は Cloudflare 403）。
  ★ **PMC は Europe PMC REST `.../PMC<id>/fullTextXML`**（⚠️ `pmc.ncbi.nlm.nih.gov` は reCAPTCHA）。
  ★ **SourceForge SVN は `svn.code.sf.net` の DAV**（⚠️ `sourceforge.net/p/.../tree/` は 403）。
- コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs: .steering/[YYYYMMDD]-[task-name]/`
