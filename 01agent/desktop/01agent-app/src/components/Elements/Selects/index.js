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

  const getItemFromValue = useCallback((val) => {
    return itemsByValue.get(val) || null;
  }, [itemsByValue]);

  const [inputText, setInputText] = useState(getItemFromValue(value) !== null ? getItemFromValue(value)[itemText] : '');
  const [selectedItems, setSelectedItems] = useState([]);
  const selectedItemsRef = useRef(selectedItems);
  useEffect(() => {
    selectedItemsRef.current = selectedItems;
  }, [selectedItems]);

  // ⚡ Bolt: Memoize the Set creation to turn O(N) array scans into O(1) lookups
  const selectedItemsSet = useMemo(() => new Set(selectedItems), [selectedItems]);

  const getMultipleSelectionText = useCallback((selected=selectedItemsRef.current) => {
    let text = '';
    if (selected.length === 0) {
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

  const closeOpenSelect = useCallback((event) => {
    if (selectRef.current && !selectRef.current.contains(event.target)) {
      setOptionsOpen(false);
    }
  }, []);

  useEffect(() => {
    window.addEventListener('click', closeOpenSelect, { passive: true });

    return () => {
        window.removeEventListener('click', closeOpenSelect);
    };
  }, [closeOpenSelect]);


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
  }, [value, multiple, getMultipleSelectionText, getItemFromValue, itemText]);

  let SelectContainer = LabeledSelectContainer;
  if (verticalLabel) {
    SelectContainer = VerticalLabeledSelectContainer;
  }

  return (
    <SelectContainer>
      {label && <SelectLabel>{label}</SelectLabel>}
      <Select
        ref={selectRef}
        outlined={outlined}
        background={background}
        padding={padding}
        borderRadius={borderRadius}
        onClick={onSelectClick}
      >
        <SelectInput
          placeholder={placeholder}
          value={inputText}
          readOnly={!searchable}
          onChange={(e) => {
            if (searchable) {
              setInputText(e.target.value);
            }
          }}
        />
        <ListItemIcon>
          {isOptionsOpen ? <IoCaretUp /> : <IoCaretDown />}
        </ListItemIcon>
      </Select>
      {error && <SelectError>{error}</SelectError>}
      {isOptionsOpen && (
        <OptionsDivContainer>
          <OptionsDiv>
            {filteredItems.map((item, index) => {
              return (
                <ListItem
                  key={index}
                  onClick={() => onItemSelected(item[itemValue])}
                >
                  <ListItemContent>
                    <ListItemTitle>{item[itemText]}</ListItemTitle>
                    {item[itemText2] && <ListItemSubtitle>{item[itemText2]}</ListItemSubtitle>}
                  </ListItemContent>
                  {multiple && (
                    <ListItemEnd>
                      {isItemSelected(item[itemValue]) ? <ImCheckboxChecked /> : <ImCheckboxUnchecked />}
                    </ListItemEnd>
                  )}
                </ListItem>
              );
            })}
          </OptionsDiv>
        </OptionsDivContainer>
      )}
    </SelectContainer>
  );
};

export default PieSelect;
