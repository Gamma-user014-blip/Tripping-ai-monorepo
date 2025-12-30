import React, { useState, useRef, useEffect, ReactNode } from "react";
import * as RadixSelect from "@radix-ui/react-select";
import TextLabel from "../text-label";
import SearchBar from "../search-bar";
import styles from "./select-content.module.css";

interface SelectOption {
  value: string;
  label: string;
  renderLabel?: () => ReactNode;
}

interface SelectContentProps {
  options: SelectOption[];
}

const SelectContent: React.FC<SelectContentProps> = ({ options }): JSX.Element => {
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredOptions = searchQuery
    ? options.filter((opt) => opt.label.toLowerCase().includes(searchQuery.toLowerCase()))
    : options;

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus({ preventScroll: true });
  }, []);

  return (
    <RadixSelect.Portal>
      <RadixSelect.Content 
        className={styles.content} 
        position="popper" 
        sideOffset={4}
      >
        <div 
          className={styles.searchWrapper}
        >
          <SearchBar
            ref={inputRef}
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search..."
          />
        </div>
        <div className={styles.separator} />
        <RadixSelect.Viewport className={styles.viewport}>
          {filteredOptions.length > 0 ? (
            filteredOptions.map((opt) => (
              <RadixSelect.Item key={opt.value} value={opt.value} className={styles.item}>
                <RadixSelect.ItemText asChild>
                  {opt.renderLabel ? opt.renderLabel() : <TextLabel type="P100" color="black">{opt.label}</TextLabel>}
                </RadixSelect.ItemText>
              </RadixSelect.Item>
            ))
          ) : (
            <div className={styles.noResults}>
              <TextLabel type="P050" color="gray">No results found</TextLabel>
            </div>
          )}
        </RadixSelect.Viewport>
      </RadixSelect.Content>
    </RadixSelect.Portal>
  );
};

export default SelectContent;
