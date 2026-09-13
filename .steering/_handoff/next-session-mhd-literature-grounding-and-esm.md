# 次セッション開始プロンプト — **文献接地の 1 ラウンド（起票 4/5）／⚠️★★★ その前に起票 11（ESM）の研究者判断**

> ✅★★★ **2026-09-13 に消費済み。**⚠️ **このメモを次セッションの入口にしない。**
> → ★ **後継は `next-session-after-literature-grounding.md`。**
> ★ 済んだこと: 順序 0（起票 11 = **(a) 6 択フル**）／順序 1（**[P357]–[P360] / [V146]–[V150]**）／順序 2（ADR-030 への接地）。
> ⚠️ **残ったこと**: 起票 11 の **⓪〜④**（★ 締切あり）／未踏 `.docx` の再生成／起票 15〜18。

> 作成: 2026-09-13 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `docs/adr/ADR-030-stall-onset-and-decision-episode.md` /
> `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md`（★ **551 行。§6.1 だけ読まないこと**）/
> `.idea/20260910-mhd-criterion-practice-trace-and-g-o-validation.md` /
> `.idea/20260911-mhd-growth-personalization-and-gse-overview-roadmap.md`（⚠️ **追跡外・SSOT ではない**）/
> `docs/references.md` / `docs/literature/_index.md` /
> `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md`（★ **起票 11**）/
> `.steering/20260913-mhd-inference-ssot/`（★ **前セッションの記録・判断 12 まで**）。

## §0 ⚠️★★★ まずこれを実行する（★ 省略しない）

```bash
cd /c/GSE-prototype        # Windows は git-bash 必須
git switch main && git pull
git branch -a | grep adr-030
git log --oneline main..docs/adr-030-stall-onset-definition | cat
ls docs/adr/ | tail -4      # ★ ADR-030 が main に在るか（⚠️ 無ければ未マージ → §5）
```

⚠️★★★ **モデルは Opus**（★ 文献の採否判断と裁定が入る。`CLAUDE.md` のモデル選択ルール）。
⚠️ **応答は日本語で。**

## §1 ★ 前セッションで何が起きたか（★ 2 回、同じ失敗をした）

★ 前セッションは `ADR-030`（`stall onset` / `Decision Episode` の操作的定義）を書き、
レビュー 4 本（Codex 2 巡 ＋ `code-reviewer` ＋ `security-checker`）を通した。
⚠️★★★ **しかし研究者の指摘で 2 回、同じ型の欠陥が見つかった。**

| # | ⚠️ 何をやっていたか | ★ 何が正しかったか |
|---|---|---|
| **1** | `.idea` の文献サーヴェイ **551 行のうち §6.1（Tier 表・約 25 行）しか読まず**に特徴量の枠を確定した。roadmap メモ 356 行は**未読**。`citation-ssot` 未起動。★ **ADR の引用はゼロ件だった** | ★ 同じメモの **§3.2 / §4 / §4.1** が反証を持っていた（→ §2） |
| **2** | `Context-3` で **`p_stuck` の循環**だけを塞いで「**本 ADR の核心**」と自称した | ⚠️★★★ `.idea/survey §5.2` 逐語「**行動だけで criterion を作ると循環する**」。★ **D3 は `key` 行だけで onset を決める ＝ まさにそれ**。→ 広い循環は **ESM 監査 criterion（起票 11）**が要る |

> ### ⚠️★★★ **次セッションが繰り返してはいけない型**
> ★ **「一次資料の一部だけを見て、核心を閉じたと称する」。**
> → ★ **`.idea` を引くときは、節を 1 つだけ読んで済ませない。**
> ★ 特に `survey §3.2`（チャネル増分）/ `§4`（証拠地図）/ `§4.1`（強い反証）/ `§5`（方法論）/
> `§13`（主要文献）/ `§17`（個人化・tuning）は **設計判断に直結する**。

★ 是正の記録は `.steering/20260913-mhd-inference-ssot/decisions.md` **判断 10 / 11 / 12**。

## §2 ★ 決まったこと（⚠️ 蒸し返さない）

