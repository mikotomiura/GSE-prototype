# 判断の記録

## 判断 1: 決める前にサーヴェイを 1 ラウンド挟む（研究者・2026-10-09）

- 研究者の問い「具体的に議論・サーヴェイしてから決定する？」に、Claude が理由 4 つ（撤回できない・issue の要の主張に根拠が無い・repo にこの主題のラウンドが無い・急ぐ理由が無い）を示して推奨し、研究者が「ok行ってよし」。
- 下位問いは S1 先例 / S2 攻撃 / S3 防御 / S4 制度（`requirement.md`）。
- 名前空間は V（データの公開の方法論）。

## 判断 2: 探索は 4 本並列、断定の根拠はメインが原本を取り直して照合する

- 4 本（general-purpose・Sonnet・各 20 分・入れ子禁止）。4 本とも 5 分以内に戻った。
- ⚠️ 下位エージェントの抽出テキストは照合に使わない。27 件をメインが curl で取り直し、pypdf / HTML から逐語を確かめた。
  - ⚠️ 途中で、Monaco & Tappert と Migdal & Rosenberger の 2 本を下位エージェントが保存したテキストで照合していたことに気づき、自分で取り直して照合し直した（逐語・表の数値とも一致）。
- 下位エージェントの報告で一次を確かめられなかったもの（BiAffect・Kaggle の Q-type・Wright 2008・code-to-data・UK Data Service ほか）は登録せず、カードの「やり残し」に置いた。

## 判断 3: 訂正 3 件は ADR-039 に反映せず、研究者の判断に回す

本ラウンドで、ADR-039（Proposed）と issue #333 の記述のうち 3 件が一次と食い違うと分かった。

| # | 箇所 | 旧 | 一次 |
|---|---|---|---|
| 1 | ADR-039 事実 1 の注 | 「『編集者の裁量』という言葉は、私が確かめた逐語には無い」 | BRM の投稿規定（見出し "Retrospective ethics approval"）に逐語 *"The decision on whether to proceed to peer review in such cases is at the Editor's discretion."* がある [V237] |
| 2 | ADR-039 D5 案 A の代償 | 「例外の逐語は自分で確かめていない [V237]」 | 逐語 *"When it is not possible to share research data publicly, for instance when individual privacy could be compromised, data availability should still be stated in the manuscript along with any conditions for access."* を確かめた [V237] |
| 3 | ADR-039 D6・issue #333 | 「時刻の丸めは、攻撃側の前処理で効き目を失いうる [V240]」 | 誤読。§2.6 は攻撃側が離散化して EER を良くできるか（改善はわずか）。§3.2 は防御側の離散化と乱数の遅延がどちらも保護を与え、同じ遅れなら乱数が上と書く [V240] |

- ADR は本文を書き換えない規約（`docs/agent-shared.md`）なので、ADR-039 には触れていない。`references.md` の [V237] [V240] の注記と、カード・`_index.md` には訂正を書いた。
- → **研究者が決めること**: ADR-039 に訂正の注を足すか、【決 5】【決 6】を裁くときの改訂（または後続 ADR）でまとめて直すか。issue #333 には訂正をコメントした。

## 判断 4: research-positioning は §4 の 1 か所だけ精緻化する

- 「本文非保存だから公開しやすい＝GSE の差分 = 否決 1-2」の下に、本文非保存でも結び付け・健康状態の推定は残り、照合も否定できないことを 1 段落で足した。研究の主張範囲（§1〜§3）は動かない。

## 判断 5: PR は出さず push だけにする

- 今日（2026-10-09）は計測の run が走っている可能性があり、PR を出すと self-hosted runner で CI が走る（memory: 計測中は docs/* に push だけ）。ブランチは `docs/` なので push では CI は走らない。
- PR にする時期は、計測が終わったことを確かめてから（完了報告に書く）。
