from flask import Flask, request, render_template_string
from markupsafe import Markup
import base64
import ssl

"""
pip install gunicorn flask Flask-Cors
sudo apt install certbot
sudo certbot certonly --standalone --preferred-challenges http -d {{yourdomain.com}}
sudo crontab -e
0 0 * * * certbot renew --quiet && systemctl reload gunicorn
gunicorn --bind 0.0.0.0:443 --certfile=/etc/letsencrypt/live/{{yourdomain.com}}/fullchain.pem --keyfile=/etc/letsencrypt/live/{{yourdomain.com}}/privkey.pem --workers 4 --daemon jsonpeek-webserver:app
"""

app = Flask(__name__)

# Define the HTML template
template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSONPeek</title>
    <style>
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f7fa;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    height: 100vh;
    overflow: hidden;
}

.container {
    background-color: #fff;
    padding: 30px 40px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    width: 90%;
    max-width: 1200px;
    text-align: center;
    overflow: auto;
    max-height: 90vh;
}

table {
    margin-top: 30px;
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}

th, td {
    padding: 15px;
    text-align: center;
    font-size: 1.1rem;
    border: 1px solid #e0e0e0;
}

th {
    background-color: #f0f0f0;
    font-weight: bold;
}

td {
    background-color: #fafafa;
    word-wrap: break-word;
    overflow: hidden;
    text-overflow: ellipsis;
    word-break: break-word;
}

th:nth-child(1), td:nth-child(1) { 
    width: 100px;
}

th:nth-child(2), td:nth-child(2) { 
    width: 100%;
}

th:nth-child(3), td:nth-child(3) { 
    width: 100px;
}

.status {
    font-size: 2rem;
    font-weight: bold;
}

.success {
    color: #28a745;
}

.failure {
    color: #dc3545;
}

.footer {
    margin-top: 40px;
    font-size: 1rem;
    color: #666;
}

.footer a {
    color: #007bff;
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

.copy-btn {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 50px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s ease, transform 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.copy-btn:hover {
    background-color: #0056b3;
    transform: scale(1.05);
}

.copy-btn:active {
    transform: scale(1);
}

/* JSONP parameter styling */
.jsonp-parameter {
    color: red;
    font-weight: bold;
}

/* Tooltip style */
.tooltip {
    position: absolute;
    top: -5px;
    left: 100%;
    background-color: #333;
    color: white;
    padding: 5px;
    font-size: 0.85rem;
    border-radius: 5px;
    opacity: 0;
    transition: opacity 0.3s;
}

.copy-container:hover .tooltip {
    opacity: 1;
}

p {
    color: #444;
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 20px;
    max-width: 70%;
    margin-left: auto;
    margin-right: auto;
}

    </style>
  </head>
  <body>
    <div class="container">
      <h1>JSONPeek</h1>
      <p><strong>JSONPeek</strong> is a Firefox extension and a web service designed to test potential <strong>JSONP</strong> endpoints by injecting payloads into the common callback parameters of a given URL. This webserver accepts a <b>url</b> GET parameter that includes a single base64 encoded suspected JSONP endpoint. Common JSONP parameters of the suspected endpoint are injected with proof of concept payloads (highlighted in red below) in an attempt to trigger the <b>alert()</b> function. This webpage hooks the alert function and records the success or failure of each payload attempt in the table below.</p>
      <p>To try it out, simply click <a href="https://jsonpeek.com?url=aHR0cHM6Ly93d3cudzNzY2hvb2xzLmNvbS9qcy9kZW1vX2pzb25wMi5waHA/Y2FsbGJhY2s9anNvbnBlZWs=">HERE</a> to test a sample URL.</p>
      <p>If you discover a valid JSONP endpoint, please report it by creating a quick <a href="https://github.com/ACK-J/CSP-B-Gone/issues">GitHub issue</a>!</p>
      <a href="https://addons.mozilla.org/en-US/firefox/addon/jsonpeek/"><img src="https://blog.mozilla.org/addons/files/2020/04/get-the-addon-fx-apr-2020.svg" alt="for Firefox" height="60px" style="display: block;margin-left: auto;margin-right: auto;"></a>
      <table>
        <tr>
          <th>Copy</th>
          <th>JSONP Callback URL</th>
          <th>Status</th>
        </tr>
        <tbody id="table-body"></tbody>
      </table>
      <div class="footer">
        <p><a href="https://github.com/ACK-J/JSONPeek">GitHub Repo</a></p>
      </div>
    </div>

    <script>
      const originalAlert = window.alert;

      const replacementValues = [
        "alert", "alert(1)", '-alert`1`-', 'alert(1)//', 'alert();', 'alert(1)-'
      ];

      const jsonpParams = [
        'callback', 'jsonpCallback', 'jsonp', 'callback_func', 'func', 
        'handler', 'jsonp_handler', 'cbfn', 'onload', 'j', 'oncomplete'
      ];

      function generateVariations(url) {
        const variations = [];
        const urlObj = new URL(url);
        const params = new URLSearchParams(urlObj.search);

        jsonpParams.forEach(param => {
          if (params.has(param)) {
            replacementValues.forEach(replacement => {
              const modifiedParams = new URLSearchParams(params);
              modifiedParams.set(param, replacement);
              const modifiedUrl = `${urlObj.origin}${urlObj.pathname}?${modifiedParams.toString()}`;
              variations.push(modifiedUrl);
            });
          }
        });

        return variations;
      }

      function hookAlert(row) {
        window.alert = function(...args) {
          row.querySelector('.status').innerHTML = '<span class="success">✔</span>';
          originalAlert.apply(window, args);
        };
      }

      function highlightJsonpParams(url) {
        jsonpParams.forEach(param => {
          const regex = new RegExp(`(${param}=)([^&]*)`, 'g');
          url = url.replace(regex, (match, p1, p2) => {
            return `${p1}<span class="jsonp-parameter">${p2}</span>`;
          });
        });
        return url;
      }

      async function processAndDisplayVariations(url) {
        const variations = generateVariations(url);
        const tableBody = document.querySelector('#table-body');

        for (let modifiedUrl of variations) {
          const row = document.createElement('tr');
          const highlightedUrl = highlightJsonpParams(modifiedUrl); // Highlight JSONP params
          row.innerHTML = 
            `<td><button class="copy-btn" onclick="copyToClipboard('${modifiedUrl}')">Copy</button></td>
            <td>${highlightedUrl}</td>
            <td class="status"><span class="failure">✘</span></td>`;
          tableBody.appendChild(row);

          hookAlert(row);
          await injectScript(modifiedUrl, row);
        }
      }

      function injectScript(url, row) {
        return new Promise((resolve) => {
          const script = document.createElement('script');
          script.src = url;
          script.onload = () => {
            resolve();
          };
          script.onerror = () => {
            resolve();
          };
          document.body.appendChild(script);
        });
      }

      function copyToClipboard(url) {
        navigator.clipboard.writeText(url);
      }

      const checkURL = '{{ decoded_url }}';
      processAndDisplayVariations(checkURL);
    </script>

  </body>
</html>
"""


@app.route('/')
def index():
    base64_value = request.args.get('url')

    if not base64_value:
        return render_template_string(template, decoded_url="")

    try:
        decoded_value = base64.b64decode(base64_value).decode('utf-8')
    except Exception as e:
        return render_template_string(template, decoded_url="")

    return render_template_string(template, decoded_url=Markup(decoded_value))

if __name__ == '__main__':
    #context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    #app.run(host='0.0.0.0', port=443, ssl_context=context)
    app.run(host='0.0.0.0', port=5000)  # Default run for testing locally
