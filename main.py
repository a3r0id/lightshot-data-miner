from numpy.lib.type_check import imag
from requests import get
from string import ascii_lowercase
from random import choice
from time import sleep, thread_time, time
from user_agent import generate_navigator
import pytesseract as tess
tess.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
from PIL import Image
from os import remove
import threading
from json import dumps
import face_recognition

class images:
    found     = []
    processed = 0
    success   = 0

process_lock = threading.Lock()    
request_lock = threading.Lock()  

process_thread_count = 10 # BE CAREFUL // 25 threads will cause denial of service and your ip will be banned within seconds.
request_thread_count = round(process_thread_count / 4)

proxies      = []
currentProxy = None

def updateProxies():
    r = get(
        "https://api.proxyscrape.com" \
        "/v2/" \
        "?request=getproxies" \
        "&protocol=http" \
        "&timeout=500" \
        "&country=all" \
        "&ssl=yes" \
        "&anonymity=all" \
        "&simplified=true"
        )
    
    if (r.ok):
        lines = r.text.splitlines()
        print(f"[UPDATED PROXIES] Found {len(lines)} Proxies!")

        for line in lines:

            address    = line.split(":")[0]
            port       = int(line.split(":")[1])

            proxified  = {
                'http':  f'http://{address}:{port}',
                'https': f'http://{address}:{port}'
            }

            try:
                r      = get("http://prnt.sc", proxies = proxified, timeout=1.1)
                time_  = r.elapsed.microseconds / 1000
                if r.status_code == 403:
                    print(f"[PROXY TEST]: {address}:{port} is BANNED by prnt.sc!")
                    continue     
            except:
                print(f"[PROXY TEST]: {address}:{port} is DEAD!")
                continue

            proxies.append({"time": time_, "proxy": proxified})
            print(f"[PROXY TEST]: {address}:{port} is WORKING @ {time_}ms!")

        print(proxies)    

def getBestProxy():
    fastestProxy = min([proxy['time'] for proxy in proxies])
    for proxy in proxies:
        if proxy['time'] == fastestProxy:
            return proxy
    return None

alpha = list(ascii_lowercase) + [str(i) for i in range(10)]

def makeToken(size):
    buffer = ""
    for _ in range(size):
        buffer += choice(alpha)
    return buffer    

def process_image_daemon():
    
    while True:

        if len(images.found) == 0:
            continue

        job = images.found.pop(0)

        fname = "images/" + job['token'] + ".png"

        UA = generate_navigator()["user_agent"]

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            "accept-encoding": "gzip, deflate, br", 
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8", 
            "cache-control": "no-cache",
            "cookie": "__cfduid=d83a1ff8f16c7c7185d40f5edc0d39b6c1607400000;",
            "dnt": "1", 
            "pragma": "no-cache",
            "sec-ch-ua": """Google Chrome";v="87", "\"Not;A\\Brand";v="99", "Chromium";v="87""",
            "sec-ch-ua-mobile": "?1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1", 
            "user-agent": UA
        }
        
        re = get(job['url'], stream=True, allow_redirects=True, headers=headers)

        if not re.ok:
            continue

        with open(fname, 'wb') as handle:
            
            for block in re.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        with open(fname, "rb") as f:
            if not len(f.read()):
                print("Removed dead file.")
                try:
                    remove(fname)
                except:
                    pass    
                continue

        job["text"] = None

        job["faces"] = None    

        
        images.processed += 1
        image = Image.open(fname)
        text = tess.image_to_string(image)

        if len(text):
            job["text"] = text


        imag = face_recognition.load_image_file(fname)
        face_locations = face_recognition.face_locations(imag)
        # Improting Image class from PIL module 

        faces_found = []

        for face in face_locations:

            uid = makeToken(6)

            # crop (left, top, right, bottom)
            # face (top, right, bottom, left)
            im1 = image.crop((face[3], face[0], face[1], face[2])) 
            fnaem = "images/faces/%s.png" % (uid,)
            im1.save(fnaem)     

            im1.close()

            faces_found.append({"image": fnaem, "locations": [i for i in face]})

        image.close()
        
        job['faces'] = faces_found

        process_lock.acquire()
        
        if len(faces_found):
            with open("data/faces.json", "a") as f:
                f.write(dumps(job) + "\n")

        if len(text):
            with open("data/text.json", "a") as f:
                f.write(dumps(job) + "\n")

        process_lock.release()        

        remove(fname)
        images.success += 1


def request_daemon():
    while 1:
        UA = generate_navigator()["user_agent"]
        token = makeToken(6)
        url = "https://prnt.sc/" + token
        headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "accept-encoding": "gzip, deflate, br", 
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8", 
        "cache-control": "no-cache",
        "cookie": "__cfduid=d83a1ff8f16c7c7185d40f5edc0d39b6c1607408271;",
        "dnt": "1", 
        "pragma": "no-cache",
        "sec-ch-ua": """Google Chrome";v="87", "\"Not;A\\Brand";v="99", "Chromium";v="87""",
        "sec-ch-ua-mobile": "?1",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1", 
        "user-agent": UA
    }
        
        r = get(url, headers=headers)

        if not r.ok:
            if (r.status_code == 403):
                print("Your IP address has been banned by prnt.sc!")
            print({"status_code": r.status_code, "url": url})
            continue
        
        try:
            imgUrl = r.text.split("<meta property=\"og:image\" content=\"")[1].split("\"")[0]
        except Exception as f:
            #print("[:(] -> " + str(f))
            continue

        if "st." in imgUrl:
            continue
        #                                               THREADS        TRAY COUNT         PROCESSED COUNT                IMG URL
        print("[Threads: %s Tray Count: %s Proccessed: %s ] -> %s" % (process_thread_count, len(images.found), images.processed, imgUrl,))

        images.found.append({"token": token, "url": imgUrl})        

if __name__ == "__main__":

    #UPDATE PROXY LIST
    updateProxies()

    for i in range(process_thread_count):
        print("Started thread #%s" % (i+1,))
        t = threading.Thread(target=process_image_daemon)
        t.start()

    for i in range(request_thread_count):
        t = threading.Thread(target=request_daemon)
        t.start()    









