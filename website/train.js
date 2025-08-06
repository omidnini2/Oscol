const audioInput = document.getElementById("audio-sample");
const textInput = document.getElementById("sample-text");
const uploadBtn = document.getElementById("upload-btn");
const statusEl = document.getElementById("upload-status");
const recordBtn = document.getElementById("record-btn");

let mediaRecorder;
let chunks = [];

uploadBtn.addEventListener("click", async () => {
  const audio = audioInput.files[0];
  const text = textInput.value.trim();
  if (!audio || !text) {
    alert("لطفاً فایل صوتی و متن را وارد کنید");
    return;
  }
  uploadBtn.disabled = true;
  statusEl.textContent = "در حال آپلود…";
  const formData = new FormData();
  formData.append("audio", audio, "sample.wav");
  formData.append("text", text);
  formData.append("lang", "fa");

  try {
    const res = await fetch("http://localhost:5000/dataset", { method: "POST", body: formData });
    if (!res.ok) throw new Error("خطا در سرور");
    statusEl.textContent = "نمونه با موفقیت ذخیره شد!";
    textInput.value = "";
    audioInput.value = "";
  } catch (e) {
    statusEl.textContent = "خطا: " + e.message;
  } finally {
    uploadBtn.disabled = false;
  }
});

recordBtn?.addEventListener("click", async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    recordBtn.textContent = "🎤 ضبط صدا";
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];
  mediaRecorder.ondataavailable = e => chunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(chunks, { type: "audio/webm" });
    // Auto-transcribe
    const formData = new FormData();
    formData.append("audio", blob, "sample.webm");
    statusEl.textContent = "در حال تشخیص متن…";
    const res = await fetch("http://localhost:5000/transcribe", { method: "POST", body: formData });
    if (res.ok) {
      const json = await res.json();
      textInput.value = json.transcript;
      statusEl.textContent = "متن تشخیص داده شد؛ اکنون می‌توانید آپلود کنید";
    } else {
      statusEl.textContent = "خطا در تشخیص متن";
    }
  };

  mediaRecorder.start();
  recordBtn.textContent = "⏹️ توقف";
});