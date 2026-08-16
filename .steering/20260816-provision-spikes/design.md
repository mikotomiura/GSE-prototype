# 設計 — 配布自動化 spike

⚠️ ★ **配布自動化そのものの設計は `.steering/20260807-vps-provisioning-automation/design.md` が
SSOT である。** ここはそれを覆さず、**spike をどう安全な順で走らせるか**だけを決める。

## ★ 実行順序（⚠️ 順序そのものが安全装置である）

```
[1] 資格情報を取る ───────────────────────────► spike-3 の時計はここで始まる
        │                                        (発行時刻を記録し、後日 失効を確かめる)
        ▼
[2] 偽 API で drive_client.py のテストを緑にする  ★ Drive を叩く前
        │                                        ⚠️ 照合が赤→共有しない (D-4) を
        ▼                                           実装より先にテストで固定する
[3] PILOT-spike を生成 ──────────────────────► 実被験者の割付を使わない (S-2)
        │
        ▼
[4] 捨ての親フォルダを用意 ───────────────────► ⚠️ 新クライアント自身に作らせない
        │                                        (それでは spike-1 の条件を満たさない)
        ▼
[5] spike-1 子フォルダ作成
        │  否 → ★ 代替 (親もアプリに作らせる) へ切り替えて続行
        ▼
[6] spike-4 mimeType ＋ spike-5 sha256Checksum   ★ 同じ 1 回のアップロードで連続して見る
        │                                        ⚠️ 4 が否 (Google 形式に変換) なら 5 は無意味
        ▼
[7] spike-2 共有 → ★ 読み返す → ★ 即座に外す
        │  否 → ⚠️ 止めて相談 (匿名性の設計に触る)
        ▼
[8] 後始末 (捨てフォルダ削除・PILOT-spike 削除) → spike-results.md
        │
        ▼
[9] 後日: spike-3 の失効確認
```

### ⚠️★ なぜ spike-2（共有）を最後に置くか

`decisions.md` D-4 は「照合が緑になるまで共有しない」だが、★ spike でも同じ規律を守る。
⚠️ 先に共有をかけてからアップロードを試すと、**壊れた/不完全な状態が公開されている窓**ができる。
捨てフォルダとはいえ `type=anyone` は世界に開く操作なので、★ **開ける時間を最小にする**
（確認したら即座に外す）。

### ⚠️★ なぜ [2] を Drive より先に置くか

★ 偽 API のテストは資格情報も Drive も要らない。⚠️ 先に Drive を叩いてしまうと、
「動いたから良し」で **順序（照合→共有）を実装で固定し損ねる**。
D-4 は**順序が逆だと fail-open** なので、ここは実装より先にテストで縛る。

## 変更対象

### 新規作成
- `experiments/20260801-controlled-friction-task/drive_client.py` — 薄い Drive API ラッパ（S-3）
- `experiments/20260801-controlled-friction-task/test_drive_client.py` — 偽 API の単体テスト
- `scripts/provision-credentials.md` — ⚠️ **秘密そのものは置かない**。取り方と置き場だけ
- `.steering/20260816-provision-spikes/spike-results.md` — ★ 実測値の記録

### 変更
- `scripts/requirements-dev.txt` — ★ 既存規約どおりバージョン固定で追記
- `docs/glossary.md` — ★ grill で確定した用語（追記済み）

### ⚠️ 触らない
- `provision.py`（Stage 1 本体）／ VPS ／ systemd
- `prepare-subjects.sh` / `make-upload-manifest.sh` / `verify-drive-upload.py`（D-5 の退路）
- `Form_G1/`（GAS。D-3 の④で「1 行も変えない」）
- ★ **G1 本番の配布物**: `dist/_drive/` / `blocks/P0*.json` / 本番の親フォルダ

## テスト戦略

- **偽 API の単体テスト**（`tasklist.md` §2）が本丸。⚠️ **陽性対照込み**で回し、
  ★「常に緑を返すガード」を緑と読み違えない（memory `silent-failure-in-guard-scripts`）。
- **統合**は捨てフォルダでの 1 人ぶん実走のみ。⚠️ 本番の親フォルダで試さない。
- **回帰**: このタスクは既存コードを変えないので、⚠️ 既存テストが赤くなったら
  ★ それは「変えないつもりで変えた」ことの検出である。

## ⚠️★ 測定器そのものを疑う点（memory `measurement-instrument-false-positives`）

- spike-4 の「`text/html` のまま」を **API の応答 (`mimeType`) だけ**で判定しない。
  ★ 実際にダウンロードして手元と byte を突き合わせる（Google 形式に変換されると別物になる）。
- spike-5 で `sha256Checksum` が返っても、⚠️ それが**手元の SHA と一致するか**まで見る。
  ★ 「フィールドが存在した」を「照合できた」と読み替えない。
- spike-2 の「共有できた」を `permissions.create` の成功だけで言わない。
  ★ `permissions.list` で**読み返し**、`allowFileDiscovery=false` を確かめる。

## ロールバック計画

★ このタスクは既存の配布経路を**一切変えない**ので、失敗しても G1 の運用に影響しない。
⚠️ 唯一の外界への副作用は「捨てフォルダの作成と一時共有」であり、
★ 後始末（削除）が Done 条件に入っている。
