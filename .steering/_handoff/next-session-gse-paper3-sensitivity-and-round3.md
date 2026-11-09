# 引き継ぎ —— 論文 3: 手順の感度を合成で確かめる試験（S15）と、attack-me round 3（Mac）

> 作成: 2026-11-10（Mac）。このメモを一次資料にしない。一次は `.steering/20261107-gse-paper3-per-person-learning/decisions.md`（判断 1〜23）と `.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-2/verdict.md`。外枠は `papers/per-person-learning/manuscript/outline.md`（commit 47d9b1b2）。worktree は `/Users/johnd/GSE-prototype-paper3`（枝 `docs/gse-paper3-per-person-learning`）。

## 0 入口の文（Mac の新しいセッションで打ち込む）

```
/Users/johnd/GSE-prototype-paper3/.steering/_handoff/next-session-gse-paper3-sensitivity-and-round3.md を読み、§2 の合成の感度の試験を /start-task から始めてください（条件と SEED をコードより前にコミット）。結果を外枠の S15 と 4.3 に入れた後、§3 のとおり attack-me round 3 を Codex も加えて回してください。push と PR は私が確かめてから。
```

## 1 ここまで（2026-11-10）

- attack-me round 1 major → 直す順 1〜14 を入れた（判断 19・20）。
- round 2 major（R1〜R3 major・E「直してから回す」・Codex major）。直す順 1〜3・5〜10 を入れた（判断 22・23）。直す順 4（感度の合成）だけが残り、外枠では S15 を「予定」と書いてある。
- 研究者の決定（判断 21）: take-home と実例を重なる窓の記号化に限る／感度は合成で確かめる／運用の場面は 1 文で定める／直した後に round 3 を回す（感度の結果を入れた後）。
- 構造の足りなさの試験は notes まで済んだ（`/Users/johnd/GSE-prototype-structure-deficit`・枝 exp/gse-structure-deficit-test・9d4edcba・未 push）。結果は外枠の S14 と Discussion に入れた（判断 17・18）。
- push していないコミット: 論文 3 の枝に 12、構造の試験の枝に 3（2026-11-10 の時点）。

## 2 合成の感度の試験（S15・新しい試験）

- 目的（round 2 の R2 N2・Codex）: 手順（構造と τ を他人で選ぶ・τ = ∞ を候補に入れる）が、実在する個人差を拾えるか。「個人差が無い」と「手順が保守的で拾えない」を分ける。
- やり方の骨（設計は /start-task の後に /reimagine で比べる）:
  - 合成の書き手（前の試験の selftest の合成の作りが下敷きになる。例: ml-improve conditions の P-POOL の合成）に、遷移の個人差を既知の大きさ（0 を含む数段）で埋める。
  - 手順をそのまま当て、選ばれた τ と構造、本人 − 共通の中央値と良い側の割合が、埋めた大きさに応じて上がるかを見る。
  - 陰性対照: 埋めた差 0・乱数の種を複数。事前分布の最頻値と共通の違いだけで、どれだけの正の残りが出るかを見る（外枠の「残りは本人の上積みとして読まない」の根拠を強めるか弱める）。
  - 読みの形（何が出れば「拾える」と書くか）を、結果より前に条件に書く。
- 場所: Mac（合成だけ・実データを使わない）。前の試験のコード（`experiments/20261104-timeseries-tau-extend/scripts/` など）を使うなら、条件にハッシュで固定する。
- 守ること: 実データ・書き手ごとの値・npz を開かない。結果を段 1 の候補の採否や ADR-047 の根拠にしない（D2・D6）。
- 結果の置き場: `experiments/<日付>-per-person-sensitivity/notes.md` → 外枠の S15 と 4.3 の 1〜2 文。open items の S15 の行を消す。

## 3 attack-me round 3

- Skill `attack-me`（`.claude/skills/attack-me/SKILL.md`）の Step 0〜5。round 2 と同じ立場・同じ接地の文献（本文は `round-1/tmp/sources/` に残っている）。
- 引き継ぎ（carryover）は役ごとに、round 2 の指摘・裏取り・採否・対応（判断 22・23 と S15）。他の役の指摘は渡さない。
- Codex は 5 本の後に直列で。既知の未決の一覧（round 2 の 5 件に、K の上端・2 次のマルコフ・多水準を回していないこと・含める共通と比べていないこと・記号化の範囲を足す）を添え、再掲しないよう頼む。入力は `scripts/run-codex-consult.sh --preview` で目で確かめる。
- 投稿規程: Springer は curl を拒む（2026-11-10）。Chrome で開いて照合するか、前回の照合のままと印を付ける。
- 判定の推移は major → major。round 3 が minor なら閉じて本文（Step 2）を勧める。major なら直す順を研究者に聞く。

## 4 研究者に残っていること

- push（論文 3 の枝・構造の試験の枝）と PR の順（構造の試験の枝は tau-mode・tau-extend・ml-improve の上に載っている。PR の前に順を研究者に聞く）。
- 文献番号: この枝は [V497]〜[V534]・[V496]。次は [V535] から（fetch してから全枝の最大を確かめる）。[V534] は論文 2 の枝の [V448]・[V488] と同じ文献（マージの後の方で tombstone）。[V496]（Dunn & Smyth 1996）の本文は未照合。
- 打鍵の user modelling と冷えた始動の文献（R2 N7・自信 低）は文献の調べが要る（/literature-review・既にある文献は番号だけ）。
- 記号列のハッシュの公開（R3 N7）は、公開 repo を作るときに判断 9 の追加として決める。
- `symbolizer.py` の docstring の friction・fluency は、残差の試験の来歴がハッシュを固定しているので未修正（公開の前に来歴の扱いを決めてから）。
- `.codex/budget.json` は未コミット。2026-11-07 の 26,322 tokens は未記帳。
- requirement.md（論文 3 のタスク）が判断 10・11・19 の後で古い（監査 3-4）。

## 5 守ること

- 決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて日本語で。報告を地の文の問いで終えない。
- papers/ に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。
- 外部の LLM（Codex を含む）にキーストロークの内容・NDJSON・書き手ごとの値を送らない。
- 返答は日本語。記号を多用しない。
