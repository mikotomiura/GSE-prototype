# G1 P-1（macOS 回）の後処理と、P-1 が見つけた不具合の是正

## 背景

2026-08-04 に **P-1 の macOS 回（`PILOT-mac` / topic02）が研究者本人によって実施された**。
`.steering/_handoff/next-session-prompt-g1-p1-run-and-followups.md` §2 が「実施後にやること」を
定めているが、実施セッションでは後処理まで到達していなかった。

提出物は `~/Documents/GSE-submissions/` に **`.age` 4 本**（ブロック 1〜4）。
⚠️ 生 NDJSON は `~/Documents/GSE-sessions/` に **2 本しか残っていなかった**ため、
`.age` を `gse-unpack` で復号して 4 本そろえるところから始める必要があった。

さらに研究者から、実施中に感じた**3 つの違和感**が報告された。
★ **いずれも P-1 の目的 (ii)「課題文と実施手順が機能するか」（`preregistration.md §2.8`）に
真正面から当たる**ので、P-1 の成果として扱う。

1. **bash ターミナル前提の運用**が、研究者以外の被験者には難度が高い
2. **3 ブロック目の課題文（`topic02_lo` 商店街の駐輪場）が矛盾している**
   —— 料金表（2 時間無料＋以降は一日 100 円）と割引券（2 時間分の追加無料券）が噛み合わない
3. 記入ページの **「消去して次のブロックへ」を押しても次のブロックへ行かない**

## ゴール

1. P-1 macOS 回のデータが `gse-dataset` に載り、`validate_blocks.py --dataset` が緑
2. P-1 の主目的「5 分で十分な打鍵が出るか」の**実測値**が記録に残っている
3. 上記 3 件が、**直せるものは直り、直さないものは「直さない理由」ごと記録**されている
4. `run.sh` GREEN と各 `--selftest` 緑が維持されている

## スコープ

### 含むもの

- `.age` の復号 → `~/gse-dataset/raw/PILOT-mac/` 配置 → 割付ファイルへの転記
- `analyze.py --verify-blocks` の**初回実行**と、その出力の健全性確認
- `HMM_VERSION` の刻印（`env.md` / `config.json`）
- `topic02_lo` の不整合の是正（`§2.8` が「パイロットを見て変えてよい」と明示している範囲）
- ★ **全 8 題材の lo 版の再監査**（1 件見つかった以上、他も見る）
- 記入ページのボタンラベルの是正と、**同型のバグを捕まえる機械検査の追加**
- ターミナル依存の**記録と設計案の提示**

### 含まないもの

- ★ **判定（`§3`）は一切行わない**（`§2.8` の凍結。P-1 は打鍵の量と手順だけを見る）
- ★ **`preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` の変更**
- **アプリ内 G1 モード（案 3 ＋ 案 B）の実装** — `§5.4` に触るため**第 10 版の論証が必要**。
  研究者判断で**別セッション送り**（2026-08-05 確認）
- Windows 回（`PILOT-win`）の実施 — **未実施のまま**

## 受け入れ条件

- [x] `~/gse-dataset/raw/PILOT-mac/` に 4 本の NDJSON がある
- [x] 4 本とも `probe_assignment` / `probe_triggered` / `realtime_label` が **0 行**
- [x] `validate_blocks.py --dataset ~/gse-dataset` が **緑**
- [x] `analyze.py --verify-blocks` が動き、打鍵数と実測長が記録された
- [x] `config.json` / `env.md` の `HMM_VERSION` が**実測値**で埋まっている
- [x] `validate_materials.py --strict` が緑（総文字数 5% 制約を維持）
- [x] `build_task_pages.py --selftest` が緑（★ 追加した検査が**空回りしていない**ことを含む）
- [x] `run.sh` が GREEN

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/preregistration.md` §2.2 / §2.8 / §2.13 / §5.4
- `experiments/20260801-controlled-friction-task/protocol.md` §1 / §4.4 / §6.1
- `.steering/_handoff/next-session-prompt-g1-p1-run-and-followups.md`

## 運用メモ

- /reimagine 適用: No
- 理由: 実測データの後処理と、実施で露見した具体的な不具合の是正。設計の選択肢が
  開いている箇所（アプリ内 G1 モード）は本タスクのスコープ外に置いた。
