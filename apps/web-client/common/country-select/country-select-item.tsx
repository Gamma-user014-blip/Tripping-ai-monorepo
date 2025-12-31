import ReactCountryFlag from 'react-country-flag';
import styles from './country-select-item.module.css';

interface CountrySelectItemProps {
  name: string;
  code: string;
}

export const CountrySelectItem = ({ name, code }: CountrySelectItemProps) => {
  return (
    <div className={styles.item}>
      <ReactCountryFlag countryCode={code} svg />
      <span>{name}</span>
    </div>
  );
};
