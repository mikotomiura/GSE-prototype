# 次セッション開始プロンプト — G1 パイロット P-1 を実施し、その結果を受けて確証標本の n を凍結する

このファイルの「===」以下をコピペして開始する。

**前提**: 実施準備は**すべて終わっている**。事前登録は **第 5 版で凍結**、`bash run.sh` は GREEN、
PR #84 は main にマージ済み（`7e01edc`）、リリースタグ **`v0.1.22`** を打って CI ビルド済み。
⚠️ **データは依然 1 件も無い。**
本セッションは **P-1 を実際に回し、その結果を記録する**。
⚠️ **`preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` を変更しない。**

---

===

## §0 このセッションの位置づけ

**パイロット P-1 を実施し、結果を記録して、確証標本の n を凍結するところまで。**

前ラウンド（`.steering/20260803-g1-pilot-readiness/`）で**実施を止めていた blocker は全部消えた**。
★ **もう「準備」は要らない。次は実際に回す回である。**

### ★★ §0-A 決着済み（やり直さない・再検討しない）

| # | 何 | 決着 |
|---|---|---|
| **B-1** | アプリ内プローブが G1 ブロック中に発火する | ✅ **kill switch 実装済み**（第 5 版 `§5.4`）。実施時は `GSE_DISABLE_PROBES=1` |
| **B-2** | 操作チェックはどの分母でも 1 問しか外せない | ✅ **判定の封印**（第 4 版 `§5.3`）。⚠️ `--unseal` を使わないこと |
| **B-3** | ブロックの区切り方 | ✅ **現行どおり**（1 回の来所で 10 ブロック通し） |
| **B-5** | 被験者の入力先が未指定だった | ✅ **`writing-pad.html` に固定**（第 5 版 `§2.11`） |
| **P-ID** | Phase1 と分けるか | ✅ ★ **共有する**（同じ人＝同じ ID）。採番元は **Phase1 のロスターただ 1 つ** |
| **アンケート** | 終了後アンケートを取るか | ✅ **取る。ただし判定には使わない**（第 5 版 `§2.10`・取る前に宣言済み） |
| **実施端末** | Windows / macOS | ✅ **両対応**。⚠️ macOS は `ime_dwell_med` が構造的に欠測し**実質 13 特徴**（`§5.1`） |

⚠️ ★ **これらを「再検討」しないこと。** 判断の根拠は
`.steering/20260803-g1-pilot-readiness/decisions.md`（F-1〜F-8）にある。

---

## §1 実施前にやること（研究者の実務・順番どおり）

### T-1 ビルド成果物を実施端末に入れる

- **`v0.1.22`** の Release から取る。**9 アセットすべて公開済み**:
  - Windows: `gse-next_0.1.22_x64-setup.exe` / `gse-next.exe` / `gse-package.exe` / `gse-submit.exe` / `gse-unpack.exe`
  - macOS: `gse-next_0.1.22_aarch64.dmg` / `gse-package` / `gse-submit` / `gse-unpack`
- ★ **CI が作った本番バイナリを使う**（開発ビルドで回さない）。
- ⚠️ **10 セッションは同一バイナリで回す**（`protocol.md §6.1`）。

> ### ⚠️ `v0.1.22` のビルドで起きたこと（次にタグを打つ人向け・**対処済み**）
>
> `build-macos` が **failure** になったが、★ **ビルド自体は完全に成功していた**
> （ジョブ全体で `##[error]` は 0 件。dmg も tools もアップロード済み）。
> 失敗したのは後片付けの `Post Run Swatinem/rust-cache@v2` だけで、
> `Failed to save: Unable to reserve cache with key ...` が job を failure にし、
> `release` ジョブの macOS ダウンロード段（`needs.build-macos.result == 'success'`）が
> 弾かれて **dmg がリリースから落ちた**。
> → 成果物は手動で `gh release upload` して補完済み。
> → ★ **再発防止**: タグビルドでは `save-if: ${{ !startsWith(github.ref, 'refs/tags/v') }}` で
>   **キャッシュを保存しない**ようにした（復元はするのでビルド時間は不変）。
>   ⚠️ release 側のゲートは**緩めていない** — 緩めると「本当にビルドが壊れたとき」に
>   部分的なリリースを黙って公開してしまうため。

### T-2 ★★ `GSE_DISABLE_PROBES=1` を起動手段に固定する

