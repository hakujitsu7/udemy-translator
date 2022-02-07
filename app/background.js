const port = chrome.runtime.connectNative("com.hakujitsu.udemy_translator");
let latestSender = null;

chrome.webRequest.onSendHeaders.addListener(
    details => {
        chrome.storage.local.get(
            {
                "sourceLanguage": "en",
                "targetLanguage": "ko",
                "apiKey": null
            },
            result => {
                port.postMessage(JSON.stringify({
                    message: "INITIALIZE",
                    webvtt_url: details.url,
                    source: result.sourceLanguage,
                    target: result.targetLanguage,
                    api_key: result.apiKey
                }));
            }
        );
    },
    { urls: ["*://vtt-b.udemycdn.com/*"] },
    ["requestHeaders"]
);

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.message === "TRANSLATE_CAPTION") {
        port.postMessage(JSON.stringify({
            message: "TRANSLATE_SCRIPT",
            script: message.caption.trim().replaceAll('\n', ' ')
        }));

        latestSender = sender;
    }
});

port.onMessage.addListener(response => {
    if (response.message === "SCRIPT_TRANSLATED") {
        chrome.tabs.sendMessage(latestSender.tab.id, {
            message: "CAPTION_TRANSLATED",
            translated_caption: response.translated_script
        });
    }
});