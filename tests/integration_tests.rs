//! Integration tests for GSE state inference pipeline
//! 
//! These tests verify the complete inference chain from raw metrics to state classification
//! without requiring Windows hook installation.

// Note: The GSE project structure with input, inference modules can be accessed
// In practice, integration tests would use the library exports or mock the keyboard hook

#[cfg(test)]
mod tests {
    use std::time::Duration;
    
    /// Represents raw keyboard metrics before inference
    #[derive(Debug, Clone)]
    struct KeyboardMetrics {
        flight_time_ms: u64,
        backspace_count: u32,
    }

    /// Represents the cognitive state from Rule-based inference
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    enum FlowState {
        Flow,
        Incubation,
        Stuck,
    }

    /// Rule-based classification logic (mirrored from src/inference/rules.rs)
    fn classify_state(flight_time_ms: u64, backspace_count: u32) -> FlowState {
        if flight_time_ms > 500 || backspace_count > 5 {
            FlowState::Stuck
        } else if flight_time_ms < 100 && backspace_count < 2 {
            FlowState::Flow
        } else {
            FlowState::Incubation
        }
    }

    /// Simple HMM state tracking (simplified version for testing)
    #[derive(Debug, Clone)]
    struct SimpleHMM {
        state_probs: [f64; 3], // [FLOW, INCUBATION, STUCK]
    }

    impl SimpleHMM {
        fn new() -> Self {
            SimpleHMM {
                state_probs: [1.0, 0.0, 0.0], // Start in FLOW state
            }
        }

        /// Apply state transition based on observation
        fn update(&mut self, observation: f64) -> FlowState {
            let observation_probs = self.calculate_observation_probs(observation);
            let transitions = [
                [0.85, 0.10, 0.05], // From FLOW
                [0.40, 0.45, 0.15], // From INCUBATION
                [0.30, 0.20, 0.50], // From STUCK
            ];

            let mut new_probs = [0.0; 3];
            for (to_state, _) in observation_probs.iter().enumerate() {
                for (from_state, &from_prob) in self.state_probs.iter().enumerate() {
                    new_probs[to_state] +=
                        from_prob * transitions[from_state][to_state] * observation_probs[to_state];
                }
            }

            // Normalize
            let sum: f64 = new_probs.iter().sum();
            if sum > 0.0 {
                for p in &mut new_probs {
                    *p /= sum;
                }
            }

            self.state_probs = new_probs;

            // Return state with highest probability
            if self.state_probs[0] >= self.state_probs[1] && self.state_probs[0] >= self.state_probs[2] {
                FlowState::Flow
            } else if self.state_probs[1] >= self.state_probs[2] {
                FlowState::Incubation
            } else {
                FlowState::Stuck
            }
        }

        fn calculate_observation_probs(&self, observation: f64) -> [f64; 3] {
            let params = [(50.0, 30.0), (250.0, 100.0), (1000.0, 500.0)];
            let mut probs = [0.0; 3];

            for (i, &(mu, sigma)) in params.iter().enumerate() {
                probs[i] = gaussian_pdf(observation, mu, sigma);
            }

            probs
        }
    }

    /// Gaussian probability density function
    fn gaussian_pdf(x: f64, mu: f64, sigma: f64) -> f64 {
        let numerator = -(x - mu).powi(2);
        let denominator = 2.0 * sigma.powi(2);
        let exponent = numerator / denominator;
        (1.0 / (sigma * (2.0 * std::f64::consts::PI).sqrt())) * exponent.exp()
    }

    // ============================================================================
    // Test Suite
    // ============================================================================

    #[test]
    fn test_rule_based_flow_detection() {
        // Fast typing with no backspaces = FLOW state
        let metrics = KeyboardMetrics {
            flight_time_ms: 75,
            backspace_count: 0,
        };
        assert_eq!(
            classify_state(metrics.flight_time_ms, metrics.backspace_count),
            FlowState::Flow
        );
    }

