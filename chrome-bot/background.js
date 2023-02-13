// background.js

chrome.runtime.onInstalled.addListener(function (details) {
  if (details.reason === "install") {
    // The extension has been installed for the first time
    chrome.notifications.create({
      type: "basic",
      iconUrl: "logo_crop.png",
      title: "Welcome to OpenAssistant!",
      message: "Thank you for installing OpenAssistant.",
    });

    chrome.tabs.create({
      url: "congrats.html",
    });
  }
});
