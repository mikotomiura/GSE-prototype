/// Represents the current cognitive state of the user based on typing patterns
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FlowState {
    /// User is in flow state: typing smoothly with minimal pauses
    /// Characterized by fast, consistent typing with few corrections
    Flow,

    /// User is in incubation state: thinking with moderate delays
    /// Characterized by occasional pauses and minor corrections
    Incubation,

    /// User is stuck: struggling with long delays or many corrections
    /// Characterized by frequent deletions or extended pauses
    Stuck,
}

impl FlowState {
    /// Returns a human-readable string representation of the state
    pub fn as_str(&self) -> &'static str {
        match self {
            FlowState::Flow => "FLOW",
            FlowState::Incubation => "INCUBATION",
            FlowState::Stuck => "STUCK",
        }
    }
}

/// Classifies the user's cognitive state based on typing metrics
///
/// # Arguments
/// * `flight_time_ms` - Time in milliseconds between the last two key presses
/// * `backspace_count` - Number of backspace key presses in the last 5 seconds
///
/// # Returns
/// A FlowState representing the classified cognitive state
///
/// # Classification Rules
/// - **Flow**: flight_time < 100ms AND backspace_count < 2
/// - **Stuck**: flight_time > 500ms OR backspace_count > 5
/// - **Incubation**: Everything else (moderate delays or occasional corrections)
pub fn classify_state(
    flight_time_ms: u64,
    backspace_count: u32,
    pause_after_delete_ms: Option<u64>,
) -> FlowState {
    // F6: Pause-after-Delete (Hesitation) - if pause after backspace exceeds 2000ms, treat as STUCK
    if let Some(ms) = pause_after_delete_ms {
        if ms >= 2000 {
            return FlowState::Stuck;
        }
    }

    let flight_time_exceeds_threshold = flight_time_ms > 500;
    let backspace_exceeds_threshold = backspace_count > 5;
    let flight_time_normal = flight_time_ms < 100;
    let backspace_minimal = backspace_count < 2;

    if flight_time_exceeds_threshold || backspace_exceeds_threshold {
        FlowState::Stuck
    } else if flight_time_normal && backspace_minimal {
        FlowState::Flow
    } else {
        FlowState::Incubation
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_flow_state() {
        assert_eq!(classify_state(50, 0, None), FlowState::Flow);
        assert_eq!(classify_state(99, 1, None), FlowState::Flow);
    }

    #[test]
    fn test_incubation_state() {
        assert_eq!(classify_state(250, 2, None), FlowState::Incubation);
        assert_eq!(classify_state(150, 1, None), FlowState::Incubation);
    }

    #[test]
    fn test_stuck_state() {
        assert_eq!(classify_state(600, 0, None), FlowState::Stuck);
        assert_eq!(classify_state(100, 6, None), FlowState::Stuck);
        assert_eq!(classify_state(800, 3, None), FlowState::Stuck);
        // F6 hesitation should force STUCK
        assert_eq!(classify_state(50, 0, Some(2500)), FlowState::Stuck);
    }
}
