// Utility function to encode URL to base64
function encodeUrlToBase64(url) {
  return btoa(unescape(encodeURIComponent(url)));
}

// List of query parameters to identify JSONP requests
const jsonpParams = [
  'callback', 'jsonpCallback', 'jsonp', 'callback_func', 'func', 
  'handler', 'jsonp_handler', 'cbfn', 'onload', 'j', 'oncomplete'
];

// Query the active tab in the current window
browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
  const tabId = tabs[0].id;

  // Retrieve the tab-specific data from local storage
  browser.storage.local.get("tabData").then((data) => {
    const jsonpListElement = document.getElementById("jsonp-list");
    jsonpListElement.innerHTML = ""; // Clear previous content

    // If data exists for the current tab, display the endpoints and query parameters
    if (data.tabData && data.tabData[tabId]) {
      const tabJsonpData = data.tabData[tabId];

      // Display each unique JSONP endpoint with its query parameters
      if (tabJsonpData.jsonpEndpoints.size > 0) {
        tabJsonpData.jsonpEndpoints.forEach((endpoint) => {
          const url = new URL(endpoint);
          const li = document.createElement("li");
          li.classList.add('endpoint-item');
          
          // Add the endpoint text to the card without the "Endpoint:" prefix
          const endpointText = document.createElement("p");
          endpointText.textContent = url.origin + url.pathname;
          li.appendChild(endpointText);
          
          // Add query parameters below the endpoint
          const queryParams = Array.from(url.searchParams.entries());

          // Filter out only the JSONP-related parameters
          const jsonpQueryParams = queryParams.filter(([param, value]) => jsonpParams.includes(param));
          
          if (jsonpQueryParams.length > 0) {
            const paramList = document.createElement("ul");
            jsonpQueryParams.forEach(([param, value]) => {
              const paramItem = document.createElement("li");
              paramItem.textContent = `${param}: ${value}`;

              // Highlight the JSONP parameter in red
              paramItem.style.color = 'red';
              
              paramList.appendChild(paramItem);
            });

            li.appendChild(paramList);
          } else {
            const noParamsMessage = document.createElement("li");
            noParamsMessage.textContent = "No JSONP parameters found.";
            li.appendChild(noParamsMessage);
          }

          // Add the exploit button to each endpoint
          const exploitButton = document.createElement("button");
          exploitButton.textContent = "Exploit";
          exploitButton.style.backgroundColor = "#ff6347"; // Subtle button style
          exploitButton.style.color = "white";
          exploitButton.style.border = "none";
          exploitButton.style.padding = "5px 10px";
          exploitButton.style.cursor = "pointer";
          exploitButton.style.fontSize = "12px";
          exploitButton.style.marginTop = "10px";

          // Handle the exploit button click
          exploitButton.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent opening the endpoint in a new tab

            // Modify query parameters and replace with "alert"
            jsonpQueryParams.forEach(([param, value]) => {
              url.searchParams.set(param, 'alert');
            });

            // Encode the modified URL to base64
            const base64Url = encodeUrlToBase64(url.href);

            // Open a new tab with the base64-encoded URL
            const newTab = window.open(`https://jsonpeek.ail.fail/?url=${base64Url}`);
          });

          li.appendChild(exploitButton);

          jsonpListElement.appendChild(li);

          // Add click event listener to open the endpoint in a new tab
          li.addEventListener('click', () => {
            browser.tabs.create({ url: endpoint });  // Open the endpoint URL in a new tab
          });
        });
      } else {
        const li = document.createElement("li");
        li.textContent = "No JSONP callbacks found for this tab.";
        jsonpListElement.appendChild(li);
      }
    } else {
      const li = document.createElement("li");
      li.textContent = "No JSONP callbacks found for this tab.";
      jsonpListElement.appendChild(li);
    }
  }).catch((err) => {
    console.error("Error fetching tab data: ", err);
  });
});
