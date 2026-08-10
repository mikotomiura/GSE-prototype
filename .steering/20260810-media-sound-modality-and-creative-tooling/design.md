# 設計: 制作ツールと Claude Code の連携（試作・デザイン探索専用）

> ⚠️ **本タスクはアイディア段階である**（`requirement.md` §本タスクの温度）。
> 本ファイルが確定させるのは **「実機で何ができるか」** までであり、
> **何を作るかは確定させない。**

## 0. 原則（これだけは先に固定する）

1. **GSE 本体（Rust / Tauri）を変更しない。** 試作は既存の出力を**読むだけ**。
2. **`data-privacy` の外部送信境界を増やさない。**
   → **第 1 歩に OSC / WebSocket を実装しない。** 既にある `gse-replay` の出力を
     ファイル経由で渡す（オフライン）。ライブ連携が本当に要るとわかってから足す。
3. **被験者に配る成果物に TouchDesigner を含めない。**
   ライセンス・GPU 負荷・起動運用・再現性の要件が跳ね上がるため（`requirement.md` スコープ外）。
4. **キーストローク内容・NDJSON 生ログを制作ツールへ渡さない**
   （`docs/development-guidelines.md §10` / `data-privacy` Skill）。
   → 渡してよいのは **`FeatSnapshot`（content-free な集約値）**のみ。

---

## 1. 実機で確認した事実（2026-08-10・この Windows 機で実行して確認）

### 1.1 入手できる信号

`src-tauri/src/analysis/loop_step.rs:134` の `FeatSnapshot`（**1Hz**・content-free）:

```
timestamp / f1 / f3 / f4 / f5 / f6 / p_flow / p_inc / p_stuck
         / raw_x / raw_y / ewma_x / ewma_y / obs / alpha
```

取り出し口は既存の CLI（`src-tauri/src/bin/replay.rs`。**新規実装は不要**）:

```bash
cd src-tauri   # ★ Cargo.toml は repo 直下に無い
cargo run --bin gse-replay -- ../tests/fixtures/minimal.ndjson --snapshot out.json
```

`--snapshot / --metrics / --json / --segment / --segments / --intervention /
--calibration / --sweep / --nudge-diag / --corr-floor` を確認済み（モード系は相互排他）。

> ★ **これが「表現の実験台」に必要なものの全部である。**
> 表現側は `p_stuck` と `ewma_x/ewma_y` の**時系列を再生するだけ**でよく、
> GSE 本体にフックを足す必要がない。

### 1.2 各ツールの CLI 入口（★ 全て実行して存在を確認済み）

| ツール | バージョン | Claude Code から叩ける入口 | 確認方法 |
|---|---|---|---|
| **TouchDesigner** | 2025.33070 | ★★ **`toeexpand.exe` / `toecollapse.exe`** | `toeexpand.exe` を実行しヘルプを取得 |
| TouchDesigner | 同上 | 同梱 **`python.exe` = 3.11.15** | `python.exe -c "import sys; print(sys.version)"` |
| TouchDesigner | 同上 | `TouchDesigner.exe` / `TouchPlayer.exe` / `TouchEngine.exe` | `bin/` の実体を確認 |
| **Substance 3D Designer** | — | ★★ **`sbsrender.exe`**（`info` / `render`）・`sbscooker.exe`・`substance3d_baker.exe` | `sbsrender.exe --help` を実行 |
| **After Effects 2026** | — | ★ **`aerender.exe`** | `Support Files/aerender.exe` の実体を確認 |
| **Blender** | 5.1 | `blender.exe`（`-b -P script.py`） | 実体を確認 |
| **Cinema 4D 2026** | — | **`c4dpy.exe`**（Python API）・`Commandline.exe` | 実体を確認 |
| **Adobe Audition 2026** | — | ⚠️ **CLI は無い**（GUI `Adobe Audition.exe` のみ） | `*.exe` を列挙して確認 |
| **Media Encoder 2026** | — | ⚠️ **CLI は確認できず**（GUI のみ） | 同上 |

⚠️ **未確認**: Media Encoder の watch folder 機構は**実機で試していない**ので当てにしない。

### 1.3 ★ 最重要の発見: `toeexpand` が TouchDesigner を Claude Code の射程に入れる

