# 次セッション開始プロンプト — メディア表現の試作（Step 0 から作りながら考える）

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-10〜11 に (i) 音・表現層の未決 10 問を閉じ、(ii) インパクト／認知の核の全体地図を作り、
(iii) **2026-08-11 に方針を α（常時リアルタイム）へ転換**した。**コードは 1 行も変更していない。**
このセッションは**その続き**であり、**前セッションの文脈を持ち込まない**
（引き継ぎファイルだけを読んで成立するかの検査でもある）。

---

===

## §0 このセッションでやること

**手を動かす。** 紙の上の議論は前セッションで終わっている。

> **Step 0（`toeexpand` / `toecollapse` の往復検証）から始め、実際に作りながら考える。**

⚠️★★ **Step 0 は「安く畳むための関門」である。** ここが通らなければ TouchDesigner は
Claude Code から扱えず（`.toe` はバイナリで git diff もレビューも不可）、**表現層トラック全体を早期に畳める**。
**通らなかったら以降は全部やめる**——これは失敗ではなく設計どおりの結果である。

⚠️★★★ **MhD（推論層）の設計議論はしない**（研究者指示・2026-08-11）。
`p_stuck` / `ewma_x` / `ewma_y` は**入力として使うだけ**にする。軸の再定義・オンライン学習・
潜在状態の話に**引きずられないこと**。

## §1 最初に読むもの（この順で・すべて git 追跡下）

1. `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` ← ★ **本体。ここが仕様**
2. `.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md` の
   ★★ **D21 を D13 より先に読む**（**D13 は改訂済み**。D21 を読まずに D13 を引用しないこと）
3. `.steering/20260810-media-sound-modality-and-creative-tooling/design.md` §1（**実機で確認済みの CLI 事実**）・§3（Step 1–3）
4. `.steering/20260811-impact-and-cognitive-core-map/design.md` §4（**表現層を `p_stuck` の下流に置かない・系統 A/B**）

必要になったら:

- `docs/literature/20260810-auditory-modality-and-aesthetic-sensitivity.md`
  （⚠️★★ **本編だけを引用しない。追補 2 が本編カード4 を誤りとして訂正している**——
  ISE の条件は**変化ではなく分節（segmentation）**）
- `.steering/20260811-impact-and-cognitive-core-map/improvement-ideas.md` §1（リアルタイム性の整理）

> ⚠️ `.idea/*.md` は **`.gitignore:40` により git 管理外**（研究者のローカルにのみ存在）。
> ★ ただし**除外されるのは `.idea/` 直下の `.md` だけ**である（`git check-ignore` で実測）。
> **本セッションに必要な情報はすべて上記 1〜4（追跡下）に写してあるので、`.idea` が無くても成立する。**

## §2 前提として確定していること（もう議論しなくてよい）

| # | 確定事項 | 記録 |
|---|---|---|
| 1 | ★★ **常時リアルタイム（α）で作る**。視覚も聴覚も。β はセッション後の**比較条件として残すだけ** | D21 |
| 2 | ★ **α は「安全と分かったから」ではない**——判定は**「判定不能に近い引き分け」**。**引き受けて自分で測る** | D21 |
| 3 | **媒体は画面内**（既存 `src/components/Overlay.tsx`）。**ハードウェア調達はしない** | D17 |
| 4 | **3 状態（Flow/Incubation/Stuck）を非評価的な 3 語彙へ**（流れ／拡散／滞留）。★ 実測で **Incubation が最頻の予測クラス（42.2%）** | D16 |
| 5 | ★★ **ユーザーが止められること／音量を変えられることは必須要件**（交渉不可） | D3d / [P71] |
| 6 | **主観指標だけで go を出さない**（「主観は動くが客観は動かない」形が **3 例**ある） | D3f |
| 7 | **試作は `experiments/` 配下**（`reproducibility-discipline` を背負う。★ **SEED 固定が特に効く**——グラニュラー合成は乱数を使う） | D18 |
| 8 | **表現層だけにして Physical Anchor を外すのは不可** | D8 |
| 9 | **歩行は量を測らない・MhD に入れない**（有無のみ・表現層で合流） | D10 / D11 |

## §3 ★ Step 0 の具体手順（実機のパスは確認済み・そのまま叩ける）

```bash
# ★ 実体は確認済み（2026-08-11 実測）
TOEEXPAND="/c/Program Files/Derivative/TouchDesigner/bin/toeexpand.exe"
TOECOLLAPSE="/c/Program Files/Derivative/TouchDesigner/bin/toecollapse.exe"

# ★ 空プロジェクトのテンプレートが同梱されている（GUI で作らなくてよい）
TEMPLATE="/c/Program Files/Derivative/TouchDesigner/Samples/Setup/Base/NewProject.toe"
```

**検証すること 2 つ**（`design.md` §1.3 の未検証点）:

