# 実測結果と所見 — v0.1.27 配布 zip (2026-08-19)

## 成果物 (§5-1: バイト数)

| ファイル | バイト数 | sha256 |
|---|---:|---|
| `dist/_common/G1_実施用_macOS.zip` | 10,367,710 | `fef1e97fbf9197641572102666f31be4dba78f842e7d8a812da6a415dcc58a8f` |
| `dist/_common/G1_実施用_Windows.zip` | 6,024,445 | `7c7964ef8d81f2544d98eeab02a52a7f7e70c11eb47e80d602f1a0ec4fd0a994` |

中間生成物 `dist/_release/v0.1.27/gse-next_0.1.27_aarch64.dmg` (10,376,341 B) は**配らない**。

## §3 の 4 項目 (実測)

### §3-1 zip の中身 ✅

- `G1_実施用_macOS.zip`: 全 51 エントリ。`gse-next.app/` 配下 **39 エントリ**、`.dmg` は **0 件**。
  トップレベルは `G1_実施用_macOS/` と `__MACOSX/` (⚠️ macOS 側は `ditto --sequesterRsrc` の
  仕様どおり。機械検査が `__MACOSX` を禁じているのは Windows zip のみ)。
- フォルダ直下: `gse-next.app` / `g1.mode` / `g1-submit.json` / `README_先に読む.txt` /
  `初回セットアップ_mac.sh`
- `G1_実施用_Windows.zip`: 7 エントリ (`gse-next.exe` / `gse-submit.exe` /
  `launch-g1-windows.bat` / `pubkey.txt` / `g1-submit.json` / `g1.mode` / フォルダ)
- 展開後 `codesign --verify --strict` = `valid on disk` / `satisfies its Designated Requirement`、
  `Contents/MacOS/` の 7 バイナリすべて `-rwxr-xr-x`、quarantine 無し

### §3-2 `app_version` ✅ (★ 本リリースの主目的)

配布 zip を scratchpad に展開して起動し、生成された NDJSON の `meta` 行:

```
app_version  = 0.1.27
hmm_version  = 0.4.0
g1_mode      = marker
capabilities = {unconditional, threshold_gated, config_gated}
  config_gated = [probe_assignment, realtime_label, intervention_decision, intervention_response]
```

★ `g1_mode = marker` は **zip 経由でもフォルダのマーカーが効いている**ことの実測でもある
(起動ログ: `G1 MODE ENABLED (source=marker)`)。画面にも「G1 モードで動作しています（marker）」。

### §3-3 G-1 二度押し ✅ (★ 今回直した本体)

経路: 「開始する」→「← 戻る」→「開始する」。
⚠️ `handleBack` (`App.tsx:1028`) は**フロントの状態しか戻さない** (バックエンドのセッションは
active のまま) ので、これが `was_active == true` = P010 block07 と同じ経路になる。

起動ログ:

```
G1: rotating session log (restart while active (G-1)) -> ".../gse_20260819_141054.ndjson"
```

生成された NDJSON (⚠️ 生ログは repo に置かない。件数のみ記録):

| ファイル | `session_start` | `session_end` |
|---|---:|---:|
| `gse_20260819_140722.ndjson` (二度押しで閉じられた側) | 1 | 1 |
| `gse_20260819_141054.ndjson` (新しくできた側) | 1 | 1 |

★ **1 ファイルに `session_start` が 2 本入らない**ことを確認 (受け入れ条件 4)。
`decide_start_action` の表どおり、1 回目は `NoRotate` (起動時ファイルを使用)、
2 回目は `RotateForRestart` で発火した。

⚠️★ **計測器の誤り (記録に残す)**: 最初 `session_end` を `type` フィールドで数えて
「0 件＝閉じていない」と誤判定した。実体は **`{"type":"meta","session_end":<ts>}`** であり、
`type` ではなく**フィールドの有無**で数えるのが正しい。
→ 異常値を見たら、まず自分の数え方を対照で検算する。

### §3-4 `starve_window` — 未発火 (⚠️ 異常ではない)

- 配布バイナリ `gse-next` に `starve_window` 文字列が **3 箇所**存在
- 起動した実ビルドの `capabilities.threshold_gated` に `starve_window` が載っている (ADR-013)
- 今回**出なかった理由は仕様どおり**: `lib.rs` の `micro_window.tick(...)` は
  **30 秒未満**の hook 停止が 60 秒窓に 1 回以上ある時だけ tally を返す
  (`starve_window_omits_empty_windows`)。本検証では hook が**完全停止**しており
  (`starved_ms=120422` = 30 秒超)、**微小帯 `n_lt30` に該当しない**。
- ⚠️ hook が停止していたのは TCC の問題であって v0.1.27 の欠陥ではない (所見 1)。

## 所見

### 所見 1: 新しいビルドは Documents / Input Monitoring の許可を**必ず取り直す** (実測)

`.app` をダブルクリック相当 (`open`) で起動すると、`~/Documents` へのアクセス許可
ダイアログが出て、アプリは `applog::spawn` の `open()` で**ブロックしたまま待つ**
(`sample` のコールスタックで確認)。tccd ログ:

