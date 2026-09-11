# data.md — 入力データの来歴

⚠️★★★ **本実験は GSE のデータを 1 行も使わない。** 入力は外部の公開データ [P321] だけである。
→ `docs/experiment-tracking.md` の「gse-dataset の commit hash で固定」は
**figshare のデータセット版 ＋ ファイルの SHA-256** に読み替える (→ `notes.md` §5)。

## 1. 出典

| | |
|---|---|
| 文献 | **[P321]** Alaboudi, A. & LaToza, T. D. — *An Exploratory Study of Debugging Episodes* |
| 版 | **arXiv:2105.02162v1** (2021)。⚠️ 査読掲載状況は未確認 (`docs/references.md` と同じ留保) |
| ライセンス | **CC BY 4.0** (figshare の item ページに表示) |
| データ | figshare **article 14068802** / **file 26553647** `replication_package_FSE2021.zip` (178.03 kB) |
| private link | `https://figshare.com/s/6c4026a941db49ea3de3` (★ **論文 PDF の脚注 4 に逐語で記載されていることを一次で確認済み** —— arXiv:2105.02162v1 を pypdf で抽出し `4https://figshare.com/s/6c4026a941db49ea3de3` を確認。★ 私信リンクではなく**著者が論文に公開したリンク**である。2026-09-06 時点で **有効**) |
| item 表題 | "What is debugging replication package" |

### 中身

| ファイル | サイズ | SHA-256 |
|---|---|---|
| `replication_package_FSE2021.zip` | 182,303 B | `6f506cba88ef30a7027b367967a6d92628c84e90d80b4a1a343190e1083d04b2` |
| `replication_package_FSE2021/rowData.json` | 2,306,479 B | `497df0b4da398c39cc0fd8b28544d4ac1d61c728708f4f9cdaa32469acda78b9` |
| `replication_package_FSE2021/codingBookFSE2021.pdf` | 63,231 B | `0a1cc4cbe9224fff87c8a4bc85bfa7eeee4052203e5df578d2ef124cfd35a197` |
| `replication_package_FSE2021/Observe-devOnlineDataSetLink.txt` | 81 B | (★ 下記 §3 の死んだ URL が 1 行入っているだけ) |

`rowData.json` の形: **15 セッション**の配列。各セッションは
`videoLength` / `programmingLanguage` / `githubURL` 等のメタと `annotations`
(トップ = `Debugging` / `Development` / `Irrelevant`、その下に `subAnnotations` = 活動) を持つ。
コードブックの回答は `description` に **`DF1`..`DF11` / `U1`..`U8` / `O1`..`O7` / `OT1`..`OT5` / `IF1`..`IF5`**
という接頭辞つきの平文で埋め込まれている。

## 2. ★ 取得手順 (★ 再現時はこの通りにする)

⚠️★★★ **`curl` / `wget` では取れない。** 2026-09-06 に実測した結果:

| 経路 | 結果 |
|---|---|
| `curl https://figshare.com/s/6c4026a941db49ea3de3` | **HTTP 202 / 0 バイト** (bot チャレンジ) |
| `curl https://figshare.com/ndownloader/files/26553647?private_link=…` | **HTTP 403** |
| `curl https://ndownloader.figshare.com/files/26553647?private_link=…` | **HTTP 202 / 0 バイト** |
| `GET https://api.figshare.com/v2/articles/14068802` | `{"message":"Entity not found: ArticleVersion"}` (★ private のため公開 API に出ない) |
| `POST https://api.figshare.com/v2/articles/search` (表題 / 著者名) | **0 件** (★ private link の item は検索索引に出ない) |
| ★ **実ブラウザ (Chrome)** で `https://figshare.com/s/6c4026a941db49ea3de3` → ダウンロード | ★ **成功** |

→ ★ **取得手順**:

1. ブラウザで `https://figshare.com/s/6c4026a941db49ea3de3` を開く
   (⚠️ チャレンジの解決に数秒かかる。表題が "What is debugging replication package" になれば成功)
2. `replication_package_FSE2021.zip` をダウンロードする
3. `experiments/20260906-p321-resumption-baseline/raw/` に置く
4. `bash run.sh` を実行する (★ Step 0' が SHA-256 を照合し、違えば止まる)

⚠️★★★ **`raw/` は `.gitignore` の `experiments/**/raw/` で塞がれている。**
★ 生データは repo にコミットしない (`docs/agent-shared.md` / `data-privacy`)。
⚠️ 本データは CC BY の公開データだが、**`githubURL` / `videoId` / `developerGithubURL` という
個人に辿れる列を含む**ので、集計値だけを `results/` に置く方針は変えない。
★ `results/metrics.json` に URL・動画 ID・セッション名が入っていないことを検査済み (2026-09-06)。

## 3. ⚠️★★★ もう一方の配布元は **消滅している**

★ 論文 脚注 5 / 脚注 7 と `Observe-devOnlineDataSetLink.txt` が案内する
`https://observe-dev.online/dataset/…` は **到達不能**である (2026-09-06 実測):

| 検査 | 結果 |
|---|---|
| ローカル resolver (`nslookup observe-dev.online`) | **Non-existent domain** |
| Cloudflare DoH (`cloudflare-dns.com/dns-query`) | **Status 3 = NXDOMAIN** |
| bit.ly 短縮 (`3kkbL2W` / `3qWdMVA`) | 301 で当該ホストへ → 解決不能 |

→ ★ **論文本体が案内する 2 経路のうち 1 つは既に死んでいる。**
★ Wayback には 2022-10-11 のスナップショットが残るが、**Next.js アプリの外殻であって
データ本体ではない**。→ ★ **figshare の replication package が唯一の生存経路**である。
⚠️ **その figshare も private link 1 本に依存している** (★ 公開 API にも検索にも出ない)
ので、★ **本実験は zip の SHA-256 を来歴として刻んだ上で、`raw/` に現物を保持する**。

## 4. 被験者・対象

★ 論文 §3: 職業開発者 **11 名 / 15 セッション / 約 30 時間**の Twitch / YouTube 配信。
⚠️ **セッション < 2 時間の場合は同じ開発者の別セッションを追加**しているため、
★ **セッションは開発者に対して独立ではない** (→ `notes.md` §4 のクラスタ注意)。
⚠️ OS / 言語 / ツールはセッションごとにばらばら (JavaScript ほか)。
