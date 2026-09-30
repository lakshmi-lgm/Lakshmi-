document.getElementById('pdfUpload').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const statusText = document.getElementById('fileStatus');
    statusText.innerText = `Uploading ${file.name}...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            statusText.innerText = `Active: ${file.name} (${data.chunks_processed} chunks)`;
            statusText.style.color = '#34d399';
        } else {
            statusText.innerText = `Error: ${data.detail}`;
            statusText.style.color = '#f87171';
        }
    } catch (err) {
        statusText.innerText = 'Upload failed. Check server console.';
        statusText.style.color = '#f87171';
    }
});

async function sendMessage() {
    const input = document.getElementById('userInput');
    const question = input.value.trim();
    if (!question) return;

    appendMessage('user', question);
    input.value = '';

    const aiMessageDiv = appendMessage('ai', 'Thinking...');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        const data = await response.json();
        if (response.ok) {
            aiMessageDiv.innerText = data.response;
        } else {
            aiMessageDiv.innerText = `Error: ${data.detail}`;
        }
    } catch (err) {
        aiMessageDiv.innerText = 'Failed to fetch response from server.';
    }
}

async function generateTool(toolType) {
    const outputCard = document.getElementById('toolOutputContainer');
    const title = document.getElementById('toolTitle');
    const content = document.getElementById('toolContent');

    outputCard.classList.remove('hidden');
    title.innerText = `Generating ${toolType.toUpperCase()}...`;
    content.innerText = 'Analyzing document and building response...';

    const formData = new FormData();
    formData.append('tool_type', toolType);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            title.innerText = `Generated ${toolType.toUpperCase()}`;
            content.innerText = data.content;
        } else {
            title.innerText = 'Error';
            content.innerText = data.detail;
        }
    } catch (err) {
        title.innerText = 'Error';
        content.innerText = 'Failed to generate study material.';
    }
}

function closeToolOutput() {
    document.getElementById('toolOutputContainer').classList.add('hidden');
}

function appendMessage(sender, text) {
    const chatContainer = document.getElementById('chatContainer');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
    msgDiv.innerText = text;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return msgDiv;
}