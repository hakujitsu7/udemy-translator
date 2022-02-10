import languages from "./languages.js"

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#form");

    const alertSuccess = document.querySelector("#alert-success");

    const selectSourceLanguage = document.querySelector("#select-source-language");
    const selectTargetLanguage = document.querySelector("#select-target-language");
    const InputApiKey = document.querySelector("#input-api-key");

    for (const key in languages) {
        selectSourceLanguage.options.add(new Option(languages[key], key));
        selectTargetLanguage.options.add(new Option(languages[key], key));
    }

    browser.storage.local.get(
        {
            "sourceLanguage": "en",
            "targetLanguage": "ko",
            "apiKey": null
        },
        result => {
            selectSourceLanguage.value = result.sourceLanguage;
            selectTargetLanguage.value = result.targetLanguage;
            InputApiKey.value = result.apiKey;
        }
    );

    form.addEventListener("submit", event => {
        event.preventDefault();

        if (form.checkValidity()) {
            browser.storage.local.set({
                "sourceLanguage": selectSourceLanguage.value,
                "targetLanguage": selectTargetLanguage.value,
                "apiKey": InputApiKey.value || null
            });

            alertSuccess.classList.remove("collapse");
        }

        form.classList.add("was-validated");
    });
});