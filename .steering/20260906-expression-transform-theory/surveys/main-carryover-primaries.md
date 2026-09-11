# メインが直列で回収した一次資料（2026-09-06・本ラウンド）

> ★ 本ファイルは **subagent の出力ではない**。⚠️ `HANDOFF-next-session.md` §4.3「その他の持ち越し」
> （前ラウンドで一次を取れなかったもの）を、**メインが `pypdf` / Europe PMC / Crossref 経路で回収した記録**である。
> ★ 4 件を試み、**3 件で一次全文を取得、1 件は closed access で取得不能を確定**した。

---

## 1. ★★★ [P49] Bae et al. (2022) —— **取得成功**（⚠️ 2 ラウンド連続の失敗を解消）

- **出典**: Bae, S. S., Zheng, C., West, M. E., Do, E. Y.-L., Huron, S. & Szafir, D. A. —
  *Making Data Tangible: A Cross-disciplinary Design Space for Data Physicalization*, **CHI 2022**, 18 pages.
- ★★★ **CHI 版 DOI を確定**: `10.1145/3491102.3501939`（★ 本文 1 頁目の逐語
  `https://doi.org/10.1145/3491102.3501939` ＋ `ACM ISBN 978-1-4503-9157-3/22/04`）
  → ⚠️ **references.md の [P49] 行は現在「CHI 版 DOI 未確認・本文未取得」で `provisional`。★ `active` へ上げられる。**
- **取得経路**: `https://arxiv.org/pdf/2202.10520` を curl で保存 → `pypdf` で 18 頁・126,885 字を抽出。
  ⚠️★★★ **失敗の原因が判明した —— PDF が 31 MB あり、WebFetch のサイズ上限を超えていた**
  （★ 403 ではなくサイズだった。★ curl + pypdf なら通る）。

### ★ 一次で確認できた逐語（3 点）

1. **要旨（既存 gloss の裏取り・支持）**:
   > *"research currently **lacks a synthesis across the different communities** data physicalization sits upon,
   > including their approaches, theories, and even terminologies"*
   → ★ **references.md の既存 gloss は一次で支持された。**

2. ⚠️★★★ **著者自身が設計空間の性格を限定している（★ 新規・既存 gloss を *強める*）**:
   > *"While design spaces can be characterized by their (1) **descriptive power** ... (2) **evaluative power** ...
   > (3) **generative power** ... , this design space is **more descriptive by nature**"*
   → ★★★ **「引けるのは設計語彙と事例集まで」という既存の温度設定は、著者本人の自己限定で裏付けられた。**
   ⚠️ **効果の主張には使えない**（★ 著者が evaluative power を主張していない）。

3. ★ **`reflection` は *最頻のタスク* である（★ 新規の数値）**:
   > *"we found **reflection—the act of increasing one's self-knowledge—to be the most popular task
   > physicalizations support (18/47)**"*
   → ⚠️★★★ **これは「データ物理化は反省を促す」の証拠ではない。**
   ★ 18/47 は **設計者が意図したタスクの分類** であって、**反省が起きたことの測定ではない**。
   → ★ **既存 gloss「分野の作業仮説であって統合された効果証拠ではない」は、この数値によってむしろ *精密になる*** ——
   **「分野の 38% が反省を *狙って* いるが、狙いの集計であって効果の集計ではない」**と書ける。

### ★ 併せて確定したコーパス構成（★ 数値の精密化）
ACM DL `n = 520` ＋ IEEE Xplore `n = 107` → 重複・非アーカイブ除去後 `n = 411` →
包含基準で `n = 42` → 専門家補完 `n = 5` → **計 47**。

---

## 2. ★★★ van der Bles et al. (2020) PNAS —— **取得成功**（⚠️ 前ラウンドは伝聞のみ）

- **出典**: van der Bles, A. M., van der Linden, S., Freeman, A. L. J. & Spiegelhalter, D. J. —
  *The effects of communicating uncertainty on public trust in facts and numbers*,
  **PNAS 117(14):7672–7683, 2020**。DOI `10.1073/pnas.1913678117`（CC BY 4.0）
