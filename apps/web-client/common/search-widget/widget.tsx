import React, { useState, useMemo } from "react";
import { DateObject } from "react-multi-date-picker";
import ReactCountryFlag from "react-country-flag";
import { useRouter } from "next/router";
import styles from "./widget.module.css";
import Select from "../select";
import PeopleSelect from "../people-select";
import DateSelect from "../date-select";
import TextLabel from "common/text-label";
import Button from "../button";
import classnames from "classnames";
import countries from "../countries.json";
import airports from "../airports.json";
import { CountrySelectItem } from "../country-select/country-select-item";
import { AirportSelectItem } from "../airport-select/airport-select-item";
import { popularAirportCodes, popularCountryCodes } from "./popular-destinations";

type People = { adults: number; children: number };
type WidgetType = "primary" | "secondary";

interface WidgetProps {
  type?: WidgetType;
}

const Widget: React.FC<WidgetProps> = ({ type = "primary" }): JSX.Element => {
  const router = useRouter();
  const [dateRange, setDateRange] = useState<DateObject | DateObject[] | null>(
    null
  );
  const [fromValue, setFromValue] = useState<string | undefined>(undefined);
  const [toValue, setToValue] = useState<string | undefined>(undefined);
  const [people, setPeople] = useState<People>({ adults: 1, children: 0 });

  const airportOptions = useMemo(() => {
    return airports.map((airport) => ({
      value: airport.iata!,
      label: airport.name!,
      renderLabel: () => (
        <AirportSelectItem name={airport.name!} code={airport.iata!} />
      ),
    }));
  }, []);

  const countryOptions = useMemo(() => {
    const popularCountries = popularCountryCodes
      .map((code) => {
        const country = countries.find((c) => c.code === code);
        return country
          ? {
              value: country.code,
              label: country.name,
              renderLabel: () => (
                <CountrySelectItem name={country.name} code={country.code} />
              ),
            }
          : null;
      })
      .filter((c): c is NonNullable<typeof c> => c !== null);

    const otherCountries = countries
      .filter((country) => !popularCountryCodes.includes(country.code))
      .map((country) => ({
        value: country.code,
        label: country.name,
        renderLabel: () => (
          <CountrySelectItem name={country.name} code={country.code} />
        ),
      }));

    return [...popularCountries, ...otherCountries];
  }, []);

  const renderAirportTrigger = (selectedOption: { value: string; label: string } | undefined) => {
    if (!selectedOption) {
      return <TextLabel type="P100" color="gray">Airport</TextLabel>;
    }
    return <AirportSelectItem name={selectedOption.label} code={selectedOption.value} />;
  };

  const renderCountryTrigger = (selectedOption: { value: string; label: string } | undefined) => {
    if (!selectedOption) {
      return <TextLabel type="P100" color="gray">Locations</TextLabel>;
    }
    return <CountrySelectItem name={selectedOption.label} code={selectedOption.value} />;
  };

  const isDateRangeValid = (d: DateObject | DateObject[] | null): boolean => {
    if (!d) return false;
    if (Array.isArray(d)) return d.length >= 2;
    return true;
  };

  const handleSearch = (): void => {
    const from = fromValue;
    const to = toValue;
    const dates = dateRange;

    if (
      !from ||
      !to ||
      !isDateRangeValid(dates) ||
      !people ||
      people.adults < 1
    ) {
      console.log("Please fill out the search parameters");
      return;
    }

    const formattedDates = Array.isArray(dates)
      ? dates.map((dt) =>
          (dt as any).format ? (dt as any).format("YYYY-MM-DD") : String(dt)
        )
      : dates && (dates as any).format
      ? [(dates as any).format("YYYY-MM-DD")]
      : [String(dates)];

    router.push({
      pathname: '/results',
      query: {
        from,
        to,
        dates: formattedDates.join(','),
        adults: people.adults,
        children: people.children
      }
    });
  };

  return (
    <div
      className={classnames(styles.widgetRoot, {
        [styles.primary]: type === "primary",
        [styles.secondary]: type === "secondary",
      })}
    >
      <div className={styles.selectWrapper}>
        <TextLabel type="P200" classname={styles.label}>
          From
        </TextLabel>
        <Select
          options={airportOptions}
          placeholder="Airport"
          value={fromValue}
          onValueChange={setFromValue}
          renderTriggerLabel={renderAirportTrigger}
        />
      </div>
      <div className={styles.selectWrapper}>
        <TextLabel type="P200" classname={styles.label}>
          To
        </TextLabel>
        <Select
          options={countryOptions}
          placeholder="Locations"
          value={toValue}
          onValueChange={setToValue}
          renderTriggerLabel={renderCountryTrigger}
        />
      </div>
      <div className={styles.selectWrapper}>
        <TextLabel type="P200" classname={styles.label}>
          Dates
        </TextLabel>
        <DateSelect
          value={dateRange}
          onChange={setDateRange}
          placeholder="Select dates"
        />
      </div>
      <div className={styles.selectWrapper}>
        <TextLabel type="P200" classname={styles.label}>
          Group
        </TextLabel>
        <PeopleSelect initial={people} onChange={setPeople} />
      </div>
      <div className={classnames(styles.selectWrapper, styles.buttonWrapper)}>
        <TextLabel type="P200" classname={styles.hidden}>
          a
        </TextLabel>
        <Button
          type="primary"
          classname={styles.searchButton}
          onClick={handleSearch}
        >
          <TextLabel type="P200" classname={styles.searchButtonText}>
            Search
          </TextLabel>
        </Button>
      </div>
    </div>
  );
};

export default Widget;
