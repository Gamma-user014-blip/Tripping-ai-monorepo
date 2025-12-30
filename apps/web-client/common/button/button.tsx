import React from "react";
import classnames from "classnames";
import styles from "./button.module.css";

type ButtonType = "primary" | "secondary";

interface ButtonProps {
  type?: ButtonType;
  classname?: string;
  children: React.ReactNode;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({
  type = "primary",
  classname = "",
  children,
  onClick,
}) => {
  return (
    <button
      className={classnames(styles.button, styles[type], classname)}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default Button;
