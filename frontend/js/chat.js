// frontend/js/chat.js

let chatHistory = [];
let currentHarContext = {}; // Populate this with data from the /api/upload-har response

async function sendChatMessage() {
    const inputField = document.getElementById('chat-input');
    const userMessage = inputField.value.trim();
    if (!userMessage) return;

    // 1. Display user message in UI (Implementation depends on your DOM)
    appendMessageToUI("user", userMessage);
    inputField.value = "";

    try {
        // 2. Call the backend API
        const response = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: "current-file-id", // Update with actual ID
                message: userMessage,
                history: chatHistory,
                context_data: currentHarContext
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // 3. Display AI response
            appendMessageToUI("assistant", data.reply);
            
            // 4. Update local history array for the next turn
            chatHistory.push({ role: "user", content: userMessage });
            chatHistory.push({ role: "assistant", content: data.reply });
        }
    } catch (error) {
        console.error("Chat Error:", error);
        appendMessageToUI("system", "Failed to connect to the AI service.");
    }
}