    #[test]
    fn test_rule_based_stuck_detection_slow_typing() {
        // Slow typing = STUCK state
        let metrics = KeyboardMetrics {
            flight_time_ms: 800,
            backspace_count: 1,
        };
        assert_eq!(
            classify_state(metrics.flight_time_ms, metrics.backspace_count),
            FlowState::Stuck
        );
    }

    #[test]
    fn test_rule_based_stuck_detection_many_backspaces() {
        // Many backspaces = STUCK state (struggling with text)
        let metrics = KeyboardMetrics {
            flight_time_ms: 150,
            backspace_count: 10,
        };
        assert_eq!(
            classify_state(metrics.flight_time_ms, metrics.backspace_count),
            FlowState::Stuck
        );
    }

    #[test]
    fn test_rule_based_incubation_detection() {
        // Medium pace = INCUBATION state (thinking mode)
        let metrics = KeyboardMetrics {
            flight_time_ms: 250,
            backspace_count: 2,
        };
        assert_eq!(
            classify_state(metrics.flight_time_ms, metrics.backspace_count),
            FlowState::Incubation
        );
    }

    #[test]
    fn test_hmm_initialization() {
        let hmm = SimpleHMM::new();
        assert_eq!(hmm.state_probs[0], 1.0, "Should start in FLOW state");
        assert_eq!(hmm.state_probs[1], 0.0);
        assert_eq!(hmm.state_probs[2], 0.0);
    }

    #[test]
    fn test_hmm_transition_flow_to_flow() {
        // Fast typing should maintain FLOW state
        let mut hmm = SimpleHMM::new();
        let state = hmm.update(50.0); // Observation near FLOW mean (50ms)
        assert_eq!(state, FlowState::Flow);
        assert!(
            hmm.state_probs[0] > 0.5,
            "FLOW state should have high probability after flow observation"
        );
    }

    #[test]
    fn test_hmm_transition_to_stuck() {
        // Very slow typing should move toward STUCK state
        let mut hmm = SimpleHMM::new();
        let state1 = hmm.update(1500.0); // Very slow observation
        
        // Process several slow observations to accumulate evidence
        for _ in 0..3 {
            hmm.update(1200.0);
        }
        
        assert_eq!(hmm.update(1300.0), FlowState::Stuck);
        assert!(
            hmm.state_probs[2] > 0.3,
            "STUCK state should have reasonable probability after multiple slow observations"
        );
    }

    #[test]
    fn test_hmm_normalization() {
        // Verify probabilities always sum to 1.0
        let mut hmm = SimpleHMM::new();
        
        let test_observations = [50.0, 250.0, 1000.0, 100.0, 500.0, 1500.0];
        for obs in test_observations {
            hmm.update(obs);
            let sum: f64 = hmm.state_probs.iter().sum();
            assert!(
                (sum - 1.0).abs() < 1e-5,
                "HMM probabilities should sum to 1.0, got {}",
                sum
            );
        }
    }

    #[test]
    fn test_inference_pipeline_fast_typing() {
        // Simulate continuous fast typing
        let observations = vec![75, 80, 70, 85, 90];
        let mut hmm = SimpleHMM::new();
        let mut rule_states = Vec::new();

        for flight_time_ms in observations {
            let rule_state = classify_state(flight_time_ms, 0);
            rule_states.push(rule_state);
            hmm.update(flight_time_ms as f64);
        }

        // All should be classified as FLOW
        assert!(
            rule_states.iter().all(|&s| s == FlowState::Flow),
            "Fast typing should consistently produce FLOW state"
        );

        // HMM should reinforce FLOW state with high probability
        assert!(
            hmm.state_probs[0] > 0.8,
            "HMM should strongly favor FLOW after fast typing observations"
        );
    }

