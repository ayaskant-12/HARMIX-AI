// ======================================================
// HARMIX AI Frontend
// frontend/js/app.js
// ======================================================

const API_BASE = "http://localhost:8000";

// ======================================================
// Global Application State
// ======================================================

// Stores the response returned after HAR upload
let currentHAR = null;

// Stores only completed conversation messages
let chatHistory = [];

// Prevent multiple chat requests at the same time
let chatSending = false;


// ======================================================
// Navigation
// ======================================================

function showTab(tabId) {

    // Hide all tabs
    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // Remove active state from sidebar
    document.querySelectorAll(".nav-links li").forEach(li => {
        li.classList.remove("active");
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabId);

    if (selectedTab) {
        selectedTab.classList.add("active");
    }

    // Activate matching sidebar item
    document.querySelectorAll(".nav-links li").forEach(li => {

        const onclickValue = li.getAttribute("onclick");

        if (
            onclickValue &&
            onclickValue.includes(`'${tabId}'`)
        ) {
            li.classList.add("active");
        }

    });
}


// ======================================================
// Upload HAR
// ======================================================

async function uploadFile() {

    const fileInput =
        document.getElementById("harFileInput");

    if (!fileInput) {
        console.error("HAR file input not found.");
        return;
    }

    if (!fileInput.files.length) {

        alert("Select a HAR file first.");

        return;
    }

    const file = fileInput.files[0];

    // Basic client-side validation
    if (!file.name.toLowerCase().endsWith(".har")) {

        alert("Please select a valid .har file.");

        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    const loading =
        document.getElementById("loading");

    if (loading) {
        loading.style.display = "block";
        loading.innerText = "Processing HAR file...";
    }

    try {

        // --------------------------------------------------
        // Upload HAR to FastAPI
        // --------------------------------------------------

        const response = await fetch(
            `${API_BASE}/api/upload-har`,
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {

            let errorMessage =
                `Upload failed. HTTP ${response.status}`;

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.error || errorMessage;

            } catch (e) {
                // Ignore JSON parsing error
            }

            throw new Error(errorMessage);
        }

        const data =
            await response.json();

        // --------------------------------------------------
        // Validate Backend Response
        // --------------------------------------------------

        if (data.status !== "success") {

            throw new Error(
                data.error || "HAR processing failed."
            );
        }

        // --------------------------------------------------
        // Store HAR Context
        // --------------------------------------------------

        currentHAR = data;

        // Reset chat for the new HAR
        chatHistory = [];

        // --------------------------------------------------
        // Dashboard Statistics
        // --------------------------------------------------

        const totalApis =
            document.getElementById("total-apis");

        if (totalApis) {

            totalApis.innerText =
                data.total_requests || 0;
        }

        // --------------------------------------------------
        // Calculate Correlation Candidates
        // --------------------------------------------------

        const apis =
            Array.isArray(data.apis)
                ? data.apis
                : [];

        const correlations =
            apis.filter(api => {

                return (
                    api &&
                    (
                        api.correlation ||
                        api.correlation_candidate ||
                        api.correlation_candidates
                    )
                );

            }).length;

        const correlationElement =
            document.getElementById(
                "corr-candidates"
            );

        if (correlationElement) {

            correlationElement.innerText =
                correlations;
        }

        // --------------------------------------------------
        // Generate AI Executive Analysis
        // --------------------------------------------------

        if (loading) {
            loading.innerText =
                "Generating AI Performance Analysis...";
        }

        await analyzeHAR();

        // --------------------------------------------------
        // Enable Download Buttons
        // --------------------------------------------------

        const pdfButton =
            document.getElementById(
                "btn-download-pdf"
            );

        const jmxButton =
            document.getElementById(
                "btn-download-jmx"
            );

        if (pdfButton) {
            pdfButton.style.display =
                "inline-block";
        }

        if (jmxButton) {
            jmxButton.style.display =
                "inline-block";
        }

        // --------------------------------------------------
        // Reset Chat Window
        // --------------------------------------------------

        resetChatWindow();

        // --------------------------------------------------
        // Success
        // --------------------------------------------------

        alert(
            "HAR processed successfully!\n\n" +
            `${data.total_requests || 0} API requests detected.\n` +
            "JMX Test Plan generated."
        );

        // Open AI Analysis
        showTab("analysis");

    }

    catch (error) {

        console.error(
            "HARMIX Upload Error:",
            error
        );

        alert(
            error.message ||
            "Failed to process HAR file."
        );

    }

    finally {

        if (loading) {
            loading.style.display =
                "none";
        }

    }
}


// ======================================================
// AI Executive Analysis
// ======================================================

async function analyzeHAR() {

    if (!currentHAR) {

        console.warn(
            "No HAR context available."
        );

        return;
    }

    const summaryElement =
        document.getElementById(
            "ai-summary-content"
        );

    if (summaryElement) {

        summaryElement.innerText =
            "HARMIX AI is analyzing the HAR file...\n\n" +
            "Please wait...";
    }

    try {

        const response = await fetch(
            `${API_BASE}/api/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    apis:
                        currentHAR.apis || []

                })
            }
        );

        if (!response.ok) {

            throw new Error(
                `AI analysis failed. HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        if (summaryElement) {

            summaryElement.innerText =
                data.analysis ||
                "No AI analysis was generated.";
        }

        return data.analysis;

    }

    catch (error) {

        console.error(
            "AI Analysis Error:",
            error
        );

        if (summaryElement) {

            summaryElement.innerText =
                "Unable to generate AI analysis.\n\n" +
                error.message;
        }

        return null;
    }
}


// ======================================================
// Download PDF Report
// ======================================================

function downloadPDF() {

    if (!currentHAR) {

        alert(
            "Upload and process a HAR file first."
        );

        return;
    }

    if (!currentHAR.file_id) {

        alert(
            "File ID is missing."
        );

        return;
    }

    const url =
        `${API_BASE}/api/download-report/${encodeURIComponent(
            currentHAR.file_id
        )}`;

    window.open(
        url,
        "_blank"
    );
}


// ======================================================
// Download JMX
// ======================================================

function downloadJMX() {

    if (!currentHAR) {

        alert(
            "Upload and process a HAR file first."
        );

        return;
    }

    if (!currentHAR.file_id) {

        alert(
            "File ID is missing."
        );

        return;
    }

    const url =
        `${API_BASE}/api/download-jmx/${encodeURIComponent(
            currentHAR.file_id
        )}`;

    window.open(
        url,
        "_blank"
    );
}


// ======================================================
// Chat UI
// ======================================================

function appendMessageToUI(
    role,
    text
) {

    const chatWindow =
        document.getElementById(
            "chat-window"
        );

    if (!chatWindow) {

        console.error(
            "Chat window not found."
        );

        return;
    }

    const msgDiv =
        document.createElement("div");

    msgDiv.style.marginBottom =
        "15px";

    msgDiv.style.padding =
        "12px";

    msgDiv.style.borderRadius =
        "8px";

    msgDiv.style.lineHeight =
        "1.6";

    // --------------------------------------------------
    // User Message
    // --------------------------------------------------

    if (role === "user") {

        msgDiv.style.background =
            "rgba(0, 210, 255, 0.10)";

        msgDiv.style.borderLeft =
            "4px solid #00d2ff";

        msgDiv.innerHTML =
            `
            <strong>You:</strong>
            <br>
            ${escapeHTML(text)}
            `;
    }

    // --------------------------------------------------
    // Assistant Message
    // --------------------------------------------------

    else if (role === "assistant") {

        msgDiv.style.background =
            "rgba(0, 255, 136, 0.10)";

        msgDiv.style.borderLeft =
            "4px solid #00ff88";

        msgDiv.innerHTML =
            `
            <strong>HARMIX AI:</strong>
            <br>
            ${formatAIResponse(text)}
            `;
    }

    // --------------------------------------------------
    // System / Error Message
    // --------------------------------------------------

    else {

        msgDiv.style.background =
            "rgba(255, 0, 0, 0.08)";

        msgDiv.style.borderLeft =
            "4px solid #ff4444";

        msgDiv.style.color =
            "#ff7777";

        msgDiv.innerHTML =
            `
            <strong>System:</strong>
            <br>
            ${escapeHTML(text)}
            `;
    }

    chatWindow.appendChild(
        msgDiv
    );

    // Auto-scroll
    chatWindow.scrollTop =
        chatWindow.scrollHeight;
}


// ======================================================
// Escape HTML
// Prevent HTML injection from AI/user messages
// ======================================================

function escapeHTML(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ======================================================
// Format AI Response
// ======================================================

function formatAIResponse(text) {

    if (!text) {
        return "No response generated.";
    }

    let safeText =
        escapeHTML(text);

    // Preserve line breaks
    safeText =
        safeText.replace(
            /\n/g,
            "<br>"
        );

    return safeText;
}


// ======================================================
// Reset Chat Window
// ======================================================

function resetChatWindow() {

    const chatWindow =
        document.getElementById(
            "chat-window"
        );

    if (!chatWindow) {
        return;
    }

    chatWindow.innerHTML = `
        <div
            class="chat-msg system-msg"
            style="
                color:#00d4ff;
                margin-bottom:15px;
            "
        >
            <strong>System:</strong>
            <br><br>

            HAR processed successfully.

            <br><br>

            You can now ask HARMIX AI questions
            about the uploaded HAR file.

            <br><br>

            Examples:

            <br><br>

            • Which APIs require authentication?

            <br>

            • Which APIs have correlation candidates?

            <br>

            • What are the performance risks?

            <br>

            • What are the response times?

            <br>

            • Which APIs should be parameterized?

            <br>

            • What JMeter assertions should I use?

            <br>

            • What timers should I configure?

        </div>
    `;
}


// ======================================================
// AI Chat
// ======================================================

async function sendChatMessage() {

    // --------------------------------------------------
    // Validate HAR
    // --------------------------------------------------

    if (!currentHAR) {

        alert(
            "Upload and process a HAR file first."
        );

        return;
    }

    // --------------------------------------------------
    // Prevent duplicate requests
    // --------------------------------------------------

    if (chatSending) {
        return;
    }

    const input =
        document.getElementById(
            "chat-input"
        );

    if (!input) {

        console.error(
            "Chat input not found."
        );

        return;
    }

    const message =
        input.value.trim();

    if (!message) {
        return;
    }

    // --------------------------------------------------
    // Save previous history BEFORE adding
    // current question.
    //
    // This prevents the current message from being
    // sent twice to the backend.
    // --------------------------------------------------

    const previousHistory =
        [...chatHistory];

    // --------------------------------------------------
    // Display user message
    // --------------------------------------------------

    appendMessageToUI(
        "user",
        message
    );

    // Clear input immediately
    input.value = "";

    // Disable input while AI responds
    input.disabled = true;

    chatSending = true;

    // --------------------------------------------------
    // Show thinking message
    // --------------------------------------------------

    const thinkingId =
        showThinkingMessage();

    try {

        // ------------------------------------------------
        // Build HAR Context
        // ------------------------------------------------

        const contextData = {

            apis:
                currentHAR.apis || [],

            warnings:
                currentHAR.warnings || []

        };

        // ------------------------------------------------
        // Call FastAPI /api/chat
        // ------------------------------------------------

        const response = await fetch(
            `${API_BASE}/api/chat`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    file_id:
                        currentHAR.file_id,

                    message:
                        message,

                    history:
                        previousHistory,

                    context_data:
                        contextData

                })
            }
        );

        // ------------------------------------------------
        // Handle HTTP errors
        // ------------------------------------------------

        if (!response.ok) {

            let errorMessage =
                `Chat request failed. HTTP ${response.status}`;

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.error ||
                    errorMessage;

            }
            catch (e) {
                // Ignore JSON parsing errors
            }

            throw new Error(
                errorMessage
            );
        }

        // ------------------------------------------------
        // Parse response
        // ------------------------------------------------

        const data =
            await response.json();

        // ------------------------------------------------
        // Remove Thinking Indicator
        // ------------------------------------------------

        removeThinkingMessage(
            thinkingId
        );

        // ------------------------------------------------
        // Successful Response
        // ------------------------------------------------

        if (
            data.status === "success" &&
            data.reply
        ) {

            appendMessageToUI(
                "assistant",
                data.reply
            );

            // Store completed user message
            chatHistory.push({

                role: "user",

                content: message

            });

            // Store AI response
            chatHistory.push({

                role: "assistant",

                content: data.reply

            });

        }

        // ------------------------------------------------
        // Backend Error
        // ------------------------------------------------

        else {

            appendMessageToUI(
                "system",
                data.error ||
                "HARMIX AI returned an empty response."
            );
        }

    }

    catch (error) {

        console.error(
            "HARMIX Chat Error:",
            error
        );

        removeThinkingMessage(
            thinkingId
        );

        appendMessageToUI(
            "system",
            error.message ||
            "Unable to connect to HARMIX AI backend."
        );

    }

    finally {

        chatSending = false;

        input.disabled = false;

        input.focus();

    }
}


