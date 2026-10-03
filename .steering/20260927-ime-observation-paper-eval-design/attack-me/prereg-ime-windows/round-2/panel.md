# panel — 3 つの立場と接地の文献（attack-me・stage `prereg`・対象物 Windows の追補・round 2）

作成: 2026-10-03（Surface・メイン）。★ round 1 と同じ文献・同じ本文（`round-1/tmp/sources/`）を使う。macOS の事前登録（`..\..\prereg-ime-macos\round-1〜5`）と**同じ立場・同じ文献**で回す（研究者の指示「macOS の round 1〜4 と同じ立場・同じ接地の文献で」・判断 140）。書誌の確認（OpenAlex）は `..\..\prereg-ime-macos\round-1\panel.md` のとおり。

## 本文の置き場（この round で取り直した）

macOS の round の `tmp\` は G-GEAR にあり、この機械に無い → この round で取り直した。置き場は `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\prereg-ime-windows\round-1\tmp\`（`raw\` に原本・`sources\` に本文テキスト）。`git check-ignore -q` が真であることを確かめた。本文は印字していない（題の有無・文字数だけ）。PDF は `uv run --no-project --with pypdf`（使い捨ての環境）で開いた。

| 役 | 文献 | 原本 SHA-256（round 1 の値との照合） | 本文（文字数・題） |
|---|---|---|---|
| R1 | Pinet et al. (2017). *BRM, 49*, 1163–1176. doi:10.3758/s13428-016-0776-3 | `5b22bf8d…943ec2` 一致 | `sources\pinet2016.txt`（53,646 字・題あり） |
| R1 | Bridges et al. (2020). *PeerJ, 8*, e9414. doi:10.7717/peerj.9414（Europe PMC の全文 XML・PMC7512138） | `25dcabfc…6d9f` 一致 | `sources\bridges2020.txt`（87,177 字・題あり・参考文献の一覧を除いた） |
| R1 | Plant (2016). *BRM, 48*, 408–411. doi:10.3758/s13428-015-0577-0 | `7913cbac…ad61fef` 一致 | `sources\plant2016.txt`（21,329 字・題あり） |
| R2 | Conijn, Roeser, & van Zaanen (2019). *Reading and Writing, 32*, 2353–2374. doi:10.1007/s11145-019-09953-8 | `76b0a804…5196` 一致 | `sources\conijn2019.txt`（70,378 字・題あり） |
| R2 | Monaco (2018). SoK: Keylogging side channels. *IEEE S&P*, 211–228. doi:10.1109/SP.2018.00026 | `af13534f…24aa5` 一致（1 回目は IEEE がボットに HTML を返した → ブラウザの UA で取り直した） | `sources\monaco2018.txt`（118,290 字・題あり） |
| R3 | Lakens (2022). Sample size justification. *Collabra: Psychology, 8*(1), 33267. doi:10.1525/collabra.33267（著者の公開版・OSF `9d3yf`） | `9346742b…ceca2648` 一致 | `sources\lakens2022.txt`（147,824 字・題あり） |
| R3 | Wicherts et al. (2016). *Frontiers in Psychology, 7*, 1832. doi:10.3389/fpsyg.2016.01832 | `26d1f9f6…46bb` 一致 | `sources\wicherts2016.txt`（73,087 字・題あり） |
| R3 | Koo & Li (2016). *Journal of Chiropractic Medicine, 15*(2), 155–163. doi:10.1016/j.jcm.2016.02.012（PubMed Central の HTML・PMC4913118） | ⚠️ `6d258c6e…40ea`（round 1 の `dd4ff493…b2292` と違う。PMC のページの動的な部分による。題・筆頭著者は一致） | `sources\koo2016.txt`（29,052 字・題あり） |

→ 各立場に「確認済み、かつ読めた」文献が 2 本以上（R1 3・R2 2・R3 3）。

## 立場と下位人格（macOS の round と同じ）

- **R1** 打鍵の時刻を測る道具を外部の基準で検証する計測の伝統。下位人格: 「その測定は本当にそれを測っているか」を疑う懐疑家（基準そのものの妥当性・基準と測定の独立性・合成入力の代表性）。
- **R2** 打鍵記録を使う書字過程の研究者と、行動ログの公開の安全（利用者の側）。下位人格: 「で、読者は何に使えるのか」と問う実務家・冗長さに厳しい読者。
- **R3** 投稿先の方法論と再現性の番人（統計・事前登録・規程）。下位人格: 事前に 1 通りに決まっていない分岐・根拠の無い n・後から選べる指標を探す摘発者。

## 投稿規程

この round で取り直した: `tmp\raw\brm-guidelines.html`（SHA-256 `1df2819e4913c9d9b4c9dae26737becb2680c5bae19bf617805d82a7a814834c`）→ `tmp\sources\brm-guidelines.txt`。照合の結果は `context-A.md`。
