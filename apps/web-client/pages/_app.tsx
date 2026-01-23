import type { AppProps } from "next/app";
import Head from "next/head";
import { Toaster } from "react-hot-toast";
import "../styles/variables.css";
import "@fontsource/inter/300.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "maplibre-gl/dist/maplibre-gl.css";

const App = ({ Component, pageProps }: AppProps): JSX.Element => {
  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
        />
      </Head>
      <Component {...pageProps} />
      <Toaster
        position="bottom-center"
        toastOptions={{
          duration: 1800,
          style: {
            background: "var(--color-card-background)",
            color: "var(--color-text-dark)",
            border: "1px solid var(--border-muted)",
            boxShadow: "0 8px 24px var(--shadow-faint)",
            borderRadius: "12px",
            padding: "10px 14px",
            fontFamily: "Inter, sans-serif",
            fontSize: "13px",
            fontWeight: 600,
          },
          success: {
            iconTheme: {
              primary: "var(--color-teal-dark)",
              secondary: "var(--color-card-background)",
            },
          },
          error: {
            iconTheme: {
              primary: "var(--color-danger)",
              secondary: "var(--color-card-background)",
            },
          },
        }}
      />
    </>
  );
};

export default App;
