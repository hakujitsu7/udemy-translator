robocopy . chrome * /XD chrome firefox /XF .gitignore build.bat manifest_*.json /S
robocopy . firefox * /XD chrome firefox /XF .gitignore build.bat manifest_*.json /S

xcopy .\manifest_chrome.json .\chrome\manifest.json /Y
xcopy .\manifest_firefox.json .\firefox\manifest.json /Y