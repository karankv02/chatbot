import React from "react";
import ChatInterface from "./components/ChatInterface";
import { ThemeProvider, createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        primary: {
            main: "#1976d2", // Define your primary color
        },
        secondary: {
            main: "#f50057", // Optional: Define your secondary color
        },
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <ChatInterface />
        </ThemeProvider>
    );
}

export default App;
