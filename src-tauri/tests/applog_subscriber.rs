//! ★ **本物の購読者を通して**、`tracing::info!` がファイルに落ちることを確かめる。
//!
//! # ⚠️ なぜ単体テストと別に要るのか
//!
//! `applog.rs` の単体テストは `MakeWriter` から下 (channel → スレッド → ファイル) しか見ない。
//! ⚠️ ★ **今回直したバグはそこではない。** 壊れていたのは
//! 「購読者がどこへ書くように配線されているか」であり、
//! `tracing_subscriber::fmt::init()` = stdout だけ、という**配線の間違い**だった。
//! → ★ `tracing::info!` から始めて、ファイルの中身で終わるところまでを 1 本で通す。
//!
//! # ⚠️ なぜ統合テスト (別プロセス) なのか
//!
//! `init_tracing` はグローバル購読者を設置する。★ **プロセスにつき 1 回しかできない**ので、
//! 他のテストと同居させられない。統合テストのファイルは 1 本ごとに別プロセスで走る。

use std::time::{Duration, Instant};

#[test]
fn info_events_reach_the_log_file() {
    let dir = std::env::temp_dir().join(format!("gse-applog-it-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    let path = dir.join("gse-app.log");

    // ★ 本物の初期化をそのまま呼ぶ (`lib.rs` の `run()` が呼ぶのと同じ関数)。
    gse_next_lib::applog::init_tracing(&path);

    // ★ 実際に起きる形で出す: G1 自動提出の失敗ログと同じ `error!` を含める。
    tracing::info!("integration: app started");
    tracing::error!("integration: G1 auto-submit detail: something went wrong");
    // ⚠️ `debug!` はファイルに出てはならない (`data-privacy` ルール 1 の防波堤)。
    tracing::debug!("integration: VK=0x41 must not reach the file");

    let deadline = Instant::now() + Duration::from_secs(10);
    let body = loop {
        let body = std::fs::read_to_string(&path).unwrap_or_default();
        if body.contains("integration: G1 auto-submit detail") || Instant::now() > deadline {
            break body;
        }
        std::thread::sleep(Duration::from_millis(20));
    };

    assert!(
        body.contains("integration: app started"),
        "★ info がファイルに出ていない。購読者の配線が壊れている:\n{body}"
    );
    assert!(
        body.contains("integration: G1 auto-submit detail: something went wrong"),
        "★ error がファイルに出ていない (これが「詳細はローカルのログにだけ残す」の本体):\n{body}"
    );
    assert!(
        !body.contains("VK=0x41"),
        "⚠️★ debug がファイルに落ちている。キーコードがディスクに残る (data-privacy ルール 1):\n{body}"
    );
    // ★ ANSI エスケープが混ざっていないこと (混ざると研究者が読めない)。
    assert!(
        !body.contains('\u{1b}'),
        "★ ANSI エスケープ列がファイルに入っている:\n{body:?}"
    );

    let _ = std::fs::remove_dir_all(&dir);
}
