import type { AppProps } from "next/app";
import "../styles/variables.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/400.css";

const App = ({ Component, pageProps }: AppProps): JSX.Element => {
  return <Component {...pageProps} />;
};

export default App;