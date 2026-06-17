---
name: codex-consult
description: >
  設計フェーズで OpenAI Codex CLI に第二意見やアイデアを求める。Plan mode、要件詰め、
  アーキテクチャ判断、/reimagine の代替案検討、設計の盲点洗い出しなど、コード変更前の
  局面で起動する。入力は設計ドキュメント / 候補案 / トレードオフメモ等の markdown 抜粋
  (公開可能な最小範囲)。read-only で書き込みは行わない。proprietary plugin の出力 /
  機密情報を含む場合は実行を中止する。日常的な設計判断で 1-2 回呼ぶ運用を想定。
allowed-tools: Bash(scripts/run-codex-consult.sh *), Bash(jq *), Read
disable-model-invocation: false
---

# Codex Consult Skill

## 適用条件

このスキルは以下の状況で起動する:

1. Plan mode で設計案がまとまった後、ユーザーに提示する **前** に第二意見が欲しい時
2. `/reimagine` で「破壊」(初回案を捨てる) を実行した後、再生成した代替案の検討時
3. アーキテクチャ判断 / トレードオフ評価で Claude 単独の自己レビューに不安がある時
4. ユーザーが「Codex の意見も聞いて」「ついでにアイデアもらって」と明示した時
5. 自分の設計に対する **盲点 / 抜け** を洗い出したい時

## 適用しないケース

- 機密情報 / proprietary plugin 出力を含む設計ドキュメント
- 既に実装が始まったタスク (それは codex-review / codex-rescue の領域)
- 自明な設計判断 (Claude 単独で十分な軽量タスク)
- `.codex/budget.json` の予算余裕が `per_invocation_max` 未満

## 入力の作り方 (公開可能な最小抜粋)

設計ドキュメントをそのまま送らず、以下の **要素のみ** に絞る:

1. **何を解決したいか** (1-3 行)
2. **検討した候補案** (各 2-5 行)
3. **採用したい案 + 理由** (5-10 行)
4. **トレードオフ / 不安点** (3-5 行)

プロジェクト固有の internal 名称 (社内サービス名、顧客名等) は仮名化する。`scripts/secrets-filter.sh` を必ず通す。

## 実行フロー

### Step 1: 入力の準備

```bash
cat > /tmp/codex-consult-input.md <<'EOF'
## 何を解決したいか
[1-3 行]

## 検討した候補案
- A: ...
- B: ...
- C: ...

## 採用したい案 + 理由
[5-10 行]

## トレードオフ / 不安点
[3-5 行]
EOF
```

### Step 2: preview で送信前確認 (必須)

```bash
scripts/run-codex-consult.sh --preview /tmp/codex-consult-input.md
```

ユーザーが内容を確認して OK を出したら Step 3 へ。

### Step 3: wrapper 経由で Codex 呼び出し

```bash
scripts/run-codex-consult.sh /tmp/codex-consult-input.md
```

## 出力の取り扱い

- Codex の指摘で **明らかな盲点** だったものは設計案を修正
- **既知のトレードオフ** だったものは判断理由を強化して書き残す
- **誤検知 / 文脈理解不足** だった指摘は却下理由を記録
- ユーザーに「Codex はこういう指摘もしてきた」と提示し、最終判断を仰ぐ

## 関連 Skill / ファイル

- `codex-review` — 実装後の diff レビュー
- `codex-rescue` — 詰まった実装の委譲
- `.codex/config.toml`, `.codex/budget.json` — 予算管理
- `scripts/run-codex-consult.sh` — 本 Skill 専用 wrapper
- `scripts/secrets-filter.sh` — 機密フィルタ

## アンチパターン

- ❌ 設計ドキュメント全文を生で送る
- ❌ プロジェクト固有の internal 名称を仮名化せずに送る
- ❌ Codex の指摘を盲信して設計を変える (Codex は文脈の半分しか持っていない)
- ❌ 既に実装が始まったタスクで本 Skill を使う
- ❌ 軽量な設計判断で毎回呼ぶ (token コスト爆発)
- ❌ ユーザー preview なしに送信する
