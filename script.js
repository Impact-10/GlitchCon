document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector(".chat-toggle");
    const closeButton = document.querySelector(".chevron");
    const chatMessages = document.querySelector(".chat-messages");
    const chatInput = document.querySelector(".chat-input");
    const sendButton = document.querySelector(".send-button");
    const voiceButton = document.querySelector(".voice-button"); // Microphone button

    toggleButton.addEventListener("click", function () {
        sidebar.classList.toggle("expanded");
    });

    closeButton.addEventListener("click", function () {
        sidebar.classList.remove("expanded");
    });

    sendButton.addEventListener("click", async function () {
        await sendMessage(chatInput.value.trim());
    });

    chatInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendButton.click();
        }
    });

    async function sendMessage(message) {
        if (!message) return;

        // Display user message
        const userMessage = document.createElement("p");
        userMessage.textContent = "You: " + message;
        chatMessages.appendChild(userMessage);

        // Send message to FastAPI server
        try {
            const response = await fetch("http://127.0.0.1:8000/api/chatbot", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Display bot response
            const botResponse = document.createElement("p");
            botResponse.textContent = "Bot: " + (data.response || "Error occurred");
            chatMessages.appendChild(botResponse);

            // Speak out the bot's response
            speakResponse(data.response);

        } catch (error) {
            console.error("Error fetching response:", error);
        }

        chatInput.value = "";
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function speakResponse(text) {
        let speech = new SpeechSynthesisUtterance(text);
        speech.lang = "en-US";
        speech.rate = 1.0;
        speechSynthesis.speak(speech);
    }

    let recognition;

    voiceButton.addEventListener("click", function () {
        if (!recognition) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "en-US";
            recognition.interimResults = false;
            recognition.onresult = function (event) {
                let spokenText = event.results[0][0].transcript;
                chatInput.value = spokenText;
                sendMessage(spokenText); 
            };

            recognition.onerror = function (event) {
                console.error("Speech recognition error:", event.error);
            };

            recognition.onend = function () {
                console.log("Speech recognition ended.");
            };
        }
        recognition.start();
    });

});
