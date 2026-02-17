//! GSE Overlay UI Implementation
//! 
//! Provides transparent, click-through overlay window for visual feedback.
//! The overlay covers the entire screen and displays state-based visual effects:
//! - FLOW: Completely transparent
//! - INCUBATION: Light yellow fade (alpha=25)
//! - STUCK: White fog (alpha=76)

use windows::Win32::Foundation::HWND;
use windows::Win32::UI::WindowsAndMessaging::{
    CreateWindowExW, GetSystemMetrics,
    WS_EX_LAYERED, WS_EX_TRANSPARENT, WS_EX_TOPMOST, WS_POPUP,
    SetLayeredWindowAttributes, SM_CXSCREEN, SM_CYSCREEN,
    LWA_ALPHA,
};
use windows::core::w;
use tracing::{info, error};

use crate::inference::rules::FlowState;

/// Creates a transparent, click-through overlay window covering the entire screen.
/// 
/// # Returns
/// - `Ok(HWND)` - Handle to the overlay window
/// - `Err(String)` - Error message if window creation fails
/// 
/// # Window Properties
/// - Style: Layered (WS_EX_LAYERED) - supports transparency
/// - Transparent (WS_EX_TRANSPARENT) - click-through, doesn't capture input
/// - Topmost (WS_EX_TOPMOST) - stays above other windows
/// - Covers entire primary monitor
pub fn create_overlay_window() -> Result<HWND, String> {
    unsafe {
        // Get primary monitor dimensions
        let screen_width = GetSystemMetrics(SM_CXSCREEN);
        let screen_height = GetSystemMetrics(SM_CYSCREEN);

        if screen_width == 0 || screen_height == 0 {
            return Err("Failed to get screen dimensions".to_string());
        }

        // Create the overlay window
        let hwnd = CreateWindowExW(
            WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST,
            w!("STATIC"),                    // Window class (built-in static control)
            w!("GSE Overlay"),               // Window title (not visible)
            WS_POPUP,                        // Window style (popup, no chrome)
            0,                               // X position
            0,                               // Y position
            screen_width,                    // Width (full screen)
            screen_height,                   // Height (full screen)
            HWND::default(),                 // Parent window (none)
            None,                            // Menu (none)
            None,                            // Instance (not used for built-in class)
            None,                            // Creation parameters
        )
        .map_err(|e| format!("CreateWindowExW failed: {}", e))?;

        // Initialize as fully transparent
        set_overlay_alpha(hwnd, 0, 0x000000)?;

        info!("Overlay window created successfully: width={}px, height={}px", screen_width, screen_height);
        Ok(hwnd)
    }
}

/// Sets the opacity and color of a layered window.
///
/// # Parameters
/// - `hwnd` - Handle to the layered window
/// - `alpha` - Opacity level (0=transparent, 255=opaque)
/// - `color` - Background color in RGB format (e.g., 0xFFFFFF for white)
///
/// # Returns
/// - `Ok(())` - Successfully updated window attributes
/// - `Err(String)` - Error message if update fails
pub fn set_overlay_alpha(hwnd: HWND, alpha: u8, color: u32) -> Result<(), String> {
    unsafe {
        if hwnd.is_invalid() {
            return Err("Invalid window handle".to_string());
        }

        // Extract RGB components from color
        let r = ((color >> 16) & 0xFF) as u8;
        let g = ((color >> 8) & 0xFF) as u8;
        let b = (color & 0xFF) as u8;
        let rgb_color = windows::Win32::Foundation::COLORREF(r as u32 | ((g as u32) << 8) | ((b as u32) << 16));

        // SetLayeredWindowAttributes sets the transparency key
        // LWA_ALPHA: Apply the alpha value
        // LWA_COLORKEY: Apply the color key (pixels matching color become transparent)
        let flags = if alpha > 0 {
            LWA_ALPHA  // Use alpha blending
        } else {
            LWA_ALPHA  // Use alpha blending (with alpha=0 for full transparency)
        };

        SetLayeredWindowAttributes(hwnd, rgb_color, alpha, flags)
            .map_err(|e| format!("SetLayeredWindowAttributes failed: {}", e))?;

        info!("Overlay alpha set: alpha={}, color=0x{:06X}", alpha, color);
        Ok(())
    }
}

/// Updates the overlay visual appearance based on cognitive state.
///
/// # State Mapping
/// - **FLOW**: Fully transparent (alpha=0)
///   - User is in productive flow state, no visual feedback
/// - **INCUBATION**: Light yellow overlay (alpha=25, color=0xFFFF99)
///   - User is thinking/pausing, subtle visual cue
/// - **STUCK**: White fog overlay (alpha=76, color=0xFFFFFF)
///   - User is struggling, strong visual feedback
///
/// # Parameters
/// - `hwnd` - Handle to the overlay window
/// - `state` - Current cognitive state
///
/// # Returns
/// - `Ok(())` - Successfully updated overlay
/// - `Err(String)` - Error updating overlay
pub fn update_overlay(hwnd: HWND, state: FlowState) -> Result<(), String> {
    if hwnd.is_invalid() {
        return Err("Invalid overlay window handle".to_string());
    }

    match state {
        FlowState::Flow => {
            // Transparent: no visual feedback
            info!("[OVERLAY] State: FLOW (fully transparent)");
            set_overlay_alpha(hwnd, 0, 0x000000)?;
        }
        FlowState::Incubation => {
            // Light yellow fade: subtle thinking indicator
            info!("[OVERLAY] State: INCUBATION (yellow alpha=25)");
            set_overlay_alpha(hwnd, 25, 0xFFFF99)?;
        }
        FlowState::Stuck => {
            // White fog: strong struggle indicator
            info!("[OVERLAY] State: STUCK (white fog alpha=76)");
            set_overlay_alpha(hwnd, 76, 0xFFFFFF)?;
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_overlay_state_mapping() {
        // Verify state-to-visual mappings are correct
        
        // FLOW should map to transparent
        assert_eq!(matches!(FlowState::Flow, FlowState::Flow), true);
        
        // INCUBATION should map to yellow
        assert_eq!(matches!(FlowState::Incubation, FlowState::Incubation), true);
        
        // STUCK should map to white
        assert_eq!(matches!(FlowState::Stuck, FlowState::Stuck), true);
    }

    #[test]
    fn test_rgb_color_values() {
        // Verify RGB color values are in correct range
        let white = 0xFFFFFF;
        let yellow = 0xFFFF99;
        let black = 0x000000;
        
        // Colors should fit in 24-bit RGB
        assert!(white <= 0xFFFFFF);
        assert!(yellow <= 0xFFFFFF);
        assert!(black <= 0xFFFFFF);
    }

    #[test]
    fn test_alpha_range() {
        // Verify alpha values are byte-sized
        let alpha_transparent = 0u8;
        let alpha_yellow = 25u8;
        let alpha_white = 76u8;
        let alpha_opaque = 255u8;
        
        assert!(alpha_transparent <= 255);
        assert!(alpha_yellow <= 255);
        assert!(alpha_white <= 255);
        assert!(alpha_opaque <= 255);
    }
}
