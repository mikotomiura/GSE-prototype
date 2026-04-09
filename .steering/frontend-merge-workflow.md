# フロントエンド統合ワークフロー

## 概要

Rust バックエンドのクロスプラットフォーム統合は完了（commit 5e3c85c）。
残りはフロントエンド（src/ 配下の TypeScript/React）の差分マージ。

## 対象ファイルと差分の性質

| ファイル | diff行数 | 差分の性質 |
|---|---|---|
| `App.css` | ~485行 | macOS版に追加のUIスタイル（スタート画面、パーミッションバナー等）。Windows版にないスタイルを追加する方向。 |
| `App.tsx` | ~154行 | 変数順序、コメント言語、Lv2累積タイマーの変数名 (`stuckAccMsRef` vs `stuckAccumMsRef`)、hookActive の初期化タイミング |
| `Overlay.tsx` | ~191行 | Wall Server state管理の構造差（macOS: `qrSvg`/`serverUrl` 個別state → Windows: `wallServerInfo` オブジェクト）、クリック透過のタイミング差 |
| `Dashboard.tsx` | ~68行 | prop順序、パーミッションバナーのテキスト（macOS: "Input Monitoring"）、コメント差 |

## 統合方針

### 原則
- **プラットフォーム判定はフロントエンドで行わない**
- `get_hook_status()` の返値で UI を変更する（既に両方同じ仕組み）
- Windows 版のコードをベースに、macOS 版の改善点を取り込む

### ファイル別の方針

#### 1. App.css（最大差分）
- macOS版に追加されたスタイル（`.start-screen`, `.start-button`, permission系）を Windows版に追加
- 重複するセレクタは Windows 版の値を優先（既に動作確認済みのため）
- macOS 固有のスタイル（`-webkit-*` prefix）はそのまま追加（Windows では無視される）

#### 2. App.tsx
- 変数名を `stuckAccumMsRef` に統一（Windows版）
- hookActive/keyboardIdleMs の宣言順序を統一
- Lv2累積タイマーの実装は Windows 版を採用（Ref ミラーパターンがより堅牢）
- コメントは日英混在を許容（既存スタイル踏襲）

#### 3. Overlay.tsx
- `wallServerInfo` オブジェクトパターン（Windows版）を採用
- クリック透過のタイミング: Windows版の実装を採用
  - マウント直後に `setIgnoreCursorEvents(true)` で即座に透過
  - `isWallActive` 変更時にトグル
- `earlyUnlockBtn`（早期解除ボタン）は両方に存在するので問題なし

#### 4. Dashboard.tsx（最小差分）
- prop 順序を統一
- パーミッションバナー: `hookActive === false` で表示する仕組みは共通
  - テキストは「キーボード監視の権限が必要です」に統一（OS非依存）
  - 具体的な手順（Input Monitoring / 管理者権限）は `hookActive` の値に基づいて出し分け可能だが、現時点では不要（Windowsでは常にtrue）

## 実行手順

```
1. ブランチ作成: feature/frontend-merge
2. App.css のマージ（macOS版の追加スタイルを取り込み）
3. Dashboard.tsx のマージ（最小差分、低リスク）
4. App.tsx のマージ（変数名統一、タイマーロジック確認）
5. Overlay.tsx のマージ（構造差の解消）
6. `npm run dev` で Windows 動作確認
7. commit & push → CI で macOS ビルドも確認
```

## macOS リポからの参照元

macOS 版のフロントエンドは以下にクローン済み（一時ファイル）:
```
/tmp/gse-mac/src/
├── App.tsx
├── App.css
└── components/
    ├── Dashboard.tsx
    └── Overlay.tsx
```

再クローンが必要な場合:
```bash
git clone https://github.com/mikotomiura/GSE-prototype-for-mac.git /tmp/gse-mac
```

## 完了後の後処理

- [ ] GSE-prototype-for-mac リポの README に統合先を記載
- [ ] GSE-prototype-for-mac リポをアーカイブ
