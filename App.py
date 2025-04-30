from flask import Flask, request, render_template_string
import pytesseract
from PIL import Image
import re

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>標籤擷取工具</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family:sans-serif; padding:20px; max-width:600px; margin:auto">
    <h2>📸 上傳標籤照片</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" required style="margin-bottom:10px"><br>
        <button type="submit" style="padding:10px 20px; font-size:16px">上傳並擷取</button>
    </form>
    {% if result %}
        <h3>✅ 擷取結果：</h3>
        <pre id="resultText" style="background:#f0f0f0; padding:10px">{{ result }}</pre>
        <button onclick="copyText()">📋 複製結果</button>
        <script>
            function copyText() {
                const text = document.getElementById("resultText").innerText;
                navigator.clipboard.writeText(text).then(() => alert("已複製"));
            }
        </script>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    result = None
    if request.method == 'POST':
        file = request.files['image']
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)

        nc_match = re.search(r'SERV\\.\\d+\\.\\d+', text)
        sn_match = re.search(r'(?:S/N|SN)[\\s:-]*(\\w+)', text, re.IGNORECASE)

        nc = nc_match.group(0) if nc_match else '未擷取到 12NC'
        sn = sn_match.group(1) if sn_match else '未擷取到 SN'

        result = f"12NC: {nc}\\nSN: {sn}\\n\\n原始辨識內容:\\n{text}"

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