1. **(a) 展開されたツリーがテキストとして読めるか**（Claude Code が編集できる形か）
2. **(b) 往復（expand → collapse）で情報が失われないか**

**手順の骨子**:

```text
1. 作業用ディレクトリへ NewProject.toe をコピーする（★ Program Files 内で作業しない）
2. toeexpand で展開 → ディレクトリ構造とファイルの中身を見る
     - テキストか / 何が読めるか / バイナリが混ざるか
3. toecollapse で戻す
4. ★ 元の .toe と往復後の .toe を byte 比較する（cmp / sha256）
     ⚠️ ★ byte-equal にならなくても直ちに失格ではない（タイムスタンプ等が入りうる）。
        その場合は「何が変わったか」を展開後のツリー同士で比較して判定する
5. ★ .tox（795 本同梱）でも 1 本試す — .toe と .tox で挙動が違う可能性があるため
```

⚠️★★ **`toeexpand` は引数なしで usage を出して `exit 0` を返す**（実測）。
→ **「exit 0 なら成功」という判定を書かない**（`verify-before-claiming` ルール 5b の実例そのもの）。
**出力の中身を見て判定すること。**

⚠️ **実測ログを `.steering/` に残す**（`verify-before-claiming`）。
★ **Step 0 は「実験」ではなく「実機の事実確認」なので `experiments/` を起こさない**
（`design.md` §5 がそう書いている）。`experiments/` を起こすのは **Step 3 以降**。

## §4 Step 0 が通ったら（順に）

```text
Step 1  gse-replay --snapshot の出力を CSV 化（依存は標準ライブラリのみ）
          cd src-tauri
          cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot out.json
          ⚠️ ★ パスは `tests/fixtures/`（`../` を付けない）。Cargo.toml は repo 直下に無い

Step 2  ★★ 表現層の平滑化を先に実装する（時定数 ≥60 秒）
          → 1Hz の離散サンプルをそのまま音量/密度に当てると
            毎秒の段差が振幅のオンセットになり、オンセットが分節を作る [P64]＝ISE の条件そのもの
          ⚠️ 既存のヒステリシスは ≈2.5 秒（engine.rs:113 に「~2.5s time-constant」と逐語）で不足

Step 3  層 0（基層）だけを鳴らす。★ 状態に応答させない
          55–110 Hz 帯 ＋ 整数次倍音のみ／非調和成分ゼロ
          → 「ずっと鳴っていて気にならないか」を先に確かめる（[P71] のオフスイッチ要件も同時に試す）
          ⚠️ ここを飛ばすと、不快の原因が基層なのかマッピングなのか切り分けられなくなる

Step 4  層 2（粒子）を足す。★ 粒子率は 100 grains/s 以上を維持
          → 系統 A（p_*/ewma_*）と系統 B（keys 密度・沈黙長・BS 率）の両方を流して聴き比べる

Step 5  層 1（うねり）・層 3（空間）を足す

Step 6  ★ Python で変調スペクトルを計算し、4 Hz 付近にエネルギーが無いことを機械検算

Step 7  気に入った設定を JSON に書き出し、EXPR_VERSION を刻んで凍結する
```

**Python 環境（実測）**: TD 同梱 **3.11.15** / uv 側 **3.11.15**（一致）/ システム 3.11.9。
⚠️ **`numpy` / `scipy` / `soundfile` は未導入**。導入は別判断（`duckdb` が解析専用 dev 依存で入っているのと同じ扱いにするか要検討）。

## §5 ⚠️★ 落とし穴（同じ失敗を繰り返さない）

1. ⚠️★★★ **「波」の周波数を間違えると最悪の帯域に乗る**——**4 Hz 付近が最悪**
   （fluctuation strength のピークであり、**ISE を 70 例中 63 例予測した予測子**）。15–70 Hz も避ける。
   **状態の波は 0.001–0.02 Hz（分〜十分オーダー）＝禁止帯の 2〜3 桁下**に置く。
   ★ 書き方は「緩慢だから安全」ではなく「**禁止帯から離れているから安全**」。
2. ⚠️★★★ **本当の危険は変調周波数ではなくステップである**（Step 2 を飛ばさない）。
3. ⚠️★★ **文献カードの本編だけを引用しない。** 追補 2 が本編カード4 を**誤りとして訂正**している。
4. ⚠️★★ **「リアルタイムに適応する表現」と「リアルタイムに調整する開発者」は別物**。
   試作中は動かしてよいが、**pilot 実施中にマッピングを動かすと因果識別が壊れる**
   （ADR-008 D4 / prequential [V64] / 適応的デザインの事前規定 [V65]）。
5. ⚠️ **`.toe` / `.tox` をバイナリのままコミットしない**（D6）。展開後のツリーを置く。
6. ⚠️ **GSE 本体（Rust）を変更しない。OSC / WebSocket を実装しない**
   （`data-privacy` の外部送信境界を増やさない）。既存の `gse-replay --snapshot` で足りることは確認済み。