TouchDesigner のプロジェクト（`.toe` / コンポーネント `.tox`）は**バイナリ**であり、
そのままでは Claude Code が読めず、git diff もレビューもできない。

`toeexpand.exe` の**逐語ヘルプ**:

> "will expand a toe or tox file into a directory structure that can then be
> **edited using standard tools**, then collapsed back into a regular file using toecollapse."

→ ★★ **これがあるので、TD パッチを「Claude Code が書き・git が差分を取り・レビューできる対象」にできる。**
  この 1 点が無ければ TD は本プロジェクトの作業プロトコル
  （`.steering/` 記録・`/review-changes`・`/cross-review`）に載らない。

⚠️ **未検証**: 展開されたツリーの**可読性の程度**と、`toecollapse` の往復で
**情報が失われないか**は実際に往復させて確かめていない。**第 1 歩の検証項目にする**（§3）。

### 1.4 Python 環境

- システム: **CPython 3.11.9**（`py -0p`）＋ **uv 管理の CPython 3.11.15**
- TouchDesigner 同梱: **CPython 3.11.15**
- → ★ **uv 側と TD 側のマイナー/パッチ版が一致**するため、同じ wheel が使える見込み。
- 現状インストール済みは **`duckdb` のみ**。`numpy` / `scipy` / `soundfile` / `python-osc` は**未導入**。
  ⚠️ 導入は**別の判断**（`duckdb` が解析専用 dev 依存として入っているのと同じ扱いにするか要検討）。

---

## 2. 何にどのツールを使うか（★ 選択肢。決定ではない）

`.idea/20260810-media-expression-sound-and-prototyping.md` の未決事項に対応させる。

| 試したいこと | 向くツール | 理由 |
|---|---|---|
| **段 0→1→2 の見え方を比べる**（[P54] の change blind / make aware） | ★ **TouchDesigner** | 1Hz の時系列を食わせてパラメータをライブに動かせる。**候補を並べて同時に見る**のが本来の用途 |
| **「今日の思考の地形」の造形**（第 2 版 §4.1 の媒体 B 主案） | ★ **Substance 3D Designer**（`sbsrender` バッチ） | ノードグラフのパラメータを振って **N 案を CLI で一括生成**できる＝Claude Code が回せる |
| 地形の立体化・レンダ | Blender / C4D / Stager | `blender -b -P` と `c4dpy` で完全にスクリプト化できる |
| **比較用の動画・図版** | After Effects（`aerender`） | バッチレンダのみ。**探索には使わない**（重い） |
| **音の候補を作る** | ⚠️ **Python で WAV を生成**（Audition ではない） | Audition に CLI が無いため。§3 の演繹パラメータ（単発・低 F0・緩やかなアタック・整数次倍音）は**数式で書ける** |
| 音を**聴いて判断する**・スペクトルを見る | **Audition**（手作業） | ここは自動化しない。人が聴く工程として残す |

> ⚠️★★ **音の試作は「作れる」が「入れると決めた」ではない。**
> `docs/literature/20260810-*.md` の gate 判定は **「音は第 1 版に入れない」を維持**している。
> 作るのは**判断材料**（聴き比べて初めて分かることがある）としてであり、採用の前倒しではない。

---

## 3. 第 1 歩の候補（★ 実施は未定・ユーザー判断待ち）

最小で、かつ **§1.3 の未検証点を潰せる**もの。

```text
Step 1  toeexpand / toecollapse を空の .toe で往復させ、
        (a) ツリーがテキストとして読めるか (b) 往復で壊れないか を確認する
          → ここが通らなければ TD は Claude Code から扱えない。以降は全部やめる

Step 2  gse-replay --snapshot の出力を TD の Table DAT が読める形（CSV）に変換する
        小さな Python スクリプト（依存: 標準ライブラリのみ）

Step 3  同じ 1Hz 信号を 2〜3 通りの表現に同時に流す TD パッチを 1 枚だけ作る
          → 「候補を並べて見比べる」という第 2 版 §4.1 の方針をそのまま実体化する
```

⚠️ Step 3 まで行っても **決めるのは人**である。本タスクは選択肢を作るところまで。

### 置き場所の案（未決）

