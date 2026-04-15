//! gse-dataset repo に置く JSON Schema を機械生成する。
//!
//! 使い方:
//!   cargo run --bin emit_schema > ../gse-dataset/schema/current.json
//!
//! CI (.github/workflows/ci.yml) では出力を src-tauri/schema/current.json と diff して
//! schema drift を検知する。gse-prototype 側のコミット済みゴールデンは
//! src-tauri/schema/current.json で、gse-dataset 側はそのコピー。同期ルーティンは
//! docs/development-guidelines.md §Session データ管理 を参照。

use std::io::{self, Write};
use std::process::ExitCode;

use gse_next_lib::schema_dto::LogEntryDto;
use schemars::schema_for;

fn main() -> ExitCode {
    let schema = schema_for!(LogEntryDto);
    let json = match serde_json::to_string_pretty(&schema) {
        Ok(s) => s,
        Err(e) => {
            let _ = writeln!(
                io::stderr(),
                "emit_schema: failed to serialize schema: {}",
                e
            );
            return ExitCode::from(1);
        }
    };
    let stdout = io::stdout();
    let mut lock = stdout.lock();
    if let Err(e) = writeln!(lock, "{}", json) {
        let _ = writeln!(io::stderr(), "emit_schema: stdout write failed: {}", e);
        return ExitCode::from(1);
    }
    ExitCode::SUCCESS
}