| 何 | どこ |
|---|---|
| `stall onset` = 条件 A（因果窓 `W` 内の `net < net_diff_min`）が `θ_person` 継続した**検出時点** ＋ **不応期** | **ADR-030 D2 / D3** |
| `θ_person` = **個人 × `task_kind` の分位点**（⚠️ 床も天井も置かない）。★ **凍結するのは決め方だけ** | **ADR-030 D4** |
| `phase` は自然セッションで `unspecified` に collapse | **ADR-030 D5**（`task-adaptation §3.6` を確定） |
| `Decision Episode` は **新設しない**（ADR-008 D2 / ADR-010 D4 / ADR-014 D6） | **ADR-030 D7** |
| 特徴量は **Tier 枠 ＋ 投資順序 ＋ ablation 6 層**だけを accept（⚠️ 特徴リストは accept しない） | **ADR-030 D10** |
| ★ **`T1` の内側で `T1b`（境界）を `T1a`（分布）より先に投資する**（根拠 **[P121]**） | **ADR-030 D10** |
| 計器を変えない範囲に **`T1c` の一部**も入る（⚠️ `undo`/`redo` 往復**だけ**が「要」） | **ADR-030 D11** |
| ⚠️ **「HMM を主推定器にしない」は文献根拠ではない**（★ [P270] は**新規性の否定**。★ stateless を正とするのは **ADR-009 D3 / ADR-019** という設計判断） | **ADR-030 Context-3b** |

## §3 ★★★ 本セッションでやること（★ この順で・⚠️ 飛ばさない）

### ⚠️★★★ 順序 0 —— **起票 11（ESM 監査 criterion）の研究者判断を先に取る**

★ **`.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md` の起票 11 を読む。**

- ⚠️★★★ **これは締切を持つ** —— 起票 11 逐語
  「**打鍵ログは後から再解析できるが、その場の自己申告は後から生成できない**」
  「★ 締切の性質: **O1 配布前ではなく「O1 の収集が本格化する前」**」。
- ★ **ADR-030 §Migration 2 がこれを 2 番に挿した** —— ⚠️ 次タスク（O1 向け特徴実装）は
  **起票 11 の期限を消費する向きに働く**。
- ⚠️ **研究者が決めるのは 2 択**: **(a) O1 で取る** / **(b) 取らない**。
  ★ (b) なら「**`left_observation` の混合は O1 では検証しない**」を**明示的に記録して配布する**。
- ⚠️★★★ **取るなら `security-checker` の 4 点を先に読む**（起票 11 の 2026-09-13 追記）——
  特に **`data-privacy` ルール 7 の穴**（★ 6 択の「外部資料」「会話」は役割カテゴリと意味的に等価だが、
  条文は *計器由来* だけを禁じており **自己申告経由は明文の射程外**）。

> ★ **これは裁定ではなく研究者の意思決定である。⚠️ エージェントが決めない。**

### ★ 順序 1 —— `/literature-review` を 1 ラウンド（★ 起票 4 / 起票 5）

★ **`.steering/20260913-mhd-inference-ssot/blockers.md` の起票 4 / 起票 5 を読む。**

⚠️★★★ `.idea/survey §13` の主要文献 **33 件中 21 件が未登録**。★ **最優先は「強い反証」3 本**:

| 優先 | 文献 | ⚠️ 何を示すか | ★ どこに効くか |
|---|---|---|---|
| **1** | **Tabarsi et al. (2022)**（isnap PDF） | ⚠️★★★ **5 分超 idle が負の感情と関連する一方、成績とは正相関 `r=.507`** ＝ **長い沈黙の意味は一方向でない** | ★★★ **ADR-030 D2 / D3 の onset 定義に直撃** |
| **2** | **Conijn et al. (2022)** `10.1007/s40593-021-00268-w` | 豊富な writing process 特徴でも **回帰は平均予測を超えず、分類は最大 AUC=.57** | ★ D10 の投資順序・`Q`（abstention）の必要性 |
| **3** | **Zou & Godfrey (2012)** | **ラボ約 80% → 実地で 70% 以上の誤差**（task boundary 推定） | ★ Context-3b (vi) の外的妥当性 |

★ 次点（★ 起票 4 の 4 番・**原典が無い**）:
**Fine & Gray (1999)** `10.1080/01621459.1999.10474144`（★ 近縁の [V61] [V62] は登録済み）/
**Nahum-Shani et al. (2018) JITAI 定義論文** PMC5364076 /
**Willett & Singer (1995) multiple-spell** `10.3102/10769986020001041`（★ **ADR-030 D2 の反復エピソード規則の出典**）。

