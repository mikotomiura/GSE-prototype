# 次セッション開始プロンプト（★ **Mac で実行する**）— v0.1.27 の配布 zip を作る

このファイルの「===」以下をコピペして開始する。
⚠️★★★ **このタスクは macOS でしか実行できない。** Windows 機では `hdiutil` / `codesign` /
`ditto` が無いので途中で必ず止まる。

---

===

## §0 ⚠️ このセッションの前提（★ 議論し直さない）

★ 2026-08-19 に **G1 をリブート**し、計器（ADR-013）と運用（G-1 二度押し）を直して
**`v0.1.27` をリリース**した（main 上のタグ・push 済み）。
→ ⚠️★★★ **被験者に配るアプリを入れ替えないと、新しい計器は 1 行も効かない。**
★ 本セッションの仕事は **配布 zip を 2 つ作ること**である。

⚠️★★★ **`v0.1.26` のまま配ってはならない。** v0.1.26 は既に配布済みで、
そのまま配ると **同じ `app_version` を名乗る 2 つの異なる能力セット**が生まれ、
★ `app_version` を刻んだ意味が消える（ADR-013 の動機そのものの再生産）。

### ★ 何を作るか（★ 呼び方を間違えない）

| 成果物 | 中身 |
|---|---|
| `dist/_common/G1_実施用_macOS.zip` | ★ **`gse-next.app` を入れたフォルダ**の zip（⚠️ dmg ではない） |
| `dist/_common/G1_実施用_Windows.zip` | `gse-next.exe` / `gse-submit.exe` / `launch-g1-windows.bat` / `pubkey.txt` |

⚠️★ **dmg は CI の中間生成物にすぎない。** スクリプトが dmg をマウントして
`.app` を取り出し、`g1.mode` と同じフォルダに置いてから zip に固める。

★ **なぜこの形か**（★ 全部 repo に実測記録がある。設計し直さない）:

1. ⚠️ **dmg のドラッグ工程を残すと G1 モードにならない** —— 被験者が dmg から直接起動して
   **2026-08-07 に実機で発生**（`decisions.md` D-9）。→ `.app` を**あらかじめ**フォルダに入れる
2. ⚠️ **`g1.mode` を `.app` の中に置けない** —— `codesign --verify --strict` が
   `a sealed resource is missing or invalid` で落ちる（`g1.rs` D-7）。→ マーカーはバンドルの**外**
3. ⚠️ **Drive はパーミッションを保存しない**（2026-08-07 実測）—— フォルダのまま配ると
   `Contents/MacOS/` の**実行ビットが落ちた `.app`** が届く。→ **単一ファイルの zip** で配る
4. ⚠️ **公証を通していない** —— macOS が「壊れているため開けません」と出す。
   → `初回セットアップ_mac.sh`（quarantine 解除）を**初回だけ研究者と一緒に**実行する

## §1 ★ 事前に確かめること（⚠️ 1 つでも欠けると途中で止まる）

```bash
# 1. repo を main の v0.1.27 まで持ってくる（★ タグが無いとスクリプトが止まる）
cd <mac の GSE-prototype>
git fetch origin --tags && git checkout main && git pull --ff-only
git rev-parse v0.1.27            # ★ 出なければ fetch し直す

# 2. 道具（★ どれも macOS 標準か既存導入）
gh auth status                   # ⚠️ gh release download に要る
python3 --version                # ⚠️ 設定検査と zip 検査に要る
which hdiutil codesign ditto     # ★ macOS 標準

# 3. ⚠️★★★ 送信先の設定ファイル（**repo に無い / .gitignore 済み / シークレット入り**）
ls -l g1-submit.json             # ★ repo 直下。無ければ研究者から受け取る
```

⚠️★★ **`g1-submit.json` は git に入っていない。** スクリプトは中身を検査し、
`endpoint` が `https://script.google.com/macros/s/…/exec` で終わること、
`secret` が **24 文字以上**であることを確かめる。→ 無いまま作ると
**記録が研究者に届かない配布物**ができるので、**必ず用意してから走らせる**。

⚠️ **CI のリリースビルドが終わっていること**を先に確認する（★ 終わっていないと
`gh release download` が空振りする）:

```bash
gh run list --limit 3
gh release view v0.1.27 --json assets -q '.assets[].name'
#   期待: gse-next.exe / gse-submit.exe / gse-next_0.1.27_aarch64.dmg
```

## §2 ★ 実行（★ これ 1 コマンドで両方できる）

```bash
cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --tag v0.1.27
```

⚠️★★★ **`--tag v0.1.27` を必ず付ける。** スクリプトの既定は **`v0.1.24`** なので、
付け忘れると**古いアプリを配ることになる**（★ しかも成功したように見える）。

★ スクリプトが**自分で**やること（⚠️ 手でやり直さない）:

