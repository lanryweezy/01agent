Plan:
1. Edit `01agent/desktop/01agent-app/src/components/Elements/Selects/index.js`
2. Import `useCallback` from `react` (it only imports `useState, useEffect, useRef, useMemo` right now).
3. Wrap `getItemFromValue` in `useCallback` with dependency `[itemsByValue]`.
4. Wrap `getMultipleSelectionText` in `useCallback` with dependency `[getItemFromValue, itemText]`. It also needs to explicitly handle `selected` since we remove the default parameter which accessed `selectedItems` state, BUT we don't need the default parameter since it's always called with an argument! Wait, in `onItemSelected`, it's called with `newSelected`: `getMultipleSelectionText(newSelected)`. In `useEffect`, it's called with `value`: `getMultipleSelectionText(value)`. There are NO calls to `getMultipleSelectionText()` without arguments!
5. Remove `// eslint-disable-next-line react-hooks/exhaustive-deps` above `filteredItems` useMemo. Add `getItemFromValue` to its dependency array: `[items, multiple, value, itemText, inputText, getItemFromValue]`
6. Remove `// eslint-disable-next-line react-hooks/exhaustive-deps` above `useEffect`. Add `multiple, getItemFromValue, itemText, getMultipleSelectionText` to its dependency array: `[value, multiple, getItemFromValue, itemText, getMultipleSelectionText]`.

Wait! The `useEffect` calls `setSelectedItems(value)`.
```javascript
      if (multiple) {
        setSelectedItems(value);
        setInputText(getMultipleSelectionText(value));
      }
```
If we add `multiple`, `getItemFromValue`, `itemText`, `getMultipleSelectionText` to the `useEffect` dependencies, and `multiple` changes... wait, `multiple` shouldn't change. But even if it does, `useEffect` correctly resyncs.

Let's do this targeted Git merge diff.
