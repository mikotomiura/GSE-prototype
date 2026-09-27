# 次セッション — IME 論文: 評価設計（確定版）を issue に分解する

> 作成: 2026-09-28（`next-session-ime-paper-discussion.md` を実施し、design.md をハイブリッドで確定した直後）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す。
> ★ 2 本目（`next-session-p321-reanalysis-paper.md`）とは触るファイルが別なので**並行可能**。

## §0 打ち込む用

```
.steering/_handoff/next-session-ime-paper-issues.md を読んで、IME 論文の評価設計を issue に分解してください。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の design.md（★ 確定版 = v1＋v2 のハイブリッド。〔v2〕印に注意）・
decisions.md（判断 1–16）・design-comparison.md。
★ 分解は issue-slicing skill で（Opus）。design.md §8 の 12 本の案を出発点にし、7 基準（docs/loop-engineering.md）で切り直す。
⚠️ 分解とループ実行は別セッション（CLAUDE.md「セッション境界」）。分解が終わったら /clear。
Skill: issue-slicing・verify-before-claiming・reproducibility-discipline・architecture-rules（観測部の単体ロガーを切り出す issue）・
hook-constraints（ドライバ）・data-privacy（正解ログを content-free にする）。応答は日本語。
コミットは専用ブランチで、git add はパス指定（-A 禁止）。
```

## §1 状態（2026-09-28）

- ★ design.md は **確定版**（判断 14）。v1 = `design-v1.md`、v2 = `design-v2.md`、比較 = `design-comparison.md`。
- ★ 確定した判断: 訂正 4 点入りの初版承認（10）／較正パイロットを凍結前に行う（11）／E3 は観測部だけ再計測・バッテリーなし（12）／CHI 併願は書簡で開示（13）／ハイブリッド（14）／題 T1・Apache-2.0 ＋ CC BY 4.0（15）／[P321] 再解析を並行（16）。
- ★ 一次で確かめた事実（design.md に逐語あり）: Apple は `NSTextInputClient` の呼び出し順を文書にしていない・`unmarkText` は確定側／MS は TSF の IME が IMM 互換層で非 TSF アプリに効くとだけ書き、届くメッセージは列挙しない／BRM は TOP Level 2（信頼できるリポジトリ）・Type 4 のデータ方針・Declarations で "Not applicable" 可。

## §2 分解で気をつけること

1. **Done を観測可能な形で書く**（test 名 / exit code / 生成物の存在）。例: 照合器 = パラメータ回復テストが緑。単体ロガー = manifest 照合が exit 0。
2. **OS をまたぐ issue を分ける**: macOS の参照入力欄・較正パイロットは Mac で、Windows 側は研究者の Windows 機での**収集だけ**を依頼する運用（decisions.md 判断 4 のトレードオフ。⚠️ そこで引いている memory `windows-agent-collection-only` は 2026-09-28 時点で Windows 機の memory に**無い** —— 別の機の memory の可能性）。
3. ⚠️ **較正パイロットは ImeShadow 行を見ない**（判断 11 の境界）。issue の Allowed Files と Done にこの境界を書く。
4. ★ **凍結は段階的**: macOS 版 → Windows 版は Windows 本計測前の追補（design.md §6）。凍結物は `experiments/<date>-ime-observation-accuracy/preregistration.md`。
5. ★ 単体ロガーの切り出しは **GSE の構造を変えない**（逐語コピー ＋ manifest・design.md §4）。⚠️ GSE 本体の OSS 公開は未踏採択後。
6. ★ 縮退順（判断 14）を issue の優先度に反映する: 実アプリへの転移確認 → Google 日本語入力 → 現代文コーパス → S9 → E2 の開集合。

## §3 やらないこと

- 人の打鍵データを使う（著者本人も含む）
- Phase1 / G1 / O1 のデータを混ぜる
- プロトコル凍結前に ImeShadow と正解を突き合わせる
- バッテリーを測る（判断 12）
