const audioInput = document.getElementById("audio-sample");
const textInput = document.getElementById("sample-text");
const uploadBtn = document.getElementById("upload-btn");
const statusEl = document.getElementById("upload-status");

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