import React, { useState, useEffect, useRef, useMemo } from 'react';
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

  const getItemFromValue = (value) => {
    return itemsByValue.get(value) || null;
  };

  const [inputText, setInputText] = useState(getItemFromValue(value) !== null ? getItemFromValue(value)[itemText] : '');
  const [selectedItems, setSelectedItems] = useState([]);

  const getMultipleSelectionText = (selected=selectedItems) => {
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
  };

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
    return selectedItems.includes(value);
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items, multiple, value, itemText, inputText]);

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
        setInputText(item !== null ? item[itemText] : '');
      }
    } else {
      setInputText('');
    }
  }, [value]);

  if (label !== null) {
    if (!verticalLabel) {
      return (
        <>
          <LabeledSelectContainer>
            <SelectLabel>
              {label}
            </SelectLabel>
            <div style={{flex: '1 1 75%'}}>
              <Select background={background} padding={padding}
                ref={selectRef}
                borderRadius={borderRadius} outlined={outlined} onClick={() => onSelectClick()}>
                <SelectInput placeholder={placeholder}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  readOnly={!searchable || multiple}
                  type="text" />
                <div style={{marginLeft: 'auto'}}>
                  <ListItemIcon iconSize="22px">
                    {
                      !isOptionsOpen ? <IoCaretDown /> : <IoCaretUp />
                    }
                  </ListItemIcon>
                </div>
                {
                  isOptionsOpen ?
                  <OptionsDiv>
                    <OptionsDivContainer>
                      {
                        filteredItems.map((item, key) => {
                          return <ListItem clickable onClick={() => onItemSelected(item[itemValue])} key={'option__' + key}>
                            <ListItemContent>
                              <ListItemTitle fontWeight="400" fontSize="14px">
                                {item[itemText]}
                              </ListItemTitle>
                              {
                                itemText2 !== null ? 
                                <ListItemSubtitle fontWeight='400' fontSize='13px' color='rgba(0, 0, 0, 0.7)'>
                                  {item[itemText2]}
                                </ListItemSubtitle> : <></>
                              }
                            </ListItemContent>
                            {
                              multiple ?
                              <ListItemEnd>
                                <ListItemIcon color="var(--primary-color)" iconSize="20px">
                                  {
                                    isItemSelected(item[itemValue]) ? <ImCheckboxChecked /> : <ImCheckboxUnchecked />
                                  }
                                </ListItemIcon>
                              </ListItemEnd> : <></>
                            }
                          </ListItem>;
                        })
                      }
                    </OptionsDivContainer>
                  </OptionsDiv> :
                  <></>
                }
              </Select>
              {
                error !== null ?
                <SelectError>
                  {error}
                </SelectError> :
                <></>
              }
            </div>
          </LabeledSelectContainer>
        </>
      );
    } else {
      return (
        <>
          <VerticalLabeledSelectContainer>
            <SelectLabel verticalLabel>
              {label}
            </SelectLabel>
            <Select background={background} placeholder={placeholder} padding={padding}
              ref={selectRef}
              borderRadius={borderRadius} outlined={outlined} onClick={() => onSelectClick()}>
              <SelectInput placeholder={placeholder}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                readOnly={!searchable || multiple}
                type="text" />
              <div style={{marginLeft: 'auto'}}>
                <ListItemIcon iconSize="22px">
                  {
                    !isOptionsOpen ? <IoCaretDown /> : <IoCaretUp />
                  }
                </ListItemIcon>
              </div>
              {
                isOptionsOpen ?
                <OptionsDiv>
                  <OptionsDivContainer>
                    {
                      filteredItems.map((item, key) => {
                        return <ListItem clickable onClick={() => onItemSelected(item[itemValue])} key={'option__' + key}>
                          <ListItemContent>
                            <ListItemTitle fontWeight="400" fontSize="14px">
                              {item[itemText]}
                            </ListItemTitle>
                            {
                              itemText2 !== null ? 
                              <ListItemSubtitle fontWeight='400' fontSize='13px' color='rgba(0, 0, 0, 0.7)'>
                                {item[itemText2]}
                              </ListItemSubtitle> : <></>
                            }
                          </ListItemContent>
                          {
                            multiple ?
                            <ListItemEnd>
                              <ListItemIcon color="var(--primary-color)" iconSize="20px">
                                {
                                  isItemSelected(item[itemValue]) ? <ImCheckboxChecked /> : <ImCheckboxUnchecked />
                                }
                              </ListItemIcon>
                            </ListItemEnd> : <></>
                          }
                        </ListItem>;
                      })
                    }
                  </OptionsDivContainer>
                </OptionsDiv> :
                <></>
              }
            </Select>
            {
              error !== null ?
              <SelectError>
                {error}
              </SelectError> :
              <></>
            }
          </VerticalLabeledSelectContainer>
        </>
      );
    }
  }
  return (
    <>
      <Select background={background} placeholder={placeholder} padding={padding}
        ref={selectRef}
        borderRadius={borderRadius} outlined={outlined} onClick={() => onSelectClick()}>
        <SelectInput placeholder={placeholder}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          readOnly={!searchable || multiple}
          type="text" />
        <div style={{marginLeft: 'auto'}}>
          <ListItemIcon iconSize="22px">
            {
              !isOptionsOpen ? <IoCaretDown /> : <IoCaretUp />
            }
          </ListItemIcon>
        </div>
        {
          isOptionsOpen ?
          <OptionsDiv>
            {
              filteredItems.map((item, key) => {
                return <ListItem clickable onClick={() => onItemSelected(item[itemValue])} key={'option__' + key}>
                  <ListItemContent>
                    <ListItemTitle fontWeight="400" fontSize="14px">
                      {item[itemText]}
                    </ListItemTitle>
                    {
                      itemText2 !== null ? 
                      <ListItemSubtitle fontWeight='400' fontSize='13px' color='rgba(0, 0, 0, 0.7)'>
                        {item[itemText2]}
                      </ListItemSubtitle> : <></>
                    }
                  </ListItemContent>
                  {
                    multiple ?
                    <ListItemEnd>
                      <ListItemIcon color="var(--primary-color)" iconSize="20px">
                        {
                          isItemSelected(item[itemValue]) ? <ImCheckboxChecked /> : <ImCheckboxUnchecked />
                        }
                      </ListItemIcon>
                    </ListItemEnd> : <></>
                  }
                </ListItem>;
              })
            }
          </OptionsDiv> :
          <></>
        }
      </Select>
      <SelectError>
        {error}
      </SelectError>
    </>
  );
};

export default PieSelect;
