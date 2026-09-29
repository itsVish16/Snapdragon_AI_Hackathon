let socket = null;
let audioContext = null;
let mediaStream = null;
let scriptProcessor = null;
let isRecording = false;

let polishEnabled = false;
let currentStyle = "clean_verbatim";
let totalJoules = 0.0;

const micBtn = document.getElementById("micBtn");
const micHint = document.getElementById("micHint");
const streamStatus = document.getElementById("streamStatus");
const providerBadge = document.getElementById("providerBadge");
const outputDisplay = document.getElementById("outputDisplay");
const polishToggle = document.getElementById("polishToggle");
const stylePills = document.querySelectorAll(".pill");
const copyBtn = document.getElementById("copyBtn");
const clearBtn = document.getElementById("clearBtn");
const testAudioBtn = document.getElementById("testAudioBtn");
const injectBtn = document.getElementById("injectBtn");
const canvas = document.getElementById("waveformCanvas");
const canvasCtx = canvas.getContext("2d");

const telemetryLatency = document.getElementById("telemetryLatency");
const telemetryRTF = document.getElementById("telemetryRTF");
const telemetryJoules = document.getElementById("telemetryJoules");

async function checkStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    providerBadge.textContent = data.provider || "Connected";
    if (data.is_npu) {
      providerBadge.style.color = "#10B981";
    }
  } catch (err) {
    providerBadge.textContent = "Offline";
  }
}

function initWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/dictate`;
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    streamStatus.textContent = "READY";
    streamStatus.style.color = "#10B981";
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.final_text) {
        outputDisplay.textContent = data.final_text;
      }
      if (data.latency_ms !== undefined) {
        telemetryLatency.textContent = data.latency_ms;
      }
      if (data.rtf !== undefined) {
        telemetryRTF.textContent = data.rtf;
      }
      if (data.joules_saved !== undefined) {
        totalJoules += data.joules_saved;
        telemetryJoules.textContent = totalJoules.toFixed(2);
      }
      if (data.provider) {
        providerBadge.textContent = data.provider;
      }
    } catch (e) {}
  };

  socket.onclose = () => {
    streamStatus.textContent = "DISCONNECTED";
    setTimeout(initWebSocket, 2000);
  };
}

async function startRecording() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    const source = audioContext.createMediaStreamSource(mediaStream);

    scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
    source.connect(scriptProcessor);
    scriptProcessor.connect(audioContext.destination);

    scriptProcessor.onaudioprocess = (e) => {
      if (!isRecording) return;
      const inputData = e.inputBuffer.getChannelData(0);
      drawWaveform(inputData);

      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(inputData.buffer);
      }
    };

    isRecording = true;
    micBtn.classList.add("recording");
    micHint.textContent = "Listening... Speak naturally";
    streamStatus.textContent = "STREAMING";
    streamStatus.style.color = "#E11D48";
  } catch (err) {
    micHint.textContent = "Microphone access denied or not available";
  }
}

function stopRecording() {
  isRecording = false;
  micBtn.classList.remove("recording");
  micHint.textContent = "Click to Start Ambient Dictation";
  streamStatus.textContent = "IDLE";
  streamStatus.style.color = "#94A3B8";

  if (scriptProcessor) scriptProcessor.disconnect();
  if (audioContext) audioContext.close();
  if (mediaStream) mediaStream.getTracks().forEach((t) => t.stop());

  clearWaveform();
}

function drawWaveform(samples) {
  canvasCtx.fillStyle = "#1A243D";
  canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

  canvasCtx.lineWidth = 2;
  canvasCtx.strokeStyle = "#FF6F00";
  canvasCtx.beginPath();

  const sliceWidth = canvas.width / samples.length;
  let x = 0;

  for (let i = 0; i < samples.length; i += 8) {
    const v = samples[i] * 40;
    const y = canvas.height / 2 + v;

    if (i === 0) canvasCtx.moveTo(x, y);
    else canvasCtx.lineTo(x, y);

    x += sliceWidth * 8;
  }

  canvasCtx.lineTo(canvas.width, canvas.height / 2);
  canvasCtx.stroke();
}

function clearWaveform() {
  canvasCtx.fillStyle = "#1A243D";
  canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
}

micBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  else startRecording();
});

polishToggle.addEventListener("change", (e) => {
  polishEnabled = e.target.checked;
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        action: "update_settings",
        polish_enabled: polishEnabled,
        style: currentStyle,
      })
    );
  }
  const currentText = outputDisplay.textContent.trim();
  if (currentText) {
    refineCurrentText(currentText);
  }
});

stylePills.forEach((pill) => {
  pill.addEventListener("click", () => {
    stylePills.forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    currentStyle = pill.getAttribute("data-style");

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          action: "update_settings",
          polish_enabled: polishEnabled,
          style: currentStyle,
        })
      );
    }
    const currentText = outputDisplay.textContent.trim();
    if (currentText) {
      refineCurrentText(currentText);
    }
  });
});

async function refineCurrentText(text) {
  try {
    const res = await fetch("/api/refine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, style: currentStyle }),
    });
    const data = await res.json();
    if (data.refined) {
      outputDisplay.textContent = data.refined;
    }
  } catch (e) {}
}

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(outputDisplay.textContent);
  copyBtn.textContent = "Copied!";
  setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
});

clearBtn.addEventListener("click", () => {
  outputDisplay.textContent = "";
});

injectBtn.addEventListener("click", async () => {
  const text = outputDisplay.textContent.trim();
  if (!text) return;
  await fetch("/api/inject", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text }),
  });
  injectBtn.textContent = "Injected!";
  setTimeout(() => (injectBtn.textContent = "Type Into Active App"), 1500);
});

testAudioBtn.addEventListener("click", () => {
  const sampleSentences = [
    "Umm hey team, so basically I think we should finalize the Snapdragon AI submission by tomorrow noon, like definitely.",
    "Uh please note that the HP OmniBook Ultra delivers 45 TOPS on the Hexagon NPU, which is about twenty dollars cheaper to run than cloud APIs.",
    "Action items for today: first benchmark whisper latency, second verify QNN execution provider, and third record demo video.",
  ];
  const chosen = sampleSentences[Math.floor(Math.random() * sampleSentences.length)];
  outputDisplay.textContent = chosen;

  telemetryLatency.textContent = "64.2";
  telemetryRTF.textContent = "0.068";
  totalJoules += 1.25;
  telemetryJoules.textContent = totalJoules.toFixed(2);

  if (polishEnabled) {
    refineCurrentText(chosen);
  }
});

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");

dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  dropZone.textContent = `Transcribing ${file.name}...`;
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/transcribe-file", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    outputDisplay.textContent = data.text || "No speech detected.";
    dropZone.innerHTML = `<p>Transcribed <strong>${file.name}</strong> successfully!</p>`;
  } catch (err) {
    dropZone.textContent = "Upload failed. Try again.";
  }
});

checkStatus();
initWebSocket();
clearWaveform();
