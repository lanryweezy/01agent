## 2024-05-24 - React.memo for ChatMessage
**Learning:** Found that the Thread component re-renders its entire list of messages on every keystroke because `messageText` is local state. This can be very expensive as the thread grows.
**Action:** Always check if list item components are memoized if their parent contains frequently updating state like text inputs.
