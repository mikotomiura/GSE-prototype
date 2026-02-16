cargo :        Fresh unicode-ident v1.0.24
発生場所 行:1 文字:1
+ cargo test --verbose 2>&1 | Tee-Object -FilePath $env:TEMP\cargo_test ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (       Fresh unicode-ident v1.0.24:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
       Fresh autocfg v1.5.0
       Fresh cfg-if v1.0.4
       Fresh proc-macro2 v1.0.106
       Fresh getrandom v0.2.17
       Fresh quote v1.0.44
       Fresh libm v0.2.16
       Fresh zerocopy v0.8.39
       Fresh rand_core v0.6.4
       Fresh windows_x86_64_msvc v0.52.6
       Fresh bytemuck v1.25.0
       Fresh num-traits v0.2.19
       Fresh syn v2.0.116
       Fresh ppv-lite86 v0.2.21
       Fresh windows-targets v0.52.6
       Fresh safe_arch v0.7.4
       Fresh rand_chacha v0.3.1
       Fresh windows-link v0.2.1
       Fresh once_cell v1.21.3
       Fresh windows-result v0.2.0
       Fresh num-integer v0.1.46
       Fresh syn v1.0.109
       Fresh tracing-core v0.1.36
       Fresh rand v0.8.5
       Fresh paste v1.0.15
       Fresh approx v0.5.1
       Fresh num-complex v0.4.6
       Fresh wide v0.7.33
       Fresh rawpointer v0.2.1
       Fresh lazy_static v1.5.0
       Fresh simba v0.6.0
       Fresh rand_distr v0.4.3
       Fresh serde_core v1.0.228
       Fresh typenum v1.19.0
       Fresh matrixmultiply v0.3.10
       Fresh nalgebra-macros v0.1.0
       Fresh windows-strings v0.1.0
       Fresh windows-sys v0.61.2
       Fresh num-rational v0.4.2
       Fresh windows-implement v0.58.0
       Fresh windows-interface v0.58.0
       Fresh log v0.4.29
       Fresh zmij v1.0.21
       Fresh nalgebra v0.29.0
       Fresh windows-core v0.58.0
       Fresh nu-ansi-term v0.50.3
       Fresh sharded-slab v0.1.7
       Fresh tracing-log v0.2.0
       Fresh tracing-attributes v0.1.31
       Fresh serde_derive v1.0.228
       Fresh thread_local v1.1.9
       Fresh itoa v1.0.17
       Fresh smallvec v1.15.1
       Fresh pin-project-lite v0.2.16
       Fresh memchr v2.8.0
       Fresh tracing-subscriber v0.3.22
       Fresh serde v1.0.228
       Fresh windows v0.58.0
       Fresh statrs v0.16.1
       Fresh chrono v0.4.43
       Fresh serde_json v1.0.149
       Fresh tracing v0.1.44
   Compiling gse-prototype v0.1.0 (C:\gse-prototype)
warning: unused import: `std::time::Duration`
  --> tests\integration_tests.rs:11:9
   |
11 |     use std::time::Duration;
   |         ^^^^^^^^^^^^^^^^^^^
   |
   = note: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default
warning: unused variable: `state1`
   --> tests\integration_tests.rs:200:13
    |
200 |         let state1 = hmm.update(1500.0); // Very slow observation
    |             ^^^^^^ help: if this is intentional, prefix it with an underscore: `_state1`
    |
    = note: `#[warn(unused_variables)]` (part of `#[warn(unused)]`) on by default
     Running `C:\Users\johnd\.rustup\toolchains\stable-x86_64-pc-windows-msvc\bin\rustc.exe --crate-name gse_pr
ototype --edition=2021 src\main.rs --error-format=json --json=diagnostic-rendered-ansi,artifacts,future-incompa 
t --emit=dep-info,link -C embed-bitcode=no -C debuginfo=2 --test --check-cfg cfg(docsrs,test) --check-cfg "cfg( 
feature, values())" -C metadata=5436d8116e0611d8 -C extra-filename=-e5e592f42aea4c40 --out-dir C:\gse-prototype 
\target\debug\deps -C incremental=C:\gse-prototype\target\debug\incremental -L dependency=C:\gse-prototype\targ 
et\debug\deps --extern chrono=C:\gse-prototype\target\debug\deps\libchrono-016dd7f0040ce807.rlib --extern once_ 
cell=C:\gse-prototype\target\debug\deps\libonce_cell-0c3a3c223d21dba8.rlib --extern serde=C:\gse-prototype\targ 
et\debug\deps\libserde-b2137b98591bd257.rlib --extern serde_json=C:\gse-prototype\target\debug\deps\libserde_js 
on-a4bf0c4ea4a3d491.rlib --extern statrs=C:\gse-prototype\target\debug\deps\libstatrs-87a73b30334d36c5.rlib --e 
xtern tracing=C:\gse-prototype\target\debug\deps\libtracing-d399d6a8142c25ea.rlib --extern tracing_subscriber=C 
:\gse-prototype\target\debug\deps\libtracing_subscriber-f0cfdb883b4efbae.rlib --extern windows=C:\gse-prototype 
\target\debug\deps\libwindows-a870f41ed452b263.rlib -L native=C:\Users\johnd\.cargo\registry\src\index.crates.i 
o-1949cf8c6b5b557f\windows_x86_64_msvc-0.52.6\lib`
     Running `C:\Users\johnd\.rustup\toolchains\stable-x86_64-pc-windows-msvc\bin\rustc.exe --crate-name gse_pr
ototype --edition=2021 src\main.rs --error-format=json --json=diagnostic-rendered-ansi,artifacts,future-incompa 
t --crate-type bin --emit=dep-info,link -C embed-bitcode=no -C debuginfo=2 --check-cfg cfg(docsrs,test) --check 
-cfg "cfg(feature, values())" -C metadata=7eef20a2548f83eb --out-dir C:\gse-prototype\target\debug\deps -C incr 
emental=C:\gse-prototype\target\debug\incremental -L dependency=C:\gse-prototype\target\debug\deps --extern chr 
ono=C:\gse-prototype\target\debug\deps\libchrono-016dd7f0040ce807.rlib --extern once_cell=C:\gse-prototype\targ 
et\debug\deps\libonce_cell-0c3a3c223d21dba8.rlib --extern serde=C:\gse-prototype\target\debug\deps\libserde-b21 
37b98591bd257.rlib --extern serde_json=C:\gse-prototype\target\debug\deps\libserde_json-a4bf0c4ea4a3d491.rlib - 
-extern statrs=C:\gse-prototype\target\debug\deps\libstatrs-87a73b30334d36c5.rlib --extern tracing=C:\gse-proto 
type\target\debug\deps\libtracing-d399d6a8142c25ea.rlib --extern tracing_subscriber=C:\gse-prototype\target\deb 
ug\deps\libtracing_subscriber-f0cfdb883b4efbae.rlib --extern windows=C:\gse-prototype\target\debug\deps\libwind 
ows-a870f41ed452b263.rlib -L native=C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows 
_x86_64_msvc-0.52.6\lib`
warning: `gse-prototype` (test "integration_tests") generated 2 warnings (run `cargo fix --test "integration_te
sts" -p gse-prototype` to apply 2 suggestions)
error[E0432]: unresolved import `windows::Win32::UI::WindowsAndMessaging::PostQuitMessageW`
 --> src\main.rs:4:59
  |
4 |     GetMessageW, TranslateMessage, DispatchMessageW, MSG, PostQuitMessageW,
  |                                                           ^^^^^^^^^^^^^^^^
  |                                                           |
  |                                                           no `PostQuitMessageW` in `Win32::UI::WindowsAndMe
ssaging`
  |                                                           help: a similar name exists in the module: `PostQ 
uitMessage`
error[E0432]: unresolved import `windows::Win32::UI::WindowsAndMessaging::VK_BACK`
 --> src\input\keyboard.rs:8:34
  |
8 |     WM_KEYDOWN, KBDLLHOOKSTRUCT, VK_BACK,
  |                                  ^^^^^^^ no `VK_BACK` in `Win32::UI::WindowsAndMessaging`
error[E0432]: unresolved imports `windows::Win32::UI::WindowsAndMessaging::GetMonitorInfoW`, `windows::Win32::U
I::WindowsAndMessaging::MonitorFromPoint`, `windows::Win32::UI::WindowsAndMessaging::MONITORINFO`, `windows::Wi 
n32::UI::WindowsAndMessaging::MONITOR_DEFAULTTOPRIMARY`
  --> src\ui\overlay.rs:11:22
   |
11 |     CreateWindowExW, GetMonitorInfoW, MonitorFromPoint, GetSystemMetrics,
   |                      ^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^ no `MonitorFromPoint` in `Win32::UI::WindowsAndMess 
aging`
   |                      |
   |                      no `GetMonitorInfoW` in `Win32::UI::WindowsAndMessaging`
...
14 |     MONITORINFO, MONITOR_DEFAULTTOPRIMARY, LWA_ALPHA, LWA_COLORKEY,
   |     ^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^ no `MONITOR_DEFAULTTOPRIMARY` in `Win32::UI::WindowsAndMessaging
`
   |     |
   |     no `MONITORINFO` in `Win32::UI::WindowsAndMessaging`
   |
help: a similar name exists in the module
   |
11 -     CreateWindowExW, GetMonitorInfoW, MonitorFromPoint, GetSystemMetrics,
11 +     CreateWindowExW, GetMenuBarInfo, MonitorFromPoint, GetSystemMetrics,
   |
help: a similar name exists in the module
   |
11 -     CreateWindowExW, GetMonitorInfoW, MonitorFromPoint, GetSystemMetrics,
11 +     CreateWindowExW, GetMonitorInfoW, MenuItemFromPoint, GetSystemMetrics,
   |
error[E0432]: unresolved import `windows::Win32::Graphics::Gdi::RGB`
  --> src\ui\overlay.rs:16:5
   |
16 | use windows::Win32::Graphics::Gdi::RGB;
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ no `RGB` in `Win32::Graphics::Gdi`
warning: unused import: `RECT`
 --> src\ui\overlay.rs:9:40
  |
9 | use windows::Win32::Foundation::{HWND, RECT};
  |                                        ^^^^
  |
  = note: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default
warning: unused import: `LWA_COLORKEY`
  --> src\ui\overlay.rs:14:55
   |
14 |     MONITORINFO, MONITOR_DEFAULTTOPRIMARY, LWA_ALPHA, LWA_COLORKEY,
   |                                                       ^^^^^^^^^^^^
error[E0369]: binary operation `!=` cannot be applied to type `std::sync::MutexGuard<'_, Option<FlowState>>`
   --> src\input\keyboard.rs:143:51
    |
143 | ...                   if last_state != Some(FlowState::Flow) {
    |                          ---------- ^^ --------------------- Option<FlowState>
    |                          |
    |                          std::sync::MutexGuard<'_, Option<FlowState>>
    |
note: `std::sync::MutexGuard<'_, Option<FlowState>>` does not implement `PartialEq<Option<FlowState>>`
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\std\src\sync\poison\mutex.rs:277:1
    |
    = note: `std::sync::MutexGuard<'_, Option<FlowState>>` is defined in another crate
error[E0369]: binary operation `!=` cannot be applied to type `std::sync::MutexGuard<'_, Option<rules::FlowStat
e>>`
   --> src\input\keyboard.rs:143:51
    |
143 | ...                   if last_state != Some(FlowState::Flow) {
    |                          ---------- ^^ --------------------- Option<rules::FlowState>
    |                          |
    |                          std::sync::MutexGuard<'_, Option<rules::FlowState>>
    |
note: `std::sync::MutexGuard<'_, Option<rules::FlowState>>` does not implement `PartialEq<Option<rules::FlowSta 
te>>`
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\std\src\sync\poison\mutex.rs:277:1
    |
    = note: `std::sync::MutexGuard<'_, Option<rules::FlowState>>` is defined in another crate
error[E0369]: binary operation `!=` cannot be applied to type `std::sync::MutexGuard<'_, Option<FlowState>>`    
   --> src\input\keyboard.rs:158:51
    |
158 | ...                   if last_state != Some(FlowState::Incubation) {
    |                          ---------- ^^ --------------------------- Option<FlowState>
    |                          |
    |                          std::sync::MutexGuard<'_, Option<FlowState>>
    |
note: `std::sync::MutexGuard<'_, Option<FlowState>>` does not implement `PartialEq<Option<FlowState>>`
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\std\src\sync\poison\mutex.rs:277:1
    |
    = note: `std::sync::MutexGuard<'_, Option<FlowState>>` is defined in another crate
error[E0369]: binary operation `!=` cannot be applied to type `std::sync::MutexGuard<'_, Option<rules::FlowStat 
e>>`
   --> src\input\keyboard.rs:158:51
    |
158 | ...                   if last_state != Some(FlowState::Incubation) {
    |                          ---------- ^^ --------------------------- Option<rules::FlowState>
    |                          |
    |                          std::sync::MutexGuard<'_, Option<rules::FlowState>>
    |
note: `std::sync::MutexGuard<'_, Option<rules::FlowState>>` does not implement `PartialEq<Option<rules::FlowSta
te>>`
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\std\src\sync\poison\mutex.rs:277:1
    |
    = note: `std::sync::MutexGuard<'_, Option<rules::FlowState>>` is defined in another crate
error[E0369]: binary operation `!=` cannot be applied to type `std::sync::MutexGuard<'_, Option<rules::FlowStat 
e>>`
   --> src\input\keyboard.rs:173:51
    |
173 | ...                   if last_state != Some(FlowState::Stuck) {
    |                          ---------- ^^ ---------------------- Option<rules::FlowState>
    |                          |
    |                          std::sync::MutexGuard<'_, Option<rules::FlowState>>
    |
note: `std::sync::MutexGuard<'_, Option<rules::FlowState>>` does not implement `PartialEq<Option<rules::FlowSta
te>>`
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\std\src\sync\poison\mutex.rs:277:1
    |
    = note: `std::sync::MutexGuard<'_, Option<rules::FlowState>>` is defined in another crate
error[E0369]: binary operation `!=` cannot be applied to type `std::sync::MutexGuard<'_, Option<FlowState>>`    
   --> src\input\keyboard.rs:173:51
    |
173 | ...                   if last_state != Some(FlowState::Stuck) {
    |                          ---------- ^^ ---------------------- Option<FlowState>
    |                          |
    |                          std::sync::MutexGuard<'_, Option<FlowState>>
    |
note: `std::sync::MutexGuard<'_, Option<FlowState>>` does not implement `PartialEq<Option<FlowState>>`
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\std\src\sync\poison\mutex.rs:277:1
    |
    = note: `std::sync::MutexGuard<'_, Option<FlowState>>` is defined in another crate
error[E0277]: the trait bound `isize: Param<HHOOK, CopyType>` is not satisfied
   --> src\input\keyboard.rs:193:24
    |
193 |         CallNextHookEx(handle, n_code, w_param, l_param)
    |         -------------- ^^^^^^ the trait `CanInto<HHOOK>` is not implemented for `isize`
    |         |
    |         required by a bound introduced by this call
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `isize` to implement `Param<HHOOK, CopyType>`
note: required by a bound in `CallNextHookEx`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\ 
WindowsAndMessaging\mod.rs:93:9
    |
 91 | pub unsafe fn CallNextHookEx<P0, P1, P2>(hhk: P0, ncode: i32, wparam: P1, lparam: P2) -> super::super::Fo
undation::LRESULT
    |               -------------- required by a bound in this function
 92 | where
 93 |     P0: windows_core::Param<HHOOK>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CallNextHookEx`
error[E0277]: the trait bound `usize: Param<WPARAM, CopyType>` is not satisfied
   --> src\input\keyboard.rs:193:40
    |
193 |         CallNextHookEx(handle, n_code, w_param, l_param)
    |         --------------                 ^^^^^^^ the trait `CanInto<WPARAM>` is not implemented for `usize` 
    |         |
    |         required by a bound introduced by this call
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `usize` to implement `Param<WPARAM, CopyType>`
note: required by a bound in `CallNextHookEx`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\ 
WindowsAndMessaging\mod.rs:94:9
    |
 91 | pub unsafe fn CallNextHookEx<P0, P1, P2>(hhk: P0, ncode: i32, wparam: P1, lparam: P2) -> super::super::Fo 
undation::LRESULT
    |               -------------- required by a bound in this function
...
 94 |     P1: windows_core::Param<super::super::Foundation::WPARAM>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CallNextHookEx`  
error[E0277]: the trait bound `isize: Param<LPARAM, CopyType>` is not satisfied
   --> src\input\keyboard.rs:193:49
    |
193 |         CallNextHookEx(handle, n_code, w_param, l_param)
    |         --------------                          ^^^^^^^ the trait `CanInto<LPARAM>` is not implemented fo 
r `isize`
    |         |
    |         required by a bound introduced by this call
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `isize` to implement `Param<LPARAM, CopyType>`
note: required by a bound in `CallNextHookEx`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\ 
WindowsAndMessaging\mod.rs:95:9
    |
 91 | pub unsafe fn CallNextHookEx<P0, P1, P2>(hhk: P0, ncode: i32, wparam: P1, lparam: P2) -> super::super::Fo
undation::LRESULT
    |               -------------- required by a bound in this function
...
 95 |     P2: windows_core::Param<super::super::Foundation::LPARAM>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CallNextHookEx`  
error[E0308]: mismatched types
   --> src\input\keyboard.rs:193:9
    |
 44 | ) -> isize {
    |      ----- expected `isize` because of return type
...
193 |         CallNextHookEx(handle, n_code, w_param, l_param)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected `isize`, found `LRESULT`
error[E0277]: the trait bound `{integer}: Param<HHOOK, CopyType>` is not satisfied
   --> src\input\keyboard.rs:195:24
    |
195 |         CallNextHookEx(0, n_code, w_param, l_param)
    |         -------------- ^ the trait `CanInto<HHOOK>` is not implemented for `{integer}`
    |         |
    |         required by a bound introduced by this call
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `{integer}` to implement `Param<HHOOK, CopyType>`
note: required by a bound in `CallNextHookEx`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\
WindowsAndMessaging\mod.rs:93:9
    |
 91 | pub unsafe fn CallNextHookEx<P0, P1, P2>(hhk: P0, ncode: i32, wparam: P1, lparam: P2) -> super::super::Fo 
undation::LRESULT
    |               -------------- required by a bound in this function
 92 | where
 93 |     P0: windows_core::Param<HHOOK>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CallNextHookEx`
error[E0277]: the trait bound `usize: Param<WPARAM, CopyType>` is not satisfied
   --> src\input\keyboard.rs:195:35
    |
195 |         CallNextHookEx(0, n_code, w_param, l_param)
    |         --------------            ^^^^^^^ the trait `CanInto<WPARAM>` is not implemented for `usize`      
    |         |
    |         required by a bound introduced by this call
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `usize` to implement `Param<WPARAM, CopyType>`
note: required by a bound in `CallNextHookEx`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\
WindowsAndMessaging\mod.rs:94:9
    |
 91 | pub unsafe fn CallNextHookEx<P0, P1, P2>(hhk: P0, ncode: i32, wparam: P1, lparam: P2) -> super::super::Fo 
undation::LRESULT
    |               -------------- required by a bound in this function
...
 94 |     P1: windows_core::Param<super::super::Foundation::WPARAM>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CallNextHookEx`  
error[E0277]: the trait bound `isize: Param<LPARAM, CopyType>` is not satisfied
   --> src\input\keyboard.rs:195:44
    |
195 |         CallNextHookEx(0, n_code, w_param, l_param)
    |         --------------                     ^^^^^^^ the trait `CanInto<LPARAM>` is not implemented for `is
ize`
    |         |
    |         required by a bound introduced by this call
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `isize` to implement `Param<LPARAM, CopyType>`
note: required by a bound in `CallNextHookEx`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\ 
WindowsAndMessaging\mod.rs:95:9
    |
 91 | pub unsafe fn CallNextHookEx<P0, P1, P2>(hhk: P0, ncode: i32, wparam: P1, lparam: P2) -> super::super::Fo 
undation::LRESULT
    |               -------------- required by a bound in this function
...
 95 |     P2: windows_core::Param<super::super::Foundation::LPARAM>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CallNextHookEx`  
error[E0308]: mismatched types
   --> src\input\keyboard.rs:195:9
    |
 44 | ) -> isize {
    |      ----- expected `isize` because of return type
...
195 |         CallNextHookEx(0, n_code, w_param, l_param)
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected `isize`, found `LRESULT`
error[E0308]: mismatched types
   --> src\input\keyboard.rs:209:18
    |
209 |             Some(keyboard_proc),
    |             ---- ^^^^^^^^^^^^^ expected fn pointer, found fn item
    |             |
    |             arguments to this enum variant are incorrect
    |
    = note: expected fn pointer `unsafe extern "system" fn(_, WPARAM, LPARAM) -> LRESULT`
                  found fn item `unsafe extern "system" fn(_, usize, isize) -> isize {keyboard_proc}`
help: the type constructed contains `unsafe extern "system" fn(i32, usize, isize) -> isize {keyboard_proc}` due
 to the type of the argument passed
   --> src\input\keyboard.rs:209:13
    |
209 |             Some(keyboard_proc),
    |             ^^^^^-------------^
    |                  |
    |                  this argument influences the type of `Some`
note: tuple variant defined here
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\core\src\option.rs:608:5
error[E0271]: type mismatch resolving `<Result<HMODULE, Error> as TypeKind>::TypeKind == CopyType`
    --> src\input\keyboard.rs:210:13
     |
 207 |         let hook_handle = SetWindowsHookExW(
     |                           ----------------- required by a bound introduced by this call
...
 210 |             hmodule,
     |             ^^^^^^^ expected `CopyType`, found `InterfaceType`
     |
     = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `Param<HINSTANCE, CopyTy 
pe>`
note: required by a bound in `SetWindowsHookExW`
    --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI
\WindowsAndMessaging\mod.rs:3101:9
     |
3099 | pub unsafe fn SetWindowsHookExW<P0>(idhook: WINDOWS_HOOK_ID, lpfn: HOOKPROC, hmod: P0, dwthreadid: u32)  
-> windows_core::Result<HHOOK>
     |               ----------------- required by a bound in this function
3100 | where
3101 |     P0: windows_core::Param<super::super::Foundation::HINSTANCE>,
     |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `SetWindowsHo 
okExW`
error[E0277]: the trait bound `Result<HMODULE, windows_result::error::Error>: Param<HINSTANCE, CopyType>` is no 
t satisfied
    --> src\input\keyboard.rs:210:13
     |
 207 |         let hook_handle = SetWindowsHookExW(
     |                           ----------------- required by a bound introduced by this call
...
 210 |             hmodule,
     |             ^^^^^^^ the trait `CanInto<HINSTANCE>` is not implemented for `Result<HMODULE, windows_resul 
t::error::Error>`
     |
     = help: the following other types implement trait `CanInto<T>`:
               `HBITMAP` implements `CanInto<HGDIOBJ>`
               `HBRUSH` implements `CanInto<HGDIOBJ>`
               `HCURSOR` implements `CanInto<HICON>`
               `HFONT` implements `CanInto<HGDIOBJ>`
               `HINSTANCE` implements `CanInto<HMODULE>`
               `HMODULE` implements `CanInto<HINSTANCE>`
               `HPALETTE` implements `CanInto<HGDIOBJ>`
               `HPEN` implements `CanInto<HGDIOBJ>`
             and 756 others
     = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `Param<HINSTANCE, CopyTy 
pe>`
note: required by a bound in `SetWindowsHookExW`
    --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI
\WindowsAndMessaging\mod.rs:3101:9
     |
3099 | pub unsafe fn SetWindowsHookExW<P0>(idhook: WINDOWS_HOOK_ID, lpfn: HOOKPROC, hmod: P0, dwthreadid: u32)  
-> windows_core::Result<HHOOK>
     |               ----------------- required by a bound in this function
3100 | where
3101 |     P0: windows_core::Param<super::super::Foundation::HINSTANCE>,
     |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `SetWindowsHo
okExW`
error[E0277]: the trait bound `Result<HMODULE, windows_result::error::Error>: Param<HINSTANCE, CopyType>` is no 
t satisfied
    --> src\input\keyboard.rs:210:13
     |
 207 |         let hook_handle = SetWindowsHookExW(
     |                           ----------------- required by a bound introduced by this call
...
 210 |             hmodule,
     |             ^^^^^^^ the trait `Interface` is not implemented for `Result<HMODULE, windows_result::error: 
:Error>`
     |
     = help: the following other types implement trait `Interface`:
               IAgileObject
               IAgileReference
               ID2D1AnalysisTransform
               ID2D1Bitmap
               ID2D1Bitmap1
               ID2D1BitmapBrush
               ID2D1BitmapBrush1
               ID2D1BitmapRenderTarget
             and 255 others
     = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `TypeKind`
     = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `Param<HINSTANCE, CopyTy
pe>`
note: required by a bound in `SetWindowsHookExW`
    --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI 
\WindowsAndMessaging\mod.rs:3101:9
     |
3099 | pub unsafe fn SetWindowsHookExW<P0>(idhook: WINDOWS_HOOK_ID, lpfn: HOOKPROC, hmod: P0, dwthreadid: u32)  
-> windows_core::Result<HHOOK>
     |               ----------------- required by a bound in this function
3100 | where
3101 |     P0: windows_core::Param<super::super::Foundation::HINSTANCE>,
     |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `SetWindowsHo 
okExW`
error[E0308]: mismatched types
   --> src\input\keyboard.rs:214:27
    |
214 |         if hook_handle == 0 {
    |            -----------    ^ expected `Result<HHOOK, Error>`, found integer
    |            |
    |            expected because this is `Result<HHOOK, windows_result::error::Error>`
    |
    = note: expected enum `Result<HHOOK, windows_result::error::Error>`
               found type `{integer}`
error[E0308]: mismatched types
   --> src\input\keyboard.rs:218:45
    |
218 |         *HOOK_HANDLE.lock().unwrap() = Some(hook_handle);
    |                                        ---- ^^^^^^^^^^^ expected `isize`, found `Result<HHOOK, Error>`    
    |                                        |
    |                                        arguments to this enum variant are incorrect
    |
    = note: expected type `isize`
               found enum `Result<HHOOK, windows_result::error::Error>`
help: the type constructed contains `Result<HHOOK, windows_result::error::Error>` due to the type of the argume 
nt passed
   --> src\input\keyboard.rs:218:40
    |
218 |         *HOOK_HANDLE.lock().unwrap() = Some(hook_handle);
    |                                        ^^^^^-----------^
    |                                             |
    |                                             this argument influences the type of `Some`
note: tuple variant defined here
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\core\src\option.rs:608:5
error[E0277]: the trait bound `isize: Param<HHOOK, CopyType>` is not satisfied
    --> src\input\keyboard.rs:228:41
     |
 228 |             let _ = UnhookWindowsHookEx(handle);
     |                     ------------------- ^^^^^^ the trait `CanInto<HHOOK>` is not implemented for `isize` 
     |                     |
     |                     required by a bound introduced by this call
     |
     = help: the following other types implement trait `CanInto<T>`:
               `HBITMAP` implements `CanInto<HGDIOBJ>`
               `HBRUSH` implements `CanInto<HGDIOBJ>`
               `HCURSOR` implements `CanInto<HICON>`
               `HFONT` implements `CanInto<HGDIOBJ>`
               `HINSTANCE` implements `CanInto<HMODULE>`
               `HMODULE` implements `CanInto<HINSTANCE>`
               `HPALETTE` implements `CanInto<HGDIOBJ>`
               `HPEN` implements `CanInto<HGDIOBJ>`
             and 756 others
     = note: required for `isize` to implement `Param<HHOOK, CopyType>`
note: required by a bound in `UnhookWindowsHookEx`
    --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI
\WindowsAndMessaging\mod.rs:3242:9
     |
3240 | pub unsafe fn UnhookWindowsHookEx<P0>(hhk: P0) -> windows_core::Result<()>
     |               ------------------- required by a bound in this function
3241 | where
3242 |     P0: windows_core::Param<HHOOK>,
     |         ^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `UnhookWindowsHookEx`
error[E0599]: no method named `is_invalid` found for enum `Result<T, E>` in the current scope
     --> src\ui\overlay.rs:59:17
      |
   59 |         if hwnd.is_invalid() {
      |                 ^^^^^^^^^^ method not found in `Result<HWND, windows_result::error::Error>`
      |
note: the method `is_invalid` exists on the type `HWND`
     --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\F 
oundation\mod.rs:10868:5
      |
10868 |     pub fn is_invalid(&self) -> bool {
      |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
help: use the `?` operator to extract the `HWND` value, propagating a `Result::Err` value to the caller
      |
   59 |         if hwnd?.is_invalid() {
      |                +
error[E0308]: mismatched types
  --> src\ui\overlay.rs:65:31
   |
65 |         if !set_overlay_alpha(hwnd, 0, 0x000000).is_ok() {
   |             ----------------- ^^^^ expected `HWND`, found `Result<HWND, Error>`
   |             |
   |             arguments to this function are incorrect
   |
   = note: expected struct `HWND`
                found enum `Result<HWND, windows_result::error::Error>`
note: function defined here
  --> src\ui\overlay.rs:85:8
   |
85 | pub fn set_overlay_alpha(hwnd: HWND, alpha: u8, color: u32) -> Result<(), String> {
   |        ^^^^^^^^^^^^^^^^^ ----------
help: use the `?` operator to extract the `Result<HWND, windows_result::error::Error>` value, propagating a `Re 
sult::Err` value to the caller
   |
65 |         if !set_overlay_alpha(hwnd?, 0, 0x000000).is_ok() {
   |                                   +
error[E0308]: mismatched types
  --> src\ui\overlay.rs:71:12
   |
71 |         Ok(hwnd)
   |         -- ^^^^ expected `HWND`, found `Result<HWND, Error>`
   |         |
   |         arguments to this enum variant are incorrect
   |
   = note: expected struct `HWND`
                found enum `Result<HWND, windows_result::error::Error>`
help: the type constructed contains `Result<HWND, windows_result::error::Error>` due to the type of the argumen
t passed
  --> src\ui\overlay.rs:71:9
   |
71 |         Ok(hwnd)
   |         ^^^----^
   |            |
   |            this argument influences the type of `Ok`
note: tuple variant defined here
  --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\core\src\result.rs:561:5
help: use the `?` operator to extract the `Result<HWND, windows_result::error::Error>` value, propagating a `Re 
sult::Err` value to the caller
   |
71 |         Ok(hwnd?)
   |                +
error[E0599]: no method named `as_bool` found for enum `Result<T, E>` in the current scope
   --> src\ui\overlay.rs:107:70
    |
107 |         if SetLayeredWindowAttributes(hwnd, rgb_color, alpha, flags).as_bool() == false {
    |                                                                      ^^^^^^^ method not found in `Result< 
(), windows_result::error::Error>`
error[E0308]: mismatched types
     --> src\main.rs:29:33
      |
   29 |         let overlay_hwnd = HWND(overlay_hwnd_value);
      |                            ---- ^^^^^^^^^^^^^^^^^^ expected `*mut c_void`, found `isize`
      |                            |
      |                            arguments to this struct are incorrect
      |
      = note: expected raw pointer `*mut c_void`
                        found type `isize`
note: tuple struct defined here
     --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\F 
oundation\mod.rs:10866:12
      |
10866 | pub struct HWND(pub *mut core::ffi::c_void);
      |            ^^^^
error[E0599]: no method named `is_invalid` found for enum `Result<T, E>` in the current scope
     --> src\main.rs:56:20
      |
   56 |         if hmodule.is_invalid() {
      |                    ^^^^^^^^^^ method not found in `Result<HMODULE, windows_result::error::Error>`       
      |
note: the method `is_invalid` exists on the type `HMODULE`
     --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\F
oundation\mod.rs:10774:5
      |
10774 |     pub fn is_invalid(&self) -> bool {
      |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
help: use the `?` operator to extract the `HMODULE` value, propagating a `Result::Err` value to the caller
      |
   56 |         if hmodule?.is_invalid() {
      |                   +
error[E0308]: mismatched types
  --> src\main.rs:67:24
   |
67 |             hInstance: hmodule,
   |                        ^^^^^^^ expected `HINSTANCE`, found `Result<HMODULE, Error>`
   |
   = note: expected struct `HINSTANCE`
                found enum `Result<HMODULE, windows_result::error::Error>`
error[E0308]: mismatched types
  --> src\main.rs:69:22
   |
69 |             hCursor: LoadCursorW(None, IDC_ARROW).ok(),
   |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected `HCURSOR`, found `Option<HCURSOR>`
   |
   = note: expected struct `HCURSOR`
                found enum `Option<HCURSOR>`
help: consider using `Option::expect` to unwrap the `Option<HCURSOR>` value, panicking if the value is an `Opti 
on::None`
   |
69 |             hCursor: LoadCursorW(None, IDC_ARROW).ok().expect("REASON"),
   |                                                       +++++++++++++++++
error[E0271]: type mismatch resolving `<Result<HMODULE, Error> as TypeKind>::TypeKind == CopyType`
   --> src\main.rs:88:13
    |
 77 |         let hwnd = CreateWindowExW(
    |                    --------------- required by a bound introduced by this call
...
 88 |             hmodule,
    |             ^^^^^^^ expected `CopyType`, found `InterfaceType`
    |
    = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `Param<HINSTANCE, CopyTyp
e>`
note: required by a bound in `CreateWindowExW`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\ 
WindowsAndMessaging\mod.rs:544:9
    |
538 | pub unsafe fn CreateWindowExW<P0, P1, P2, P3, P4>(dwexstyle: WINDOW_EX_STYLE, lpclassname: P0, lpwindowna 
me: P1, dwstyle: WINDOW_STYLE, x...
    |               --------------- required by a bound in this function
...
544 |     P4: windows_core::Param<super::super::Foundation::HINSTANCE>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CreateWindowE 
xW`
error[E0277]: the trait bound `Result<HMODULE, windows_result::error::Error>: Param<HINSTANCE, CopyType>` is no 
t satisfied
   --> src\main.rs:88:13
    |
 77 |         let hwnd = CreateWindowExW(
    |                    --------------- required by a bound introduced by this call
...
 88 |             hmodule,
    |             ^^^^^^^ the trait `CanInto<HINSTANCE>` is not implemented for `Result<HMODULE, windows_result
::error::Error>`
    |
    = help: the following other types implement trait `CanInto<T>`:
              `HBITMAP` implements `CanInto<HGDIOBJ>`
              `HBRUSH` implements `CanInto<HGDIOBJ>`
              `HCURSOR` implements `CanInto<HICON>`
              `HFONT` implements `CanInto<HGDIOBJ>`
              `HINSTANCE` implements `CanInto<HMODULE>`
              `HMODULE` implements `CanInto<HINSTANCE>`
              `HPALETTE` implements `CanInto<HGDIOBJ>`
              `HPEN` implements `CanInto<HGDIOBJ>`
            and 756 others
    = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `Param<HINSTANCE, CopyTyp 
e>`
note: required by a bound in `CreateWindowExW`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\
WindowsAndMessaging\mod.rs:544:9
    |
538 | pub unsafe fn CreateWindowExW<P0, P1, P2, P3, P4>(dwexstyle: WINDOW_EX_STYLE, lpclassname: P0, lpwindowna 
me: P1, dwstyle: WINDOW_STYLE, x...
    |               --------------- required by a bound in this function
...
544 |     P4: windows_core::Param<super::super::Foundation::HINSTANCE>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CreateWindowE
xW`
error[E0277]: the trait bound `Result<HMODULE, windows_result::error::Error>: Param<HINSTANCE, CopyType>` is no 
t satisfied
   --> src\main.rs:88:13
    |
 77 |         let hwnd = CreateWindowExW(
    |                    --------------- required by a bound introduced by this call
...
 88 |             hmodule,
    |             ^^^^^^^ the trait `Interface` is not implemented for `Result<HMODULE, windows_result::error::
Error>`
    |
    = help: the following other types implement trait `Interface`:
              IAgileObject
              IAgileReference
              ID2D1AnalysisTransform
              ID2D1Bitmap
              ID2D1Bitmap1
              ID2D1BitmapBrush
              ID2D1BitmapBrush1
              ID2D1BitmapRenderTarget
            and 255 others
    = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `TypeKind`
    = note: required for `Result<HMODULE, windows_result::error::Error>` to implement `Param<HINSTANCE, CopyTyp 
e>`
note: required by a bound in `CreateWindowExW`
   --> C:\Users\johnd\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\windows-0.58.0\src\Windows\Win32\UI\ 
WindowsAndMessaging\mod.rs:544:9
    |
538 | pub unsafe fn CreateWindowExW<P0, P1, P2, P3, P4>(dwexstyle: WINDOW_EX_STYLE, lpclassname: P0, lpwindowna 
me: P1, dwstyle: WINDOW_STYLE, x...
    |               --------------- required by a bound in this function
...
544 |     P4: windows_core::Param<super::super::Foundation::HINSTANCE>,
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ required by this bound in `CreateWindowE
xW`
error[E0609]: no field `0` on type `Result<HWND, windows_result::error::Error>`
  --> src\main.rs:92:17
   |
92 |         if hwnd.0 == 0 {
   |                 ^ unknown field
   |
help: one of the expressions' fields has a field of the same name
   |
92 |         if hwnd.unwrap().0 == 0 {
   |                 +++++++++
error[E0609]: no field `0` on type `Result<HWND, windows_result::error::Error>`
  --> src\main.rs:96:32
   |
96 |         HWND_STATIC.store(hwnd.0, Ordering::SeqCst);
   |                                ^ unknown field
   |
help: one of the expressions' fields has a field of the same name
   |
96 |         HWND_STATIC.store(hwnd.unwrap().0, Ordering::SeqCst);
   |                                +++++++++
error[E0308]: mismatched types
  --> src\main.rs:97:12
   |
97 |         Ok(hwnd)
   |         -- ^^^^ expected `HWND`, found `Result<HWND, Error>`
   |         |
   |         arguments to this enum variant are incorrect
   |
   = note: expected struct `HWND`
                found enum `Result<HWND, windows_result::error::Error>`
help: the type constructed contains `Result<HWND, windows_result::error::Error>` due to the type of the argumen 
t passed
  --> src\main.rs:97:9
   |
97 |         Ok(hwnd)
   |         ^^^----^
   |            |
   |            this argument influences the type of `Ok`
note: tuple variant defined here
  --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\core\src\result.rs:561:5
help: use the `?` operator to extract the `Result<HWND, windows_result::error::Error>` value, propagating a `Re 
sult::Err` value to the caller
   |
97 |         Ok(hwnd?)
   |                +
error[E0308]: mismatched types
   --> src\main.rs:136:39
    |
136 |             HWND_OVERLAY_STATIC.store(overlay_hwnd.0, Ordering::SeqCst);
    |                                 ----- ^^^^^^^^^^^^^^ expected `isize`, found `*mut c_void`
    |                                 |
    |                                 arguments to this method are incorrect
    |
    = note:     expected type `isize`
            found raw pointer `*mut c_void`
note: method defined here
   --> /rustc/01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\library\core\src\sync\atomic.rs:3970:1
    = note: this error originates in the macro `atomic_int` which comes from the expansion of the macro `atomic 
_int_ptr_sized` (in Nightly builds, run with -Z macro-backtrace for more info)
Some errors have detailed explanations: E0271, E0277, E0308, E0369, E0432, E0599, E0609.
For more information about an error, try `rustc --explain E0271`.
warning: `gse-prototype` (bin "gse-prototype" test) generated 2 warnings (2 duplicates)
error: could not compile `gse-prototype` (bin "gse-prototype" test) due to 37 previous errors; 2 warnings emitt 
ed
Caused by:
  process didn't exit successfully: `C:\Users\johnd\.rustup\toolchains\stable-x86_64-pc-windows-msvc\bin\rustc.
exe --crate-name gse_prototype --edition=2021 src\main.rs --error-format=json --json=diagnostic-rendered-ansi,a 
rtifacts,future-incompat --emit=dep-info,link -C embed-bitcode=no -C debuginfo=2 --test --check-cfg cfg(docsrs, 
test) --check-cfg "cfg(feature, values())" -C metadata=5436d8116e0611d8 -C extra-filename=-e5e592f42aea4c40 --o 
ut-dir C:\gse-prototype\target\debug\deps -C incremental=C:\gse-prototype\target\debug\incremental -L dependenc 
y=C:\gse-prototype\target\debug\deps --extern chrono=C:\gse-prototype\target\debug\deps\libchrono-016dd7f0040ce 
807.rlib --extern once_cell=C:\gse-prototype\target\debug\deps\libonce_cell-0c3a3c223d21dba8.rlib --extern serd 
e=C:\gse-prototype\target\debug\deps\libserde-b2137b98591bd257.rlib --extern serde_json=C:\gse-prototype\target 
\debug\deps\libserde_json-a4bf0c4ea4a3d491.rlib --extern statrs=C:\gse-prototype\target\debug\deps\libstatrs-87 
a73b30334d36c5.rlib --extern tracing=C:\gse-prototype\target\debug\deps\libtracing-d399d6a8142c25ea.rlib --exte 
rn tracing_subscriber=C:\gse-prototype\target\debug\deps\libtracing_subscriber-f0cfdb883b4efbae.rlib --extern w 
indows=C:\gse-prototype\target\debug\deps\libwindows-a870f41ed452b263.rlib -L native=C:\Users\johnd\.cargo\regi 
stry\src\index.crates.io-1949cf8c6b5b557f\windows_x86_64_msvc-0.52.6\lib` (exit code: 1)
warning: build failed, waiting for other jobs to finish...
warning: `gse-prototype` (bin "gse-prototype") generated 2 warnings
error: could not compile `gse-prototype` (bin "gse-prototype") due to 37 previous errors; 2 warnings emitted    
Caused by:
  process didn't exit successfully: `C:\Users\johnd\.rustup\toolchains\stable-x86_64-pc-windows-msvc\bin\rustc.
exe --crate-name gse_prototype --edition=2021 src\main.rs --error-format=json --json=diagnostic-rendered-ansi,a 
rtifacts,future-incompat --crate-type bin --emit=dep-info,link -C embed-bitcode=no -C debuginfo=2 --check-cfg c 
fg(docsrs,test) --check-cfg "cfg(feature, values())" -C metadata=7eef20a2548f83eb --out-dir C:\gse-prototype\ta 
rget\debug\deps -C incremental=C:\gse-prototype\target\debug\incremental -L dependency=C:\gse-prototype\target\ 
debug\deps --extern chrono=C:\gse-prototype\target\debug\deps\libchrono-016dd7f0040ce807.rlib --extern once_cel 
l=C:\gse-prototype\target\debug\deps\libonce_cell-0c3a3c223d21dba8.rlib --extern serde=C:\gse-prototype\target\ 
debug\deps\libserde-b2137b98591bd257.rlib --extern serde_json=C:\gse-prototype\target\debug\deps\libserde_json- 
a4bf0c4ea4a3d491.rlib --extern statrs=C:\gse-prototype\target\debug\deps\libstatrs-87a73b30334d36c5.rlib --exte 
rn tracing=C:\gse-prototype\target\debug\deps\libtracing-d399d6a8142c25ea.rlib --extern tracing_subscriber=C:\g 
se-prototype\target\debug\deps\libtracing_subscriber-f0cfdb883b4efbae.rlib --extern windows=C:\gse-prototype\ta 
rget\debug\deps\libwindows-a870f41ed452b263.rlib -L native=C:\Users\johnd\.cargo\registry\src\index.crates.io-1 
949cf8c6b5b557f\windows_x86_64_msvc-0.52.6\lib` (exit code: 1)