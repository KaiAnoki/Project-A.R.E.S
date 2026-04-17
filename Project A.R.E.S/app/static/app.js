const chat = document.getElementById('chat');
const messageBox = document.getElementById('message');
const sendButton = document.getElementById('send');

function appendMessage(role, text, meta='') {
  const wrapper = document.createElement('div');
  wrapper.className = 'msg';

  const main = document.createElement('div');
  main.className = role;
  main.textContent = `${role === 'user' ? 'You' : 'ARES'}: ${text}`;
  wrapper.appendChild(main);

  if (meta) {
    const metaDiv = document.createElement('div');
    metaDiv.className = 'meta';
    metaDiv.textContent = meta;
    wrapper.appendChild(metaDiv);
  }

  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const message = messageBox.value.trim();
  if (!message) return;
  appendMessage('user', message);
  messageBox.value = '';

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await response.json();
    const metaBits = [];
    if (data.mode) metaBits.push(`mode=${data.mode}`);
    if (data.model) metaBits.push(`model=${data.model}`);
    if (data.latency_ms !== undefined) metaBits.push(`latency=${Math.round(data.latency_ms)}ms`);
    appendMessage('assistant', data.reply || 'No reply received.', metaBits.join(' | '));
  } catch (error) {
    appendMessage('assistant', `Request failed: ${error}`);
  }
}

sendButton.addEventListener('click', sendMessage);
messageBox.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});
