# 次セッション開始プロンプト — **Mh-D と特徴量再設計の SSOT 化（T3）／第 1 歩 = `stall onset` の操作的定義**

> ⚠️★★★ **2026-09-14 追記 —— §8b の「縦切りの目安 5 本」は是正された。**
> ★ 当時は `ADR-030 D11` の **初版が `T1c` を丸ごと「計器変更 要」に送っていた**ため表から落ちていたが、
> ⚠️ その後 `code-reviewer` の指摘で **`T1c` のうち 5 項目（delete run / rewrite / 再削除 / loop depth / 局所 recurrence）は
> 計器変更 *不要*** に直っている。★ かつ 2026-09-14 に **`capability matrix`**（ADR-032 M7）が加わった。
> → ★★★ **目安は 7 本である。現行の指示は `next-session-loop-foundation-and-task2-slicing.md` §3 を見ること。**
> ★ **§8c（deny リストの実体）はそのまま有効**（⚠️ 再導出しない）。

> 作成: 2026-09-13 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.idea/20260910-mhd-criterion-practice-trace-and-g-o-validation.md` /
> `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md` /
> `.idea/20260911-mhd-growth-personalization-and-gse-overview-roadmap.md`（⚠️ **追跡外・SSOT ではない**）と
> `docs/adr/ADR-009` / `ADR-014` / `ADR-016` / `ADR-020` / `ADR-029` / `docs/architecture/personalization-and-online-learning.md`。

## §0 ⚠️★★★ まずこれを実行する（★ 省略しない）

```bash
cd /c/GSE-prototype        # Windows は git-bash 必須
git switch main && git pull
git status && git branch --show-current
ls docs/adr/ | tail -4      # ★ ADR-029 まで在ることを確認する（⚠️ 無ければ未マージ → §9）
```

⚠️★★★ **モデルは Opus。** ★ 本タスクは**裁定**であり、`issue-slicing` ではない
（★ 切り方を誤ると T0/T1 の実装が全部無駄になる。`CLAUDE.md` のモデル選択ルール）。
⚠️★★★ **`/reimagine` を設計段階で起動する。** ★ ADR-029 で実際に効いた
（⚠️ 初回案は `ADR-014 D1` と衝突しており、再生成で初めて見えた）。

## §1 ★ 何が決まっていて、何が決まっていないか（★ 2026-09-13 時点）

### ✅ 決まったこと（⚠️ 蒸し返さない）

| 何 | どこ |
|---|---|
| **転帰の役割割当** —— 予測トラック（criterion・**O1 の主解析**）= **ADR-009 D2** ／ 報告トラック（主要アウトカム）= **ADR-024 D1** | **ADR-029 D1** |
| **一方向の禁止** —— 予測トラックの量を報告トラックの主要アウトカムに流用しない | ADR-029 D1 |
| **観測不能な期の受け方** —— **ADR-016 D4** の除外規則に対して 2 点だけ動かした（`recording_pause` を挟む側へ／`secure_input` を除外規則から外す） | ADR-029 **D3** |
| `.idea` の第三語彙（`departure` / `externalization`）は **名前を採らず構造だけ採る** | ADR-029 **D5** |
| **ADR-009 は Proposed のまま**（★ G1 が `n = 0/3`）／`metrics.rs` 不変／prereg 不変 | ADR-029 **D6** |
| **`Decision Episode` を標本単位にする** | **ADR-010 D4** 逐語「推定は streaming 窓、読み出しは **Decision Episode**、セッション単位は研究解析のみ」 |
| O1 の答える問い = `left_observation` の内訳／判定量 = **G2 の上下界の幅**／主張の格 = **形成的のみ** | **ADR-014 D1 / D2 / D4c** |

### ⚠️ 決まっていないこと（★ 本トラックの対象）

★ **研究者の方針（2026-09-13・逐語要旨）**:
「**Mh-D のコンセプトとしては accept、特徴量再設計なども大まかに accept**」

⚠️★★★ **ただし「accept」の粒度に注意がある。** ★ メモ自身が `criterion:98` 逐語で
「**特徴を増やせば精度が上がるとは仮定しない。**」と書いている。
→ ★ **accept すべきは *手続き* であって特徴リストではない**（→ §3）。

## §2 ★★★ 第 1 歩 = **`stall onset` と `Decision Episode` の操作的定義**（★ 本セッションの射程）

### ⚠️ なぜこれが最初か —— **依存の根である**

- ★ `.idea/20260910-criterion:329` が §9「ADR 化前に閉じる必要がある問い」の **筆頭**に置いている。
- ⚠️★★★ **ADR-029 D2 は `stall onset` を時間原点として確定したが、その実装定義を持っていない。**
  ★ 引いたのは `personalization-and-online-learning.md:336-337` 逐語:
  > **stall onset** = 個人×task_kind×phase 基準を下回る産出が、個人基準の pause 閾値を超えて継続し始めた時点。
  ⚠️ **これは概念定義であって、コードに落ちる形ではない**（★ 「個人基準」「phase」が未定義）。
- → ⚠️ **これが無いと T1d（restart shape）も episode の標本単位も定義できない。**

### ★ 閉じるべき穴（★ 一次で確認した）

| # | 穴 | ⚠️ なぜ難しいか |
|---|---|---|
| 1 | 「個人基準の pause 閾値」の算出規則 | ⚠️ `personalization:336-337` 逐語「**絶対秒数で固定しない**（★ F5 実測中央値が **個人間で 66 倍**ばらつくため）」→ ★ **個人内分布から決める規則が要る** |
| 2 | `phase` の定義 | ⚠️ **`docs/` に実装定義が見つからない**（★ 着手時に grep で再確認すること） |
| 3 | `task_kind` への依存 | ⚠️★★★ **`App.tsx` の argumentative lock が残っており実運用で分散ゼロ**（**ADR-014 D4d**）→ ★ **task_kind に依存する定義は O1 では動かない** |
| 4 | `Decision Episode` との関係 | ★ ADR-008 D2 / ADR-010 D4 / ADR-014 D6 に既に在る。⚠️ **新設しない。既存の受け皿に載せる** |
| 5 | 期の幅 **Δ** との相互作用 | ⚠️ **Δ は ADR-009 §Accepted 条件 B で P1 のデータ待ち** → ★ **Δ を決めずに onset を決められるか**を先に判断する |

### ★ ゴール

**`stall onset` と `Decision Episode` の操作的定義を、新しい観測ゼロ・`HMM_VERSION` 不変で確定する
新規 ADR（ADR-030 相当）を書く。**

⚠️★★★ **決められないなら「決められない理由」を書いて止める**（→ §5）。

## §3 ★ 「特徴量再設計を大まかに accept」の実装形（★ 本セッションで方針だけ確定する）

⚠️ **特徴リストを accept の対象にしない。** ★ accept するのは次の 3 つ:

1. **Tier の枠** —— T0 / T1a（分布・個人相対）/ T1b（境界）/ T1c（revision topology）/ T1d（restart）/
   T2（cross-channel）/ T3（domain-local）/ **Q（evidence quality）**
   （★ 一次は `survey:184-194` ／ `criterion:86-98`）
2. **投資順序 T0 → T1 → T2 → T3** と、★ **上位 Tier は必ず下位への held-out block ablation で評価する**規律
3. **leakage 防止 6 項**（`criterion:62-70`。★ うち「`Decision Episode` を標本単位に」は **ADR-010 D4 で既決**）

### ★★★ 決定的な仕切り線 —— **計器を変えるかどうか**

| 範囲 | 計器変更 | 配布 | ★ 導出可能性（2026-09-13 に実測） |
|---|---|---|---|
| **T0 / T1a / T1b / T1d / Q** | ✅ **不要** | ✅ 不要 | ★ 現行 NDJSON から導出可能（`KeyCategory` 14 種に `sentence_punctuation` 分離済み・`ime_shadow` 在り・`capabilities` / `hook_health` 在り） |
| ⚠️ **T1c** | **要** | **要** | ⚠️★★★ **`undo/redo` は不可** —— **ADR-014 判断 6** で生 VK を `KeyCategory` へ量子化済みなので `Ctrl+Z` と `Ctrl+A` を区別できない |
| ⚠️ **T2** | **要（部分）** | **要** | ⚠️ `focus_transition{t}` は **方向が無い**（`schema_dto.rs:203-211` 逐語「★ フィールドは `t` **だけ**」）→ 「return」が作れない |
| ⚠️ **T3** | **要** | **要** | ❌ メモ自身が「**O1 の現行観測空間外**」と自認（`criterion:95`） |

### ★★★ 重要な設計上の抜け道（★ 本セッションで確定する価値がある）

⚠️ 新特徴を `features.rs` に入れると **`HMM_VERSION` bump ＋ ゴールデン再生成**が要る
（★ `engine.rs:30-58` が `features.rs` の `phi` / `make_silence_observation` / `calculate_features` を列挙）。
★ **しかし `gse-replay` 側（オフライン）に置けばどちらも不要**である。

★ **先例がある** —— `metrics.rs:1-5` 逐語:
> **派生値はログ記録時ではなく本モジュールで計算する設計**のため、閾値変更時に過去セッションを再処理するだけで再計算できる。

→ ★ **予測トラックは G1 待ちで凍結中**なので、**オフライン側に置くのが筋**である。
⚠️ **ADR-014 D4b**（逐語「**記録のみ。推論には 1 バイトも流さない**」）とも整合する。

## §4 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **ADR-009 を Accepted にしない**（★ G1 が `n = 0/3`・ADR-029 D6 と同じ）。
2. ⚠️★★★ **ADR 本文を書き換えない。** ★ 改訂は**番号の大きい新 ADR 側**に書き、`docs/adr/README.md` の
   重ね書き注記で追跡する（★ ADR-021 → 022 → 026 → 027、および **ADR-029 → ADR-016 D4** の先例）。
3. ⚠️★★★ **新しい判定量を作らない**（**ADR-014 D4c** 逐語「**新しい量を作らない**」）。
4. ⚠️★★★ **`left_observation` の 4 択に第 5 のカテゴリを足さない**（**ADR-016 D1**）。
5. ⚠️★★★ **特徴量を「実装する対象」として accept しない**（→ §3。★ メモ自身の警告に反する）。
6. ⚠️ **`M1`〜`M4` の段呼称を使わない** —— **ADR-021 D11 が撤回済み**（★ 26 週 WBS の `M0`〜`M5` と衝突）。
   ★ **実体名で呼ぶ**（固定 baseline / criterion 直結 / 個人・タスク適応 / 時系列）。
7. ⚠️ **`docs/preregistration-v0.3.md` を書き換えない**（★ 転帰・特徴量は凍結条項の外・ADR-029 D6 で実測確認済み）。
8. ⚠️ **`HMM_VERSION` を bump しない**（★ オフライン側に置けば不要。→ §3）。
9. ⚠️ **`.idea` の本文を書き換えない**（★ 追跡外）。
10. ⚠️ **`git add -A` / `git add <dir>` を使わない。**
11. ⚠️★★★ **Codex へ送る前に `P0\d\d` 形式の ID と個人別の値が同居していないか目視する**
    （`docs/external-skills.md:92`。★ **2026-09-13 に私がこれを踏み外した** → `blockers.md` 起票 14）。

## §5 ⚠️ 決められないときは止まる（★ Stop Conditions）

- ⚠️★★★ **`stall onset` が期の幅 Δ を先に決めないと定義できないと判明した場合**
  → ★ **止まる。**（⚠️ Δ は **ADR-009 §Accepted 条件 B で P1 のデータ待ち**なので、
  ここで決めると**データを見る前に凍結すべきものを推測で埋めた**ことになる）
  → ★ その場合は「**Δ に依存しない部分だけを確定し、依存する部分を明示的に未決として残す**」形を検討する。
- ⚠️★★★ **`task_kind` への依存が外せないと判明した場合**
  → ★ **止まる。**（⚠️ **ADR-014 D4d** により `App.tsx` の argumentative lock が残る限り O1 では分散ゼロ）
- ⚠️ **新しい観測を要求すると判明した場合** → ★ **§3 の「計器を変える範囲」へ送り、本 ADR では決めない。**
- ⚠️ **ADR-009 / ADR-014 / ADR-016 の本文を書き換えないと整合が取れない場合** → 規約違反なので止まる。

## §6 ★ 受け入れ条件（⚠️ 機械 AC は衛生条件にすぎない）

⚠️★★★ **この裁定の「正しさ」は機械検証できない。**
★ `docs/loop-engineering.md` の無人ループ（モード C）に**載せない**。

| # | AC | 検証 |
|---|---|---|
| 1 | `stall onset` の操作的定義が**コードに落ちる形**で書かれている | ★ 人が承認（⚠️ 「個人基準」「phase」が未定義のまま残っていないか） |
| 2 | `Decision Episode` との関係が明記され、**新設していない**こと | ★ 人が承認（ADR-008 D2 / ADR-010 D4 / ADR-014 D6 を引くこと） |
| 3 | 特徴量の **Tier 枠 ＋ 投資順序 ＋ ablation 規律**が確定している | ★ 人が承認 |
| 4 | ⚠️★★★ **「計器を変えない範囲」と「変える範囲」の仕切りが明記**されている | ★ 人が承認 |
| 5 | 却下案が `Alternatives` に理由付きで残っている | ★ 人が承認 |
| 6 | 禁止用語違反なし | `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0 |
| 7 | 引用の整合 | `PYTHONUTF8=1 python scripts/check_citations.py` が exit 0（⚠️ **1 回で全件出ない**ので「違反なし」まで反復） |
| 8 | `docs/adr/README.md` に行があり、ファイルが実在する | grep |
| 9 | ヘッダに `昇格元: .idea/...` がある | grep（★ ADR-008 / 009 / 014 / 029 と同じ形式） |
| 10 | `/cross-review` ＋ `code-reviewer` ＋ `security-checker` を通している | ★ **3 つとも回す。**⚠️ ADR-029 では **Codex が HIGH 1 件・`code-reviewer` が HIGH 2 件**を出し、**裁定の枠組みごと差し替わった** |