```
Failed to match existing code requirement for subject com.johnd.gse-next
                                     and service kTCCServiceSystemPolicyDocumentsFolder
AUTHREQ_PROMPTING: service=kTCCServiceSystemPolicyDocumentsFolder, subject=com.johnd.gse-next
```

★ 原因は **ad-hoc 署名のため版が変わると code requirement が一致しない**こと。
→ ⚠️ **v0.1.26 で許可済みの被験者も、v0.1.27 で再度許可を求められる。**

- Input Monitoring / Accessibility 側は**アプリ自身が画面で案内済み**
  (「ad-hoc 署名のため自動付与が動作しません」「アップデート後は署名が変わるため再設定が必要です」
  ＋ System Settings を開くボタン)。★ 対応済みなので追加作業は不要。
- ⚠️ ただし **Documents フォルダ**の許可は `README_先に読む.txt` にも
  `participant-guide.md` にも**記述が無い** (grep で 0 件)。README が触れているのは
  「キーボードの入力の監視」だけ。
- ★ **今回は README を直していない**。理由: README 文言はスクリプトの grep 検査と
  結合しており (引き継ぎ §4-5)、書き換えると zip の作り直しが要る。研究者判断とする。

### 所見 2: 送信ゲートは保たれている (実測)

起動時の収束器は `{"packaged":1,"sent":0,"awaiting_approval":1,...}` を返した。
★ 送信層は `.age.ok` (被験者の確認印) が付いたものだけを送るため、
**「送信する」を押さない限り実エンドポイントへは 1 本も飛ばない**ことを実測で確認した。

⚠️ テストで `P999_block05_gse_20260811_042646.age` が 1 本できた (未承認・未送信)。
★ P999 は検証用の名前空間なので実害は無いが、**削除は研究者判断**として残す。

### 所見 3: ⚠️ `experiments/*/dist/` が `.gitignore` の対象外

- `.gitignore:19` の `/dist` は **repo 直下への錨止め** (S0-D9) なので、
  `experiments/20260801-controlled-friction-task/dist/` には効かない。
- `g1-submit.json` 自体は `.gitignore:67` の `**/g1-submit*.json` で無視される。
  ⚠️ **しかし zip の中身は grep されない** —— `G1_実施用_macOS.zip` /
  `G1_実施用_Windows.zip` は**無視されず**、その中に `g1-submit.json` (secret 33 文字) が入る。
- 実測: `git status --untracked-files=all` で dist 配下 **439 ファイル**が追跡候補。
  → ★ `git add -A` 1 回で **secret を含む zip が commit される**経路が開いている。
- ★ 本タスクでは `.gitignore` を変更していない (S0-D9 の錨止め方針に触れるため研究者判断)。
  提案: `experiments/*/dist/` を追加する。

## Drive 配備の検算 (2026-08-19・研究者がアップロード後に実施)

★ アップロードは**研究者が手で**行った。私は上げていない (引き継ぎ §5-2)。
以下は上がった実体の**読み取りだけ**の検算である。

| 項目 | 実測 |
|---|---|
| `G1_実施用_macOS.zip` | `fileSize = 10,367,710` → 手元と**バイト一致** ✅ |
| `G1_実施用_Windows.zip` | `fileSize = 6,024,445` → 手元と**バイト一致** ✅ |
| 置き場所 | `GSE_ユーザー検証_G1_アプリダウンロードリンク` (`1FDkU52n9EXO92TzCieivexg7WKsXHkFP`) ✅ |
| フォルダの中身 | ★ **zip 2 つだけ**。旧版・展開フォルダ・dmg の混入なし ✅ |
| `modifiedTime` | 2026-08-19 13:59 UTC = 22:59 JST → 本タスクでビルドした実体と一致 ✅ |
| 共有範囲 | 両 zip とも `{"role":"reader","type":"anyone"}` (リンクを知っている全員) |

### ⚠️ ファイル ID は変わったが、被験者リンクは切れない

両 zip とも `createdTime` が今日 ＝ 旧版を**上書きではなく削除＋新規アップロード**した形で、
新しいファイル ID が振られている。

```
macOS   : 1y1B2XAXKmY5Lyeuedf7yBNBBnSGgDXCs
Windows : 1t67RrbGDvdI4eWlEUemnMgCA0U-FBIOZ
```

★ **しかし被験者に渡しているのは「フォルダ」のリンク** (`.idea/短縮版リンク集.md`:
`https://x.gd/QyX35` → `drive/folders/1FDkU52n9EXO92TzCieivexg7WKsXHkFP`) であり、
個別ファイル ID ではない。→ **リンクの貼り替えは不要** (⚠️ 一度「ID が変わったのでリンクが
切れる」と書いたが、リンク集を読んで**撤回**した。実測前の断定だった)。

### 共有範囲について (★ 既存の運用どおり・新しい問題ではない)

zip には `g1-submit.json` (secret 33 文字 ＋ Apps Script の `/exec` URL) が入るので、
「リンクを知っている全員」= **リンクを得た者は誰でも secret を読める**。
★ これは配布モデル上の既存の割り切りであり、`.idea/短縮版リンク集.md` にも
「配る相手は同意済みの被験者に限る。無闇に共有しない」と記録済み。
→ ⚠️ 本タスクでは変更していない。secret を漏らさない担保は **URL の配り先**だけである。
