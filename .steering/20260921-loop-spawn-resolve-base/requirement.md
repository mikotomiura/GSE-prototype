# loop-spawn-resolve-base — 起票 23 の是正（`resolve_base` が config を `tail -1` で黙って選ぶ）

## 背景

⚠️★★★ **`scripts/loop-spawn.sh` は、いま回そうとしているタスクとは無関係に base branch を pin する。**

★ 一次（`scripts/loop-spawn.sh:57` 逐語）:

```bash
cfg="$(ls -1 .steering/*/_loop-config.json 2>/dev/null | tail -1 || true)"
```

→ ⚠️ `.steering/` 配下の `_loop-config.json` を **名前順で最後の 1 つ**拾う。

### ★ すでに踏める状態である（⚠️ 2026-09-21 の実測。推測ではない）

- ★ 現存する config は **1 つだけ** = `.steering/20260914-mhd-feature-offline-tiers/_loop-config.json`
- ⚠️ その `base_branch` は **`docs/adr-030-stall-onset-definition`**（★ **完了済みタスクの作業ブランチ**）
- ★ 起票 23 に残る再現手順の実測:

  ```text
  $ LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz
  loop-spawn: base=docs/adr-030-stall-onset-definition (start=origin/docs/adr-030-stall-onset-definition) …
  HEAD is now at ca7764f docs(steering): 次タスク（前提条件 1〜6 の確かめ方）の引き継ぎを置く
  ```

  → ⚠️★★★ **main ではなく 38 コミット前の枝から worktree が切られた。**

### ⚠️ なぜ *いま* 直すのか（★ 研究者判断・2026-09-21）

★ `blockers.md` 起票 23 逐語:

> 「⚠️ **⑤'（理論の回）の *後* に実施する。★★★ ⑥（P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極）の実施前には *必ず* 解決させる。**」
> 「⚠️ **理由**: ⑥ は **Loop で回す**ので、★ `resolve_base` が古い枝を選ぶと **worktree が 38 コミット前から切られ、全 issue が誤った base の上で走る**。」

★ 先例（`decisions.md` 判断 25 #4 逐語）: 「**Loop 基盤の穴は次に Loop を回す前に直す**」。

### ⚠️ 既存の注記は「逆向きの事故」しか警告していない

★ `loop-spawn.sh:49-52` は **pin し忘れ → main から切られて全 issue 即死**だけを書いている。
⚠️ **pin が古いまま残る**形（本起票）は 1 行も書かれていない。→ ★ **両向きとも閉じる。**

### ★ 併せて見つけた既存の fail-open（⚠️ 起票 23 には書かれていない）

★ 一次（`loop-spawn.sh:59` 逐語）:

```bash
b="$(jq -r '.base_branch // empty' "$cfg" 2>/dev/null || true)"
```

→ ⚠️★★★ **`jq` が無い / config が壊れている / 値が空 —— どの場合も `b` が空になり、
黙って `origin/HEAD` → `main` へ落ちる。** ★ **pin が無言で消える**（＝ 起票 23 の注記が
警告する「全 issue 即死」の方向の事故が、**config を書いたのに**起きうる）。

## ゴール

★ **`loop-spawn.sh` が base を pin する経路で、「黙って間違う」形を 1 つも残さない。**

具体的には:

1. ★ config は **タスクで選ぶ**（`--task` / `LOOP_TASK`）。⚠️ **`tail -1` で黙って選ばない。**
2. ⚠️ 特定できないときは **fail-closed で止まる**（★ **config が 1 件でも**止める —— 研究者裁定）。
3. ★ 解決した base の **provenance と default からの乖離**を必ず出し、
   ⚠️ **無人モードC でも記録に残る**（★ 現在 `loop-run.sh:436` は `2>/dev/null` で捨てている）。
4. ★ モードC は **task を渡す**（`loop-run.sh` は `TASK_DIR` を持っているのに渡していない）。

## スコープ

### 含むもの

- `scripts/loop-spawn.sh` の `resolve_base` と、その前段の引数解析（`--task` の追加）
- `scripts/loop-run.sh` の `loop-spawn.sh` 呼び出し（★ task を渡す・stderr を捨てない）
- `scripts/loop-spawn-cleanup-test.sh` への**回帰群の追加**（★ 変異対照つき）
- `.steering/_template/loop-config.README.md` の `base_branch` 節（★ 解決順が変わるため）
- `docs/loop-engineering.md`（★ 起動の記述に `--task` が要るなら）