★ 起票 5（**ENJA15 の IME 記録**）—— **Zou & Carl (2026)** `10.3390/data11070176` ＋ ENJA15 / RUC17 生データ。
⚠️ `.idea §3.1` と `docs/references.md:307` [P273] が食い違っており、**どちらが一次確認済みか未確定**。

**規約**（⚠️ 守る）:
- `citation-ssot` Skill を**起動してから**書く。★ append-only / renumber 禁止 / 番号再利用禁止。
- ★ 次番号は **[P357]** / **[V146]**（2026-09-13 時点。⚠️ **着手時に再確認する**）。
- ⚠️ **書誌未確定は `provisional`。捏造した URL を書かない。**
- ⚠️★★★ **サーヴェイは毎ラウンド即コミット**（★ 複数ラウンドが同居すると `git add -p` で分離できない）。
- ★ 探索は**サブエージェント並列**。`references.md` への append だけメインが直列。

### ★ 順序 2 —— ADR-030 へ inline `[Pn]` を足す

★ 登録できたものを **`Context-3b`** に足す。
⚠️★★★ **ADR 本文の *追記* は規約違反ではない** —— ★ 禁じられているのは **決定の書き換え**である。
⚠️ **決定（D1〜D11）の中身は変えない。** ★ 変える必要が出たら **ADR-031 を立てる**。

## §4 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **`.idea` の節を 1 つだけ読んで設計判断をしない**（★ 前セッションの失敗 1）。
2. ⚠️★★★ **「循環を閉じた」「核心を押さえた」と書かない**（★ 前セッションの失敗 2・ADR-030 禁止リスト #9a）。
3. ⚠️★★★ **「HMM は推定器として劣ると文献が示す」と書かない**（★ ADR-030 禁止リスト #9d）。
4. ⚠️★★★ **ADR-009 を Accepted にしない**（★ G1 が `n = 0/3`）。
5. ⚠️★★★ **ADR 本文の *決定* を書き換えない。** ★ 改訂は番号の大きい新 ADR へ。
6. ⚠️★★★ **`docs/preregistration-v0.3.md` を書き換えない。**
7. ⚠️ **`HMM_VERSION` を bump しない** / **`.idea` の本文を書き換えない**（★ 追跡外）。
8. ⚠️★★★ **`git add -A` / `git add <dir>` を使わない**（★ 作業ツリーに常に別ブランチの未コミット作業がある）。
9. ⚠️★★★ **Codex へ送る前に `P0\d\d` 形式の ID と個人別の値が同居していないか目視する**
   （`docs/external-skills.md:92`）。
10. ⚠️ **参加者 ID を伴う個人別の値を ADR / 恒久文書に書かない**（★ ADR-029 D2 / ADR-030 D4 の規律）。

## §5 ★ ブランチとマージの状態（⚠️ 律速がある）

| 何 | 状態 |
|---|---|
| **ADR-029** | ⚠️★★★ ブランチ `docs/adr-029-outcome-role-arbitration`・**未 push / 未 PR**。**AC 1〜3 は研究者承認待ち** |
| **ADR-030** | ⚠️★★★ ブランチ `docs/adr-030-stall-onset-definition`（★ **ADR-029 から分岐**）・**未 push / 未 PR**。**8 コミット** |

→ ⚠️★★★ **マージ順序は ADR-029 → ADR-030 に固定されている。**
★ **ADR-029 の承認が律速**であり、それが済むまで ADR-030 も `main` に入らない。
→ ★ **セッション冒頭で研究者に「ADR-029 / ADR-030 の承認をどうするか」を確認する。**

★ ADR-030 の**人が承認する AC**（⚠️ 未了）: AC1 操作的定義 / AC2 Decision Episode が新設でない /
AC3 Tier 枠・投資順序・ablation 規律 / AC4 計器の仕切り / AC5 Alternatives。

## §6 ★ このトラックの全体順序（★ 更新版）

