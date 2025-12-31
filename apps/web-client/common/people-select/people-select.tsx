"use client";

import * as Popover from "@radix-ui/react-popover";
import { ChevronDownIcon, ChevronUpIcon } from "@radix-ui/react-icons";
import React, { useMemo, useState } from "react";
import styles from "./people-select.module.css";
import TextLabel from "../text-label";

type People = { adults: number; children: number };

interface PeopleSelectProps {
  initial?: People;
  onChange?: (p: People) => void;
}

const PeopleSelect: React.FC<PeopleSelectProps> = ({
  initial = { adults: 1, children: 0 },
  onChange,
}) => {
  const [people, setPeople] = useState<People>(initial);
  const [open, setOpen] = useState(false);

  const update = (next: People) => {
    setPeople(next);
    onChange?.(next);
  };

  const increase = (key: keyof People) =>
    update({ ...people, [key]: people[key] + 1 });
  const decrease = (key: keyof People, min = 0) =>
    update({ ...people, [key]: Math.max(min, people[key] - 1) });

  const totalGuests = people.adults + people.children;
  const triggerText = useMemo(() => `${totalGuests} Guests`, [totalGuests]);

  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger asChild>
        <button type="button" className={styles.trigger}>
          <span className={styles.valueWrapper}>
            <TextLabel type="P100" color="accent">
              {triggerText}
            </TextLabel>
          </span>
          <span className={styles.icon}>
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
          className={styles.panel}
          sideOffset={6}
          align="start"
        >
          <div className={styles.row}>
            <div className={styles.label}>
              <span className={styles.title}>Adults</span>
              <span className={styles.subtitle}>Ages 18+</span>
            </div>
            <div className={styles.controls}>
              <button
                type="button"
                aria-label="Decrease adults"
                className={styles.counterBtn}
                onClick={() => decrease("adults", 1)}
              >
                -
              </button>
              <div className={styles.counterValue}>{people.adults}</div>
              <button
                type="button"
                aria-label="Increase adults"
                className={styles.counterBtn}
                onClick={() => increase("adults")}
              >
                +
              </button>
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.label}>
              <span className={styles.title}>Children</span>
              <span className={styles.subtitle}>Ages 0-12</span>
            </div>
            <div className={styles.controls}>
              <button
                type="button"
                aria-label="Decrease children"
                className={styles.counterBtn}
                onClick={() => decrease("children", 0)}
              >
                -
              </button>
              <div className={styles.counterValue}>{people.children}</div>
              <button
                type="button"
                aria-label="Increase children"
                className={styles.counterBtn}
                onClick={() => increase("children")}
              >
                +
              </button>
            </div>
          </div>
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
};

export default PeopleSelect;
