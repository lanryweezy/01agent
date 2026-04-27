## 2024-04-27 - [Prevent Unnecessary Re-renders in Chat List]
**Learning:** In React, heavy components rendered in long lists (like `ChatMessage` which parses JSON strings) will severely degrade performance if they re-render on every parent state change (e.g., typing in a chat input field).
**Action:** Always wrap list items in `React.memo()` if they depend only on specific props. Add performance metrics and explicit comments to document the expected impact of the optimization. Avoid committing unrelated configurations.
