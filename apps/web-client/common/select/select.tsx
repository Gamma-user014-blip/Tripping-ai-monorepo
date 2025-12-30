"use client";

import * as Popover from "@radix-ui/react-popover";
import { ChevronDownIcon, ChevronUpIcon } from "@radix-ui/react-icons";
import React, { useMemo, useState, useRef, useEffect, ReactNode } from "react";
import styles from "./select.module.css";
import triggerStyles from "../select-trigger/select-trigger.module.css";
import contentStyles from "../select-content/select-content.module.css";
import classnames from "classnames";
import TextLabel from "../text-label";
import SearchBar from "../search-bar";

interface SelectOption {
  value: string;
  label: string;
  renderLabel?: () => ReactNode;
}

interface SelectProps {
  options: SelectOption[];
  value?: string;
  placeholder?: string;
  onValueChange?: (value: string) => void;
  className?: string;
  renderTriggerLabel?: (selectedOption: SelectOption | undefined) => ReactNode;
}

const Select: React.FC<SelectProps> = ({
  options,
  value,
  placeholder = "Select an option",
  onValueChange,
  className,
  renderTriggerLabel,
}): JSX.Element => {
  const [internalValue, setInternalValue] = useState<string | undefined>(
    undefined
  );
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleValueChange = (newValue: string): void => {
    if (value === undefined) {
      setInternalValue(newValue);
    }
    onValueChange?.(newValue);
    setOpen(false);
  };

  const selectedValue = value !== undefined ? value : internalValue;

  const selectedOption = useMemo(() => {
    return selectedValue !== undefined
      ? options.find((o) => o.value === selectedValue)
      : undefined;
  }, [selectedValue, options]);

  const filteredOptions = useMemo(() => {
    return searchQuery
      ? options.filter((opt) =>
          opt.label.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : options;
  }, [options, searchQuery]);

  useEffect(() => {
    if (open) {
      setSearchQuery("");
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  const triggerContent = renderTriggerLabel
    ? renderTriggerLabel(selectedOption)
    : selectedOption?.label ?? placeholder;

  const isPlaceholder = !selectedOption;

  return (
    <div className={classnames(styles.selectRoot, className)}>
      <Popover.Root open={open} onOpenChange={setOpen}>
        <Popover.Trigger asChild>
          <button
            className={triggerStyles.trigger}
            type="button"
            data-state={open ? "open" : "closed"}
            data-placeholder={isPlaceholder ? "" : undefined}
          >
            <span className={triggerStyles.valueWrapper}>
              {renderTriggerLabel ? (
                triggerContent
              ) : (
                <TextLabel
                  type="P100"
                  color={isPlaceholder ? "gray" : "accent"}
                >
                  {triggerContent as string}
                </TextLabel>
              )}
            </span>
            <span className={triggerStyles.icon}>
              {open ? (
                <ChevronUpIcon width={16} height={16} aria-hidden="true" />
              ) : (
                <ChevronDownIcon width={16} height={16} aria-hidden="true" />
              )}
            </span>
          </button>
        </Popover.Trigger>
        <Popover.Portal>
          <Popover.Content
            className={contentStyles.content}
            sideOffset={4}
            align="start"
            onOpenAutoFocus={(e: Event) => e.preventDefault()}
          >
            <div className={contentStyles.searchWrapper}>
              <SearchBar
                ref={inputRef}
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search..."
              />
            </div>
            <div className={contentStyles.separator} />
            <div className={contentStyles.viewport}>
              {filteredOptions.length > 0 ? (
                filteredOptions.map((opt) => (
                  <button
                    key={opt.value}
                    className={contentStyles.item}
                    data-state={
                      opt.value === selectedValue ? "checked" : "unchecked"
                    }
                    onClick={() => handleValueChange(opt.value)}
                    type="button"
                  >
                    {opt.renderLabel ? (
                      opt.renderLabel()
                    ) : (
                      <TextLabel type="P100" classname={triggerStyles.label} color="accent">
                        {opt.label}
                      </TextLabel>
                    )}
                  </button>
                ))
              ) : (
                <div className={contentStyles.noResults}>
                  <TextLabel type="P050" color="gray">
                    No results found
                  </TextLabel>
                </div>
              )}
            </div>
          </Popover.Content>
        </Popover.Portal>
      </Popover.Root>
    </div>
  );
};

export default Select;