## §7 ⚠️ 実行時に効く前提（★ 忘れると空振りする）

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。** `cd src-tauri` するか `--manifest-path` を付ける。
- ⚠️ Hook はすべて bash 前提。Windows では **git-bash 必須**。
- ⚠️ `/cross-review` は無関係な未コミット変更で BLOCKED になるので
  `bash scripts/run-codex-review.sh <range> -- <paths>` で**パス限定**して回す。
  ⚠️★★★ **引数なしだとコミット済みの変更はレビューされない**（★ `git diff` は未ステージのみ）。
- ⚠️★★★ **Codex は `--sandbox read-only` だと Windows のエラー 1312 でシェルが起動できず repo を読めない。**
  ★ 資料はプロンプトに貼り「シェルは使えない」と明記する。
- ⚠️ **`check_doc_lexicon.py` は ADR を検査していない**（★ 対象は `docs/mitou_submission/**` ＋
  `glossary.md` ＋ `physical-anchor/SKILL.md` だけ・2026-09-13 に実測）。→ ★ **緑を「検査された」と読まない。**
- コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs: .steering/[YYYYMMDD]-mhd-inference-ssot/`
- 応答は**日本語**で。

## §8 ★ このトラックの全体順序（★ 本セッションは 1 だけ）

| # | タスク | 計器 | 状態 |
|---|---|---|---|
| **0** | **O1 同意へ二次利用の任意項目** | 不要 | ★ `next-session-o1-consent-secondary-use.md`（⚠️ **唯一締切を持つ** = O1 配布前） |
| **1** | ★★★ **`stall onset` / `Decision Episode` の操作的定義** | 不要 | ⚠️ **本セッション** |
| **2** | **T0 / T1a / T1b / T1d / Q を `gse-replay` に実装** | 不要 | ★ 1 の後。⚠️ `issue-slicing` で分解（**別セッション**） |
| **3** | **leakage 防止・split 規律の SSOT 化** | 不要 | ★ 2 と並行可 |
| **4** | ⚠️ **計器を変える一式**（T1c / T2 / T3 ＋ **起票 11 の ESM**）を **1 本に束ねて裁く** | **要** | ⚠️ `decisions.md` **判断 12** の順序（**idea 議論 → Mh-D 全体の修正 → 再配布**）に乗せる。⚠️★★★ **2026-09-13 更新 —— 起票 11 の ESM は「取る」で確定済み**（★ 研究者判断 (a)）なので、**ここで裁くのは *要否* ではなく ⓪〜④ の実施**である。★ かつ **締切を持つのはこれだけ**（「O1 の収集が本格化する前」）→ ⚠️ **本行の他の要素（T1c / T2 / T3）と同じ速度で扱わない** |
| **5** | **T4（Practice Portrait）** | — | ⚠️ **後**。★ ただし **ADR-020 D3 の 6 条件**との照合が必須 |

## §8b ★★★ タスク 2 は **Loop Engineering モード C の初回**である（★ 研究者判断 2026-09-13）

★ 研究者の判断: 「**Loop Engineering を本格的に実施する形をとろう**」
⚠️★★★ **ただし Loop に載せるのは タスク 2 だけ**（→ `decisions.md` **判断 15**）。
★ タスク 0 / 1 / 3 / 5 は**裁定または契約文書**なので、**判断 1** のとおり Loop に載せない。

### ⚠️★★★ 前提監査の結果（★ 2026-09-13 に**実測**・⚠️ 予測ではない）

`docs/loop-engineering.md` 逐語「**ただし C の客観性は自動的には成立しない。次の 3 条件を満たした結果として
出てくる**: ①events を書くのは `loop-run.sh` だけ ②AC の検証コマンドが `verify` / `acceptance` に載っている
③verify がベースラインで緑」

| # | 前提 | ★ 実測結果 |
|---|---|---|
| **③** | **verify がベースラインで緑** | ✅ **合格** —— `cargo test --workspace` **655 passed / 0 failed**（★ 623 lib ＋ 31 ＋ 1）／ ゴールデン **`OK: 15 snapshots match`** ／ `emit_schema` **SCHEMA PARITY OK** ／ `cargo fmt --check` 差分なし ／ `cargo clippy --workspace --all-targets -- -D warnings` **exit 0** |
| — | テンプレート一式 | ✅ **揃っている** —— `.steering/_template/` に `loop-config.json` / **`loop-config.README.md`** / `loop-issue.md` / `loop-retrospective.md` |
| **②** | `verify` キーの規約 | ✅ **固定 3 種**（`test` → `typecheck` → `lint` の順に `loop-run.sh:220` が読む）＋ **acceptance は `$TASK_DIR/issues/<id>-acceptance.sh`** |
| — | model frontmatter の drift | ✅ **drift なし** —— `.claude/agents/*.md` 12 本が SSOT のモデル割当表と一致（`loop-worker`=sonnet / `loop-watchdog`=haiku / `test-runner`=haiku / `code-reviewer`・`security-checker`=opus） |
| ⚠️ | **`permissions.deny`** | ⚠️★★★ **README 必須リストから 5 件欠けている** —— 現状 `.claude/settings.json` は **`chmod -R` / `sudo` の 2 件だけ**。★ `loop-config.README.md` が必須と書くのは **`git push` / `gh pr merge` / `git reset --hard` / `git rebase` / `rm -rf`** を含む 7 件（逐語「★ `.claude/settings.json` の `permissions.deny` を**必ず併用する**（`deny` は allow と frontmatter の**両方に優先**）」） |
| ⚠️ | deny を **worktree へ入れる仕組み** | ⚠️★★★ **無い** —— `loop-spawn.sh` / `loop-run.sh` を grep して `settings` は **0 件**。★ **ただし `.claude/settings.local.json` は gitignore 済み**（`.gitignore:46`）で、`.claude/` 自体は **git 追跡（79 ファイル）**なので worktree には `settings.json` / agents / commands / skills が複製される。→ ★★★ **worktree の `.claude/settings.local.json` が正しい置き場**（⚠️ main checkout の `settings.json` に入れると**対話セッションでも `git push` が塞がれる**） |
| ⚠️ | **replay の警告** | ⚠️ `session hmm_version = 0.2.0, current engine = 0.5.0. snapshots may not be comparable.` が出る（★ fixture が HMM 0.2.0 で生成されているため）。★ **ただし exit 0 / 15 一致**で、**これが既存のベースラインである**。⚠️ **「無視してよい」と断定しない** |

### ⚠️★★★ 訂正 —— **「Loop を一度も回していない」は不正確だった**

★ `.steering/` に `_loop-events.jsonl` / `_loop-board.md` / `_loop-config.json` は **1 つも無い**（実測）。
⚠️ **しかし無人実行自体は 2 回試して、両方死んでいる。**
★ `.steering/_template/loop-config.README.md` 逐語:

> 実測 (claude 2.1.220) では最初の 2 回の無人実行が**コード 0 行のまま終了**した (約 $11 を消費)。
> 対話セッション (モードA/B) では人間が承認するので顕在化せず、**無人のモードC で初めて即死する**。

★ 原因は **`allowed_tools` を `null` にしたこと**（⚠️ `acceptEdits` は **Edit/Write を通すだけで Bash を通さない**。
★ worker が打つのは `cmd ; echo "EXIT:$?"` のような**複合コマンド**で、**各部分が個別に許可判定される**）。
→ ★ **テンプレートの既定リストは既に修正済み。⚠️ `null` に戻さないこと。**

### ★ タスク 2 を Loop に載せる前の着手順（★ この順で・⚠️ 飛ばさない）

| # | やること | ⚠️ 注意 |
|---|---|---|
| **1** | ⚠️★★★ **deny リストを worktree へ入れる経路を作る**（★ 下記 §8c に実体を置いた） | ★ `loop-run.sh`（または `loop-spawn.sh`）が worktree 作成後に `.claude/settings.local.json` を書く形にする。⚠️ **main checkout の `settings.json` には入れない**（★ 対話セッションの `git push` を塞ぐ） |
| **2** | `_loop-config.json` を `_template/loop-config.json` から写す | ⚠️★★★ **`loop-config.README.md` を必ず読む**（★ 落とし穴集）。★ `mode: "C"` ／ ⚠️ **`budget.parallel: 1`**（初回）／ `verify` は **GSE の実体へ pin**（`test` = `cargo test --manifest-path src-tauri/Cargo.toml --workspace` 等。⚠️ **テンプレの `pytest -q` をそのまま使わない**）／ `events_path` は **main checkout の絶対パス** |
| **3** | ⚠️ **`acceptance.sh` を書く**（★ 基準 4 / `loop-run.sh` の acceptance 段） | ⚠️★★★ **`cargo test` が無条件に緑になる issue では AC 未充足のまま `issue_done` になる**（★ `loop-run.sh` のコメント逐語）。→ ★ **新特徴が実際に出力に出ていることを検査する** |
| **4** | ★ **最も安い issue 1 本を `parallel=1` で回して基盤を検証する** | ★ SSOT 逐語。⚠️ **`--dry-run` では権限・cwd 境界・hook 発火・契約の二重定義が観測できない**（★ 実測で 2 回空振り） |
| **5** | 残り issue を回す | ★ 基準 3（Allowed Files 非交差）を満たす範囲で `parallel` を上げる |

### ★ タスク 2 の縦切り方針（⚠️ 分解セッションが確定する）

⚠️★★★ **Tier ごとの横切りにしない**（★ 基準 1「**層別の横切り分割は禁止**」）。
★ **特徴群ごとに縦に割る** —— 目安 **5 本**:

| issue 候補 | 中身 | ★ acceptance の考え方 |
|---|---|---|
| T0 | keys / delete / paste / mean IKI / 単純 pause / net production | ★ 出力に当該フィールドが出ること ＋ 手計算との一致 |
| T1a | pause p50/p90/max・CV・個人相対 surprise | ★ 同上 ＋ 分布統計の境界値 |
| T1b | 直前/直後 `KeyCategory`・Space/Enter/punctuation・IME phase | ★ `sentence_punctuation` が分離されていること |
| T1d | pause 後の生成/削除/移動・再停止時間・安定生成時間 | ★ `stall onset` の定義（**タスク 1 の成果**）に依存 |
| Q | capability / missingness reason / logger・IME health / observability mask | ⚠️★★★ **状態特徴にしない**（`survey:194`「**欠測を 0 として入力せず、推論の抑制・abstention に使う**」） |

⚠️★★★ **T1d は タスク 1（`stall onset` の操作的定義）の完了後でないと AC が書けない** —— ★ `## Dependencies` で直列化する。

## §8c ★★★ 着手順 1 の実体 —— **worktree へ書く deny リスト**（★ 再導出しないこと）

⚠️★★★ **これは研究者判断（2026-09-13）で「新しいセッションで Loop 基盤整備と同時にやる」と決めた作業である。**
★ 2026-09-13 セッションはコンテキストの都合で**実装せず、材料だけ確定した**。

### ★ 書く内容（★ `loop-config.README.md` の逐語リストに `gh pr merge` を含む 7 件）

★ worktree 作成直後に `<worktree>/.claude/settings.local.json` を**新規作成**する:

```json
{
  "permissions": {
    "deny": [
      "Bash(git push:*)",
      "Bash(gh pr merge:*)",
      "Bash(git reset --hard:*)",
      "Bash(git rebase:*)",
      "Bash(sudo:*)",
      "Bash(rm -rf:*)",
      "Bash(chmod -R:*)"
    ]
  }
}
```

### ★ なぜ worktree 側なのか（⚠️ main checkout に入れない理由）

| # | 事実（★ 2026-09-13 実測） |
|---|---|
| 1 | ★ `.claude/settings.local.json` は **`.gitignore:46` で ignore 済み** → **worktree ごとに別物にできる** |
| 2 | ★ `.claude/` 自体は **git 追跡（79 ファイル）** → worktree には `settings.json` / agents / commands / skills が**自動で複製される** |
| 3 | ⚠️★★★ **main checkout の `.claude/settings.json` に入れると、対話セッションでも `git push` が塞がれる** |
| 4 | ★ `loop-config.README.md` 逐語「★ `.claude/settings.json` の `permissions.deny` を**必ず併用する**（`deny` は allow と frontmatter の**両方に優先**）」 |
| 5 | ⚠️ **現状の `.claude/settings.json` は `chmod -R` / `sudo` の 2 件だけ**（= 必須 7 件のうち **5 件欠け**） |
| 6 | ⚠️★★★ **それを worktree へ入れる仕組みが無い**（`loop-spawn.sh` / `loop-run.sh` を grep して `settings` は **0 件**） |

### ⚠️ 実装時の注意

1. ⚠️ **既存の `settings.local.json` を上書きしない** —— worktree は新規作成なので通常は無いが、
   ★ **在ったら `deny` 配列へ**マージする（⚠️ 他のキーを消さない）。
2. ⚠️★★★ **検査を一緒に置く**（★ `verify-before-claiming` ルール 6）——
   ★ worktree 作成後に `deny` が 7 件入っていることを確認する段を入れ、
   ⚠️ **3 状態（在る / 無い / 壊れている）で試す**（ルール 5b）。
3. ⚠️ **`.steering/` に独立した作業記録を切る**（★ `/start-task` から。Loop 基盤への変更なので）。
4. ★ **`allowed_tools` は触らない** —— ⚠️ テンプレートの既定リストは
   「**最初の 2 回の無人実行がコード 0 行のまま終了した（約 $11）**」を受けて修正済みである。
   ⚠️★★★ **`null` に戻さない。**
5. ⚠️ **`deny` は「完全な境界」ではない** —— ★ README 逐語
   「許可を 1 つ間違えるだけで全体が迂回できる。**実質的な境界は worktree 隔離と人間の merge ゲート**」。

## §9 ★ 併走している未了事項（⚠️ このセッションでは触らない）

| 何 | どこ | 状態 |
|---|---|---|
| **ADR-029** | `docs/adr/ADR-029-outcome-role-arbitration.md` | ⚠️★★★ **ブランチ `docs/adr-029-outcome-role-arbitration` に 4 コミット・未 push / 未 PR。AC 1〜3 は研究者承認待ち**（★ `main` に無ければまずこれを確認する） |
| **起票 11**（ESM 監査 criterion） | `20260911-outcome-arbitration-and-o1-preflight/blockers.md` | ⏳★★★ **2026-09-13 更新 —— 研究者判断は出た =「(a) 6 択フルを O1 で取る」。⚠️ 再決定しないこと。**★ ただし**未着手**で、⚠️ **⓪〜④ が丸ごと残っている**（⓪ ESM 行の提出猶予と第三者の扱い → ① `data-privacy` ルール 7 の改訂 → ② 同意文書の改訂 → ③ `capabilities` 粒度の決定 → ④ `schema_dto.rs`）。⚠️★★★ **④ から始めてはならない。**⚠️ 締切は「O1 配布前」ではなく **「O1 の収集が本格化する前」** |
| **起票 12**（セッション終了の independent 仮定） | 同上 | ⚠️ 未解決 |
| **起票 13**（2 設計文書に ADR-024 / 029 未反映） | 同上 | ⚠️ 未着手（★ ADR-029 §Migration **N1 / N2**）。⚠️★★★ **`workspace-behavior-observation.md` は O1 の観測設計の SSOT** なので O1 未開始のうちに直すのが安い |
| **起票 6**（macOS ライブ変換で `abandon` 過大） | 同上 | ⚠️ **意図的に直していない**（★ 判断 12・特徴量設計が動きうるため） |
| `README.md:49`（ADR-022 行のセル区切り 1 本多い） | `docs/adr/README.md` | ⚠️ **pre-existing**・別 issue |
| PR #182 / #183 | GitHub | ⚠️ マージは研究者判断 |
