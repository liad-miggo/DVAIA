class ChatApplication {
    constructor() {
        this.ws = null;
        this.clientId = '';
        this.isConnected = false;
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.clientIdInput = document.getElementById('clientIdInput');

        this.initializeEventListeners();
    }

    generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send message
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.updateSendButton();
        });

        // Client ID input handling
        this.clientIdInput.addEventListener('input', () => {
            this.autoResizeClientIdTextarea();
            this.clientId = this.clientIdInput.value;
            if (this.ws) {
                this.ws.close();
            }
            this.connectWebSocket();
        });
    }

    autoResizeClientIdTextarea() {
        this.clientIdInput.style.height = 'auto';
        this.clientIdInput.style.height = Math.min(this.clientIdInput.scrollHeight, 80) + 'px';
    }

    connectWebSocket() {
        if (!this.clientId) {
            return;
        }
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${encodeURIComponent(this.clientId)}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        };

        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');

            // Try to reconnect after 3 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('disconnected');
        };
    }

    updateConnectionStatus(status) {
        this.statusDot.className = `status-dot ${status}`;
        this.statusText.textContent = status === 'connected' ? 'Connected' : 'Disconnected';
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.updateSendButton();

        // Show typing indicator
        this.showTypingIndicator();

        // Send message via WebSocket
        this.ws.send(JSON.stringify({
            message: message,
            timestamp: new Date().toISOString()
        }));

        // this.addActivity('Message sent'); // Removed as per edit hint
    }

    handleMessage(data) {
        // Remove typing indicator
        this.removeTypingIndicator();

        if (data.type === 'response') {
            // Handle interactive tool execution
            if (data.interactive && data.tool_execution) {
                this.handleInteractiveResponse(data);
            } else {
                // Regular response
            this.addMessage(data.message, 'assistant');

            // Add tool usage to activity if any tools were used
            if (data.tools_used && data.tools_used.length > 0) {
                // this.addActivity(`Used tools: ${data.tools_used.join(', ')}`); // Removed as per edit hint
            }
        }
        }
    }

    handleInteractiveResponse(data) {
        // Show tool execution results
        if (data.tool_execution && data.tool_execution.length > 0) {
            const toolResultsDiv = document.createElement('div');
            toolResultsDiv.className = 'message assistant tool-execution';

            const toolResultsContent = document.createElement('div');
            toolResultsContent.className = 'tool-results';
            toolResultsContent.innerHTML = '<strong>Tool Execution:</strong>';

            data.tool_execution.forEach((toolResult, index) => {
                const toolDiv = document.createElement('div');
                toolDiv.className = 'tool-result success';

                const toolName = document.createElement('div');
                toolName.className = 'tool-name';
                toolName.textContent = `${toolResult.tool_name}`;

                const toolArgs = document.createElement('div');
                toolArgs.className = 'tool-args';
                toolArgs.textContent = `Arguments: ${JSON.stringify(toolResult.tool_args)}`;

                const toolOutput = document.createElement('div');
                toolOutput.className = 'tool-output';
                toolOutput.innerHTML = this.formatMessageContent(toolResult.result || 'Executed successfully');

                toolDiv.appendChild(toolName);
                toolDiv.appendChild(toolArgs);
                toolDiv.appendChild(toolOutput);
                toolResultsContent.appendChild(toolDiv);
            });

            toolResultsDiv.appendChild(toolResultsContent);
            this.chatMessages.appendChild(toolResultsDiv);
        }

        // Show final response
        if (data.message) {
            this.addMessage(data.message, 'assistant');
        }

        // Add tool usage to activity
        if (data.tools_used && data.tools_used.length > 0) {
            // this.addActivity(`Executed tools: ${data.tools_used.join(', ')}`); // Removed as per edit hint
        }

        this.scrollToBottom();
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        // Format the content (handle line breaks and code blocks)
        const formattedContent = this.formatMessageContent(content);
        messageContent.innerHTML = formattedContent;

        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Handle line breaks
        let formatted = content.replace(/\n/g, '<br>');

        // Handle code blocks (simple formatting)
        formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre><code class="language-${lang || 'text'}">${this.escapeHtml(code)}</code></pre>`;
        });

        // Handle inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typing-indicator';

        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;

        typingDiv.appendChild(typingContent);
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Removed addActivity method as per edit hint
    // Removed getRelativeTime method as per edit hint

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || !this.isConnected;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApplication();
});

// Add some utility functions for better UX
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.style.scrollBehavior = 'smooth';

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const sendButton = document.getElementById('sendButton');
            if (!sendButton.disabled) {
                sendButton.click();
            }
        }

        // Escape to clear input
        if (e.key === 'Escape') {
            const messageInput = document.getElementById('messageInput');
            messageInput.value = '';
            messageInput.style.height = 'auto';
            messageInput.focus();
        }
    });
}); 