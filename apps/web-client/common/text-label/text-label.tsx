import React from "react";
import styles from "./text-label.module.css";
import classnames from "classnames";

type TextType =
  | "P025"
  | "P050"
  | "P100"
  | "P200"
  | "P300"
  | "H100"
  | "H200"
  | "H300";

interface TextLabelProps {
  children: string | React.ReactNode;
  type?: TextType;
  color?: "white" | "black" | "gray" | "accent";
  classname?: string;
}

const TextLabel: React.FC<TextLabelProps> = ({
  children,
  classname,
  color = "white",
  type = "P200",
}): JSX.Element => {
  const colorClass =
    color === "white"
      ? styles.colorWhite
      : color === "black"
        ? styles.colorBlack
        : color === "accent"
          ? styles.colorAccent
          : styles.colorGray;

  return (
    <span
      className={classnames(
        styles.textLabel,
        styles[type],
        colorClass,
        classname,
      )}
    >
      {children}
    </span>
  );
};

export default TextLabel;
