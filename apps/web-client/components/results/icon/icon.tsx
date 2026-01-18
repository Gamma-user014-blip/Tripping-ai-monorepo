import React from "react";
import { ICON_SVGS, IconName } from "../../../assets/icons/icon-registry";

interface IconProps {
  icon: IconName;
  height?: number | string;
  width?: number | string;
  color?: string;
  className?: string;
}

export const Icon: React.FC<IconProps> = ({
  icon,
  height = 16,
  width,
  color = "black",
  className,
}) => {
  const iconSrc = ICON_SVGS[icon];

  // Helper to extract a string SVG source from various import shapes
  const getSvgString = (src: any): string | null => {
    if (!src) return null;
    if (typeof src === "string") return src;
    if (typeof src === "object") {
      if (typeof src.default === "string") return src.default;
      if (typeof src.src === "string") return src.src;
    }
    return null;
  };

  const svgString = getSvgString(iconSrc);

  // If we have a raw SVG string, decide whether it's inline markup or a URL.
  if (svgString) {
    const isInlineSvg = svgString.indexOf("<svg") !== -1;

    if (isInlineSvg) {
      const svgMarkup = React.useMemo(() => {
        return svgString.replace(
          /<svg\b/,
          '<svg width="100%" height="100%" aria-hidden="true" focusable="false"'
        );
      }, [svgString]);

      return (
        <span
          className={className}
          style={{
            width: width ?? height,
            height,
            color,
            display: "inline-block",
            verticalAlign: "middle",
            lineHeight: 0,
          }}
          dangerouslySetInnerHTML={{ __html: svgMarkup }}
        />
      );
    }

    // Otherwise treat the string as a URL to an SVG asset (e.g. asset/resource).
    // Render an <img> so the browser loads the SVG file instead of injecting the URL text.
    return (
      <img
        src={svgString}
        alt=""
        role="img"
        className={className}
        style={{
          width: width ?? height,
          height,
          display: "inline-block",
          verticalAlign: "middle",
          lineHeight: 0,
        }}
      />
    );
  }

  // If the import is a React component (SVGR), render it directly
  if (typeof iconSrc === "function") {
    const SvgComp = iconSrc as React.ComponentType<React.SVGProps<SVGSVGElement>>;
    return (
      <span
        className={className}
        style={{
          width: width ?? height,
          height,
          color,
          display: "inline-block",
          verticalAlign: "middle",
          lineHeight: 0,
        }}
      >
        <SvgComp width="100%" height="100%" aria-hidden focusable={false} />
      </span>
    );
  }

  // Fallback: try toString and inject if possible
  try {
    const asString = String(iconSrc);
    if (asString && asString.indexOf("<svg") !== -1) {
      const svgMarkup = asString.replace(
        /<svg\b/,
        '<svg width="100%" height="100%" aria-hidden="true" focusable="false"'
      );
      return (
        <span
          className={className}
          style={{
            width: width ?? height,
            height,
            color,
            display: "inline-block",
            verticalAlign: "middle",
            lineHeight: 0,
          }}
          dangerouslySetInnerHTML={{ __html: svgMarkup }}
        />
      );
    }
  } catch (e) {
    // fall through to empty fallback
  }

  // Nothing usable found — render an empty placeholder
  return (
    <span
      className={className}
      style={{
        width: width ?? height,
        height,
        display: "inline-block",
        verticalAlign: "middle",
        lineHeight: 0,
      }}
    />
  );
};

export type { IconName };
