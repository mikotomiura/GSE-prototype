# requirement — deep-silence fixture + golden (Epic2 安全網の残タスク C)

## 背景
PR #74 の Epic2 golden 監査 (② track) が「深い沈黙フロア (loop_step.rs 8/10/30s 分岐・f6_floor/
f3_floor・pre_silence_features) は **どの fixture も駆動せず全 fixture で f6=0＝完全未ガード**」と指摘
(監査 row 3)。PR #74 では fixture 新規作成を伴うため別 PR に分離した、その C を実施する。

- 凍結対象 (不触): engine.rs(HMM_VERSION)/intervention 閾値/probe_scheduler/schema/App.tsx lock/preregistration。
  本タスクは fixture(テストデータ) + golden(現行挙動の記録) + テスト1行追加のみ＝エンジン挙動不変。
- ベース: origin/main @f0b9a7c。ブランチ test/deep-silence-golden。

## ゴール
深い沈黙のフロア分岐を byte-equal で守る golden を追加し、`replay_snapshot_goldens_byte_equal` に組み込む。

## 受け入れ条件
- [ ] `deep_silence.ndjson` fixture が 8/10/30s フロア分岐を実際に踏む (f6>0・f3>0 が沈黙域で出る)。
- [ ] TransitionPath (ctx フロア) と SilencePath (make_silence_observation) の両方を通す。
- [ ] golden 決定論的 (2回生成で同一)・round-trip `--snapshot` exit 0。
- [ ] `cargo test --bin gse-replay` 全パス。
- [ ] 凍結対象の変更ゼロ。

## 非スコープ
- エンジン挙動変更・HMM_VERSION bump。
