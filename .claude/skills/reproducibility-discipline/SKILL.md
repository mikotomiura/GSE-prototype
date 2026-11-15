---
name: reproducibility-discipline
description: >
  科学的実験を実行・記録・再現する時に必須参照。experiments/<YYYYMMDD>-<exp-name>/ の
  ディレクトリ規約、乱数 seed 固定、環境の lockfile (Cargo.lock 等) 固定、入力 NDJSON の
  version/hash 固定 (gse-dataset commit)、HMM_VERSION の刻印、scripts/repro.sh /
  run-calibration-cohort.sh による 1 コマンド再現を強制する。「実験を回す」「較正スモークを走らせる」
  「結果/メトリクスを記録する」「再現する」「ablation する」「HMM をチューニングして効果を測る」時、
  または experiments/ 配下のファイルを作成・編集する時に起動する。再現性規約の SSOT は
  docs/experiment-tracking.md。実装作業 (.steering/) には適用しない。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Bash(ls *)
---

# Reproducibility Discipline

## このスキルの目的
実験の再現性を「規約 doc に書いてある」状態から「実験のたびに自動で守られる」状態にする。
SSOT は `docs/experiment-tracking.md`。本 skill はその規約を作業時に発火させる薄い層であり、
規約を再定義しない。

## 適用範囲
### 適用する
- experiments/ 配下で実験を実行・記録する時（較正スモーク / チューニング / アウトカム感度分析）
- メトリクス / 結果を保存する時（metrics.json / calib.json / cohort.json）
- 過去実験を再現する時
### 適用しない
- `.steering/` の実装作業記録（実験ログではない）
- 実験として記録しない探索的な対話・デバッグ

## 主要なルール（詳細は docs/experiment-tracking.md）
### ルール 1: 実験は experiments/<YYYYMMDD>-<exp-name>/ に隔離
config / SEED / data.md / env.md / run.sh / results/ / metrics.json / notes.md を必ず置く。
### ルール 2: seed と環境を固定
ランダム要素があれば seed を SEED に固定。環境は Cargo.lock（Python 使用時は requirements.txt 等）を env.md から参照。
### ルール 3: GSE 固有アンカーを刻む
HMM_VERSION を config と結果に記録。入力 NDJSON は gse-dataset の commit hash で data.md に固定（生ログはコミットしない）。
### ルール 4: 1 コマンド再現
scripts/repro.sh（実体は run-calibration-cohort.sh をラップ）で代表実験を再走できること。できないなら実験は未完了。
### ルール 5: 仮説・事前登録・出典に接続
notes.md に「検証する仮説 = research-positioning.md §4.1 の H?（または事前登録の項目番号）」「PreReg-?」「借用手法 = [n] (references.md)」を必ず書く。

## チェックリスト
- [ ] experiments/<date>-<name>/ 構造に従ったか
- [ ] seed を固定したか（ランダム要素がある場合）
- [ ] env を lockfile で固定したか
- [ ] 入力データを gse-dataset commit hash / NDJSON hash で固定したか
- [ ] HMM_VERSION を刻んだか
- [ ] scripts/repro.sh で 1 コマンド再現できるか
- [ ] 仮説 (§5 H?) と PreReg 番号と出典 [n] にリンクしたか

## 補足資料
- `checklist.md` — 実験開始前 / 終了後の詳細チェックリスト

## 関連する他の Skill
- citation-ssot — 借用手法の [n] 登録で参照
- git-workflow — HMM_VERSION bump 時のゴールデン再生成記録
- ml-workflow — HMM パラメータチューニングの根拠記述
