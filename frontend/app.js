const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');
const playback = document.getElementById('playback');
const downloadLink = document.getElementById('downloadLink');
const conversationDiv = document.getElementById('conversation');
const aiPlayback = document.getElementById('aiPlayback');
const backendOrigin = window.location.protocol === 'file:'
  ? 'http://localhost:8000'
  : window.location.origin;
const uploadUrl = window.location.protocol !== 'file:'
  ? '/api/upload'
  : backendOrigin + '/api/upload';

let mediaRecorder = null;
let audioChunks = [];
let recordingUrl = null;
const conversation = [];

function setStatus(msg) {
  status.textContent = 'Status: ' + msg;
}

function addMessage(role, text) {
  if (!text) return;

  conversation.push({ role, text });
  renderConversation();
}

function renderConversation() {
  conversationDiv.innerHTML = '';

  conversation.forEach((msg) => {
    const bubble = document.createElement('div');
    bubble.className = 'message ' + (msg.role === 'user' ? 'user-message' : 'ai-message');

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = msg.role === 'user' ? 'You' : 'AI';

    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = msg.text;

    bubble.append(label, text);
    conversationDiv.appendChild(bubble);
  });

  conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

startBtn.addEventListener('click', async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setStatus('Microphone recording is not supported in this browser.');
      return;
    }

    if (!window.MediaRecorder) {
      setStatus('MediaRecorder is not supported in this browser.');
      return;
    }

    setStatus('Requesting microphone permission…');

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const hasAudioTrack = stream.getAudioTracks().length > 0;

    if (!hasAudioTrack) {
      setStatus('No microphone audio track found.');
      stream.getTracks().forEach(t => t.stop());
      return;
    }

    audioChunks = [];

    if (recordingUrl) {
      URL.revokeObjectURL(recordingUrl);
      recordingUrl = null;
    }

    playback.removeAttribute('src');
    playback.load();
    downloadLink.removeAttribute('href');
    downloadLink.hidden = true;
    aiPlayback.removeAttribute('src');
    aiPlayback.load();

    const mimeType = MediaRecorder.isTypeSupported('audio/webm')
      ? 'audio/webm'
      : '';

    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstart = () => {
      setStatus('Recording…');
      startBtn.disabled = true;
      stopBtn.disabled = false;
    };

    mediaRecorder.onstop = async () => {
      startBtn.disabled = false;
      stopBtn.disabled = true;

      stream.getTracks().forEach(t => t.stop());

      const blob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });

      if (blob.size === 0) {
        setStatus('Recording is empty. Try again and speak after starting.');
        return;
      }

      recordingUrl = URL.createObjectURL(blob);

      playback.src = recordingUrl;
      downloadLink.href = recordingUrl;
      downloadLink.hidden = false;

      setStatus('Processing audio…');
      await sendToBackend(blob);
    };

    mediaRecorder.start();

  } catch (err) {
    if (err.name === 'NotAllowedError') {
      setStatus('Microphone permission denied.');
    } else {
      setStatus('Error: ' + err.message);
    }
    console.error(err);
  }
});

stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
});

async function sendToBackend(blob) {
  try {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');

    setStatus('Uploading and transcribing…');

    const response = await fetch(uploadUrl, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      addMessage('user', result.transcript);
      addMessage('ai', result.reply);

      if (!result.audio_url) {
        setStatus('Done. AI reply text received, but no audio URL returned.');
        return;
      }

      const audioUrl = new URL(result.audio_url, backendOrigin).href;
      aiPlayback.src = audioUrl;

      try {
        await aiPlayback.play();
        setStatus('Done. AI reply is playing.');
      } catch (playErr) {
        setStatus('Done. Tap play to hear the AI reply.');
        console.warn('Autoplay blocked:', playErr.message);
      }
    } else {
      const error = await response.json().catch(() => null);
      const detail = error?.detail;

      if (response.status === 429 && detail?.transcript) {
        addMessage('user', detail.transcript);
        setStatus('Gemini quota reached. Try again later.');
      } else {
        setStatus('Recording ready. Upload failed: ' + (detail?.message || detail || response.status));
      }
    }
  } catch (err) {
    setStatus('Recording ready. Backend not reachable.');
    console.warn('Backend not available:', err.message);
  }
}
