use tracing::{info, error, Level};
use tracing_subscriber::FmtSubscriber;
use windows::Win32::UI::WindowsAndMessaging::{
    GetMessageW, TranslateMessage, DispatchMessageW, MSG, PostQuitMessage,
    RegisterClassW, CreateWindowExW, WS_OVERLAPPEDWINDOW, WM_DESTROY, WM_QUIT,
    CW_USEDEFAULT, WNDCLASSW, CS_VREDRAW, CS_HREDRAW, DefWindowProcW, IDC_ARROW,
    LoadCursorW,
};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::Foundation::{HWND, LPARAM, WPARAM, LRESULT};
use windows::core::w;
use std::sync::atomic::{AtomicIsize, Ordering};

mod error;
mod input;
mod inference;
mod ui;

pub use error::{HookError, HookResult};

static HWND_STATIC: AtomicIsize = AtomicIsize::new(0);
static HWND_OVERLAY_STATIC: AtomicIsize = AtomicIsize::new(0);

/// Updates the overlay window based on the current cognitive state.
/// Called from the keyboard hook to provide visual feedback.
pub fn update_overlay_from_state(state: inference::rules::FlowState) {
    let overlay_hwnd_value = HWND_OVERLAY_STATIC.load(Ordering::SeqCst);
    if overlay_hwnd_value != 0 {
        let overlay_hwnd = HWND(overlay_hwnd_value as *mut std::ffi::c_void);
        if let Err(e) = ui::overlay::update_overlay(overlay_hwnd, state) {
            error!("Failed to update overlay: {}", e);
        }
    }
}

unsafe extern "system" fn window_proc(
    hwnd: HWND,
    msg: u32,
    wparam: WPARAM,
    lparam: LPARAM,
) -> LRESULT {
    match msg {
        WM_DESTROY => {
            PostQuitMessage(0);
            LRESULT(0)
        }
        _ => DefWindowProcW(hwnd, msg, wparam, lparam),
    }
}

fn create_message_window() -> Result<HWND, String> {
    unsafe {
        let hmodule = GetModuleHandleW(None)
            .map_err(|e| format!("Failed to get module handle: {}", e))?;

        let class_name = w!("GSEPrototypeClass");

        let wnd_class = WNDCLASSW {
            style: CS_VREDRAW | CS_HREDRAW,
            lpfnWndProc: Some(window_proc),
            cbClsExtra: 0,
            cbWndExtra: 0,
            hInstance: hmodule.into(),
            hIcon: Default::default(),
            hCursor: LoadCursorW(None, IDC_ARROW).unwrap_or_default(),
            hbrBackground: Default::default(),
            lpszMenuName: windows::core::PCWSTR::null(),
            lpszClassName: class_name,
        };

        RegisterClassW(&wnd_class);

        let hwnd = CreateWindowExW(
            Default::default(),
            class_name,
            w!("GSE Prototype"),
            WS_OVERLAPPEDWINDOW,
            0,
            0,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            None,
            None,
            hmodule,
            None,
        )
        .map_err(|e| format!("CreateWindowExW failed: {}", e))?;

        HWND_STATIC.store(hwnd.0 as isize, Ordering::SeqCst);
        Ok(hwnd)
    }
}

fn main() {
    // Initialize tracing
    let _subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .with_writer(std::io::stderr)
        .init();

    info!("GSE Core Initialized");

    // Note: TSF (Text Services Framework) integration is planned for future releases
    // For now, the keyboard hook provides sufficient input monitoring
    
    // Create hidden window for message loop
    let _hwnd = match create_message_window() {
        Ok(hwnd) => {
            info!("Message window created");
            hwnd
        }
        Err(e) => {
            eprintln!("Failed to create message window: {}", e);
            return;
        }
    };

    // Install keyboard hook
    match input::keyboard::install_hook() {
        Ok(_) => {
            info!("Keyboard hook installed successfully");
        }
        Err(e) => {
            eprintln!("Failed to install keyboard hook: {}", e);
            return;
        }
    }

    // Create overlay window for visual feedback
    match ui::overlay::create_overlay_window() {
        Ok(overlay_hwnd) => {
            HWND_OVERLAY_STATIC.store(overlay_hwnd.0 as isize, Ordering::SeqCst);
            info!("Overlay window created successfully");
        }
        Err(e) => {
            eprintln!("Failed to create overlay window: {}", e);
            // Continue anyway - keyboard hook alone is functional
        }
    }

    // Message loop
    unsafe {
        let mut msg: MSG = std::mem::zeroed();
        loop {
            let ret = GetMessageW(&mut msg, None, 0, 0);
            if !ret.as_bool() || msg.message == WM_QUIT {
                break;
            }
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
    }

    // Cleanup
    input::keyboard::uninstall_hook();
    info!("GSE Core Shutdown");
}
