import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  LabeledSelectContainer,
  VerticalLabeledSelectContainer,
  SelectLabel,
  Select,
  SelectInput,
  SelectError,
  OptionsDiv,
  OptionsDivContainer
} from './Elements';
import {
  ListItem,
  ListItemContent,
  ListItemTitle,
  ListItemIcon,
  ListItemEnd,
  ListItemSubtitle
} from '../List';
import { IoCaretDown, IoCaretUp } from 'react-icons/io5';
import { ImCheckboxUnchecked, ImCheckboxChecked } from 'react-icons/im';

const PieSelect = ({
  label=null,
  verticalLabel=false,
  error=null,
  background='#fff',
  outlined=false,
  padding=null,
  borderRadius=null,
  placeholder=null,
  value=null,
  items=[],
  itemText='text',
  itemText2='null',
  itemValue='value',
  multiple=false,
  searchable=false,
  onChange
}) => {

  const [isOptionsOpen, setOptionsOpen] = useState(false);

  // ⚡ Bolt: Use an O(1) hash map to avoid O(N) array scans during renders and loops
  const itemsByValue = useMemo(() => {
    const map = new Map();
    for (let i = 0; i < items.length; i++) {
      map.set(items[i][itemValue], items[i]);
    }
    return map;
  }, [items, itemValue]);

  // ⚡ Bolt: Wrapped in useCallback to prevent function recreation on every render, allowing it to be safely included in dependency arrays without causing infinite loops or stale closures.
  const getItemFromValue = useCallback((value) => {
    return itemsByValue.get(value) || null;
  }, [itemsByValue]);

  const [inputText, setInputText] = useState(getItemFromValue(value) !== null ? getItemFromValue(value)[itemText] : '');
  const [selectedItems, setSelectedItems] = useState([]);

  // ⚡ Bolt: Memoize the Set creation to turn O(N) array scans into O(1) lookups
  const selectedItemsSet = useMemo(() => new Set(selectedItems), [selectedItems]);

  const getMultipleSelectionText = useCallback((selected) => {
    let text = '';
    if (!selected || selected.length === 0) {
      return '';
    }
    for (let i = 0; i < selected.length; i++) {
      const item = getItemFromValue(selected[i]);
      if (item === null) {
        continue;
      }
      if (text.length === 0) {
        text += item[itemText];
      } else {
        text += ', ' + item[itemText];
      }
    }
    return text;
  }, [getItemFromValue, itemText]);

  const onItemSelected = (value) => {
    if (!multiple) {
      setInputText(getItemFromValue(value)[itemText]);
      onChange(value);
      setOptionsOpen(false);
    } else {
      let newSelected = [...selectedItems];
      if (newSelected.includes(value)) {
        const index = newSelected.indexOf(value);
        newSelected.splice(index, 1);
      } else {
        newSelected.push(value);
      }
      setSelectedItems(newSelected);
      setInputText(getMultipleSelectionText(newSelected));
      onChange(newSelected);
    }
  };

  const isItemSelected = (value) => {
    return selectedItemsSet.has(value);
  }

  const onSelectClick = () => {
    if (!isOptionsOpen) {
      setOptionsOpen(true);
    }
  };

  const filteredItems = useMemo(() => {
    if (multiple) {
      return items;
    } else {
      if (getItemFromValue(value) !== null) {
        if (inputText === getItemFromValue(value)[itemText]) {
          return items;
        }
      }
      if (inputText === null || inputText.length === 0) {
        return items;
      }

      let returnedItems = [];
      for(let i = 0; i < items.length; i++) {
        if (items[i][itemText].includes(inputText)) {
          returnedItems.push(items[i]);
        }
      }
      return returnedItems;
    }
  }, [items, multiple, value, itemText, inputText, getItemFromValue]);

  const selectRef = useRef();

  const closeOpenSelect = (event) => {
    if (selectRef.current && !selectRef.current.contains(event.target)) {
      setOptionsOpen(false);
    }
  };

  useEffect(() => {
    window.addEventListener('click', closeOpenSelect, { passive: true });

    return () => {
        window.removeEventListener('click', closeOpenSelect);
    };
  }, []);

  const isMultipleSelectionChanged = (value) => {
    if (value.length !== selectedItems.length) {
      return true;
    }

    // ⚡ Bolt: Use O(1) Set lookup to prevent O(N) array scan in loop
    const selectedSet = new Set(selectedItems);
    for (let i = 0; i < value.length; i++) {
      if (!selectedSet.has(value[i])) {
        return true;
      }
    }

    return false;
  };

  useEffect(() => {
    if (value !== null) {
      if (multiple) {
        setSelectedItems(value);
        setInputText(getMultipleSelectionText(value));
      } else {
        const item = getItemFromValue(value);
        setInputText(item !== null ? item[itemText] : "");
      }
    } else {
      setInputText("");
    }
  }, [value, multiple, getItemFromValue, itemText, getMultipleSelectionText]);