- **取得経路**: ⚠️ **PNAS 本体の PDF は 403。**★ **Europe PMC の `fullTextXML`（`PMC7149229`）から全文 85,755 字**を取得。
  → ★ **PNAS / PMC 系はこの経路が効く**（★ 次回以降の定石にする）。

### ⚠️★★★ 前ラウンドの伝聞は「概ね正しいが、要点を落としていた」

★ 伝聞は「**5 実験・n=5,780・信頼への影響は小さい**」だった。⚠️ **一次を読むと、その「小さい」が *平均* であり、
形式で符号と大きさが大きく変わる。**

- ★ 設計の逐語: *"We conducted **five experiments**—including one **preregistered replication** with a national
  sample and one **field experiment on the BBC News website** (total **n = 5,780**)"*
  → ★ 内訳は **オンライン実験 4 本 ＋ BBC News 実地実験 1 本**（★ 内部メタ解析は **4 本**に対して実施）。
- ★ **内部ランダム効果メタ解析（4 研究）の逐語値**:

| 従属変数 | 全体 | **verbal**（言語的） | **numeric**（数値範囲） |
|---|---|---|---|
| 知覚された不確実性 | **d = 0.65** [0.42, 0.87] | **d = 0.88** [0.62, 1.14] | d = 0.43 [0.33, 0.52] |
| 数値の信頼性の低下 | **d = −0.34** [−0.16, −0.53] | — | — |
| 数値への信頼 | — | ⚠️★★★ **d = −0.55** [−0.35, −0.74] | d = −0.15 [−0.05, −0.24] |
| 情報源への信頼 | d = −0.12 [−0.03, −0.22] | d = −0.21 [−0.12, −0.31] | ★ **d = −0.03** [−0.03, 0.06]（**n.s.**） |

⚠️★★★ **したがって「不確実性の開示は信頼にほぼ影響しない」は *数値形式に限った* 話である。**
★ **言語的（非数値）に開示すると、数値への信頼は d = −0.55 で substantially 下がる**（★ 著者も
*"much of the overall effect seems to stem from verbal uncertainty"* と明記）。

### ★★★ GSE への含意（★ 3 系統が同じ向きに揃った）

⚠️ **GSE の表現層は定義上「数値でない」** —— 抽象的な視覚符号であり、
**「範囲つき点推定」ではなく「質的な言い方」の側に構造的に近い**。
→ ★ 次の 3 本が **独立に同じ向き**を指す:

| 一次 | 中身 |
|---|---|
| ★ **van der Bles 2020**（本件・N=5,780） | **非数値（verbal）の開示は数値への信頼を d = −0.55 で下げる。数値形式は n.s.** |
| **Gulacsik et al. 2022**（N=489・既出候補） | **色分け（非数値符号化）は数値より信頼低下・誤読増**（`F(4,484)=3.10, p=.016, d=0.26`） |
| **Dries et al. 2025**（事前登録・N=601+1001・既出候補） | 「小さい」は**先行信念との交差交互作用を隠していた**（β = −0.34〜−0.41） |

→ ★★★ **判断 (b) の「層 A は C へ縮退（第 1 版で不確実性を表現しない）」は、本一次で *もう 1 本* 支えが増えた。**
⚠️ **ただしこれは外挿である** —— ★ 上記 3 本はいずれも **外部の事実・予報・AI 予測**についての不確実性であり、
**「本人の内的状態の推定の不確実性を本人に返す」設定での実証ではない**。→ 温度は **`PLAUSIBLE BUT UNPROVEN`** に留める。

---

## 3. ⚠️ Holmquist (2004) —— **取得不能を確定**（★ 書誌だけ確定した）

- **出典**: Holmquist, L. E. — *Evaluating the comprehension of ambient displays*,
  **CHI '04 Extended Abstracts**, DOI `10.1145/985921.986121`
