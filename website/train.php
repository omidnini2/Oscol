<?php ?>
<!DOCTYPE html>
<html lang="fa">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>آموزش فارسی – Voice Clone</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header>
    <h1>افزودن نمونه فارسی</h1>
    <nav>
      <a href="index.php">صفحه اصلی</a>
    </nav>
  </header>

  <main>
    <section>
      <p>برای بهبود کیفیت خواندن فارسی، یک فایل صوتی (حداقل ۳ ثانیه) و متن همان جمله را بارگذاری کنید.</p>
      <input type="file" id="audio-sample" accept="audio/*" />
      <textarea id="sample-text" rows="3" placeholder="متن فارسی مربوط به فایل صوتی را اینجا بنویسید"></textarea>
      <button id="upload-btn">آپلود نمونه</button>
      <p id="upload-status"></p>
    </section>
  </main>

  <script src="train.js"></script>
</body>
</html>