# JSONPeek
[<img src="https://blog.mozilla.org/addons/files/2020/04/get-the-addon-fx-apr-2020.svg" alt="for Firefox" height="60px">](https://addons.mozilla.org/en-US/firefox/addon/jsonpeek/)

![Mozilla Add-on Stars](https://img.shields.io/amo/stars/jsonpeek)
![Mozilla Add-on Version](https://img.shields.io/amo/v/jsonpeek)

This addon passively listens for network requests which include GET parameters commonly used by JSONP endpoints. The extension popup will show you any of these detected requests. Clicking on a request in the popup will open the JSONP endpoint in a new tab for you to play around with. Additionally, there is an "exploit" button that sends the suspected JSONP url to my webserver to check if it is exploitable. The source code for the webserver can be found <a href=https://github.com/ACK-J/JSONPeek/blob/main/jsonpeek-webserver.py>HERE</a>. Multiple proof of concepts are attempted with check marks indicating success and an X indicating failure.
# Popup
The image below shows the extension popup with the domain name at the top, the suspected JSONP parameter discovered highlighted in red, and an exploit button in the bottom left corner.
<p align="center">
  <img src="https://github.com/user-attachments/assets/a6d26b23-d34b-4920-bcef-9eead8952eb5" alt="GUI">
</p>

# JSONPeek.com Exploit Server
Clicking the bottom left "exploit" button will open a new tab probing the URL to see if it is a JSONP endpoint. 
<p align="center">
  <img src="https://github.com/user-attachments/assets/750ba7f1-f703-417a-9906-f4a853848eac" alt="GUI">
</p>
If successful an alert box will fire. This event will change the row's status in the table from an X to a check mark. 
<p align="center">
  <img src="https://github.com/user-attachments/assets/97d509fb-0e7d-4181-9520-d257bf2ded34" alt="GUI">
</p>

# Why do I want to find JSONP endpoints?
The most common way to bypass CSP is by finding a JSONP endpoint on a trusted domain within the CSP. <a href=https://dev.to/benregenspan/the-state-of-jsonp-and-jsonp-vulnerabilities-in-2021-52ep>JSONP</a> takes advantage of the fact that the same-origin policy does not prevent execution of external `<script>` tags. Usually, a `<script src="some/js/file.js">` tag represents a static script file. But you can just as well create a dynamic API endpoint, say `/userdata. jsonp`, and have it behave as a script by accepting a query parameter (such as `?callback=CALLBACK`). 

## Donations 
- Monero Address: `89jYJvX3CaFNv1T6mhg69wK5dMQJSF3aG2AYRNU1ZSo6WbccGtJN7TNMAf39vrmKNR6zXUKxJVABggR4a8cZDGST11Q4yS8`

## Terms of Service
## Terms of Service
By using JSONPeek, you agree to use it solely for lawful and ethical purposes, specifically for authorized penetration testing and security research with the explicit, written consent of the system owner. Unauthorized use of this tool against third-party systems without permission is strictly prohibited and may constitute a violation of local, national, or international laws. You are solely responsible for ensuring your use complies with all applicable regulations. The developers and distributors of JSONPeek disclaim all liability for any misuse or damage resulting from its use and provide the tool “as-is” without warranties of any kind. By using the tool, you agree to indemnify and hold harmless its creators from any claims, damages, or legal consequences arising from your actions. Continued use of the tool following any updates to these terms constitutes your acceptance of the revised Terms of Service.
