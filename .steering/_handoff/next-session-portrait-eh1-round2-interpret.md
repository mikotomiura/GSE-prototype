# 引き継ぎ — 肖像の EH1 第 2 回の結果を読む（まとめのセッション）

> 作成: 2026-10-09（G-GEAR で本番を回したセッション）。本番のコミットは `5ef3c5d1`（ブランチ `docs/portrait-eh1-round2`）。
> ⚠️ このメモを一次資料にしない。基準は `.steering/20261009-portrait-eh1-round2/design.md` §3・§3.11、実行の記録と逸脱は `experiments/20261009-portrait-eh1-round2/notes.md`、値は `results/<world>/*.json`。
> 本番を回したセッションは結果の値を読んでいない（解釈をこのセッションに残すため）。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh1-round2-interpret.md を読んで、肖像の EH1 第 2 回の結果を読み、固定の基準で判定して notes・decisions・親タスクへ還元してください。
worktree は C:\wt\portrait-eh1-round2（ブランチ docs/portrait-eh1-round2）。
```

## §1 どこまで済んでいるか

- 基準の固定（`ea02e557`）→ 神託の追加（§3.11・`6b8ef7de`）→ 計器 → スモーク → `/cross-review` 2 巡（判断 4・5）→ **本番 v2・v1（G-GEAR・2026-10-09）**。
- 本番: 両 world とも `exit=0`・selftest `0 failed`（変異 4 本 PASS）・provenance は `git_commit` `0429e3aa`・`experiment_dir_dirty` false・`seed` 20261009・`jobs` 8。
- 逸脱（notes「逸脱・気づいたこと」1〜5）: `--jobs 16` → 8（Claude Code が裏のコマンドをメモリ不足で止めたため・研究者の決定）。v2・v1 とも 1 回ずつ途中で止められ、回し直した。結果は並列の数に依らない設計（design §3.9）。**design §8 の表にはまだ反映していない**（このセッションで反映する）。

## §2 このセッションでやること（順に）

1. **一次を読む**: design §3 全節と §3.11（基準）・§8（固定の後の逸脱）、`decisions.md` 判断 1〜5、notes 全体。第 1 回の読み方は `.steering/20261009-portrait-eh1-eh2/decisions.md` 判断 9 と `experiments/20261009-portrait-eh1/notes.md` §結果（書き方の型として）。⚠️ 長い一次を 1 節だけで代表させない（verify-before-claiming ルール 7・8）。
2. **判定を出す**（`results/v2/` が主・`results/v1/` が副）:
   - E1-3（§3.1）: **L300 が主・L60 が副**。両方を報告し、どちらかを選び直さない。先に「判定不能」の条件（PC1・PC2 の下限の最大 ≤ 0.10、または帰無の 95 パーセンタイル ≥ 0.03）を確かめてから、16 組の緑・赤を読む。
   - 神託（§3.11）: scheduler（既定・`recent`）ごと・ラベルごとに channel_narrow / partial / open。**実際の組の判定と並べるが、神託が「狭い」でも実際の組を緑と呼ばない**。
   - v1 の E1-3 は結果の前に not_applicable と宣言済み（§3.1）。PC が 0.10 を超えていても宣言を変えない。値は記述として出す。
   - E1-2・E1-4・E1-6・E1-7・帯ごとの更新の発生率・材料の情報量（§3.7・記述・合否なし）を §3 の各節の基準どおりに読む。
   - ⚠️ `summary.json` の `verdict` を写すだけにしない。基準の式と JSON の値（上限の最大・下限の最大・帰無）を突き合わせ、計器の判定が基準どおりかを少なくとも主の判定（v2 の L300・PC・神託）で手で確かめる。
3. **書く**:
   - notes の「結果」節（第 1 回 notes の型: world ごと・記述・限界）。
   - design §8 の表に本番の逸脱（`--jobs 8`・止められた 2 回）を時刻つきで足す。
   - `decisions.md` に判断 6 として「結果と解釈・次の段」を書き、研究者に聞く論点は AskUserQuestion（推奨と理由を添える）で決める。候補: U-4（`recent` を第一候補にしたままでよいか）、`lattice` を残すか、第 3 回が要るか、E1-8・EH3 への引き継ぎ。
   - 親への還元: `.steering/20261005-portrait-invitation-constraints/decisions.md` に、第 1 回の判断 12 と同じ型で新しい判断を足す（このブランチではなく親の worktree `C:\wt\portrait-invitation-constraints` か、merge の順に従ってどこに書くかを先に決める・研究者に確かめる）。
4. **`/cross-review` を 2 巡**（1 巡目＝自文書・他文書との矛盾、2 巡目＝自分が足した規則の境界条件）。パスを限定して回す（`run-codex-review.sh -- <paths>`）。出力は scratchpad。結果を decisions に記録する。
5. tasklist の「結果を読んで解釈する」を閉じる。コミット（ファイルを名指し）→ push だけ（PR はまだ出さない・merge の順は S-MR → 親 → `docs/portrait-eh1-eh2` → このブランチ）。

## §3 主張の格（守ること）

- EH0 の実験。結果は「検査した範囲で見つからなかった」まで。合成した「停滞」は打鍵の統計の型で、認知の状態ではない。「GSE が示した」と書かない。
- 判定は生成器の組ごと。全体を 1 つの合否にまとめない。
- 基準の値は動かさない。結果を見てから足す解析は「探索（固定の外）」と明記し、判定に使わない（第 1 回の `explore_material_info.py` と同じ扱い）。

## §4 守ること

- 応答は日本語。AskUserQuestion には推奨と理由を添える。★・⚠️ を多用しない。
- `git add` はファイルを名指しする（`-A`・ディレクトリ指定は禁止）。main checkout（`C:\GSE-prototype`）の git には触らない。
- 生成した NDJSON・`work-*/`・結果の PNG を Codex や外部の LLM に送らない。`/cross-review` に渡すのは notes・design・decisions の差分だけ。
- Codex の台帳は回す前に 3 つを足して確かめる: origin/main、このブランチ、main checkout（`.codex/budget.json`・上限を超える前例あり）。
- 重い計算は要らない（JSON を読むだけ）ので、どの機械でもよい。追加の解析で計器を回し直す場合は、計測の run・self-hosted CI と重ならないことを研究者に確かめる。

## §5 片付け（任意・研究者の判断）

- `experiments/20261009-portrait-eh1-round2/work-*/`（コミットしない一時ファイル）と、`C:/wt/_eh1r2-*.log`・`_eh1r2-*.start`（本番のログ・止められた回のログを含む）。notes に写す必要のあるログの行は写し済み。
