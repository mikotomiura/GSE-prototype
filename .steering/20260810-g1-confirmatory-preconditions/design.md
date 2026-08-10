# 設計

## 実装アプローチ

「確証標本に誰が入るか」を **git 管理下の 1 か所（`config.json` の `sample_roster`）**に集約し、
`analyze.py` がそれを**実行時に強制**する。文書だけの区別をやめる。

```jsonc
"sample_roster": {
  "_note": "誰が確証標本かの単一の正。analyze.py はここを見る。blocks/*.json は見ない",
  "confirmatory": [],                       // ★ n=3。実施のたびに追記する
  "pilot":        ["PILOT-mac", "PILOT-win"],
  "shakedown":    ["P010"]
}
```

★ **なぜ config.json か** → `decisions.md` D-3。`blocks/*.json` は gitignore 対象でこの Mac にしかない。

## 変更対象

### 修正するファイル

- **`experiments/20260801-controlled-friction-task/config.json`**
  - `design.n_subjects`: `"TO_BE_FROZEN_AFTER_PILOT"` → **`3`**（数値・D-2）
  - `sample_roster` を新設（D-3）
  - `status`: `PREREGISTERED_FROZEN_NOT_EXECUTED` → 実態に合わせる
    （shakedown 1 件実施済み・確証標本 0 件）
  - `revision.version`: 14 → **15**、`v15_changes` に非対称性を記述

- **`experiments/20260801-controlled-friction-task/preregistration.md`** 第 15 版
  - `§2.8` に **shakedown 条項**を追加（D-1）
  - 冒頭「この文書の位置づけ」の実施条件に、⚠️ **研究者承認で開始した事実**と
    Phase1 GATE3 が保留のままであるリスクを追記（D-4）
  - `§2.4` に **n=3 の凍結**を記録（D-2）と、`§2.4-4/5/6` の再宣言
  - ⚠️ **改訂履歴に「本改訂は P010 取得後・いかなる解析より前」**を明記

- **`experiments/20260801-controlled-friction-task/analyze.py`**
  - `main()`: `sample_roster.confirmatory` にある被験者だけを解析対象にする
  - ⚠️ roster のどのリストにも無い割付ファイルを **明示的に報告**（D-5）。黙って落とさない
  - roster が空 / キーが無い場合の扱い（★ 下記「境界」参照）
  - 結果に `sample_roster_applied`（誰を入れ、誰をなぜ外したか）を刻む
  - `PREREG_REVISION` を 15 に（★ 版一致検査 3 本が守る）
  - `selftest()` に回帰ケース

- **`experiments/20260801-controlled-friction-task/notes.md`**
  - `§2.4-1` 手続き 3: **凍結した日付とコミットハッシュ**を追記
    （⚠️ 時刻は書かない — repo を一時 public にする運用があるため）
  - 「確証標本の n — 凍結していない」節を**凍結済みに更新**

- **`experiments/20260801-controlled-friction-task/data.md`**
  - 冒頭「⚠️ **本実験は未実施**。被験者募集も行っていない。`results/` は空である。」の訂正
    （★ `results/` が空なのは**今も真**。訂正するのは前段 2 つ）

### 新規作成するファイル

なし。

### 削除するファイル

なし。

## ⚠️★ 境界の設計（ここを曖昧にすると黙って壊れる）

| 状況 | 振る舞い | 理由 |
|---|---|---|
| roster の `confirmatory` が**空** | ★ **止まる**（`[NG] 確証標本が 0 名`） | ⚠️ 空を「全員」と読むと、roster 導入前と同じ挙動に黙って戻る |
| 割付ファイルがあるが roster の**どこにも無い** | ★ **報告して除外**（`[warn]` + 結果に刻む） | D-5。追記漏れを黙って落とさない |
| roster にあるが**割付ファイルが無い** | ★ **止まる** | 確証標本の欠員を黙って n-1 で解析しない |
| `sample_roster` キー自体が無い | ★ **止まる** | ⚠️ 「古い config なら全員」と読むと保護が消える |
| 収集済み人数 < `n_subjects` | ★ **止まる**（`§2.4-4` optional stopping の禁止） | ⚠️ 途中で解析を見ないことを**実装で強制**する |

★ 最後の 1 行が `§2.4-4` を初めて機械化する。⚠️ これまで「見ない」は努力目標だった
（`§5.3` の封印が `§3.4` を機械化したのと同じ形）。

## 影響範囲

- ★ **`src-tauri/` はゼロ**。配布物は無変更（zip 再配布不要は前タスクで確認済み）
- `analyze.py` は **roster を書くまで動かなくなる** = 意図した破壊的変更。
  ⚠️ `results/` は `.gitkeep` のみで既存結果が無いため再現性の破れは起きない
