const port = browser.runtime.connectNative("com.hakujitsu.udemy_translator");
let latestSender = null;

browser.webRequest.onSendHeaders.addListener(
    details => {
        browser.storage.local.get(
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

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.message === "TRANSLATE_CAPTION") {
        port.postMessage(JSON.stringify({
            message: "TRANSLATE_SCRIPT",
            script: message.caption.trim().replaceAll('\n', ' ')
        }));

        latestSender = sender;
    }
});

port.onMessage.addListener(message => {
    if (message.message === "SCRIPT_TRANSLATED") {
        browser.tabs.sendMessage(latestSender.tab.id, {
            message: "CAPTION_TRANSLATED",
            translated_caption: message.translated_script
        });
    }
    else if (message.message === "EXCEPTION_OCCERRED") {
        browser.extension.getBackgroundPage().console.log(message.exception);
    }
});