### 含まないもの

- ⚠️ **`--cleanup` の一致規則**（★ 起票 18 で是正済み。**混ぜない**）
- ⚠️ **`_loop-config.json` のスキーマ変更**（★ `task` / `base_branch` は既存フィールドをそのまま使う）
- ⚠️ **完了済みタスクの config の削除・整理**（★ 別の判断。⚠️ 本タスクは「黙って選ばない」ことだけを保証する）
- ⚠️ **起票 24**（`docs/loop-engineering.md` とは無関係。★ `20260914-mhd-feature-offline-tiers` 側は**取り下げ済み**。
  もう 1 つは `20260914-instrument-change-arbitration/blockers.md` 側で、研究者判断は「**起票だけ**」）
- ⚠️ **md lint / リンク到達性の機械検査**（★ S5 の `/cross-review` で別タスクとして起票したもの）

## 受け入れ条件

- [ ] **AC1**: `--task <t>` と `LOOP_TASK=<t>` の**両方**でタスクを指定でき、そのタスクの
      `_loop-config.json` の `base_branch` が pin される（★ `--task` が env より優先）
- [ ] **AC2**: `--task` が無く、`.steering/*/_loop-config.json` が **1 件以上**あるとき、
      ⚠️ **非 0 で止まり**、メッセージが **候補一覧**と **2 つの逃がし口**（`--task` / `LOOP_BASE_BRANCH`）を出す
- [ ] **AC3**: `--task` が無く、config が **0 件**のときは**従来どおり** `origin/HEAD` → `main` → `master` で解決する
- [ ] **AC4**: `--task <t>` が **0 件 / 複数件**に一致したとき、⚠️ **非 0 で止まり候補を列挙する**
- [ ] **AC5**: `LOOP_BASE_BRANCH` が設定されていれば **config を読まない**（★ 従来どおり最優先）
- [ ] **AC6**: config が**壊れている / 値が不正 / 参照が refname として妥当でない**とき、
      ⚠️ **非 0 で止まる**（★ 黙って `main` へ落ちない ＝ 既存 fail-open を閉じる）
- [ ] **AC7**: 解決結果が **provenance つきで出力**され、⚠️ **default ブランチからの乖離コミット数**が併記される
- [ ] **AC8**: `loop-run.sh`（モードC）が `--task` を渡し、⚠️ **loop-spawn の stderr を run ログに残す**
- [ ] **AC9**: 回帰テストが `scripts/loop-spawn-cleanup-test.sh` に入り、
      ★ **変異対照**（実装を殺したら赤くなる）を持ち、⚠️ **`jq` を要らない性質を壊さない**
- [ ] **AC10**: `bash scripts/loop-spawn-cleanup-test.sh` が **exit 0**（★ 既存 29 件も緑のまま）
- [ ] **AC11**: ⚠️★★★ **実 repo には 1 バイトも触れない**（★ 既存テストの規約。`mktemp` 配下の使い捨て repo のみ）

## 関連ドキュメント

- ★ **一次**: `.steering/20260914-mhd-feature-offline-tiers/blockers.md` **起票 23**
- `scripts/loop-spawn.sh`（★ `:53` が `resolve_base` / **`:57` が当該行**）
- `scripts/loop-run.sh`（★ `:43-44` が `CFG` / **`:436` が呼び出し**）
- `scripts/loop-spawn-cleanup-test.sh`（★ 受け皿。9 群 29 件・変異対照つき）
- `.github/workflows/ci.yml`（★ **配線は 2 か所**: `:658` Windows / `:760` ubuntu。⚠️ `:651` 逐語「本テストは **jq を要らない**」）
- `docs/loop-engineering.md`（★ Loop の SSOT・モデル割当 `:60-76`）
- `.steering/_template/loop-config.README.md`（★ `:97-100` が `base_branch` の解決順）

## 運用メモ

- **/reimagine 適用: No**
- **理由**: ★ 複数案は **grill の段で列挙し、研究者が 2 問とも裁定済み**である
  （(1) config 1 件でも止める / (2) 承認は記録に残すだけ・プロンプトは置かない）。
  ⚠️ したがって「初回案を破棄して再生成し比較する」段は**すでに通した**のと同じであり、
  ★ 残るのは確定した方針の実装だけである。
- **モデル**: ★ 設計判断は **Opus**（本ファイル / `design.md`）、実装・テストは **Sonnet**。