```bash
# macOS
GSE_DISABLE_PROBES=1 open -a GSE
# Windows (PowerShell)
$env:GSE_DISABLE_PROBES=1; Start-Process "GSE.exe"
```

- ★ **1 ブロック = 1 セッションなのでアプリを 10 回起動する。毎回必要。**
  **ショートカット / launcher / シェルプロファイルに固定する。手打ちにすると 10 回のうち 1 回抜ける。**
- 起動時のログに `probe scheduler DISABLED by GSE_DISABLE_PROBES=1` が出ることを 1 回確認する。
- ⚠️ **本当の確認は実施後**（`validate_blocks.py --dataset` が `probe_assignment` 行 0 を検査する）。

### T-3 Apps Script で `setupG1Forms()` を実行する

- `Form_G1/GSE_G1_Form_Builder.gs` を Apps Script に貼って実行 → 3 フォーム ＋ 管理シートができる。
  **フォーム ID は記入済み**（form1=同意 / form2=強制比較 / form3=終了後）。
- ★ 実行後、**回答 URL を実施端末にブックマーク**する。
- ⚠️ **紙のバックアップを必ず持参する**（`protocol.md §3.1` の様式・`handouts/G1_説明・同意文書.docx`）。
- （任意）x.gd の短縮は `XGD_API_KEY` を Script Properties に入れれば動く。**G1 では必須ではない。**

### T-4 記入パッドを実施端末に置く

- `experiments/20260801-controlled-friction-task/writing-pad.html` をコピーし、
  ★ **拡張機能なしのブラウザプロファイル**で開けることを確認する（`protocol.md §1.2`）。
- 文字数が出ること・「消去して次のブロックへ」が効くことを 1 回試す。

### T-5 割付を作る

```bash
cd experiments/20260801-controlled-friction-task
python3 assign.py --pilot                    # P-1 は 4 ブロック（copy / LO / HI / copy）
python3 assign.py --pilot --json > blocks/PILOT.json
python3 validate_blocks.py                   # 実施前は「未記入」の note だけが出れば OK
```

⚠️ ★ **P-1 は確証デザインではない**（`§2.8`）。**判定を一切行わない。**
既知の逸脱（同一題材を両条件で出す・C(2,1)=2 で検定不能・強制比較の鎖が成立しない）は宣言済み。

---

## §2 ★★ P-1 の実施（`protocol.md` に従う。ここで逸脱しない）

**P-1 で見るのは 2 点だけ**（`§2.8`）:

1. ★ **5 分ブロックで両条件とも十分な打鍵が出るか**（`§2.9` の適格性ゲート ≥100 打鍵の実効性）
2. **課題文と進行手順が機能するか**

### ⚠️ P-1 で**初めて走る**もの（一度も実行されていない）

- `python3 analyze.py --verify-blocks --dataset ~/gse-dataset --subject PILOT`
- `python3 validate_blocks.py --dataset ~/gse-dataset`

★ **どちらもデータが 1 件も無かったため未実行である。** 出力が壊れていたら、
**その場で解析せず記録だけして持ち帰る**（当日デバッグしない）。

### 実施当日に必ずやること

- [ ] `HMM_VERSION` を刻む（`protocol.md §6.1`：開始前に `env.md`、解析前に `config.json`）
- [ ] 各ブロック: `GSE_DISABLE_PROBES=1` で起動 → 記入パッド → 5:00 → 停止 →
      **文字数と NDJSON 名を記録用紙に転記** → パッドを消去
- [ ] ★ **自己マーカー hotkey（Ctrl/Cmd+Shift+Alt+M）を押さない**（kill switch の対象外）
- [ ] 終了後アンケート（G1-S）に答える
- [ ] ★★ **NDJSON を gse-dataset へ送るとき「G1 のセッション」と明記する**
      ⚠️ **P-ID を Phase1 と共有しているので、ID では Phase1 の較正セッションと区別できない**
      （`data.md` の B-4）。**当日中にやる。後回しにしない。**

---

## §3 P-1 の後にやること

### T-6 ★ 確証標本の n を凍結する（`§2.4`）

- P-1 の結果（資料の量・ブロック長・打鍵の出方）を見てから決める。
- **`config.json` の `n_subjects` に数値を書き、`notes.md` に日付とコミットハッシュを記録する。**
  ⚠️ **時刻は記録しない**（本 repo は一時 public 化の運用がある）。