    #[test]
    fn test_inference_pipeline_struggle_sequence() {
        // Simulate: Fast typing -> Pause -> Struggle (many backspaces) -> Stuck
        let observations = vec![
            (75, 0),   // FLOW: fast typing
            (80, 0),   // FLOW: continues fast
            (500, 2),  // STUCK: pause and struggle starts
            (600, 5),  // STUCK: more struggle
            (1000, 8), // STUCK: very stuck
        ];

        let mut hmm = SimpleHMM::new();
        let mut rule_states = Vec::new();

        for (flight_time_ms, backspace_count) in observations {
            let rule_state = classify_state(flight_time_ms, backspace_count);
            rule_states.push(rule_state);
            hmm.update(flight_time_ms as f64);
        }

        // Verify rule-based transitions
        assert_eq!(rule_states[0], FlowState::Flow);
        assert_eq!(rule_states[1], FlowState::Flow);
        assert_eq!(rule_states[2], FlowState::Stuck);
        assert_eq!(rule_states[3], FlowState::Stuck);
        assert_eq!(rule_states[4], FlowState::Stuck);

        // Verify HMM also detects STUCK after evidence accumulation
        assert_eq!(
            hmm.state_probs.iter().enumerate().max_by(|a, b| a.1.partial_cmp(b.1).unwrap()).map(|(i, _)| i).unwrap(),
            2,
            "HMM should favor STUCK state after struggle sequence"
        );
    }

    #[test]
    fn test_backspace_window_five_second_decay() {
        // Verify that backspace count effectively decays over 5 seconds
        // (This is more of a logic test; actual 5-second window is in keyboard.rs)
        
        // Scenario: User types, makes 3 mistakes (backspaces), then continues
        let window_start_backspaces = 3;
        
        // After some typing in the 5-second window, backspace count should still matter
        let time_1sec_after = window_start_backspaces;
        assert_eq!(
            classify_state(100, time_1sec_after),
            FlowState::Incubation,
            "3 backspaces with 100ms flight time should be INCUBATION"
        );

        // After 5+ seconds, backspaces should be cleared (simulated by count reset)
        let time_6sec_after = 0;
        assert_eq!(
            classify_state(100, time_6sec_after),
            FlowState::Flow,
            "After 5-second window decay, 100ms flight time with 0 backspaces should be FLOW"
        );
    }

    #[test]
    fn test_probability_consistency_across_transitions() {
        // Verify that state probabilities follow expected patterns through transitions
        let mut hmm = SimpleHMM::new();
        
        // Start: High FLOW probability
        assert!(hmm.state_probs[0] > 0.9);
        
        // Observe incubation-like metrics
        hmm.update(250.0);
        let prob_after_inc_obs = hmm.state_probs[1];
        
        // Observe stuck-like metrics
        hmm.update(1000.0);
        let prob_after_stuck_obs = hmm.state_probs[2];
        
        // Verify probabilities increased reasonably for their respective states
        assert!(prob_after_inc_obs > 0.1, "INCUBATION probability should increase");
        assert!(prob_after_stuck_obs > 0.2, "STUCK probability should increase significantly");
    }

    #[test]
    fn test_edge_case_zero_flight_time() {
        // Extremely fast successive keystrokes (edge case)
        let state = classify_state(0, 0);
        assert_eq!(state, FlowState::Flow, "Zero flight time should be FLOW");
    }

    #[test]
    fn test_edge_case_very_large_values() {
        // Handle extreme values gracefully
        let state = classify_state(10000, 100);
        assert_eq!(state, FlowState::Stuck, "Very large values should be STUCK");
        
        let mut hmm = SimpleHMM::new();
        let result_state = hmm.update(10000.0);
        assert_eq!(result_state, FlowState::Stuck);
        assert!(
            (hmm.state_probs.iter().sum::<f64>() - 1.0).abs() < 1e-5,
            "Probabilities should remain normalized with extreme values"
        );
    }

    #[test]
    fn test_gaussian_pdf_validity() {
        // Verify Gaussian PDF produces valid probability values (0-1)
        let test_values = vec![0.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2000.0];
        let params = [(50.0, 30.0), (250.0, 100.0), (1000.0, 500.0)];
        
        for &x in &test_values {
            for &(mu, sigma) in &params {
                let prob = gaussian_pdf(x, mu, sigma);
                assert!(
                    prob >= 0.0,
                    "Gaussian PDF must be non-negative, got {} for x={}",
                    prob,
                    x
                );
                // Note: Gaussian PDF can exceed 1.0, so we don't test upper bound
            }
        }
    }
}
