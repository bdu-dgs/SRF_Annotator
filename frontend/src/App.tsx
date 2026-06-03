import { CssBaseline, ThemeProvider } from "@mui/material";

import AnnotationPage from "./pages/AnnotationPage";
import { theme } from "./theme";

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AnnotationPage />
    </ThemeProvider>
  );
}