- タグに `reconcile.rs` があるか（＝自動送信が入ったビルドか）を検査
- `gh release download` で `dist/_release/v0.1.27/` へ取得（★ 既にあれば再取得しない）
- dmg をマウント → **署名検証** → `.app` を `ditto` で取り出す → フォルダへ置いて**再度署名検証**
- `初回セットアップ_mac.sh` の `--selftest` を **zip 化の前と展開後の 2 回**走らせる
- ⚠️ README が**被験者を守る 4 つの文言**を持つか grep（「壊れていません」「ゴミ箱に入れないで」
  「研究者と一緒に」「ターミナルの窓へドラッグ」）。★ 旧版の「右クリック」「開発元を確認できません」
  が**残っていないこと**も検査する（B 型ダイアログでは効かないため）
- Windows zip は **UTF-8 フラグ (bit 11)** が立ち、`__MACOSX` / `.DS_Store` が無いことを機械検査
- ⚠️ 共通配布物に `block*.html`（被験者別の課題ページ）が紛れていないことを検査

## §3 ⚠️ 出来たら確かめること（★ 機械検査を通っても、これだけは人が見る）

```bash
ls -l dist/_common/*.zip
```

1. ★ **`G1_実施用_macOS.zip` の中に `gse-next.app` があり `.dmg` が無い**こと
2. ★ **`app_version` が `0.1.27` になること**（⚠️ ここが本リリースの主目的）
   → 展開した `.app` を**実際に 1 回起動**し、生成された NDJSON の `meta` 行を見る:
   ```bash
   # ⚠️ 生ログは repo の中に置かない
   grep -m1 '"type":"meta"' ~/Documents/GSE-sessions/gse_*.ndjson | head -1
   #   期待: "app_version":"0.1.27" と "capabilities":{...,"config_gated":[...]}
   ```
3. ★ **G-1（二度押し）の実挙動**を 1 回だけ試す（★ 今回直した本体）:
   計測中にもう一度「開始する」→ ⚠️ **前のファイルが `session_end` で閉じ、
   新しいファイルができる**こと（★ 1 ファイルに `session_start` が 2 本入らないこと）
4. ★ `starve_window` 行が出ること（⚠️ **30 秒未満の中断が 1 分間に 1 回も無いと出ない**ので、
   出ないこと自体は異常ではない。★ 出たら `win_ms` が 60000 前後であることだけ見る）

## §4 ⚠️ 落とし穴（★ すべて実測記録あり）

1. ⚠️★★★ **`--tag` の付け忘れ**（既定が `v0.1.24`）
2. ⚠️★★ **`g1-submit.json` がシークレットを含む。** ★ Drive の共有範囲に注意し、
   **zip 以外（フォルダのまま）を置かない**
3. ⚠️★★ **Drive に置くのは zip だけ。** フォルダのまま置くと実行ビットが落ちる
4. ⚠️★ **課題ページ（`block01.html`…）は共通側に入れない。** 被験者ごとに違う（D-1）。
   ★ 被験者 1 人ぶんは別スクリプト `./make-distribution.sh <ID> both --tag v0.1.27`
5. ⚠️★ README の文言を「直した」つもりで**表記を変えると grep 検査が空回りする**
   （2026-08-08 に「壊れてはいません」と書いて 0 件になった実績）
6. ⚠️ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）
7. ⚠️ Python は `PYTHONUTF8=1` を付ける習慣（★ mac では不要だが揃えておくと安全）

## §5 ★ 終わったら

1. `.steering/[YYYYMMDD]-mac-build-distribution-zips/` に結果を記録する
   （★ zip の**バイト数**と、§3 の 4 項目の実測結果）
2. ⚠️ **Drive へ上げるのは人の判断**（★ スクリプトは上げない）
3. ★ **収集開始のゲートはまだ閉じていない** —— 残るのは
   **電子同意フォーム（Google フォーム）の実物への反映と突合**である。
   → `_handoff/next-session-prompt-post-reboot-collection-gate.md` を見ること。
   ⚠️ **repo の 3 文書（`consent.md` / `participant-guide.md` / 正本ソース
   `Form_G1/GSE_G1_Form_Builder.gs`）は 2026-08-19 に更新済み**だが、
   **配布済みの実フォームは未更新**である。

⚠️★★★ **同意フォームの突合が終わるまで新コホートの収集を始めない**
（ADR-013 D5-2b / `preregistration.md` 第 17 版）。
★ 配布 zip を作ること自体は、その前に済ませてよい。

---

## ★ 補足 — Windows 側に残っている別件（⚠️ Mac では触らない）

- `C:\gse-dataset` の `schema/current.json` が**未コミット**（`v0.1.27` の schema をコピーした分）。
  ★ Windows 機でコミットする。
- `.claude/settings.json` / `.gitignore` の変更が未コミット（★ 本タスクとは無関係）。
