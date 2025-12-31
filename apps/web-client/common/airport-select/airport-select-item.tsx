import styles from './airport-select-item.module.css';

interface AirportSelectItemProps {
  name: string;
  code: string;
}

const AirportIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={styles.icon}
    style={{ transform: 'rotate(45deg)' }}
  >
    <path
      d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"
      fill="currentColor"
    />
  </svg>
);

export const AirportSelectItem = ({ name, code }: AirportSelectItemProps) => {
  return (
    <div className={styles.item}>
      <AirportIcon />
      <span>{name}</span>
    </div>
  );
};
