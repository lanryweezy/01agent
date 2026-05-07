## 2024-05-24 - React Re-renders
**Learning:** In `Thread.js`, `messages.map` is executed on every keystroke because `messageText` is part of `Thread` state. While `ChatMessage` handles memoization, recreating the VDOM nodes for potentially hundreds of messages on every keystroke is expensive (O(N) VDOM allocation). We can memoize the `ChatContainer` contents or the whole message list using `useMemo` so that the message list VDOM is only re-evaluated when `messages` actually changes, not on every keystroke.
**Action:** Let's optimize `Thread.js` by wrapping the `messages.map` in a `useMemo` block that only depends on `messages`. This is a classic and very measurable performance improvement.
## 2024-05-24 - Optimizing high frequency mappings
**Learning:** `AgentStatus` receives high-frequency updates to the `agentStatus` prop because it logs fast telemetry changes. Un-memoized mappings like `Object.entries(agentStatus.systemHealth).map` inside the component body create new VDOM elements on every tick.
**Action:** Used `useMemo` on these mapping operations to ensure VDOM elements are cached across telemetry pings. Be careful to ensure correct imports of `useMemo`.
