// List of query parameters to identify JSONP requests
const jsonpParams = [
  'callback', 'jsonpCallback', 'jsonp', 'callback_func', 'func', 
  'handler', 'jsonp_handler', 'cbfn', 'onload', 'j', 'oncomplete'
];

// Clear all data in local storage on extension load (first time or refresh)
async function clearLocalStorage() {
  try {
    // Clear all data in local storage
    await browser.storage.local.clear();
    console.log('Local storage cleared.');
  } catch (error) {
    console.error('Error clearing local storage:', error);
  }
}

// Listen for web requests
browser.webRequest.onBeforeRequest.addListener(
  (details) => {
    // Get the tab ID of the request
    const tabId = details.tabId;

    // Parse the URL of the request
    const url = new URL(details.url);

    // Check if the URL has any of the specified JSONP callback parameters
    const isJsonp = jsonpParams.some(param => url.searchParams.has(param));

    if (isJsonp) {
      // Retrieve the current tab data from local storage
      browser.storage.local.get("tabData").then((data) => {
        let tabData = data.tabData || {};

        // Ensure there is an entry for the tab
        if (!tabData[tabId]) {
          tabData[tabId] = {
            jsonpCounter: 0,
            jsonpEndpoints: new Set()
          };
        }

        // Extract the base URL (excluding query params) for the endpoint
        const baseUrl = url.origin + url.pathname + url.search;

        // Add the endpoint only if it is unique (Set ensures uniqueness)
        if (!tabData[tabId].jsonpEndpoints.has(baseUrl)) {
          tabData[tabId].jsonpEndpoints.add(baseUrl);

          // Increment the counter for JSONP requests on this tab
          tabData[tabId].jsonpCounter++;

          // Update the badge for the current tab
          const badgeText = tabData[tabId].jsonpCounter > 0 ? tabData[tabId].jsonpCounter.toString() : "";
          browser.browserAction.setBadgeBackgroundColor({ color: "#C41E3A" });
          browser.browserAction.setBadgeText({ text: badgeText, tabId });

          // Store updated tab data in local storage
          browser.storage.local.set({ tabData });
        }
      }).catch((err) => {
        console.error("Error fetching or setting tab data: ", err);
      });
    }
  },
  { urls: ["<all_urls>"] }
);

// Update the badge when a tab is switched or reloaded
browser.tabs.onActivated.addListener((activeInfo) => {
  const tabId = activeInfo.tabId;

  // Retrieve the tab data from local storage and update the badge
  browser.storage.local.get("tabData").then((data) => {
    const tabData = data.tabData || {};
    const badgeText = tabData[tabId] ? tabData[tabId].jsonpCounter.toString() : "";
    browser.browserAction.setBadgeText({ text: badgeText, tabId });
  }).catch((err) => {
    console.error("Error fetching tab data: ", err);
  });
});

// Update the badge when the tab is updated (loaded/reloaded)
browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    // Retrieve the tab data from local storage and update the badge
    browser.storage.local.get("tabData").then((data) => {
      const tabData = data.tabData || {};
      const badgeText = tabData[tabId] ? tabData[tabId].jsonpCounter.toString() : "";
      browser.browserAction.setBadgeText({ text: badgeText, tabId });
    }).catch((err) => {
      console.error("Error fetching tab data: ", err);
    });
  }
});

clearLocalStorage();
