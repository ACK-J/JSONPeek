// Query the active tab in the current window
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const tabId = tabs[0].id;

  // Retrieve the tab-specific data from local storage
  chrome.storage.local.get("tabData", (data) => {
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
          
          const paramList = document.createElement("ul");
          queryParams.forEach(([param, value]) => {
            const paramItem = document.createElement("li");
            paramItem.textContent = `${param}: ${value}`;

            // Highlight the JSONP parameter in red if it matches one of the known JSONP params
            if (['callback', 'jsonpCallback', 'jsonp', 'callback_func', 'func', 'handler', 'jsonp_handler', 'cbfn', 'onload', 'j', 'oncomplete'].includes(param)) {
              paramItem.style.color = 'red'; // Highlight in red
            }

            paramList.appendChild(paramItem);
          });

          li.appendChild(paramList);
          jsonpListElement.appendChild(li);
        });
      } else {
        const li = document.createElement("li");
        li.textContent = "No JSONP requests found for this tab.";
        jsonpListElement.appendChild(li);
      }
    } else {
      const li = document.createElement("li");
      li.textContent = "No JSONP requests found for this tab.";
      jsonpListElement.appendChild(li);
    }
  });
});

