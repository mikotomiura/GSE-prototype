# τ の候補に事前分布の最頻値を足す試験（gse-tau-mode-candidate）

引き継ぎ: `.steering/_handoff/next-session-gse-tau-mode-candidate.md`（2026-11-06・研究者が「論文 3 の前に回す」と決めた）。前の試験は `experiments/20261104-timeseries-tau-extend/`（notes の結果 2 の但し書き・判断 7）。worktree `/Users/johnd/GSE-prototype-tau-mode`（枝 `exp/gse-tau-mode-candidate`・前の枝の先端 `2911f940` から）。

## 背景

前の試験では τ = ∞ に「w を除く共通の母数」（基の擬似度数を含む）を置いた。有限の τ が τ → ∞ で近づく先は事前分布の最頻値 normalize(S̄)（基の擬似度数を含まない）で、両者は合成で A・C に 0.0064 の差がある。そのため、大きい τ（10^5 以上）での約 1e-3 以下の「本人 − 同じ構造の共通」が、本人の記録の寄与なのか、最頻値と共通の母数の違いなのかを分けられなかった（CoAuthor の ar で正・CS1 で負）。

## ゴール

最頻値（本人の記録を入れない点）を τ 固定の行と相手に足し、大きい τ での差を「本人(τ) − 最頻値」（a）と「最頻値 − 共通」（b）に分ける。CoAuthor の ar の「10^6 が ∞ をわずかに上回る」と CS1 の負の差が、読みの形 1〜3 のどれに当たるかを書く。

## スコープ

### 含むもの
- 条件（前の試験から変える所だけ）と SEED を計算の前にコミット
- 前の試験の scripts・run.sh・mutate.sh を写して変える（最頻値の固定行・相手・−∞ の扱い・共通の母数の保存）
- 合成の selftest の新しい対照と名指しの変異、P-REPRO（前の試験の summary と重なるセルを 1e-9）
- 計算の前の code-reviewer、Mac での selftest と変異の門、時間の測り直し
- 職場の PC 向けの引き継ぎ（repo と Drive の `GSE_ML_run`）、結果が戻った後の Mac 向けの引き継ぎ

### 含まないもの
- 本計算（職場の PC で回す）と結果の読み（結果が戻った後の別のセッション）
- 選ぶ行（τ 他人・τ 本人 CV・2 段・K 本人 CV）の候補の変更（判断 2）
- 共通の作り直し（引き継ぎの B 案・判断 1）
- push と PR（研究者が確かめてから）
- 論文 3 の執筆

## 受け入れ条件

- [ ] `conditions.md`・`SEED` が、コードの変更より前のコミットにある
- [ ] 合成の selftest がすべて緑、名指しの変異がすべて赤（終了コード 3）を Mac で確かめた
- [ ] code-reviewer を計算の前に通した
- [ ] 職場の PC 向けの引き継ぎが repo と Drive の両方にある（Drive の古い物は上書きの前に研究者の手直しを確かめた）
- [ ] 結果が戻った後の Mac 向けの引き継ぎが repo にある（notes の骨組み・読みの形を値の前に決めた）

## 守ること（引き継ぎ §5）

- 書き手ごとの値は人が開いて読まない。repo に出すのは集計値だけ。holdout の一覧を開かない。O1 の 11-01 08:30 以降の記録を開かない。
- 条件を変えるのは実データを見る前まで。
- 結果を段 1 の候補の採否の根拠にしない（ADR-047 D2・D6）。

## 関連ドキュメント

- `experiments/20261104-timeseries-tau-extend/conditions.md`・`notes.md`（結果 2 の但し書き・判断 7）
- `docs/experiment-tracking.md`（reproducibility-discipline）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 研究者が「使う」を選んだ（2026-11-06・grill の後）。design.md の初回案を退避し、requirement.md だけから作り直した案と比べる。