- ⚠️ ★ **凍結は確証データ 1 件目より前**。以後 `§2.4-4/5/6/7` により増減・補充・
  「有意になるまで足す」は禁止。
- ★ **n=1 の既知の限界**（`notes.md` に記録済み）: counterbalance が成立せず題材交絡を排除できない /
  Fisher 統合の救済が無い / 分離できなければ何も解決しない。

### T-7 P-1 を受けた修正（`§2.8` が許容する範囲だけ）

★ **変えてよいのは「課題文・実施手順・ブロック長・資料の量」だけ。**
**`§3` の判定基準は変えない。** 変えたら「変えた」と明記し、その回の確証性を放棄する。

⚠️ 修正したら **`materials/README.md` に記録する義務**がある（E-3）。

### T-8 記録

- `.steering/20260804-g1-pilot-execution/`（新規）に requirement / design / tasklist / decisions。
- `experiments/20260801-controlled-friction-task/notes.md` に P-1 の節を追記。
- ★ **結果は `results/pilot/` に置く**（確証標本の解析とファイルを分ける・`§2.8`）。

---

## §4 制約（厳守）

- ★★ **`preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` を変更しない。**
  改訂するなら**第 6 版として記録し、判定を緩めていないことを論証**する。
- **`docs/preregistration-v0.3.md`**（Phase1 の凍結契約）/ **`research-positioning.md §5`** を変更しない。
- ⚠️ **確証実施は Phase1 の凍結解除後**（`ADR-009 D7`。現在 GATE2 pass / GATE3 DataInsufficient）。
  ★ **P-1 はこの制約の対象外**（確証データではない）。
- **PII**: 氏名・メール・所属を出力もコミットもしない。**raw NDJSON をコミットしない**。
  **`blocks/*.json` をコミットしない**。★ **セッション日時を成果物に出さない**。
- ★ **文献に依拠する記述は `citation-ssot`**。`docs/references.md` の次番号は **`[P45]` / `[V75]`**。
- 依存を足さない（Python は標準ライブラリのみ）。
- ⚠️ **事前登録を改訂したら、その規則を実行するスクリプトが同じ版か確かめる**。
  ★ `analyze.py --selftest` が `config.json` の `revision.version` との一致を**機械的に検査する**
  ので、版を上げたら `PREREG_REVISION` も上げること（上げ忘れると赤になる）。

---

## §5 現在の状態

- ブランチ **`main`**（`7a939b8 chore: bump version to v0.1.22`）。作業ツリーはクリーン。
- リリースタグ **`v0.1.22`** を push 済み。CI が Windows exe / macOS dmg を Release に公開する。
- `bash run.sh` = **GREEN**（kill switch の挙動テストを含む）。
- `validate_materials.py --strict` / `analyze.py --selftest` / `validate_blocks.py --selftest` /
  `forms_to_blocks.py --selftest` = すべて緑。
- **データは 1 件も無い**（`results/` は空・`blocks/` に割付ファイル無し）。
- Phase1: **GATE2 pass / GATE3 DataInsufficient**（判定保留）。凍結は解除されていない。

---

## §6 まず読むもの（この順）

1. `experiments/20260801-controlled-friction-task/protocol.md`（★ **当日の台本。これに従う**）
2. 同 `preregistration.md` の **改訂履歴 第 5 版** ＋ `§2.8`（パイロット条項）＋ `§2.4`（n の凍結）
3. `.steering/20260803-g1-pilot-readiness/decisions.md`（F-1〜F-8。**決着の根拠**）
4. 同 `experiments/.../data.md` の **B-4**（★ P-ID 共有の帰結・送付フロー）
5. `Form_G1/README.md`（フォームの配備と実施当日の使い方）

---

## §7 終わり方

- `.steering/20260804-g1-pilot-execution/` に記録を残す。
- `bash run.sh` が GREEN のまま。各 `--selftest` が緑のまま。
- ★ **確証標本の n を凍結**（`config.json` ＋ `notes.md` に日付とコミット）。
- ⚠️ **P-1 の結果で `§3` の判定基準を変えない。**
- 最後に `/cross-review`（★ 渡すのは git diff のみ。**NDJSON 生ログ・被験者データを渡さない**）。
