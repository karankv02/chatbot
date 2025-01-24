import React, { useState } from "react";
import axios from "axios";
import { TextField, Button, Typography, List, ListItem, Box, Paper } from "@mui/material";
import { styled } from "@mui/system";

const UserMessage = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    padding: "10px",
    borderRadius: "10px",
    margin: "5px 0",
    alignSelf: "flex-end",
    maxWidth: "70%",
}));

const BotMessage = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.grey[300],
    color: theme.palette.text.primary,
    padding: "10px",
    borderRadius: "10px",
    margin: "5px 0",
    alignSelf: "flex-start",
    maxWidth: "70%",
}));

const ChatInterface = () => {
    const [query, setQuery] = useState("");
    const [responses, setResponses] = useState([]);

    const handleSend = async () => {
        if (!query) return;

        try {
            const res = await axios.post("http://127.0.0.1:8000/query", { query });
            const chatbotResponse = res.data.response;

            setResponses([...responses, { query, response: chatbotResponse }]);
            setQuery(""); // Clear the input field
        } catch (error) {
            console.error("Error querying the chatbot", error);
        }
    };

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                height: "100vh",
                padding: "20px",
                backgroundColor: "#f4f4f9",
            }}
        >
            <Typography variant="h4" align="center" gutterBottom>
                Chat with AI
            </Typography>

            <List
                sx={{
                    flexGrow: 1,
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    padding: "10px",
                    backgroundColor: "#ffffff",
                    borderRadius: "10px",
                    boxShadow: "0px 2px 5px rgba(0,0,0,0.1)",
                }}
            >
                {responses.map((item, index) => (
                    <ListItem
                        key={index}
                        sx={{
                            display: "flex",
                            justifyContent: item.query ? "flex-end" : "flex-start",
                        }}
                    >
                        {item.query && <UserMessage>{item.query}</UserMessage>}
                        {item.response && <BotMessage>{item.response}</BotMessage>}
                    </ListItem>
                ))}
            </List>

            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    mt: 2,
                    gap: "10px",
                }}
            >
                <TextField
                    fullWidth
                    variant="outlined"
                    label="Type your query..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSend}
                    disabled={!query.trim()}
                    sx={{ whiteSpace: "nowrap" }}
                >
                    Send
                </Button>
            </Box>
        </Box>
    );
};

export default ChatInterface;
