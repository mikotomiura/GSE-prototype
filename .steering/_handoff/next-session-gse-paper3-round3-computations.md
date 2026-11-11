# 引き継ぎ: 論文 3 の attack-me round 3（major）への対応の計算と、外枠の直し

worktree: /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning・push していない）

## 入口の 1 文
判断 24 の計算 3 つを /start-task から始めてください（条件と SEED をコードより前にコミット）。結果がそろったら、verdict.md の「直す順」で外枠を直し、round 4 を回すかを判定の推移を添えて研究者に問うてください。push と PR は研究者が確かめてから。

## 前提（読むもの）
- 判断 24: .steering/20261107-gse-paper3-per-person-learning/decisions.md の末尾
- round 3 の verdict: .steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-3/verdict.md（§2〜§5 の一致・直す順、§9 の採否）
- 感度の合成: experiments/20261110-per-person-sensitivity/（conditions.md・notes.md・scripts/・results/）
- 分解の定義: experiments/20261106-tau-mode-candidate/notes.md の 9 行（a = 本人(τ) − 最頻値、b = 最頻値 − 共通、c = a + b）と「形 1〜5」。この試験は HP Z2 で回した（run_id 20261106T205818-149・約 1.9 時間）ので、職場の PC に環境の先例がある。

## 計算（判断 24）
1. 合成の分解（Mac）: 感度の合成の複製（用量の陽性 1e-2・3e-2 と陰性対照、できれば構造と分布の筋も）に a・b の分解を当て、分解が「埋めた個人差」と「最頻値と共通の差」を見分けるかを確かめる。今の複製の json は最頻値の評価を持たないので、最頻値の当てはめを足して回し直す必要があるはず（確かめてから条件に書く）。読みの形（何が出たら Take-home の「読まない」を残す・弱める・やめるか）を結果の前に条件に書く。
2. CS1 の種を足す（Mac）: 用量の各段を 2 種、陰性対照を 5 種に（足すのは約 6 本・1 本 66〜89 分）。D5 の追記として、同じ seed 規則・同じ code_hash で回せるかを先に確かめる（sens_report は複製と plan の kept の一致を検査する）。
3. 実データで最頻値を比べの相手に加える（職場の PC・HP Z2）: 本人のデータを入れない事前分布の最頻値そのもの（平滑した共通）を、比べの相手の列と、他人で選ぶ候補の両方に置くかを条件で決め、主の表（Table 2 の値）を作り直す。実データ・書き手ごとの値・npz はメインの文脈に出さない（集計値だけ）。

## 計算の間に進めてよいもの（結果に依らない）
- データの声明の範囲を公開するコードに合わせる（T8）・3.4 に合成の確かめを入れる（T9）・擬似残差の記号の順序を書く（T10）・言い回し（監査役 2-B・2-D・3-A・3-B）・Aalbers と Saeb の引き方（R2 m3・n1）。
- 論文の外: context-B の持ち帰りと requirement.md を今の外枠に合わせる（監査役 3-D・3-E・3-4）。
- 文献: 打鍵からのユーザーモデリングと cold-start（個人モデルへ切り替える時期）を /literature-review かサブエージェントの並列で調べ、S1 の検索の記録に足す（T4）。references.md にある文献は番号だけ挙げさせる。

## 守ること
- 実データ・書き手ごとの値・npz を開かない（集計値だけ）。外部の LLM（Codex を含む）に打鍵の内容・NDJSON・書き手ごとの値を送らない。
- papers/ に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない。
- 決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて日本語で。報告を地の文の問いで終えない。
- Codex の予算は本線（/Users/johnd/GSE-prototype/.codex/budget.json）で読む。2026-11-11 は 78,564 / 2,400,000。
- 職場の PC へは枝を push して渡すことになるので、push の前に研究者に確かめる。

## 残っている小さなこと
- run_synth.py の再開時の見積もりの穴（較正の時間が落ちる）は直していない（感度の notes の「結果の後の確かめ」）。種を足すときに直すなら、code_hash が変わることを条件に書く。
- .codex/budget.json の変更は前から未コミットのまま（worktree の台帳は古い・本線が正）。
