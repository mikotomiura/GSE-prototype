# panel — 3 つの立場と接地の文献（attack-me・stage `prereg`・round 2）

作成: 2026-10-01（G-GEAR・メイン）。★ round 1 と**同じ立場・同じ文献**で回す（Skill「round 2 以降は同じ立場・同じ文献」）。書誌の確認と取得元は `..\round-1\panel.md` のとおり。

## 本文の置き場（round 1 のものを使う）

- 本文テキストは round 1 で取得・保存したものをそのまま使う: `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\prereg-ime-macos\round-1\tmp\sources\`（root の `.gitignore` の `tmp/` が無視する。round 2 の着手時に 8 本とも `git check-ignore -q` が真であることを確かめた）。
- 原本が round 1 から変わっていないことを、round 2 の着手時に原本の SHA-256 で確かめた（`round-1\tmp\raw\` の 9 ファイルが、round 1 の panel.md の値と一致）。
- 本文は印字していない（round 1 と同じ）。
- ⚠️ round 1 の `tmp\` は、attack-me を閉じる（研究者が最後の round の採否を決め終える）まで消さない。

## R1 — 手法の核: 打鍵の時刻を測る道具の検証（計測の伝統）

- 立場・下位人格: round 1 と同じ（基準そのものの妥当性・基準と測定の独立性・合成入力の代表性を疑う懐疑家）。

| 文献 | 原本 SHA-256（round 2 で再確認） | 本文 |
|---|---|---|
| Pinet et al. (2017). *BRM, 49*, 1163–1176. doi:10.3758/s13428-016-0776-3 | `5b22bf8d…943ec2` 一致 | `round-1\tmp\sources\pinet2016.txt` |
| Bridges et al. (2020). *PeerJ, 8*, e9414. doi:10.7717/peerj.9414（Europe PMC の全文 XML） | `25dcabfc…6d9f` 一致 | `round-1\tmp\sources\bridges2020.txt` |
| Plant (2016). *BRM, 48*, 408–411. doi:10.3758/s13428-015-0577-0 | `7913cbac…ad61fef` 一致 | `round-1\tmp\sources\plant2016.txt` |

## R2 — 隣接分野: 打鍵記録を使う書字過程の研究者と、行動ログの公開の安全（利用者の側）

- 立場・下位人格: round 1 と同じ（「で、読者は何に使えるのか」と問う実務家・冗長さに厳しい）。

| 文献 | 原本 SHA-256（round 2 で再確認） | 本文 |
|---|---|---|
| Conijn, Roeser, & van Zaanen (2019). *Reading and Writing, 32*, 2353–2374. doi:10.1007/s11145-019-09953-8 | `76b0a804…5196` 一致 | `round-1\tmp\sources\conijn2019.txt` |
| Monaco (2018). SoK: Keylogging side channels. *IEEE S&P*, 211–228. doi:10.1109/SP.2018.00026 | `af13534f…24aa5` 一致 | `round-1\tmp\sources\monaco2018.txt` |

## R3 — 投稿先の方法論と再現性の番人（統計・事前登録・規程）

- 立場・下位人格: round 1 と同じ（事前に 1 通りに決まっていない分岐・根拠の無い n・後から選べる指標を探す摘発者）。

| 文献 | 原本 SHA-256（round 2 で再確認） | 本文 |
|---|---|---|
| Lakens (2022). Sample size justification. *Collabra: Psychology, 8*(1), 33267. doi:10.1525/collabra.33267（著者の公開版） | `9346742b…ceca2648` 一致 | `round-1\tmp\sources\lakens2022.txt` |
| Wicherts et al. (2016). *Frontiers in Psychology, 7*, 1832. doi:10.3389/fpsyg.2016.01832 | `26d1f9f6…46bb` 一致 | `round-1\tmp\sources\wicherts2016.txt` |
| Koo & Li (2016). *Journal of Chiropractic Medicine, 15*(2), 155–163. doi:10.1016/j.jcm.2016.02.012（PubMed Central の HTML） | `dd4ff493…b2292` 一致 | `round-1\tmp\sources\koo2016.txt` |

## 3 つの立場が違う角度であること

round 1 と同じ（R1 計測の道具の妥当性・R2 指標を使う側と公開の安全・R3 推論の固定と統計）。

## round 2 で新しく取得したもの

- 投稿規程だけ（`round-2\tmp\raw\brm-guidelines.html`・SHA-256 `c61c2450…2eacf2`・テキスト `round-2\tmp\sources\brm-guidelines.txt`）。照合の結果は `context-A.md`。査読者役には規程の本文を渡さず、context-A の抜粋だけを渡す（round 1 と同じ）。
