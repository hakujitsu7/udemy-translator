let translatedCaption = '';

function onCaptionUpdated() {
    const caption = document.querySelector(".captions-display--captions-cue-text--ECkJu");

    if (caption && caption.innerText !== translatedCaption) {
        chrome.runtime.sendMessage({
            message: "TRANSLATE_CAPTION",
            caption: caption.innerText
        });
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.message === "CAPTION_TRANSLATED") {
        const caption = document.querySelector(".captions-display--captions-cue-text--ECkJu");

        if (caption && caption.innerText !== message.translated_caption) {
            translatedCaption = message.translated_caption;
            caption.innerText = translatedCaption;
        }
    }
    else if (message.message === "EXCEPTION_OCCERRED") {
        alert(
            "자막을 번역하던 중 예외가 발생했습니다.\n" +
            "페이지를 새로고침해 주시기 바랍니다.\n" +
            "\n" +
            message.exception
        );
    }
});

const timer = setInterval(() => {
    const captionContainer = document.querySelector(".captions-display--captions-container--1-aQJ");

    if (captionContainer) {
        onCaptionUpdated();

        const observer = new MutationObserver(mutation => {
            onCaptionUpdated();
        });
        observer.observe(captionContainer, {
            childList: true,
            subtree: true,
            characterData: true
        });

        clearInterval(timer);
    }
}, 100);