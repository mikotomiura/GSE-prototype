---
name: typescript-standards
description: >
  GSE プロジェクトの TypeScript / React コーディング規約。src/ 配下の *.tsx / *.ts
  ファイルを書く・修正する・レビューする際に必須参照。以下の状況で必須参照:
  - Tauri IPC (invoke / listen) の呼び出しコードを書くとき
  - Dashboard.tsx / Overlay.tsx などの React コンポーネントを修正するとき
  - 新しい状態管理 (useState / useRef) を追加するとき
  - 型定義を追加・変更するとき（any 禁止の確認）
  - 新しい npm パッケージを追加するとき
  - Tauri イベントのレスポンス型を定義するとき
allowed-tools: Read, Grep, Glob, Edit
---

# TypeScript / React コーディング規約

## このスキルの目的

GSE のフロントエンド (src/) に型安全性・保守性・依存最小化を確保する。
特に Tauri IPC のレスポンス型付けと、ビジネスロジックの Rust 側への分離を徹底する。

## 適用範囲

### 適用するもの
- `src/` 配下のすべての `.tsx` / `.ts` ファイル
- `package.json` の依存関係追加

### 適用しないもの
- `src-tauri/` (Rust バックエンド)
- `vite.config.ts` / `tsconfig.json` 等のビルド設定

---

## 主要なルール

### ルール 1: `any` 型の使用禁止

Tauri IPC のレスポンスを含め、すべての値に型を付ける。

```typescript
// ✅ 良い例
interface CognitiveState {
  p_flow: number;
  p_incubation: number;
  p_stuck: number;
  label: "Flow" | "Incubation" | "Stuck";
}
const state = await invoke<CognitiveState>("get_cognitive_state");

// ❌ 悪い例
const state: any = await invoke("get_cognitive_state");
const state = await invoke("get_cognitive_state") as any;
```

---

### ルール 2: ビジネスロジックを src/ に置かない

認知状態推定・HMM 計算・介入ロジックはすべて Rust 側で完結させる。
Frontend は表示・UI インタラクションのみ担当。

```typescript
// ✅ 良い例：Rust 側の判定結果を受け取って表示
const { p_stuck } = await invoke<CognitiveState>("get_cognitive_state");
setShowNudge(p_stuck > 0.60);  // 閾値はバックエンドが決定済みの値を使う

// ❌ 悪い例：Frontend で独自に閾値判定
const rawData = await invoke<number[]>("get_raw_features");
const isStuck = rawData[2] > 0.5 && rawData[0] < 100;  // Frontend でロジック実装
```

---

### ルール 3: 状態管理は組み込み Hooks のみ

`useState` / `useRef` / `useEffect` で十分な場合は、Redux / Zustand 等の外部ライブラリを使わない。

```typescript
// ✅ 良い例
const [cogState, setCogState] = useState<CognitiveState>(defaultState);
const stuckAccumMsRef = useRef<number>(0);

// ❌ 悪い例
import { useStore } from 'zustand';  // 不要な外部依存
```

---

### ルール 4: 命名規則

| 種類 | 規則 | 例 |
|---|---|---|
| コンポーネント | PascalCase.tsx | `Dashboard.tsx`, `Overlay.tsx` |
| 変数・関数 | camelCase | `cogState`, `handleUnlock()` |
| 型・インターフェース | PascalCase | `CognitiveState`, `WallServerInfo` |
| CSS クラス | kebab-case | `nudge-overlay`, `zen-timer` |

---

### ルール 5: IPC 失敗時は安全なデフォルト値にフォールバック

Tauri IPC が失敗した場合でもアプリがクラッシュしないよう、try/catch でデフォルト値を返す。

```typescript
// ✅ 良い例
try {
  const state = await invoke<CognitiveState>("get_cognitive_state");
  setCogState(state);
} catch (e) {
  // IPC 失敗時: Flow 100% の安全なデフォルト
  setCogState({ p_flow: 1.0, p_incubation: 0.0, p_stuck: 0.0, label: "Flow" });
  console.warn("IPC failed, using default state:", e);
}
```

---

### ルール 6: 依存 npm パッケージ追加基準

新しいパッケージを追加する前に確認:
- 既存の React / Tauri API で代替できないか？
- バンドルサイズへの影響は許容範囲か？
- ライセンスは MIT / Apache-2.0 互換か？

---

## チェックリスト

- [ ] `any` 型を使っていないか
- [ ] Tauri IPC のレスポンスに型が付いているか
- [ ] ビジネスロジックが Frontend に漏れていないか（閾値計算・状態推定など）
- [ ] 状態管理に外部ライブラリを使っていないか
- [ ] IPC 失敗時のフォールバックが実装されているか
- [ ] コンポーネントが PascalCase になっているか

---

## 補足資料

- `patterns.md` — Tauri IPC 呼び出しパターン・ポーリング実装例

## 関連する他の Skill

- `architecture-rules` — Frontend に置くべきでないもの（ビジネスロジック禁止）の詳細
- `data-privacy` — Frontend で VK コード・文字内容を扱う際の制約
