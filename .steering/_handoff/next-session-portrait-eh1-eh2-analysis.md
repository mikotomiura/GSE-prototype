# 引き継ぎ — 肖像の EH1・EH2 の結果のまとめと解析（両機器の push の後）

> 作成: 2026-10-09（研究者の指示「push された後の具体的な解析などは新セッションで行いましょう。引継ぎ書いといて」）。
> ⚠️ **このメモを一次資料にしない。** 合否の基準は `.steering/20261009-portrait-eh1-eh2/design.md` §3（`abfb2c45` で結果の前に固定）、逸脱は同 §8、判断は `decisions.md` 判断 1〜8。数字は `experiments/20261009-portrait-eh1/results/<world>/*.json` と `experiments/20261009-portrait-eh2/results/*.json` を開いて確かめる。
> 前提: Windows の機器が `next-session-portrait-eh1-eh2-windows.md`（EH1 v1・v2 ＋ EH2）を、Mac の機器が `next-session-portrait-eh2-macos.md`（EH2）を回し、同じブランチへ push し終えていること。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh1-eh2-analysis.md を読んで、肖像の EH1・EH2 の結果をまとめてください。
作業は worktree C:/wt/portrait-eh1-eh2（ブランチ docs/portrait-eh1-eh2）で行います。最初に fetch して、両方の機器の push が揃っているかを確かめてください。
```

## §1 どこまで済んだか（このセッション・2026-10-09）

- **タスク** `.steering/20261009-portrait-eh1-eh2/`（親は `20261005-portrait-invitation-constraints` の判断 5・8・11）。ブランチ `docs/portrait-eh1-eh2`（最初 `feature/` で切って CI が self-hosted で走ったので改名・判断 4）。最後のコミットは `064ccc80`（このメモのコミットを除く）。
- **EH1**: 計器（合成の記録 → `gse-replay` → 仮の生成器 3 種 × drift 2 種 ＋ 陽性対照 2 → 検査）を作り、スモークで通した。**本番の結果はまだ 1 つも開いていない**（この機械で回し始めた本番は、レビューの指摘で止めて開かずに消した・design §8）。本番は Windows の機器で回す（判断 5）。
- **EH2**: Windows（`IDesktopWallpaper`）と macOS（`NSWorkspace`）のスクリプト。この機械では `-DryRun` だけ（背景がスポットライトで、替えて戻す経路は回せない）。macOS 版は未コンパイル。
- **レビュー**: code-reviewer ∥ security-checker（判断 6）・`/cross-review` 2 巡（判断 7: 26 件・判断 8: 10 件）。すべて対応済み。
- ⚠️ **スモークで見えた値**（design §8 冒頭に全部書いた・本番の結果ではない・**解析の前提にしない**）: v1 は打鍵の有無だけのモデル A の AUC が 0.997 で E1-3 が全組判定不能になりうる（これが world v2 を足した理由）。順序の感度の比はスモークで 0.4〜1.9（組が 4 本）。⚠️ 本番の値で判断し、スモークの値に合わせて解釈を作らない。

## §2 やること

### 2.1 揃っているかを確かめる（最初に）

```
cd C:/wt/portrait-eh1-eh2
git fetch origin docs/portrait-eh1-eh2
git status -sb            # 手元に未コミットが無いこと
git pull --ff-only origin docs/portrait-eh1-eh2
git log --oneline 064ccc80..HEAD
```

- 来ているはずのもの: `experiments/20261009-portrait-eh1/results/v1/`・`results/v2/`・`notes.md`（Windows）／ `experiments/20261009-portrait-eh2/results/eh2-windows-*.json`・`notes-windows.md`（Windows）／ `results/eh2-macos-*.json`・`notes-macos.md`（Mac・直したなら `macos/eh2_wallpaper.swift` も）。
- 片方しか来ていなければ、来た方だけまとめてよい（来ていない方は tasklist に残す）。
- ⚠️ 受け手が計器（`scripts/`・`config.json`・`run.sh`）を変えていないかを `git diff --stat 064ccc80..HEAD -- experiments/20261009-portrait-eh1/scripts experiments/20261009-portrait-eh1/config.json experiments/20261009-portrait-eh1/run.sh` で確かめる。変えていたら、notes の「逸脱」に理由があるかを見て、design §8 に移す。

### 2.2 EH1 の結果の検算（解釈の前に）

- `results/<world>/provenance.json`: `experiment_dir_dirty` と `src_tauri_dirty` が `false`（null なら git が失敗した）・`git_commit` が計器を変えていないコミット・`hmm_version` = 0.5.0・`platform` と `cpu_count`・パッケージの版（`env.md` の値と違えば notes と env.md に書く）。
- 標準の JSON で読めること（非有限の数は `"inf"`・`"nan"` の文字列で入っている）。
- `capabilities.json` が通っていること。selftest が `0 failed` で、本番では 3 つ目の変異（`random levels`）が PASS したこと（notes に写してあるはず。無ければ受け手のログを研究者に聞く）。

### 2.3 EH1 の結果を基準どおりに読む（design §3）

world ごとに、組（`mapping` × `drift` × scheduler）ごとの判定を表にする。**v1 が主の記録、v2 は逸脱**（design §8）として分けて書く。

| 検査 | ファイル | 読み方 |
|---|---|---|
| E1-3 | `e13.json` | `positive_controls_ok`（PC1・PC2 の下限 > 0.10）と `null_ok`（帰無の 95 パーセンタイル < 0.03）が両方真のときだけ、緑・赤に意味がある。どちらかが偽なら全組「判定不能」。緑は「検査した範囲で、打鍵の有無を超える停滞の情報は見つからなかった」までで、無いことの証明ではない。`keyed` の緑は「セッションをまたぐ攻撃者」に対してだけ（本人が 1 セッションの中で写像を覚えることは検査していない） |
| E1-6 | `e16.json` | 比の 90% 区間が [0.8, 1.25] の中なら緑。`median_other` が 0 の組は「不在の中に予定の時刻が入るか」で変化が決まっている（スモークで見えた機序）。探索の `exploratory_recent.json`（60 s 以上の不在の中では更新しない scheduler）と並べて、U-4 の材料にする |
| 経路（履歴）の感度 | `order.json` の `ratio_full`・`ratio_proj`・`verdict` | 固定した §3.3。O の組は前半の中身も違うので「順序」ではなく「履歴の違い」への感度（判断 7 Z7）。⚠️ 仮の文法の歩みは小さな揺らぎで全体が変わる（スモークで比が 1 前後）。赤なら「形が揺らぎと経路の違いを区別できていない」 |
| 順序だけの感度（探索） | `order.json` の `exploratory_order_only` | 合否なし。D_shuffled（同じ区間を別の順に）÷ Jsh（揺らし） |
| E1-4 | `e14.json` | 比べる表示が 2 つ以上ある不在だけを数える。**cap1 の組は構成上判定不能**（判断 8 Y1）。PC2 が赤になっていること（検査器が働いている）。`endpoint_only_violations` は固定した定義（終点だけ）での数 |
| E1-7 | `e17.json` | 違反 0 で緑 |
| E1-2 | `e12.json` | 記述だけ。飛ばした slot の割合・更新の時点の「最後の打鍵からの秒数」・1 時間あたりの更新の数と無打鍵の秒数の相関（判断 5 の代償 3）・打ち続ける記録の最大の間隔（「打鍵の最中」の窓が長いと何時間も更新されない）・スリープ中の更新 0 |
| 戻ったときの変化と不在の長さ | `describe.json` の `spearman_absence_len_vs_change` | 判断 5 の代償 2 の大きさ |
| E1-8 | `e18/synth-*.png` | 基準なし。研究者に見せる候補（30 s で薄れる ／ 種に畳む ／ 何もしない） |

- 書き方: 「GSE が示した」と書かない。「合成の記録で」「仮の文法で」「検査した範囲で見つからなかった」。合成の「停滞」は打鍵の統計の型で、認知の状態ではない。
- ⚠️ 基準を後から動かさない。赤・判定不能を、解釈で緑に寄せない。

### 2.4 EH2 の結果を読む

- 両 OS: `restored` がすべて `true`（`not_attempted_on_other_*` なら手の確認の途中で止まった）・`per_monitor` / `per_screen` の `readback_ok` = `calls`・呼び出しの時間の中央値と p95・CPU（`pids_changed` が真の区間は無効）・`idle_elapsed_s` / `busy_elapsed_s`・`error`。
- 手の確認（あれば）: 仮想デスクトップ / Spaces で、設定が面ごとか共通か（`readback_matches_on_other_*` と `striped_image_visible_on_other_*` の組）。画面共有で変化が映るか・ちらつき。→ ちらつきや「何も変えない更新が見える」があれば、判断 7 Z14（モデル B に実際の更新の時刻を足した理由）の裏づけになる。
- macOS 版を受け手が直していたら、その差分をレビューする（Swift のコンパイルの誤りの修正なら軽く。中断・戻しの規則に触れていたら `/cross-review`）。

### 2.5 まとめて記録する

1. `experiments/20261009-portrait-eh1/notes.md`: 受け手が写した結果を検算し、2.3 の表の形に整える。限界の節はそのまま。
2. `design.md` §8: 受け手の「逸脱・気づいたこと」を移す。
3. `experiments/20261009-portrait-eh2/README.md` の「これまでの実行」に両 OS の行を足す（`notes-windows.md`・`notes-macos.md` を指す）。
4. `decisions.md` に **判断 9**（EH1・EH2 の結果と解釈・何が言えて何が言えないか）。
5. `tasklist.md` のチェックを更新。
6. **親タスクへの還元**: `.steering/20261005-portrait-invitation-constraints/decisions.md`（このブランチにも同じファイルがある・このブランチは親のブランチから切った）に **判断 12** として、EH1・EH2 の結果が U-4（更新の文法）・E1-8（地へ戻す）・判断 5 の代償 1〜3・判断 7（物体の再検討の条件）に何を与えたかを書く。⚠️ 親の判断の中身は変えない。
7. `.idea/20261005-motivation-fatigue-reentry-surface.md` §11 に要約を 1 節足す（**main checkout `C:\GSE-prototype` にあり版管理外**。main checkout の git には触らない。ファイルを書くだけ）。

### 2.6 研究者に聞くこと（AskUserQuestion・推奨と理由を添える）

- **U-4（更新の文法）**: E1-2・E1-6・E1-4・探索の `recent` の結果から、候補（揺らぎ・上限 1 回・不在の中では更新しない・間隔と窓の幅）のどれを EH3 の版にするか。⚠️ 推奨は結果を見てから決める。
- **E1-8（地へ戻す）**: PNG の候補を見せて選んでもらう（画像は Read で確かめてから、パスを示す。必要なら artifact にしてもよい）。
- **次の段**: 仮の文法の作り直し（経路の感度が赤なら、歩みが揺らぎに敏感すぎる）・EH3 の事前登録の準備（`.idea` §8.5・凍結の前に attack-me）・ADR に上げるか（親の判断 2: ADR に上げるのは EH1 の後）。どれも研究者が決める。
- ⚠️ **このセッションから持ち越した質問**: リモートに残った `feature/portrait-eh1-eh2`（`abfb2c45` を指す・CI を起こしうる）を消してよいか。答えが「はい」なら `git push origin --delete feature/portrait-eh1-eh2`。まだ答えをもらっていない。

### 2.7 閉じる

- まとめのコミット（`docs(experiments): …` / `docs(steering): …`・`Refs: .steering/20261009-portrait-eh1-eh2/`）→ push だけ。
- `/cross-review` 2 巡（1 巡目 = 結果の書き写しと基準の読み方の食い違い ／ 2 巡目 = 足した解釈の境界）。Codex は `scripts/run-codex-review.sh <base>..<head> -- <paths>`（パス限定・差分が 2,000 行を超えるなら分ける）。⚠️ 結果の PNG は送らない（JSON と md だけ）。
- **PR は計測の run の後**。merge の順は S-MR（`docs/motivation-reentry-survey`）→ 親（`docs/portrait-invitation-constraints`）→ このブランチ。

## §3 守ること（CLAUDE.md・memory から）

- 応答は日本語。研究者に聞くときは AskUserQuestion に推奨と理由を添える。
- git: `git add -A` やディレクトリ単位の add を使わない（ファイルを名指し）。main checkout（`C:\GSE-prototype`）は別のセッションの作業が載っているので触らない（`.idea` のファイルを書くのを除く）。**ブランチ名は `docs/` のまま**（`feature/*` の push で CI が self-hosted で走る）。計測の run 中なので PR を出さず push だけ。
- Codex の台帳（worktree の `.codex/budget.json`）は `git checkout --` で戻さず、修正と一緒にコミットする。予算ガードの hook は main checkout の台帳を読むので、回す前に `git show origin/main:.codex/budget.json` の今日の値と足して 300,000 に収まるかを見る（2026-10-09 はこのブランチで 108,882・全体で約 224,600 使った）。
- 生成した NDJSON と秒ごとの特徴（`work-*/`）は合成でもコミットしない。外部の LLM に送らない。
- bash の heredoc に引用符やバックスラッシュの多い Python を書かない（Write でファイルにしてから実行する）。
- 「0 件」「無い」と書かず「検査した範囲で見つからなかった」。主張の格は EH0。
