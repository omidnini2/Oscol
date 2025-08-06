const themeToggle = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");
const audioInput = document.getElementById("audio-upload");
const recordBtn = document.getElementById("record-btn");
const recordStatus = document.getElementById("record-status");
const recordingPlayback = document.getElementById("recording-playback");
const cloneBtn = document.getElementById("clone-btn");
const ttsText = document.getElementById("tts-text");
const speakBtn = document.getElementById("speak-btn");
const ttsOutput = document.getElementById("tts-output");

let mediaRecorder;
let recordedChunks = [];
let embeddingId = null;

// Theme toggle
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  setTheme(savedTheme);
});

themeToggle.addEventListener("click", () => {
  const newTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  setTheme(newTheme);
});

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
  localStorage.setItem("theme", theme);
}

// Recording logic
recordBtn.addEventListener("click", async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    recordBtn.textContent = "🎤 Record";
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  recordedChunks = [];

  mediaRecorder.ondataavailable = e => recordedChunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: "audio/webm" });
    const url = URL.createObjectURL(blob);
    recordingPlayback.src = url;
    recordingPlayback.hidden = false;
    cloneBtn.disabled = false;
  };

  mediaRecorder.start();
  recordBtn.textContent = "⏹️ Stop";
});

// Upload or record triggers clone
cloneBtn.addEventListener("click", async () => {
  let audioBlob;
  if (audioInput.files.length > 0) {
    audioBlob = audioInput.files[0];
  } else if (recordedChunks.length > 0) {
    audioBlob = new Blob(recordedChunks, { type: "audio/webm" });
  } else {
    alert("Please upload or record an audio sample first.");
    return;
  }

  const formData = new FormData();
  formData.append("audio", audioBlob, "sample.webm");

  recordStatus.textContent = "Uploading and cloning…";
  const res = await fetch("http://localhost:5000/clone", { method: "POST", body: formData });
  if (!res.ok) {
    recordStatus.textContent = "Error during clone.";
    return;
  }
  const json = await res.json();
  embeddingId = json.embedding_id;
  recordStatus.textContent = "Voice cloned!";
  speakBtn.disabled = false;
});

// Speak button
speakBtn.addEventListener("click", async () => {
  if (!embeddingId) return alert("Clone a voice first");
  const text = ttsText.value.trim();
  if (!text) return alert("Enter some text");
  speakBtn.disabled = true;
  speakBtn.textContent = "Synthesizing…";

  const res = await fetch("http://localhost:5000/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, embedding_id: embeddingId })
  });

  if (!res.ok) {
    alert("TTS failed");
    speakBtn.disabled = false;
    speakBtn.textContent = "Speak";
    return;
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  ttsOutput.src = url;
  ttsOutput.hidden = false;
  speakBtn.disabled = false;
  speakBtn.textContent = "Speak";
});

// Enable clone button when file chosen
audioInput.addEventListener("change", () => {
  if (audioInput.files.length > 0) {
    cloneBtn.disabled = false;
  }
});