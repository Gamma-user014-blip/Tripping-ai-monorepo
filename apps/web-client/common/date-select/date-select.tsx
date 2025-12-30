import React from 'react';
import DatePicker, { DateObject } from 'react-multi-date-picker';
import { CalendarIcon } from '@radix-ui/react-icons';
import TextLabel from '../text-label';
import styles from './date-select.module.css';

type DateSelectProps = {
  value?: DateObject | DateObject[] | null;
  onChange?: (date: DateObject | DateObject[] | null) => void;
  placeholder?: string;
};

const DateSelect: React.FC<DateSelectProps> = ({ 
  value, 
  onChange, 
  placeholder = 'Select dates',
}) => {
  const formatDateRange = (dates: DateObject | DateObject[] | null | undefined): string => {
    if (!dates) return '';
    if (Array.isArray(dates) && dates.length === 2) {
      return `${dates[0].format('MMM DD')} - ${dates[1].format('MMM DD')}`;
    }
    if (!Array.isArray(dates)) {
      return dates.format('MMM DD, YYYY');
    }
    return '';
  };

  const formattedValue = formatDateRange(value);
  const displayText = formattedValue || placeholder;
  const hasValue = !!formattedValue;

  return (
    <DatePicker
      value={value as any}
      onChange={onChange}
      range
      numberOfMonths={2}
      portal
      render={(_valueStr: any, openCalendar: () => void) => (
        <button 
          type="button"
          onClick={openCalendar} 
          className={styles.trigger}
        >
          <span className={`${styles.valueWrapper} ${!hasValue ? styles.placeholderText : ''}`}>
            <TextLabel type="P100" color={hasValue ? "accent" : "gray"}>
              {displayText}
            </TextLabel>
          </span>
          <CalendarIcon className={styles.icon} width={16} height={16} />
        </button>
      )}
      className={styles.datePickerWrapper}
      calendarPosition="bottom-start"
    />
  );
};

export default DateSelect;
