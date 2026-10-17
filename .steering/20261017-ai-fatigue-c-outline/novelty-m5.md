# M5（報告の不整合）の新規性の確認（2026-10-17）

- 方法: サブエージェント（Sonnet・Web と無料の API・読むだけ）が 16 本の検索（Europe PMC 7・OpenAlex 6・WebSearch 3、各 15 件ほどを目で見た）を回した。近い 3 件は、メインが DataCite・Crossref の記録で題名と著者を照合した。
- 結果: AI 疲労の一次研究について、報告の内的な不整合（N と分母・効果の向き・判別妥当性の記載と値・倫理・コードブックと一致度・再計算）を体系的にコード化した研究は、**この検索の範囲では見つからなかった**（無いとは言わない）。
- 近いもの（いずれも報告の内的な整合の再計算はしていない）:
  - Jonaid, A. (2026). Measurement Properties and Cross-Cultural Validity of AI Anxiety and AI Attitude Scales: A COSMIN Systematic Review. OSF. doi:10.17605/osf.io/3qasd（AI 不安・態度の尺度の測定特性と不変性の検定の方法の質。メインが DataCite で照合）
  - Leite, Â. (2026). Data and Materials: Psychometric Properties of Self-Report Instruments Measuring Human-AI Relational and Attitudinal Constructs — A COSMIN-Based Systematic Review… Zenodo. doi:10.5281/zenodo.22643950（資料の寄託。メインが DataCite で照合）
  - Kempny, C., et al. (2026). The use and methodological reporting of large language models in qualitative research: a scoping review. *BMC Med Res Methodol*. doi:10.1186/s12874-026-02913-1（LLM を道具に使う質的研究の報告。メインが Crossref で照合）
- 限界: extended の検索・Google Scholar・PsyArXiv の全文・PubPeer は使っていない。既知のレビュー（Ragolane & Patel 2025 ほか）が再び当たらなかったので、拾えていない語の領域がある。
- C への含み: M5（C4）は、AI に関わる尺度の COSMIN 系のレビュー（測定特性）と別の軸（報告の内的な整合）として位置づけられる。COSMIN 系の 2 件は、背景で引く候補（引くときに `citation-ssot` で登録する）。
