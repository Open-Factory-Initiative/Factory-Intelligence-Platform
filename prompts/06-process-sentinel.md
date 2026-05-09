# Prompt 06: Process Sentinel

Act as a senior quality/process engineering software architect.

Goal: implement the first explainable Process Sentinel drift detection service.

Implement deterministic rules for:

- Gradual process drift
- Quality measurement trend toward spec limit
- Sudden process excursion

Requirements:

- Use simulator scenarios
- Use shared event contracts
- Produce detection records
- Attach time windows
- Attach severity and confidence
- Include unit tests for normal, drift, noisy, missing-data, and boundary cases
- Update architecture/testing docs if needed
- Update learning log

Do not use opaque ML for this prompt.
