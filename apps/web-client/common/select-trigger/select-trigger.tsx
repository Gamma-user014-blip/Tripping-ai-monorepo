import React, { ReactNode } from "react";
import * as RadixSelect from "@radix-ui/react-select";
import { ChevronDownIcon, ChevronUpIcon } from "@radix-ui/react-icons";
import TextLabel from "../text-label";
import styles from "./select-trigger.module.css";

interface SelectTriggerProps {
  text?: string;
  showAlways?: boolean;
  onPointerDown?: (event: React.PointerEvent<HTMLButtonElement>) => void;
  renderContent?: () => ReactNode;
}

const SelectTrigger: React.FC<SelectTriggerProps> = ({
  text,
  showAlways = false,
  onPointerDown,
  renderContent,
}): JSX.Element => {
  const content = renderContent ? renderContent() : (
    <TextLabel type="P100" color="black">
      {text}
    </TextLabel>
  );

  return (
    <RadixSelect.Trigger
      className={styles.trigger}
      aria-label={text}
      onPointerDown={onPointerDown}
    >
      <span className={styles.valueWrapper}>
        {showAlways || renderContent ? (
          content
        ) : (
          <RadixSelect.Value placeholder={text} asChild>
            {content}
          </RadixSelect.Value>
        )}
      </span>
      <RadixSelect.Icon className={styles.icon}>
        <ChevronDownIcon
          className={styles.iconDown}
          width={16}
          height={16}
          aria-hidden="true"
        />
        <ChevronUpIcon
          className={styles.iconUp}
          width={16}
          height={16}
          aria-hidden="true"
        />
      </RadixSelect.Icon>
    </RadixSelect.Trigger>
  );
};

export default SelectTrigger;
