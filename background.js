// List of query parameters to identify JSONP requests
const jsonpParams = [
  'callback', 'jsonpCallback', 'jsonp', 'callback_func', 'func', 
  'handler', 'jsonp_handler', 'cbfn', 'onload', 'j', 'oncomplete'
];

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
      browser.storage.local.get("tabData", (data) => {
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
          browser.action.setBadgeText({ text: tabData[tabId].jsonpCounter.toString(), tabId });

          // Store updated tab data in local storage
          browser.storage.local.set({ tabData });
        }
      });
    }
  },
  { urls: ["<all_urls>"] }
);

// On extension installation, load saved data (if any)
browser.runtime.onInstalled.addListener(() => {
  browser.storage.local.get("tabData", (data) => {
    if (data.tabData) {
      // Do something with the saved data if needed
    }
  });
});

// Update the badge when a tab is switched or reloaded
browser.tabs.onActivated.addListener((activeInfo) => {
  const tabId = activeInfo.tabId;
  
  // Retrieve the tab data from local storage and update the badge
  browser.storage.local.get("tabData", (data) => {
    const tabData = data.tabData || {};
    if (tabData[tabId]) {
      browser.action.setBadgeText({ text: tabData[tabId].jsonpCounter.toString(), tabId });
    } else {
      browser.action.setBadgeText({ text: "" });
    }
  });
});

// Update the badge when the tab is updated (loaded/reloaded)
browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tabId === tab.id) {
    // Retrieve the tab data from local storage and update the badge
    browser.storage.local.get("tabData", (data) => {
      const tabData = data.tabData || {};
      if (tabData[tabId]) {
        browser.action.setBadgeText({ text: tabData[tabId].jsonpCounter.toString(), tabId });
      } else {
        browser.action.setBadgeText({ text: "" });
      }
    });
  }
});

