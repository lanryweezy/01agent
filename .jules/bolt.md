## 2024-05-24 - React Re-renders
**Learning:** In `Thread.js`, `messages.map` is executed on every keystroke because `messageText` is part of `Thread` state. While `ChatMessage` handles memoization, recreating the VDOM nodes for potentially hundreds of messages on every keystroke is expensive (O(N) VDOM allocation). We can memoize the `ChatContainer` contents or the whole message list using `useMemo` so that the message list VDOM is only re-evaluated when `messages` actually changes, not on every keystroke.
**Action:** Let's optimize `Thread.js` by wrapping the `messages.map` in a `useMemo` block that only depends on `messages`. This is a classic and very measurable performance improvement.
## 2024-05-24 - Optimizing high frequency mappings
**Learning:** `AgentStatus` receives high-frequency updates to the `agentStatus` prop because it logs fast telemetry changes. Un-memoized mappings like `Object.entries(agentStatus.systemHealth).map` inside the component body create new VDOM elements on every tick.
**Action:** Used `useMemo` on these mapping operations to ensure VDOM elements are cached across telemetry pings. Be careful to ensure correct imports of `useMemo`.
## 2024-05-24 - React JSON.stringify inside renders
**Learning:** Calling `JSON.stringify` inside the render function or a `.map` loop mapping data directly to elements (e.g. `{typeof value === 'object' ? JSON.stringify(value) : value}`) forces synchronous serialization on every single component re-render. This causes performance issues, especially when rendering lists or objects with frequent parent state updates.
**Action:** When such synchronous computations are required, wrap the heavy render computations or `.map` mappings inside a `useMemo` block with appropriate dependencies so that `JSON.stringify` only fires when the actual data payload changes, rather than on every keystroke or telemetry ping.
## 2024-05-24 - React Component Definition Scope Anti-Pattern
**Learning:** Defining a component (e.g. `SettingItem`) *inside* the render body of another component (e.g. `Settings`) is a major performance anti-pattern. Because the inner function is recreated on every render of the parent (such as when typing in a text field updates the parent's state), React treats it as a fundamentally new component type. This causes the child component to be completely unmounted and remounted rather than just updated, leading to severe DOM thrashing and loss of input focus.
**Action:** Always extract child components to the module scope (outside the parent component body). Pass any required state from the parent's closure as explicit props. Optionally, wrap the extracted component in `React.memo` if its props are primitives or properly memoized references (like `useCallback`), though extraction alone solves the critical unmount/remount issue.
## 2024-05-24 - Parent State Thrashing List Iteration
**Learning:** In components with frequently updating state (like `ModernSidebar.js` receiving simulated telemetry ticks every 2s via `setPerformanceData`), mapping over static or semi-static lists directly inside the JSX causes O(N) VDOM node recreation on every update.
**Action:** Always memoize mapped lists using `useMemo` when they are housed in parent components experiencing high-frequency state updates, correctly declaring dependencies (e.g., `location.pathname`, `isDarkMode`, `agentStatus`) to only recalculate when relevant visual properties change.
## 2024-05-24 - React useMemo on Static Arrays vs Dynamic Telemetry
**Learning:** In the React frontend, static or infrequently changing array mappings (like `navigationItems` in `ModernSidebar.js`) should be wrapped in `useMemo` to prevent O(N) VDOM node recreation during high-frequency parent state updates (such as telemetry ticks updating `performanceData`). However, you should *not* use `useMemo` to memoize list mappings of real-time or frequently updating data itself (e.g., the execution metrics mappings in `Performance.js`), as this is a premature micro-optimization that provides no measurable impact due to constant recalculation.
**Action:** Always identify if the mapping is tracking high-frequency changing state or if it's static/infrequently changing but being forced to re-render *because* of sibling high-frequency state updates. Memoize the latter.
## 2024-05-24 - Hash Map Optimization in React
**Learning:** Performing `O(N)` linear array scans (like `for` loops to find items by value) inside renders or frequently called functions within components (e.g., `PieSelect`) can degrade performance when scaled.
**Action:** Replace linear scans with `O(1)` hash map lookups (`Map`). Crucially, wrap the map creation in `useMemo` so it is only rebuilt when the underlying data changes, not on every render.

## 2024-05-24 - React Stale Closures & Linter
**Learning:** Disabling the `react-hooks/exhaustive-deps` linter rule to omit a function (like an event handler) from a `useMemo` or `useCallback` dependency array to force a micro-optimization is a dangerous anti-pattern. It creates **stale closures** where the memoized function references outdated state or props, breaking component functionality.
**Action:** Never bypass the exhaustive-deps linter to avoid recalculations. If a function causes unwanted recalculations, wrap the function itself in `useCallback` higher up the component tree.
## 2024-05-24 - Database index for performance
**Learning:** Adding indexes to frequently accessed foreign keys (like user_id, thread_task_id, author_id) in SQLModel prevents sequential scans during table joins, significantly improving read query performance with minimal cost to writes.
**Action:** Use `index=True` on frequently queried fields in SQLModel/SQLAlchemy models.

## 2024-05-24 - React Rules of Hooks within JSX
**Learning:** You cannot call hooks like `useMemo` inline directly inside the return statement's JSX, even if they aren't conditionally rendered (e.g. `{useMemo(() => <div />, [])}`). This violates the rules of hooks syntax expected by Vite's esbuild React JSX transform, leading to build crashes (`Unexpected end of file before a closing "div" tag`).
**Action:** Always extract `useMemo` computations to the top level of the component's function body and assign them to a variable, then reference that variable inside the JSX `return` block.
## 2026-05-23 - Array Includes to Set
**Learning:** The `.includes()` method on an array performs an `O(N)` linear scan. When this is placed inside a loop that iterates `M` times, it creates an `O(N * M)` operation. In components like `PieSelect` that evaluate selection changes, this can cause performance issues if the list of selected items is large.
**Action:** Convert the array to a `Set` before the loop, and use `.has()` inside the loop. This changes the complexity from `O(N * M)` to `O(N + M)`, providing a significant speedup for large arrays.
