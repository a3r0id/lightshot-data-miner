# lightshot-data-miner
 I had a random idea to make a data miner for lightshot a while back. Today a friend brought it to my attention that folks are now mining Lightshot images for valuable information etc...here is a proof of concept! This script bruteforces for valid prnt.sc urls and for images containing human faces/text then saves the images.

- Install [Tesseract-OCR](https://github.com/tesseract-ocr/tessdoc)

- Install requirements.txt

- `python3 main.py`

--------

> Change Line 22: # CHANGE TO PATH TO YOUR TESSERACT BINARY
`tess.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"`

> I left some example results of old scans in the repo, I am not aware of any of the content of the images as they are random. 

> You can remove the proxy stuff and use your own ip which will be much faster, just don't use more than a few threads in that case.

> This is simply a **proof of concept**!