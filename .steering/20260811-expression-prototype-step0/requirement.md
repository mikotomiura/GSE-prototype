# 表現層の試作 Step 0 — `toeexpand` / `toecollapse` 往復検証（関門）

> 入口: `.steering/_handoff/next-session-prompt-expression-prototype.md`
> 上位仕様: `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` §7 Step 0
> 既決: D6（TD 採用は `toeexpand` の往復が壊れないことが前提）/ D18（試作は `experiments/` 配下・ただし Step 0 は対象外）

## 背景

2026-08-10〜11 の 2 セッションで表現層の設計を紙の上で確定させた（D13→D21 で **常時リアルタイム α**
へ転換）。**コードは 1 行も書いていない。** 本セッションは「手を動かす」段である。

TouchDesigner のプロジェクト (`.toe`) とコンポーネント (`.tox`) は **バイナリ**であり、
そのままでは Claude Code が読めず `git diff` も `/review-changes` も `/cross-review` も効かない。
D6 は「`toeexpand` の逐語ヘルプが *expand into a directory structure that can then be edited
using standard tools* と述べている」ことを根拠に TD を採用可能とした——が、
★ **往復が実際に壊れないかは一度も実測していない**（`20260810-.../design.md` §1.3・§4.5.4 で未検証と明記）。

★★ **これは「安く畳むための関門」である。** ここが通らなければ TD は本プロジェクトの作業プロトコルに
載らず、**表現層トラックの道具選定をここで畳める**。通らないことは失敗ではなく、設計どおりの結果である。

## ゴール

**`toeexpand` / `toecollapse` の往復について、以下 2 点を実測で判定し、`.steering/` に実測ログを残す。**

1. **(a) 展開されたツリーがテキストとして読めるか**（Claude Code が編集できる形か）
2. **(b) 往復 (expand → collapse) で情報が失われないか**

判定は **PASS / FAIL / 条件付き PASS** の 3 値で出し、**FAIL なら以降の Step 1–7 に進まない**。

## スコープ

### 含むもの

- `NewProject.toe`（TD 同梱テンプレート）を作業用ディレクトリへコピーして往復させる
- 展開ツリーの構造・各ファイルの中身（テキスト / バイナリの別）を実測
- 往復後の `.toe` と元 `.toe` の byte 比較（`sha256` / `cmp`）
  ⚠️ **byte-equal でなくても直ちに失格ではない**（タイムスタンプ等が入りうる）。
  差分が出た場合は **展開後のツリー同士**を比較して判定する
- `.tox` を 1 本（同梱サンプル）でも試す — `.toe` と挙動が違う可能性があるため
- ★ **`toeexpand` の終了コードの意味をソース/実測で確かめる**
  > ⚠️★★ **2026-08-11 訂正（S0-D2）**: 起票時の本項は引き継ぎを引き写して
  > 「引数なしで usage を出して **exit 0** を返すことが実測済み」と書いていたが、**これは誤りだった**。
  > 実測（git-bash 2 通り + PowerShell）では **引数なしは exit 1**。さらに
  > **成功で 1・失敗で 0** という**反転**である。→ 「exit 0 なら成功」ではなく
  > **「終了コードを判定に使わない」**が正しい結論。詳細は `decisions.md` S0-D2。
- 実測ログと判定を本ディレクトリに残す

### 含まないもの

- ★ **`experiments/` を起こさない** — Step 0 は「実験」ではなく **実機の事実確認**である
  （`20260810-.../design.md` §5 / D18 がそう書いている）。`experiments/` は **Step 3 以降**
- **GSE 本体（Rust / TypeScript）の変更** — 1 行も触らない
- **OSC / WebSocket の実装**（`data-privacy` の外部送信境界を増やさない・D5）
- **`.toe` / `.tox` をバイナリのままコミットすること**（D6）
- **MhD（推論層）の設計議論**（研究者指示・2026-08-11）。`p_stuck` / `ewma_x` / `ewma_y` は入力として使うだけ
- **Program Files 内での作業**（権限・汚染）
- 新規文献の `docs/references.md` 登録（試作なので発生しない見込み）

## 受け入れ条件

- [ ] `toeexpand` / `toecollapse` / `NewProject.toe` の実体が**このセッションで**存在確認されている
      （引き継ぎメモの記述を根拠にしない — `verify-before-claiming` ルール 1）
- [ ] `.toe` の展開ツリーの構造と各ファイルの種別（テキスト/バイナリ）が実測で列挙されている
- [ ] 往復後の `.toe` の sha256 が元と一致するか**実行して**記録されている
      （★ 一致しない場合、展開ツリー同士の差分で判定した根拠が書かれている）
- [ ] `.tox` 1 本でも同じ 2 点が実測されている
- [ ] ★ **終了コードだけで成功と判定した箇所が 1 つも無い**（出力の中身で判定している）
- [ ] 判定（PASS / FAIL / 条件付き PASS）と**その根拠**が `decisions.md` に記録されている
- [ ] 実測ログ（コマンドと生出力）が `verification-log.md` に残っている
- [ ] `git status` に `.toe` / `.tox` のバイナリが混入していない

## 関連ドキュメント

- `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` §7（作る順序・Step 0 が関門）
- `.steering/20260811-impact-and-cognitive-core-map/design.md` §4（表現層を `p_stuck` の下流に置かない・系統 A/B）/ §5 Stage 0'
- `.steering/20260810-media-sound-modality-and-creative-tooling/design.md` §1（実機で確認済みの CLI 事実）/ §3（Step 1–3）/ §5（テスト戦略）
- `.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md` **D21 → D13**（★ D21 を先に読む）/ D6 / D18
- `.claude/skills/verify-before-claiming/SKILL.md`（★ 断定の前に必ず）

## 運用メモ

- **/reimagine 適用: No**
- **理由**: 本 Step は設計判断ではなく **実機の事実確認**である。複数の実装案を比較する余地が無く
  （`toeexpand` は TD が提供する唯一の橋・D6）、判定は実測が出す。
  ★ 設計判断が要るのは **Step 0 が PASS した後**（どの表現をどう作るか）であり、そこで検討する。
