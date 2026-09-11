# 設計スライドを技術・アーキ・研究手段ベースで作り直す

## 背景

未踏の提出物のうち、設計スライド
`docs/mitou_submission/mitou_pptx/[提案プロジェクト補足資料]GSE設計スライド.pptx.md`（現行 24 枚）は
**主張の層構造と縮退設計が中心**であり、研究者が今回指定した
「アーキテクチャ / 各層の処理・計算過程 / 推論モデルの更新と昇格の実施手段 / モデル選定理由とアーキ解説 /
各アーキの構想のつながり」が**ほとんど入っていない**。

さらに、正本 `.pptx.md` から `.pptx` を作る `scripts/md2pptx.py`（478 行）には、
指定を満たすうえで塞がねばならない穴が 5 つある（2026-09-04 実測・引き継ぎ
`.steering/_handoff/next-session-design-slides.md`）:

1. テンプレートを読めない（`build()` が `Presentation()` 既定で始まる）
2. スライドサイズを 13.33 x 7.5 inch へ無条件に上書きする（テンプレートは 10.0 x 5.62）
3. テンプレート同梱の見本 6 枚が出力に残る
4. `![...](...)` 記法を写せない（＝**図を置けない**）
5. 表を pptx の table にしない（行として素朴に流す）

加えて、`_pick_layout` がループの外で 1 回だけ呼ばれるため
**全スライドが「タイトルとコンテンツ」1 種**になる。実測でその本文枠は
**9.01 x 1.60 inch（版面の 3 割弱）のバナー型**であり、⚠️ **図も密度のある技術説明も入らない**。

## ゴール

1. `scripts/md2pptx.py` が **テンプレート（`deck_temp1.pptx`）を土台に、図を含み、
   スライドごとにレイアウトを選べる** pptx を生成できる。`--selftest` が新機能の退行を機械検出する。
2. 指定内容を担う **新規の図を 5〜6 枚**、既存流儀（手書き SVG が正本 → PNG 書き出し）で追加する。
3. 設計スライドを **技術・アーキ・研究手段主軸**に作り直す（想定 28〜34 枚）。
   降ろしてはいけない主張の核（主張の層構造 / 確証するのは L0 だけ / 較正前後の介入可否 / 未実装の明示）は残す。

## スコープ

### 含むもの
- `scripts/md2pptx.py` の改修（テンプレート対応・サイズ非上書き・見本削除・画像埋め込み・
  スライド単位のレイアウト選択・selftest 拡張）
- テンプレート `deck_temp1.pptx` の repo 内への取り込み（生成の再現性のため）
- 新規図 5〜6 枚（`.svg` 正本 + `.png` 書き出し、寸法一致）
- `[提案プロジェクト補足資料]GSE設計スライド.pptx.md` の再構成と `.pptx` 再生成
- `docs/mitou_submission/README.md` の更新（再生成コマンド・枚数・変換器の能力）
- 一次資料との突き合わせ（別エージェント）／`/cross-review`

### 含まないもの
- `scripts/md2docx.py` の変更（`.docx` 4 本には手を入れない）
- 他の未踏文書（詳細資料 / 技術設計書 / 検証レポート / 参考文献）の本文改訂
  ※ ただし **スライドが技術設計書へ委託した計算の証明が、技術設計書に実在するか**は確認する
- `src-tauri/` の実装変更（スライドは既存実装・既存 ADR の記述であり、実装を動かさない）
- 未踏参考文献 `[n]` の新規採番（既存番号の範囲で引く。足す必要が出たら停止して相談）

## 受け入れ条件

- [ ] `PYTHONUTF8=1 python scripts/md2pptx.py --selftest` が緑（★ 新機能の変異体で落ちることを確認済み）
- [ ] 生成 `.pptx` が **10.00 x 5.62 inch**、見本 6 枚が 0 枚、図が実際に埋め込まれている
- [ ] 図を置くスライドが「2 つのコンテンツ」相当のレイアウトを使い、本文枠に収まる
- [ ] `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が緑（★/⚠️ を提出文書に入れない）
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が「違反なし」まで是正済み
- [ ] 新規図の `.png` と `.svg` の寸法が一致（`md2docx.py --selftest` が検査）
- [ ] スライド本文の事実主張が一次資料（コード / ADR / preregistration / research-positioning）と一致
      （★ 別エージェントによる突き合わせ済み。⚠️ 未実装を実装済みと読ませない）
- [ ] PowerPoint / 実表示で目視確認済み
- [ ] `/cross-review` 実施（skip した場合は理由を明記）

## 関連ドキュメント

- `.steering/_handoff/next-session-design-slides.md`（★ 本タスクの発注書・実測値の出典）
- `docs/mitou_submission/README.md`（★ 提出物運用の SSOT）
- `docs/architecture.md` / `docs/architecture/gse-v2-overview.md` ほか architecture/ 配下
- `docs/adr/ADR-019-model-maturity-and-promotion-gate.md`（★ 昇格ゲート）
- `docs/adr/ADR-006` / `ADR-002`（ドメインヘッド）
- `docs/research-positioning.md` / `docs/preregistration-v0.3.md`（★ 主張の正）
- `docs/glossary.md`（⚠️ 禁止用語）

## 運用メモ
- /reimagine 適用: No
- 理由: 発注書（引き継ぎ）が実測に基づいて方針・穴・直し方まで固定しており、
  設計の選択肢は「レイアウト指定を .pptx.md 側でどう表現するか」に限られる。
  その 1 点は design.md の中で 2 案を比較して決める。
