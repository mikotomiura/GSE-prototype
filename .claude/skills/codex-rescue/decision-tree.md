# Rescue 判断ツリー

タスクが詰まった時、誰に任せるかの判断基準。

```
タスクが詰まった
└── Claude が何回失敗した?
    ├── 0 回 (まだ試していない)
    │   └── まず Claude に試させる
    ├── 1 回
    │   └── Claude が「別アプローチ」を計画 → 再試行
    │       (ここで Codex に渡すのは早い)
    └── 2 回以上
        ├── タスクは proprietary / 機密を含む?
        │   ├── Yes → 人間 rescue (Codex 不可)
        │   └── No → 続行
        ├── タスクは設計判断を伴う?
        │   ├── Yes → 人間 rescue or /reimagine
        │   └── No → 続行
        ├── タスクは「実装の地道な詰め」?
        │   └── Yes → codex-rescue (Codex の得意領域)
        └── タスクは context-heavy (大量のファイル参照)?
            ├── Yes → Claude (Sonnet 1m context)
            └── No → codex-rescue
```

## Codex が向いているタスク例

- 規模はあるが論理は単純な refactor (rename, extract function を多数)
- 既知のパターンを既存コードに当てはめる定型作業
- テスト追加 (existing test ファイルに新ケースを追加)
- 単一ファイルの bug fix で stack trace が明確

## Codex が向いていないタスク例

- アーキテクチャ判断が伴う設計変更
- 複数モジュール横断のリファクタ (context が大きい)
- 仕様が曖昧で要件確認が必要なもの
- 機密 / proprietary を扱うもの
- GSE 固有の HMM チューニング (hmm-analysis Skill の知識が必要)