- `experiments/` は `reproducibility-discipline` の規約（seed / lockfile / HMM_VERSION 固定）が
  かかるため、**探索的な試作を置く場所としては重い**。
- → **`.idea/prototypes/` か、リポジトリ外**が妥当か。**要判断。**
  ⚠️ `.idea/` は現状 git 管理外（`git ls-files .idea` が空）である点に注意。

---

## 4. やらないこと（この設計で明示的に閉じる）

- **GSE 本体への OSC / WebSocket 送出の実装**（§0-2。必要性が確認されるまで着手しない）
- **被験者環境への TouchDesigner 配備**
- **NDJSON 生ログ・キーストローク内容の制作ツールへの受け渡し**
- **Media Encoder / Audition の自動化**（CLI が無い・未確認）
- **`experiments/` 配下への試作の設置**（再現性規約の対象を増やさない）

## 4.5 ★ 実施後に判明したこと（2026-08-10・セッション終了時に追記）

### 4.5.1 サーヴェイが 1 ラウンドで終わらず 5 ラウンドになった

当初の想定は「聴覚モダリティを 1 ラウンド」だったが、研究者からの明確化が入るたびに
**判定が変わる**ため追補を重ねた。**追補 2 では本編の結論を訂正している。**

| ラウンド | 何を判定したか | 新規登録 |
|---|---|---|
| 本編 | 「気づかせるための音」（警告・マーカー・サリエンス階段） | P54–P63 / V79–V80 |
| 追補 2 | ★ **ドローンは別カテゴリ**（ISE の条件は変化でなく**分節**）＝**本編カード4 を訂正** | P64–P69 |
| 追補 3 | 最大の空白（ドローン直接の ISE 実験）を埋める | P70–P74 |
| 追補 4 | 表現層は単独で立つか / 身体的回帰との連動 | P75–P76 |
| 追補 5 | 歩行を計測して MhD に入れるか | P77 |

⚠️ **文献カードの本編だけを引用してはならない**（冒頭に警告を入れた）。

### 4.5.2 ★★ `.idea` の他メモを読まずに書いて片手落ちになった（再発防止）

追補 5 の初稿で **「MhD はキーストローク由来だから触るな」**と断定したが、
`.idea/20260801-architecture-signal-and-online-learning.md` が**実測で反対のこと**を示していた
（§1.1 X 軸は主観摩擦を予測できていない・§2-4 詰まりは「打鍵しないこと」に現れる可能性）。

→ **再発防止**: `.idea/` は 1 ファイルではなく**複数の設計メモ群**である。
  設計判断に触れる前に **`.idea/` 全体の見出しを走査する**こと（本タスクの引き継ぎ §8 に記載済み）。

### 4.5.3 ★ 成果物の一部は git に入らない

**`.gitignore:40` が `.idea/*.md` を除外している**（`e03c02f chore(gitignore): .idea 配下の個人用 md を無視する`）。
→ ★★ **`.idea/20260810-media-expression-sound-and-prototyping.md`（726 行）はコミットされない。**
  **本タスクの設計判断の本体は `docs/literature/` と `.steering/decisions.md` 側に写してある**ので
  リポジトリ上で追跡は可能だが、**`.idea` のメモは研究者のローカルにのみ存在する**点に注意。
  ⚠️ **これは既存の意図的な設定であり、本タスクでは変更しない。**

### 4.5.4 §3 の Step 1（`toeexpand` 往復検証）は未実施

本タスクはサーヴェイと設計判断で予算を使い切ったため、**TouchDesigner の実地検証に入っていない**。
→ 引き継ぎ `.steering/_handoff/next-session-prompt-media-expression-layer.md` §4 に移した。

## 5. テスト戦略

本タスクは**コードを書かない**（Step 1–3 に進む場合のみ以下）:

- Step 1 の往復検証は **`.steering/` に実測ログを残す**（`verify-before-claiming`）
- Step 2 のスクリプトを書く場合、既存の `gse-replay --snapshot` の出力を入力にするので
  **`tests/fixtures/minimal.ndjson` のゴールデンがそのまま回帰入力になる**
- ★ **GSE 本体に触らないので `cargo test --workspace` / snapshot 回帰への影響はゼロ**
  （影響が出る変更をしたら、それはスコープ逸脱である）
