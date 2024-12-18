from flask import Flask, request, render_template_string
import base64
import ssl

"""
# Step 1: Generate a private key
openssl genpkey -algorithm RSA -out key.pem

# Step 2: Create a certificate signing request (CSR)
openssl req -new -key key.pem -out csr.pem

# Step 3: Create a self-signed certificate valid for 10 years (3650 days)
openssl x509 -req -days 3650 -in csr.pem -signkey key.pem -out cert.pem
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
        align-items: center;
        height: 100vh;
      }

      .container {
        background-color: #fff;
        padding: 30px 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        width: 90%;
        max-width: 1200px; /* Increased max-width for larger table */
        text-align: center;
      }

      h1 {
        font-size: 2.5rem;
        color: #333;
        margin-bottom: 20px;
      }

      table {
        margin-top: 30px;
        width: 100%;
        border-collapse: collapse;
      }

      th, td {
        padding: 15px; /* Increased padding for bigger table */
        text-align: center;
        font-size: 1.1rem; /* Increased font size */
        border: 1px solid #e0e0e0;
      }

      th {
        background-color: #f0f0f0;
        font-weight: bold;
      }

      td {
        background-color: #fafafa;
        word-wrap: break-word;
        max-width: 800px; /* Increased max-width for the decoded URL */
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .status {
        font-size: 2rem; /* Increased size for the status column */
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

      /* Modern copy button style */
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
    </style>
  </head>
  <body>
    <div class="container">
      <h1>JSONPeek</h1>
      <p>Testing your JSONP Callbacks...</p>
      <table>
        <tr>
          <th></th>
          <th>Decoded URL</th>
          <th>Status</th>
        </tr>
        <tr>
          <td class="copy-container">
            <!-- Modern Copy button with rounded edges -->
            <button class="copy-btn" onclick="copyToClipboard()">Copy</button>
            <span class="tooltip" id="tooltip">Click to copy URL</span>
          </td>
          <td id="decoded-url-cell">
            <span id="decoded-url">{{ decoded_url }}</span>
          </td>
          <td id="status-cell" class="status">
            <!-- Default status set to failure (X) -->
            <span class="failure">✘</span>
          </td>
        </tr>
      </table>
      <div class="footer">
        <p><a href="https://github.com/ACK-J/JSONPeek">GitHub Repo</a></p>
      </div>
    </div>

    <script>
      // Custom alert handler
      const originalAlert = window.alert;
      window.alert = function(...args) {
        const error = new Error();
        console.log(error.stack);
        document.getElementById('status-cell').innerHTML = '<span class="success">✔</span>';
        originalAlert.apply(window, args);
      };

      // Inject script for decoded URL
      const check_URL = '{{ decoded_url }}';
      const script = document.createElement('script');
      script.src = check_URL;
      document.body.appendChild(script);

      // Function to copy the decoded URL to clipboard
      function copyToClipboard() {
        const url = document.getElementById('decoded-url').textContent;

        // Check if the Clipboard API is available
        if (navigator.clipboard) {
          navigator.clipboard.writeText(url);
        }
      }
    </script>
  </body>
</html>

"""

@app.route('/')
def index():
    # Get the base64 encoded value from the URL parameter
    base64_value = request.args.get('url')

    # Decode the base64 value
    if not base64_value:
        return render_template_string(template, decoded_url="Error: Missing 'url' parameter")

    try:
        decoded_value = base64.b64decode(base64_value).decode('utf-8')
    except Exception as e:
        return render_template_string(template, decoded_url=f"Error decoding base64 value: {str(e)}")

    # Return the HTML template with the decoded URL
    return render_template_string(template, decoded_url=decoded_value)

if __name__ == '__main__':
    # Enable SSL (HTTPS)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context)