// ======================================================
// Thinking Indicator
// ======================================================

function showThinkingMessage() {

    const chatWindow =
        document.getElementById(
            "chat-window"
        );

    if (!chatWindow) {
        return null;
    }

    const id =
        "thinking-" +
        Date.now();

    const thinking =
        document.createElement("div");

    thinking.id = id;

    thinking.style.marginBottom =
        "15px";

    thinking.style.padding =
        "12px";

    thinking.style.borderRadius =
        "8px";

    thinking.style.background =
        "rgba(0,255,136,.05)";

    thinking.style.borderLeft =
        "4px solid #00ff88";

    thinking.innerHTML =
        `
        <strong>HARMIX AI:</strong>
        <br>
        <span>Analyzing HAR context...</span>
        `;

    chatWindow.appendChild(
        thinking
    );

    chatWindow.scrollTop =
        chatWindow.scrollHeight;

    return id;
}


// ======================================================
// Remove Thinking Indicator
// ======================================================

function removeThinkingMessage(id) {

    if (!id) {
        return;
    }

    const element =
        document.getElementById(id);

    if (element) {
        element.remove();
    }
}


// ======================================================
// Enter Key Support
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const input =
            document.getElementById(
                "chat-input"
            );

        if (!input) {
            return;
        }

        input.addEventListener(
            "keydown",
            function (event) {

                // Enter = Send
                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendChatMessage();
                }

            }
        );

    }
);


// ======================================================
// Backend Health Check
// ======================================================

async function checkBackendHealth() {

    try {

        const response =
            await fetch(
                `${API_BASE}/docs`,
                {
                    method: "GET"
                }
            );

        return response.ok;

    }
    catch (error) {

        console.warn(
            "HARMIX backend is not reachable."
        );

        return false;
    }
}


// ======================================================
// Initialize Application
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        console.log(
            "===================================="
        );

        console.log(
            "HARMIX AI Frontend Initialized"
        );

        console.log(
            "Backend:",
            API_BASE
        );

        console.log(
            "===================================="
        );

        // Make sure Dashboard is initially active
        showTab("dashboard");

        // Check backend
        const backendAvailable =
            await checkBackendHealth();

        if (!backendAvailable) {

            console.warn(
                "HARMIX backend is currently unavailable."
            );

        }

    }
);