# Phase 1 パイロット実機フィードバック修正

## 背景

前タスク `20260624-phase1-form-survey-design`（Phase 1 検証フォーム／自己効力感尺度確定）の
実機起動で 3 件の問題が判明した。いずれも Phase 1 較正データ収集の品質に直結する。
詳細は本ディレクトリ `next-session-prompt.md`（前セッションの根本原因調査を含む）。

## ゴール

実機起動で判明した 3 件を、データ品質とプレレジ整合性を保ったまま修正する。

- **#1（最優先・バグ）**: プローブ/Nudge カードのボタンが効かず出っぱなしになる問題を、
  実 repro でエラー文字列を確定したうえで根本修正し、無限再表示ループを断つ。
- **#2（測定整合）**: 第2週ダッシュボードの 3 状態（Flow/Incubation/Stuck）表示が
  プローブ回答をアンカリングする恐れ → ユーザー確定の上で表示方針を是正。
- **#3（プレレジ変更）**: 自作 TSE 尺度を 5 件法→4 件法（偶数・強制選択）に。
  採点法（逆転再コード 6−x→5−x）の再プレレジを含む。ユーザー確定の上で実装。

## スコープ

### 含むもの
- #1: `Overlay.tsx` / `ProbeCard.tsx` フロント修正 + `src-tauri/src/lib.rs` backend 修正
  （log channel / build_probe_ref / window_ms）+ カードのインラインエラー/リトライ UX。
- #2: `Dashboard.tsx` の第2週モデル出力表示方針の是正（A/B/C 案からユーザー確定）。
- #3: `Form_Phase1/GSE_Phase1_Form_Builder.gs` の `TSE_ITEMS` 件法変更 +
  `preregistration-tse-scale.md` / decisions / `設問草案.md` の採点法同期（decisions FD10 記録）。

### 含まないもの
- F3 プローブ（Q1摩擦/Q2前進, 1–5）の件法変更（X1 較正の正解ラベル。ユーザーに別途確認するまで不変）。
- GSE-10 公式 4 件法の改変（変更不可）。
- HMM 挙動変更（必要になった場合のみ HMM_VERSION bump + ゴールデン再生成）。
- 作業ツリーの無関係な未ステージ変更（提案書削除 / budget.json / scripts mode / MEMO）。

## 受け入れ条件

- [ ] #1: 実 repro でエラー文字列を確定し、根本原因を backend で修正。ボタン押下でカードが確実に閉じる。
- [ ] #1: 失敗継続時にインラインエラー/リトライが出て「死んだボタン」化と無限再表示を断つ。
- [ ] #2: ユーザー確定した方針で第2週のモデル出力アンカリングを排除。
- [ ] #3: ユーザー確定の上で TSE を 4 件法化、採点法 5−x をプレレジ/設問草案/decisions に同期（FD10）。
- [ ] 完了時 code-reviewer + `/cross-review`（無関係な未ステージ変更を混ぜない）。

## 関連ドキュメント

- 本 steering `next-session-prompt.md`（file:line 付き根本原因調査）
- 前タスク `.steering/20260624-phase1-form-survey-design/`（decisions FD1–FD9・`preregistration-tse-scale.md`）
- `src/components/{Overlay,ProbeCard,Dashboard}.tsx`、`src-tauri/src/{lib,logger}.rs`
- `Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md` §4.3/§4.4/§5.2、`GSE_Phase1_Form_Builder.gs`

## 運用メモ
- /reimagine 適用: No
- 理由: #1 はバグ修正で repro→根本原因が先（実装案の分岐は大きくない）。#2/#3 は
  方針自体をユーザー確定で決めるため、設計案の破壊と再構築より「案提示→確定」が適切。
