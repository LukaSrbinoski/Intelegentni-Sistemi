from flask import Flask, render_template_string, request, jsonify
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameBrain AI - Gaming Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Poppins', sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 50%, #0f141f 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        /* Animated background particles */
        body::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: radial-gradient(rgba(102, 126, 234, 0.15) 2px, transparent 2px);
            background-size: 50px 50px;
            animation: moveBackground 20s linear infinite;
        }

        @keyframes moveBackground {
            0% { transform: translateY(0); }
            100% { transform: translateY(-100px); }
        }

        /* Floating orbs */
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.4;
            animation: float 15s infinite ease-in-out;
        }

        .orb-1 {
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, #667eea, #764ba2);
            top: -100px;
            left: -100px;
        }

        .orb-2 {
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, #f093fb, #f5576c);
            bottom: -150px;
            right: -150px;
            animation-delay: -5s;
        }

        .orb-3 {
            width: 250px;
            height: 250px;
            background: radial-gradient(circle, #4facfe, #00f2fe);
            top: 50%;
            left: 50%;
            animation-delay: -10s;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) translateX(0); }
            33% { transform: translateY(-30px) translateX(20px); }
            66% { transform: translateY(30px) translateX(-20px); }
        }

        .chat-wrapper {
            width: 100%;
            max-width: 1000px;
            height: 85vh;
            background: rgba(18, 22, 35, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
            z-index: 1;
        }

        .chat-header {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            padding: 24px 32px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chat-header h1 {
            font-size: 28px;
            font-weight: 700;
            color: white;
            margin-bottom: 4px;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .chat-header h1 i {
            font-size: 32px;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        .chat-header p {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.85);
            font-weight: 500;
        }

        .status-badge {
            display: inline-block;
            background: rgba(76, 175, 80, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
            color: #4caf50;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        /* Custom scrollbar */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
        }

        .message {
            display: flex;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .user-message {
            justify-content: flex-end;
        }

        .bot-message {
            justify-content: flex-start;
        }

        .avatar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
            flex-shrink: 0;
        }

        .bot-message .avatar {
            background: linear-gradient(135deg, #667eea, #764ba2);
            order: 0;
        }

        .user-message .avatar {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            order: 1;
        }

        .message-content {
            max-width: 65%;
            padding: 12px 18px;
            border-radius: 18px;
            line-height: 1.5;
            word-wrap: break-word;
            font-size: 14px;
            font-weight: 500;
        }

        .user-message .message-content {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .bot-message .message-content {
            background: rgba(30, 35, 55, 0.9);
            color: #e0e4f0;
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-bottom-left-radius: 4px;
            backdrop-filter: blur(10px);
        }

        .chat-input-container {
            padding: 20px 24px;
            background: rgba(15, 18, 28, 0.8);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: center;
            background: rgba(25, 30, 45, 0.8);
            border-radius: 60px;
            padding: 6px 6px 6px 20px;
            border: 1px solid rgba(102, 126, 234, 0.3);
            transition: all 0.3s;
        }

        .input-wrapper:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }

        .chat-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            font-size: 14px;
            color: white;
            font-family: 'Inter', sans-serif;
        }

        .chat-input::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }

        .send-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .send-button:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .typing-indicator {
            padding: 12px 20px;
            background: rgba(30, 35, 55, 0.9);
            border-radius: 18px;
            border: 1px solid rgba(102, 126, 234, 0.3);
            width: fit-content;
            backdrop-filter: blur(10px);
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dots span {
            width: 8px;
            height: 8px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30% { transform: translateY(-10px); opacity: 1; }
        }

        .suggestions {
            padding: 16px 24px;
            background: rgba(15, 18, 28, 0.6);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .suggestion-chip {
            background: rgba(30, 35, 55, 0.8);
            border: 1px solid rgba(102, 126, 234, 0.3);
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            color: #b0b5d0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .suggestion-chip i {
            font-size: 12px;
        }

        .suggestion-chip:hover {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            transform: translateY(-2px);
        }

        @media (max-width: 640px) {
            .message-content {
                max-width: 85%;
            }

            .chat-header h1 {
                font-size: 22px;
            }

            .avatar {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="chat-wrapper">
        <div class="chat-header">
            <h1>
                <i class="fas fa-brain"></i>
                GameBrain AI
                <i class="fas fa-gamepad"></i>
            </h1>
            <p>How can I help?</p>
            <div class="status-badge">
                <i class="fas fa-circle" style="font-size: 8px; margin-right: 6px;"></i>
                Online • Ready to assist
            </div>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="avatar">
                    <i class="fas fa-robot" style="font-size: 18px; color: white;"></i>
                </div>
                <div class="message-content">
                    <i class="fas fa-sparkle" style="margin-right: 8px;"></i>
                    Hey! I'm GameBrain AI, your intelligent gaming assistant. Ask me anything about Minecraft, Fortnite, League of Legends, and more!
                </div>
            </div>
        </div>

        <div class="suggestions">
            <div class="suggestion-chip" onclick="sendSuggestion('What are the latest Fortnite updates?')">
                <i class="fas fa-fire"></i> Latest Fortnite updates
            </div>
            <div class="suggestion-chip" onclick="sendSuggestion('How to find diamonds in Minecraft 1.21?')">
                <i class="fas fa-gem"></i> Minecraft diamonds
            </div>
            <div class="suggestion-chip" onclick="sendSuggestion('Best League of Legends champions for beginners')">
                <i class="fas fa-trophy"></i> LoL beginners
            </div>
            <div class="suggestion-chip" onclick="sendSuggestion('Valorant aim training tips')">
                <i class="fas fa-crosshairs"></i> Valorant tips
            </div>
        </div>

        <div class="chat-input-container">
            <div class="input-wrapper">
                <input type="text" id="userInput" class="chat-input" placeholder="Ask me anything about gaming..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()" class="send-button">
                    Send <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerHTML = isUser ? '<i class="fas fa-user" style="font-size: 16px;"></i>' : '<i class="fas fa-robot" style="font-size: 16px;"></i>';

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;

            if (isUser) {
                messageDiv.appendChild(contentDiv);
                messageDiv.appendChild(avatar);
            } else {
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(contentDiv);
            }

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.id = 'typingIndicator';

            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerHTML = '<i class="fas fa-robot" style="font-size: 16px;"></i>';

            const contentDiv = document.createElement('div');
            contentDiv.className = 'typing-indicator';
            contentDiv.innerHTML = `
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <div style="margin-left: 8px; font-size: 12px;">GameBrain is thinking...</div>
            `;
            contentDiv.style.display = 'flex';
            contentDiv.style.alignItems = 'center';
            contentDiv.style.gap = '8px';

            typingDiv.appendChild(avatar);
            typingDiv.appendChild(contentDiv);
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTyping() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            userInput.value = '';
            userInput.disabled = true;
            showTyping();

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });

                const data = await response.json();
                hideTyping();
                userInput.disabled = false;
                userInput.focus();

                if (data.success) {
                    addMessage(data.response, false);
                } else {
                    addMessage('❌ Error: ' + data.error, false);
                }
            } catch (error) {
                hideTyping();
                userInput.disabled = false;
                addMessage('❌ Network error. Please check your connection.', false);
            }
        }

        function sendSuggestion(text) {
            userInput.value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
        }

        userInput.focus();
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        print(f"📝 Question: {user_message}")

        answer = tavily_client.qna_search(
            query=f"gaming question: {user_message}",
            search_depth="advanced",
            topic="general"
        )

        print(f"✅ Response sent")
        return jsonify({'success': True, 'response': answer})

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("🚀 GameBrain AI with Beautiful UI is starting!")
    print("📍 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)