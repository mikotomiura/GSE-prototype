# 引き継ぎ —— 公開データの知見の論文（3）: 凍結の前の計算と attack-me round 2

> 作成: 2026-11-05（Mac のセッション）。このメモを一次資料にしない。決めたことの一次は `.steering/20261105-public-data-findings-paper/decisions.md`（判断 1〜11）、草案は同じ dir の `paper-write/prereg-draft.md`（v2）、外枠は `paper-write/outline.md`、査読の記録は `attack-me/prereg-paper1/round-1/`。

## 0 入口の文

```
/Users/johnd/GSE-prototype-public-findings/.steering/_handoff/next-session-gse-public-data-findings-paper-3.md を読んで、公開データの知見の論文の続きをして。§2 の順で。
```

作業の場所: worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`。push はまだ（研究者の手元で）。コミットの前に `git branch --show-current` を見る。

## 1 前のセッションで済んだこと

- JEDM の最近の 6 本（本文の中央値 約 10,200 語）とテンプレート（要旨 100〜300 語・補足は参考文献の後の付録・上限の規定なし・双盲は任意）を測った。予算は本文 7,000 語・上限 8,500（`paper-write/length-log.md`）。
- 主張は /reimagine の 2 案のハイブリッド（判断 9）: 評価の設計の方法の論文。貢献は反証・手前の変化と局面を分ける比べ方・契機の制約の 3 つ。
- 事前登録の草案 v1 → attack-me round 1（R1〜R3・監査役・Codex。すべて major）→ v2（判断 10・11）。
  - 大きな直し: KLiCKe の取り置き 1,498 人は前の実験 K6（2026-11-01・4,992 人全員）の集計に入っていた（取り置きは 11-02 に作られた）。KLiCKe は既に見たデータでの再現に下げ、確認は CS1 2019 年版の取り置き 146 人だけ。
  - 推定量は書き手の中の対を合わせた AUC・分岐は 5 通り・同値 50% 超は計器の退化・CS1 は改行で揃え、実行・貼り付け・切り替えのある停滞と対照は別の層。

## 2 次にやること（順に）

1. 凍結の前の計算 2 つ（草案の末尾）。見た書き手だけを使う（CS1 2019 年版の見た 319 人と KLiCKe の全員）。CS1 の取り置き 146 人は開けない（一覧に当たる書き手が入力にあれば止める）。
   - 置き場は新しい `experiments/<日付>-findings-paper1-prefreeze/`。`reproducibility-discipline` に従い、`conditions.md` を計算の前にコミットする。
   - (a) 幅の換算: AUC 0.55 前後で、対照の 90 分位を閾値にしたときの当たりと誤発火の差・1 時間あたりの発火の数。
   - (b) 精度の見積もり: 319 人から 146 人を引いて推定量の 95% 区間の幅（1,000 回）。CS1 で改行の揃えと「出来事なし」の層にしたときの件数も出す。
   - 結果を草案 v2 の [未計算] に入れる（P1 の幅の根拠・P7 の予備）。
2. 草案の凍結の準備: 付録 A（前の実験の条件の該当の文を貼り、単独で読める形に）・SHA-256・コミット・版を書く。
3. attack-me round 2（同じ立場・同じ接地の文献。round 1 の `panel.md`。`tmp/sources/` は消していない）。役ごとの引き継ぎ（carryover）を書く。Codex を加えるかを研究者に聞き、加えるなら既知の未決の一覧を添える。⚠️ attack-me は worktree の版（`.claude/skills/attack-me/SKILL.md`）を読む（main のチェックアウトの版は古く、編集者の役 E が無い。prereg では E を省くので round 1 の構成は同じだった）。
4. minor が 2 回続くか accept なら、OSF で凍結（研究者の手元）→ 確認の計算。

## 3 未決・注意

- H2・H3 も CS1 の取り置きで判定する。H3 の陰性でないことの対照（同じ学習器を揃えない比べに当てる）が通らなければ H3 は「判定できない」。
- 外部の LLM（Codex を含む）に書き手ごとの値を送らない。`~/gse-public-data` の書き手ごとの値は人が開かない。repo に出すのは集計値だけ。
- Mac の空きは 19 GB（2026-11-05）。KLiCKe の中間は `work.tar.gz`（225 MB）に圧縮してある。展開する前に空きを確かめる。
- `check_citations.py` の V386〜V412 の欠番は意図どおり（判断 3）。
- 返答・問い・記録は日本語で。記号を多用しない。push は研究者の手元で。PR は研究者が確かめてから。docs だけの PR は `[skip ci]`。