- `--verify-blocks` は roster を見ない（★ 当日の検算は標本の別を問わない・`protocol.md §7`）
- `validate_blocks.py` は**変更しない**（転記検証は標本の別と独立）

## 既存パターンとの整合性

- ★ 「文書の規則を実装で強制する」は `seal_verdict`（`§3.4`）・`§3.10` の fail-loud と同じ形
- ★ 結果への刻印は `restart_handling` / `confirmatory_status_forfeited` と同じ作法
- ⚠️ roster は**単一の正**。`blocks/*.json` に同じ情報を複製しない
  （本日の教訓「鏡どうしを比べない」・`notes.md §10-7`）

## テスト戦略

★ **対照つきで確かめる**。「赤くなった」だけでは足りない。

1. `analyze.py --selftest`
   - roster の `confirmatory` に居る被験者だけが解析に入る
   - ★ 対照: roster を変えると入る/入らないが**切り替わる**（検査が空回りしていない）
   - 境界 5 種（上表）すべてが**止まる/報告する**こと
   - ★ 版一致検査 3 本（`analyze.py` / `config.json` / `preregistration.md`）が 15 で揃う
2. `validate_blocks.py --selftest` — 無変更のまま緑（回帰していない）
3. ★ **実データ**: `analyze.py` が **P010 を確証解析に入れない**
   ⚠️ **判定は出さない**（`§3.4`）。「除外された」ことの確認に留める
4. ⚠️★ **壊して赤を見る**: roster の P010 を `confirmatory` に移すと解析対象に入る
5. `bash run.sh` が GREEN

## ロールバック計画

- 変更は Python 1 + md 3 + json 1。`git revert` で戻せる
- ⚠️ `preregistration.md` は凍結文書なので、revert する場合は改訂履歴に「撤回した」と残す
- ★ `blocks/*.json` は本タスクで触らない（gitignore 対象・この Mac にしかない）

---

## ★ 実装中に変わったこと（Step 2 最終化・2026-08-10）

### 1. ⚠️★★ `/cross-review` の CRITICAL: `§3.6` との緊張が未整理だった

`§3.6` は **❌「被験者を事後に除外しない」**（除外規則: 事前に宣言した同意撤回のみ）を凍結している。
★ P010 を確証標本の外に置く操作は**機能的にこれと同型**であり、当初の第 15 版は
`§2.4-4`（結果を見ていない）にしか答えていなかった。

→ `§3.6` 第 2 版注記の**判定 3 条件**に当てて表で示し、
⚠️ ★ **1 つ（データ取得前に固定）を満たしていない**ことを明記した。
「登録簿に載ったことがない」という言い分が**弱い議論**であること、
担保が **`results/` が空であること 1 点のみ**で判定を出したら使えなくなることも書いた。

### 2. ⚠️★ 両者一致 HIGH: roster はファイル名で許可するのに結果は `subject` を使っていた

`sample_roster` は `p.stem` で許可するが、`main()` が結果に刻むのは `spec["subject"]`。
★ ずれると **roster が許可していない被験者の結果が確証解析に載る**。
⚠️ `validate_blocks.py:590` は同じ検査を持っていたのに `analyze.py` には無かった——
★ **本タスクの目的（誰が確証標本かを実装で強制する）そのものに穴が開いていた。**
→ `check_subject_matches_filename` を追加し fail-loud 化（純関数・テスト 3 件）。

### 3. ⚠️★ HIGH: コミットハッシュの引用が誤っていた（★ 自分のミス）

`commit 20ea075` を 3 箇所に書いたが、これは**直前タスク PR #95 のマージ**であり本改訂とは無関係。
★ 監査の唯一の外部証跡にするつもりの値が、別の作業を指していた。
→ 除去し `PENDING-FILL-AFTER-COMMIT` に置換。**コミット後に実ハッシュへ差し替える**。

### 4. その他

- n=3 の論拠に「向きが事前に分からないからこそ、向きを見ずに固定する」を追記（MEDIUM）
- 同一リスト内重複のメッセージを「confirmatory と confirmatory」から改善し専用テスト追加（LOW）
  ⚠️ ★ Codex は「同一リスト内重複はエラーにならない」と述べたが、**実測ではエラーになった**
  （`seen` が同一 kind でも累積するため）。★ **指摘を鵜呑みにせず再現したので気づけた。**

## ★ 配布への影響: 無し

`git status -- src-tauri src` が空。⚠️ 参加者への zip 再配布は不要。
