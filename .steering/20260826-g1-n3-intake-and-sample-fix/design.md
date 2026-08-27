# design — アプローチと変更対象

## アプローチ

★ **順序が設計の本体である。** `preregistration.md §3.4` が見る順序を凍結しているので、
「入力を確定 → 標本を確定 → 宣言 → 判定」の順を崩さない。
⚠️ **判定を 1 回でも見たら前の段階に戻れない**（`§5.3` の封印・`§3.6` の事後変更禁止）。

1. **復号は repo 外**（`gse-unpack`）。生 NDJSON を repo にもコンテキストにも持ち込まない。
2. **客観検証を先に**（`--verify-blocks` はラベルを読まない契約）。計器が壊れていたら
   標本の議論をしても無駄になる。
3. **申し送りはログで裏を取る**。研究者の記憶・ファイル名・私の memory を根拠にしない。
4. **標本の確定は `config.json` の `sample_roster`**（`analyze.py` はここだけを見る）。
5. **判定前の決定は notes.md に書いてから回す**。書いた時点で `results/` が空であることが物証。

## 変更対象

| ファイル | 何を |
|---|---|
| `experiments/.../analyze.py` | ★ `structurally_missing_features()` を新設（`§5.1` の拡張）。selftest を陽性対照つきで追加 |
| `experiments/.../config.json` | `sample_roster` / `status` |
| `experiments/.../env.md` | 確証実施の記録（OS・実施形態・逸脱・判定根拠） |
| `experiments/.../data.md` | 状態（確証標本の人数・判定の有無） |
| `experiments/.../notes.md` | §11（標本の確定）／ §12（判定前の宣言）／ §13（判定） |
| `experiments/.../blocks/*.json` | ⚠️ **gitignore 対象**（NDJSON 名にセッション日時が入る） |
| `~/gse-dataset/raw/` | 復号済み NDJSON（gitignore 済み）＋ B-4 マニフェスト（★ gitignore を追記して塞いだ） |

⚠️ **`preregistration.md` は触らない**（凍結文書の改訂は研究者の行為）。

## テスト戦略

★ **「緑になった」を信用しない。**

| 何を確かめたか | どう確かめたか |
|---|---|
| `analyze.py` の潰しが効くか | ⚠️ **変異 2 種**（潰しの無効化・綴り検証の除去）で selftest が**実際に赤になる**ことを実測 |
| 潰しが実データで効いたか | `load_subject_blocks` を宣言あり/なしで呼び分け、P007 の 10 ブロックを並べて比較 |
| n=3 ゲートが止めるか | roster を 2 名にした状態で `analyze.py` を実行し、`[NG]` と**出力ファイルが作られないこと**を確認 |
| P014 / P016 のズレ | ⚠️ ファイル名でなく **G1-M の回答時刻**（ずらすと +14〜118 秒／ずらさないと +344〜451 秒） |
| 実施 OS | `capabilities` の OS 指紋 ＋ 独立な傍証 2 つ（`ime_shadow` 行 / `starved_ms` の粒度） |
| 出力にプライバシー漏れが無いか | `results/metrics.json` を正規表現で走査（日時 0 件・`ndjson` 文字列なし） |
| 潰しが `degenerate_features` に出るか | ⚠️ **出なかった**（封印のため）。★ 主張を `notes.md §13-3` で訂正した |