| # | タスク | 計器 | 状態 |
|---|---|---|---|
| **0** | **O1 同意へ二次利用の任意項目** | 不要 | ★ `next-session-o1-consent-secondary-use.md`（⚠️ **O1 配布前**） |
| **1** | `stall onset` / `Decision Episode` の操作的定義 | 不要 | ✅ **ADR-030**（⚠️ 承認待ち） |
| **1b** | ⚠️★★★ **起票 11（ESM 監査 criterion）の研究者判断** | ⚠️ 取るなら**要** | ⚠️★★★ **本セッションの順序 0**（★ 締切あり） |
| **1c** | ★ **文献接地 1 ラウンド**（起票 4 / 5） | 不要 | ⚠️ **本セッションの順序 1** |
| **2** | **計器を変えずに作れる特徴群を `gse-replay` へ** —— `T0` / `T1a` / `T1b` / `T1d` / `Q` ＋ **`T1c` の一部** | 不要 | ★ 1b の後。⚠️ `issue-slicing` で分解（**別セッション**）。★ **Loop モード C の初回** |
| **2z** | ⚠️★★★ **Loop 基盤整備**（worktree へ `deny` 7 件を入れる経路） | 不要 | ⚠️ **タスク 2 の前**。★ 実体は `next-session-mhd-feature-redesign-ssot.md` **§8c**（★ 再導出しない） |
| **3** | leakage 防止・split 規律の SSOT 化 | 不要 | ★ 2 と並行可 |
| **4** | ⚠️ **計器を変える一式**（`T1c` の `undo`/`redo` / `T2` / `T3` ＋ **起票 11**）を 1 本に束ねて裁く | **要** | ⚠️★★★ **費用の裁定ではなく *禁止の再審* である**（ADR-030 D11） |
| **5** | T4（Practice Portrait） | — | ⚠️ **後**（★ ADR-020 D3 の 6 条件と照合） |

## §7 ⚠️ ADR-030 が **意図的に射程外にした**もの（★ 次に拾う候補）

★ `.idea/survey §5` の方法論のうち、**ADR-030 に入っていない**もの（★ 機械で確認済み・出現 0 件）:

| 節 | 何 | ★ どこで拾うか |
|---|---|---|
| **§5.3** | **推奨モデル順**（prevalence → multinomial logistic/GAM → **cause-specific discrete-time hazard** → 階層 hazard → **HMM/HSMM は 5 番目**） | ★ **ADR-019（モデル成熟度）**の側。⚠️ ADR-030 は episode 定義なので射程外 |
| **§5.5** | **評価指標**（time-dependent AUROC/AUPRC/PPV・**IPCW Brier**・calibration・**abstention coverage**・**worst-group performance**） | ★ タスク 3（split 規律の SSOT 化）と一緒に |
| roadmap §11 | **recovery の安定時間と Horizon 候補** | ★ **ADR-029 D2 の `H`** の話（⚠️ 意思決定層の読み出しパラメータ） |
| §17.5 | **shadow adaptation**（O1 中の適応は本番判断へ流さず shadow で記録） | ★ タスク 4 以降 |

## §8 ⚠️ 実行時に効く前提（★ 忘れると空振りする）

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。** `cd src-tauri` するか `--manifest-path`。
- ⚠️ Hook はすべて bash 前提。Windows では **git-bash 必須**。
- ⚠️★★★ **`check_doc_lexicon.py` は ADR を検査していない**（★ 対象は `docs/mitou_submission/**` ＋
  `glossary.md` ＋ `physical-anchor/SKILL.md` だけ）。→ ★ **緑を「検査された」と読まない。手 grep を併用する。**
- ⚠️ **`check_citations.py` は 1 回で全件出ない** → ★ 「違反なし」まで是正→再実行を繰り返す。
- ⚠️ `/cross-review` は無関係な未コミット変更で BLOCKED → `bash scripts/run-codex-review.sh <range> -- <paths>`。
  ⚠️★★★ **引数なしだとコミット済みの変更はレビューされない**。
- ⚠️★★★ **Codex は `--sandbox read-only` だと Windows のエラー 1312 で repo を読めない。**
  ★ 資料はプロンプトに貼り「シェルは使えない」と明記する。
- ⚠️ **`WebFetch` は PDF を読めない**が原本をローカル保存する。★ そのパスを **pypdf** で開けば一次全文が取れる。
- コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs: .steering/[YYYYMMDD]-[task-name]/`
- ★ 実装後は `code-reviewer` ＋ `security-checker` を**並列**、完了時に **`/cross-review`（2 巡）**。
