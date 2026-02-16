use std::fmt;

/// Represents all possible errors in the GSE (Generative Struggle Engine) application.
///
/// This custom error type provides more structured error handling compared to String-based errors,
/// enabling better error propagation and context preservation throughout the application.
#[derive(Debug, Clone)]
pub enum HookError {
    /// Failed to install or uninstall the global keyboard hook
    HookInstallation(String),

    /// Failed to create or initialize the message window
    WindowCreation(String),

    /// Failed to acquire a synchronization primitive (Mutex/RwLock)
    SyncPoisoned(String),

    /// Failed to access or manipulate the observation queue
    QueueOperation(String),

    /// Windows API call failed with context
    WindowsApiError(String),

    /// Configuration or initialization error
    Configuration(String),

    /// Unexpected internal state error
    InternalError(String),
}

impl fmt::Display for HookError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            HookError::HookInstallation(msg) => write!(f, "Hook installation failed: {}", msg),
            HookError::WindowCreation(msg) => write!(f, "Window creation failed: {}", msg),
            HookError::SyncPoisoned(msg) => write!(f, "Synchronization primitive poisoned: {}", msg),
            HookError::QueueOperation(msg) => write!(f, "Queue operation failed: {}", msg),
            HookError::WindowsApiError(msg) => write!(f, "Windows API error: {}", msg),
            HookError::Configuration(msg) => write!(f, "Configuration error: {}", msg),
            HookError::InternalError(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl std::error::Error for HookError {}

/// Result type alias for HookError
pub type HookResult<T> = Result<T, HookError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let error = HookError::HookInstallation("SetWindowsHookExW failed with code 5".to_string());
        assert_eq!(
            error.to_string(),
            "Hook installation failed: SetWindowsHookExW failed with code 5"
        );
    }

    #[test]
    fn test_sync_poisoned_display() {
        let error = HookError::SyncPoisoned("BACKSPACE_TIMES mutex poisoned".to_string());
        assert!(error.to_string().contains("Synchronization primitive poisoned"));
    }

    #[test]
    fn test_error_clone() {
        let error = HookError::Configuration("Invalid state threshold".to_string());
        let cloned = error.clone();
        assert_eq!(error.to_string(), cloned.to_string());
    }
}
