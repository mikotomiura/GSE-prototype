# Phase 1 Task 3: Dashboard Counter Widget + 実機手動検証 — design

> **用語注記**: 本タスクの「検証」は `docs/development-guidelines.md` §3 の区分で
> **実機手動検証 (manual verification)** に該当する。Playwright 等の自動 E2E は
> 含まない。回帰保護は Task 2 の `gse-replay --metrics` + ゴールデン byte-equal が担い、
> 本タスクは UI 結線（listen → setState → 再描画）が実機で通ることの目視確認のみを対象とする。

> 本 design は Phase 1 全体の v2 設計（`.steering/20260415-phase1-ground-truth/design.md`）の Frontend + 統合検証部分を具体化したもの。

## 実装アプローチ

### Frontend 最小主義

- Dashboard に counter widget のみ追加（既存ボタンや 5 秒ホールドは導入しない、v2 設計通り）
- state は local useState、`@tauri-apps/api/event` の `listen()` で `user_label_recorded` を購読
- counter は単調増加（セッション跨ぎリセットは Dashboard 再マウント or start_session コマンドに紐付ける）

### 実機手動検証の独立化

- 実機検証手順を `verification_log.md` に書き出し、各ステップにチェックボックス + 実測記録
- 検証が失敗したら Task 3 を保留し、Task 1 / Task 2 の該当部分へ修正依頼を返す

## 変更対象

### 修正するファイル

- `src/components/Dashboard.tsx`
  - counter state: `{ flow: number, incubation: number, stuck: number }`
  - `useEffect` で `listen<{ label: string, timestamp: number }>("user_label_recorded", ...)` 購読開始、アンマウント時に unlisten
  - counter widget UI（読み取り専用、既存レイアウトの余白に配置）

### 新規作成するファイル

- `.steering/20260415-phase1-counter-ui/verification_log.md` — 実機手動検証手順 + 実測結果
- `.steering/20260415-phase1-ground-truth/retrospective.md` — Phase 1 全体振り返り（Task 3 完了時に作成）

### 削除するファイル
なし

## counter widget の構造（素案）

```tsx
const [labelCounts, setLabelCounts] = useState({ flow: 0, incubation: 0, stuck: 0 });

useEffect(() => {
  const unlisten = listen<{ label: string; timestamp: number }>(
    "user_label_recorded",
    (event) => {
      setLabelCounts((prev) => {
        const key = event.payload.label as keyof typeof prev;
        if (key in prev) {
          return { ...prev, [key]: prev[key] + 1 };
        }
        return prev;
      });
    }
  );
  return () => {
    unlisten.then((fn) => fn());
  };
}, []);

return (
  <div className="gt-counter" role="status" aria-label="Ground Truth labels">
    <span>GT:</span>
    <span>Flow {labelCounts.flow}</span>
    <span>Inc {labelCounts.incubation}</span>
    <span>Stuck {labelCounts.stuck}</span>
    <span className="gt-hint">⌘⇧⌥ F/I/S</span>
  </div>
);
```

（実際の className / レイアウトは既存 Dashboard の CSS に合わせる）

## 実機手動検証手順（verification_log.md の骨子）

1. `~/.cargo/bin/cargo tauri dev` で起動、macOS Input Monitoring 権限確認
2. Dashboard が表示され、counter widget が `Flow 0 / Inc 0 / Stuck 0` を示す
3. `Cmd+Shift+Option+F` 押下 → Dashboard の Flow が 1 に
4. 2 秒以内に再度 `Cmd+Shift+Option+F` → デバウンスで 1 のまま
5. 2 秒以上待ってから再押下 → 2 に増加
6. `Cmd+Shift+Option+I` × 1、`Cmd+Shift+Option+S` × 1 を順に押下 → Inc 1, Stuck 1
7. セッション終了、`~/Documents/GSE-sessions/gse_*.ndjson` 確認
   - meta 行: `{"type":"meta","session_start":...,"hmm_version":"0.2.0"}`
   - user_label 4 行（Flow ×2, Inc ×1, Stuck ×1）
8. `cargo run --bin gse-replay -- <session.ndjson> --metrics` 実行 → 混同行列 + F1 + 中央値が出力
9. `cargo run --bin gse-replay -- <session.ndjson> --metrics --json` 実行 → JSON 出力
10. `cargo run --bin gse-replay -- src-tauri/tests/fixtures/minimal.ndjson --snapshot src-tauri/tests/snapshots/minimal.json` byte-equal 維持

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| Dashboard.tsx 既存機能 | LOW | widget を追加するだけ、state 分離 | TS 型検査で確認 |
| Overlay.tsx | NONE | 触らない | — |
| Backend (Rust) | NONE | Task 1/2 に依存、本タスクで変更なし | — |
| tests/snapshots | NONE | Frontend 追加のみ | 回帰テストで確認 |

## 既存パターンとの整合性

- **Tauri イベント購読**: 既存 `listen()` パターンに従う（`Dashboard.tsx` に既存サンプル有無を実装時確認）
- **読み取り専用 widget**: p_flow / p_stuck の表示と同じスタイル
- **アンマウント時の unlisten**: useEffect cleanup の標準パターン

## テスト戦略

- **単体**: counter reducer の挙動を型レベルで担保（TypeScript の型推論で誤 key 無視）
- **結合**: listen → setState → 再レンダリングが実機で走ることを手動検証で確認
- **実機手動検証**: `verification_log.md` の 10 ステップ手順を実施、各項目にチェック + 実測値記録
- **回帰**: Phase 0 ゴールデン byte-equal（Task 2 での回帰確認を Task 3 でも再実施、自動）

## ロールバック計画

- Dashboard.tsx の変更を revert すれば完全に元の状態に戻る（state / useEffect / UI いずれも追加のみ）
- Backend 側には影響なし、Task 1/2 の動作は単独で維持される

## 既知の Open 点

- **counter リセットタイミング**: セッション跨ぎで増え続けるか、`start_session` で reset するか。初期実装ではシンプルに「Dashboard マウント中は増える」で、必要なら後から reset 連動を追加
- **スタイリング**: 既存 Dashboard の tailwind or CSS 構成を確認してから合わせる
- **Overlay への表示**: 今回は Dashboard のみ。Overlay での確認が欲しいかは Phase 2 以降で検討
