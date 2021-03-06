const port = chrome.runtime.connectNative("com.hakujitsu.udemy_translator");
let lastSender = null;

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
                    message: "INITIALIZE_TRANSLATOR",
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
        lastSender = sender;

        port.postMessage(JSON.stringify({
            message: "TRANSLATE_SCRIPT",
            script: message.caption.trim().replaceAll('\n', ' ')
        }));
    }
});

port.onMessage.addListener(message => {
    if (message.message === "SCRIPT_TRANSLATED") {
        chrome.tabs.sendMessage(lastSender.tab.id, {
            message: "CAPTION_TRANSLATED",
            translated_caption: message.translated_script
        });
    }
    else if (message.message === "EXCEPTION_OCCERRED") {
        chrome.extension.getBackgroundPage().console.log(message.exception);

        chrome.tabs.sendMessage(lastSender.tab.id, {
            message: "EXCEPTION_OCCERRED",
            exception: message.exception
        });
    }
});