7. ⚠️ **凍結対象に触れない**: `docs/preregistration-v0.3.md` / `engine.rs` / `probe_scheduler.rs` /
   `schema_dto.rs` / `App.tsx` の argumentative lock。
8. ⚠️ **`docs/references.md` は append-only。次番号は P78 / V81**。既存番号を再利用しない。
   ★ **本セッションは新規文献を登録しない見込み**（試作なので）。
9. ⚠️ **Bash のヒアドキュメントが過去に 2 回失敗している**。
   長い多行テキストは **`Write` ツールで一時ファイルに書いてから**実行する。
10. ⚠️ **`cd src-tauri` してから `cargo` を叩く**（`Cargo.toml` は repo 直下に無い）。
11. ⚠️ **Program Files 内で作業しない**（権限・汚染）。作業用ディレクトリへコピーしてから触る。

## §6 ⚠️ 未処理のまま残っているもの（本件と無関係だが放置されている）

- **未コミットが 7 件ある**（`.steering/` の 2 タスク分 ＋ `.codex/budget.json`）。
  ★ **セッション開始時にコミットするか研究者に確認する**。
- **タグ `v0.1.21` がローカル `a26eafa` / リモート `90d86d2` で食い違う**（fetch が reject される）。
  → **破壊的操作なので研究者の指示待ち。**
- ローカル stash 1 件（`win-local: gitignore tmp_codex rule + budget.json`）と未追跡の空ファイル `MEMO`。

## §7 ★ やり残し（試作と並行して効いてくる順）

1. ★★ **`legato-music` を steady-state の例とする記述の一次逐語**——
   **`media-expression-spec.md` §2 の設計制約はこの 1 点に依存している**（現状は二次記述水準）。
2. ★★ **[P65] の "(non-)disturbance impact 過大評価" の向き**——
   **設計目標を fluctuation strength に置いてよいかがここで決まる**。
3. ★★ **ドローン ON/OFF を独立変数にした自前の測定**（**文献では埋まらない空白**）。
   ★ **骨格は G1 の設計をそのまま流用できる**（copy positive control / 1 ブロック = 1 セッション /
   5 分・位置固定＋無作為化 / 最小打鍵ゲート）。⚠️ **G1 は事前登録が凍結済みなので別実験として設計する**。
   ⚠️★★ **G1 の現況（2026-08-11・origin/main）**: **確証標本 n=3 で凍結済み**（`d3caebd`）・
   **P010 が確証標本の 1 人目として実施済み**・pilot 済み → **残り 2 名**。
   ★ **`analyze.py` は一度も判定を出していないので結果はまだ無い**（＝「未実施」ではなく「判定前」）。
   ⚠️ **`experiments/20260801-controlled-friction-task/README.md §0` は「データ 1 件も無い」「n 未凍結」のままで
   `notes.md` と食い違っている。README §0 だけを読んで現況を判断しないこと。**
   ⚠️ G1 が自ら「最も重要な弱点」と書いた**検定の到達可能性**（C(8,4)=70 の離散性で
   **主判定が事実上 AUC≈1.0 を要求**）は、**ブロック数を設計する段階で逆算して回避する**。
4. **日本語版 soundscape の調整角** [V79]（**音を測定に使うなら前提条件**。設計語彙としてなら可）。
5. **「Incubation は肯定的に読める」「滞留は悪ではない」は未検証の想定**
   → pilot に**自由記述 1 問**を足して読み取りを確認する。
6. **粒子率 100 grains/s の下限は文献の数値ではなく [P64] の分節原理からの演繹**。**聴いて確かめる**。

## §8 セッション開始時の作法（CLAUDE.md）

- **実装に入るので `/start-task` を先に実行する**（`.steering/[YYYYMMDD]-[task-name]/` を作る）。
  ★ 本件は**新規タスク**として起票してよい（例: `20260812-expression-prototype-step0`）。
- **該当 Skill を Read してから手を動かす**——本件は
  `reproducibility-discipline`（★ `experiments/` を起こす時。**Step 0 では不要**）/
  `verify-before-claiming`（★ **事実を断定する前に必ず**）/ `data-privacy`（外部送信境界）/
  `git-workflow`（コミット時）。
- **`docs/` を先読みしてからコードを読む。闇雲に探索しない。**
- ★ **事実を断定する前に `verify-before-claiming` を必ず参照する**。
  過去 2 セッションで **`.idea` を読まずに断定して片手落ち**・**既に事前登録済みの案を「新案」として出しかけた**
  という失敗が起きている。**一次資料まで降りること。**
- **タスク完了時は `/finish-task`**（Step 3 で schema parity check が走る）。
  ★ **`/cross-review` は各タスク完了時に必須**。
  ⚠️ **未追跡ファイルは `git diff` に写らない**ので、レビュー前に **`git add -N`** で可視化する
  （過去に主成果物がレビューから漏れかけた）。
