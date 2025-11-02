// Chat Application JavaScript

class ChatApp {
    constructor() {
        this.sessionId = 'default';
        this.mode = 'agent';
        this.messageCount = 0;
        this.isStreaming = false;
        
        this.initElements();
        this.attachEventListeners();
        this.checkHealth();
    }
    
    initElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.chatForm = document.getElementById('chat-form');
        this.sendBtn = document.getElementById('send-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.infoBtn = document.getElementById('info-btn');
        this.infoPanel = document.getElementById('info-panel');
        this.modeSelect = document.getElementById('mode-select');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.currentModeDisplay = document.getElementById('current-mode');
        this.sessionIdDisplay = document.getElementById('session-id');
        this.messageCountDisplay = document.getElementById('message-count');
        this.connectionStatus = document.getElementById('connection-status');
        
        // MCP Management elements
        this.mcpManageBtn = document.getElementById('mcp-manage-btn');
        this.mcpPanel = document.getElementById('mcp-panel');
        this.closeMcpBtn = document.getElementById('close-mcp-btn');
        this.addMcpForm = document.getElementById('add-mcp-form');
        this.mcpServersList = document.getElementById('mcp-servers-list');
        this.mcpCount = document.getElementById('mcp-count');
    }
    
    attachEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.clearBtn.addEventListener('click', () => this.clearChat());
        this.infoBtn.addEventListener('click', () => this.toggleInfo());
        this.modeSelect.addEventListener('change', (e) => this.changeMode(e.target.value));
        