- ★★★ **Crossref で書誌を検算した結果、`page: 1545-1545` ＝ 文字どおり *1 頁*、単著**である。
  → ★ **前ラウンドの「1 頁提案」という性格づけは、書誌レベルでは確定した。**
- ⚠️★★★ **しかし本文は取得できない** —— Semantic Scholar の逐語:
  `"openAccessPdf": {"url": "", "status": "CLOSED"}`。ACM DL は Cloudflare で遮断。Unpaywall にも OA 版なし。

### ⚠️★★★ したがって SSOT 訂正候補 (i) は **本ラウンドでも実行できない**

★ `expression-channel.md` §8 **PS-Q5**「3 段の分類学は文献上存在しない」に対する反例候補
（**Holmquist が THAT / WHAT / HOW を自己一般化している**）は、**内容の主張が依然として二次情報のまま**である。
→ ⚠️ **`verify-before-claiming` により、まだ SSOT を書き換えてはならない。**
★ **持ち越しの性格が変わった**: 「一次未確認（探せば取れるかも）」→ **「一次は OA 経路に存在しない。
図書館アクセスか著者への直接依頼が要る」**。★ 次ラウンドで漫然と再探索しないこと。

---

## 4. ★ Roddy & Bridges (2020) —— **取得成功**（★ RQ E 担当へ引き渡し済み）

- **出典**: Roddy, S. & Bridges, B. — *Mapping for meaning: the embodied sonification listening model and its
  implications for the mapping problem in sonic information design*,
  **Journal on Multimodal User Interfaces 14(2):143–151, 2020**。DOI `10.1007/s12193-020-00318-y`
- **取得経路**: ⚠️ Springer 本体はペイウォール。★ **Unpaywall → Ulster University 機関リポジトリの
  Author Accepted Manuscript（18 頁・CC BY 4.0）** を取得し `pypdf` で 54,680 字を抽出。
  ⚠️ **post-peer-review / pre-copyedit 版**である旨は引用時に明記すること。
- ★ 逐語 2 点:
  - ⚠️ *"**This is a theoretical paper** that considers the mapping problem..."*
    （★ 全文で `empirical` **0 回** / `arbitrar` **0 回** ＝ **経験的検証ゼロ**）
  - ★ *"Embodied cognition suggests that there is both **another layer of constraints** for which we must account
    and another layer of possibilities that we can exploit..."*
- → ★ **RQ E 担当 subagent へ全文パスごと引き渡し済み**（★ 判定はメインが拘束せず、subagent の 3 票に委ねた）。

---

## ★ 経路の教訓（★ 次ラウンドで再発明しないこと）

| 症状 | 原因 | ★ 効く経路 |
|---|---|---|
| arXiv PDF が WebFetch で取れない | ⚠️ **サイズ上限**（[P49] は 31 MB） | ★ `curl -L https://arxiv.org/pdf/<id>` → `pypdf` |
| arXiv abs ページが 403 | ⚠️ UA 判定 | ★ ブラウザ UA を付ける／`export.arxiv.org` も同じ本体を返す |
| PNAS / 医学系が 403 | ⚠️ 出版社側の遮断 | ★★★ **Europe PMC `webservices/rest/<PMCID>/fullTextXML`**（★ PMCID は `search?query=DOI:"..."` で引ける） |
| Springer / Elsevier がペイウォール | — | ★★★ **Unpaywall `api.unpaywall.org/v2/<doi>?email=`** → 機関リポジトリの AAM |
| ACM DL がペイウォール | ⚠️ Cloudflare | ⚠️ **OA 版が無ければ諦める。**★ `api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=openAccessPdf` で **CLOSED を確定させて持ち越しを閉じる** |
| 書誌（頁数・掲載誌・年）だけ確かめたい | — | ★ `api.crossref.org/works?query.bibliographic=...&select=DOI,title,author,container-title,issued,page` |