        // MCP Management listeners
        this.mcpManageBtn.addEventListener('click', () => this.openMcpPanel());
        this.closeMcpBtn.addEventListener('click', () => this.closeMcpPanel());
        this.addMcpForm.addEventListener('submit', (e) => this.handleAddMcpServer(e));
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('Connected', true);
            }
        } catch (error) {
            this.updateStatus('Disconnected', false);
            console.error('Health check failed:', error);
        }
    }
    
    updateStatus(text, isConnected) {
        this.connectionStatus.textContent = `● ${text}`;
        this.connectionStatus.className = isConnected 
            ? 'status-value status-connected' 
            : 'status-value status-disconnected';
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isStreaming) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageCount++;
        this.updateMessageCount();
        
        // Show typing indicator
        this.showTyping(true);
        this.setInputState(false);
        
        // Send message with streaming
        await this.sendMessageStreaming(message);
        
        // Hide typing indicator
        this.showTyping(false);
        this.setInputState(true);
    }
    
    async sendMessageStreaming(message) {
        this.isStreaming = true;
        
        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    mode: this.mode
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            let assistantMessage = this.addMessage('', 'assistant', true);
            let fullResponse = '';
            let toolsUsed = [];
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                this.updateMessage(assistantMessage, '❌ Error: ' + data.error);
                                break;
                            }
                            
                            if (data.tool) {
                                toolsUsed.push(data.tool);
                            }
                            
                            if (data.chunk) {
                                fullResponse += data.chunk;
                                this.updateMessage(assistantMessage, fullResponse, toolsUsed);
                            }
                            
                            if (data.done) {
                                if (data.tools_used) {
                                    toolsUsed = data.tools_used;
                                    this.updateMessage(assistantMessage, fullResponse, toolsUsed);
                                }
                                this.messageCount++;
                                this.updateMessageCount();
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('❌ Error: Failed to send message. Please try again.', 'assistant');
        } finally {
            this.isStreaming = false;
        }
    }
    
    addMessage(content, role, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (role === 'user') {
            messageContent.innerHTML = `<strong>You:</strong><p>${this.escapeHtml(content)}</p>`;
        } else {
            messageContent.innerHTML = `<strong>AI Assistant:</strong><p>${this.formatMessage(content)}</p>`;
        }
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    updateMessage(messageElement, content, toolsUsed = []) {
        const messageContent = messageElement.querySelector('.message-content');
        let html = `<strong>AI Assistant:</strong>`;
        
        // Add tools used badges
        if (toolsUsed.length > 0) {
            html += '<div>';
            toolsUsed.forEach(tool => {
                html += `<span class="tool-info">🔧 ${tool}</span>`;
            });
            html += '</div>';
        }
        
        html += `<p>${this.formatMessage(content)}</p>`;
        messageContent.innerHTML = html;
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert markdown-style formatting
        text = this.escapeHtml(text);
        
        // Bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Code blocks
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Line breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showTyping(show) {
        if (show) {
            this.typingIndicator.classList.remove('hidden');
        } else {
            this.typingIndicator.classList.add('hidden');
        }
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
        if (enabled) {
            this.messageInput.focus();
        }
    }
    
    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }
        
        try {
            await fetch(`/api/session/${this.sessionId}`, {
                method: 'DELETE'
            });
            
            // Clear messages except welcome message
            const messages = this.chatMessages.querySelectorAll('.message');
            messages.forEach((msg, index) => {
                if (index > 0) {
                    msg.remove();
                }
            });
            
            this.messageCount = 0;
            this.updateMessageCount();
            
        } catch (error) {
            console.error('Error clearing chat:', error);
            alert('Failed to clear chat. Please try again.');
        }
    }
    
    toggleInfo() {
        this.infoPanel.classList.toggle('hidden');
    }
    
    changeMode(newMode) {
        this.mode = newMode;
        this.currentModeDisplay.textContent = newMode === 'agent' ? 'Agent' : 'RAG';
        
        // Add a system message
        const modeText = newMode === 'agent' 
            ? 'Switched to Agent mode (with MCP tools)' 
            : 'Switched to RAG-only mode';
        
        const systemMsg = document.createElement('div');
        systemMsg.className = 'message assistant';
        systemMsg.innerHTML = `
            <div class="message-content" style="background: #fef3c7; border-color: #fcd34d;">
                <p><strong>ℹ️ ${modeText}</strong></p>
            </div>
        `;
        this.chatMessages.appendChild(systemMsg);
        this.scrollToBottom();
    }
    
    updateMessageCount() {
        this.messageCountDisplay.textContent = this.messageCount;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    // MCP Server Management Methods
    async openMcpPanel() {
        this.mcpPanel.classList.remove('hidden');
        this.infoPanel.classList.add('hidden');
        await this.loadMcpServers();
    }
    
    closeMcpPanel() {
        this.mcpPanel.classList.add('hidden');
    }
    
    async loadMcpServers() {
        try {
            this.mcpServersList.innerHTML = '<div class="mcp-loading">Loading servers...</div>';
            
            const response = await fetch('/api/mcp-servers');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderMcpServers(data.servers);
                this.mcpCount.textContent = data.count;
            }
        } catch (error) {
            console.error('Error loading MCP servers:', error);
            this.mcpServersList.innerHTML = '<div class="mcp-empty">❌ Failed to load servers</div>';
        }
    }
    
    renderMcpServers(servers) {
        if (servers.length === 0) {
            this.mcpServersList.innerHTML = '<div class="mcp-empty">📭 No MCP servers configured yet</div>';
            return;
        }
        
        this.mcpServersList.innerHTML = servers.map(server => `
            <div class="mcp-server-item" data-name="${this.escapeHtml(server.name)}">
                <div class="mcp-server-info">
                    <div class="mcp-server-name">🔧 ${this.escapeHtml(server.name)}</div>
                    <div class="mcp-server-url">${this.escapeHtml(server.url)}</div>
                </div>
                <div class="mcp-server-actions">
                    <button class="btn-delete" onclick="chatApp.deleteMcpServer('${this.escapeHtml(server.name)}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    async handleAddMcpServer(e) {
        e.preventDefault();
        
        const name = document.getElementById('mcp-name').value.trim();
        const url = document.getElementById('mcp-url').value.trim();
        
        if (!name || !url) {
            alert('Please fill in all fields');
            return;
        }
        
        try {
            const response = await fetch('/api/mcp-servers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, url })
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Clear form
                this.addMcpForm.reset();
                
                // Reload servers list
                await this.loadMcpServers();
                
                // Show success message in chat
                const successMsg = document.createElement('div');
                successMsg.className = 'message assistant';
                successMsg.innerHTML = `
                    <div class="message-content" style="background: #d1fae5; border-color: #10b981;">
                        <p><strong>✅ MCP Server Added!</strong></p>
                        <p>Server "${name}" has been added successfully. The agent can now use its tools!</p>
                    </div>
                `;
                this.chatMessages.appendChild(successMsg);
                this.scrollToBottom();
            } else {
                alert('Error: ' + (data.detail || data.message || 'Failed to add server'));
            }
        } catch (error) {
            console.error('Error adding MCP server:', error);
            alert('Failed to add MCP server. Please try again.');
        }
    }
    
    async deleteMcpServer(serverName) {
        if (!confirm(`Are you sure you want to delete the MCP server "${serverName}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/mcp-servers/${encodeURIComponent(serverName)}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Reload servers list
                await this.loadMcpServers();
                
                // Show success message in chat
                const successMsg = document.createElement('div');
                successMsg.className = 'message assistant';
                successMsg.innerHTML = `
                    <div class="message-content" style="background: #fee2e2; border-color: #ef4444;">
                        <p><strong>🗑️ MCP Server Deleted</strong></p>
                        <p>Server "${serverName}" has been removed.</p>
                    </div>
                `;
                this.chatMessages.appendChild(successMsg);
                this.scrollToBottom();
            } else {
                alert('Error: ' + (data.detail || data.message || 'Failed to delete server'));
            }
        } catch (error) {
            console.error('Error deleting MCP server:', error);
            alert('Failed to delete MCP server. Please try again.');
        }
    }
}

// Global reference for inline event handlers
let chatApp;

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    chatApp = new ChatApp();
});

