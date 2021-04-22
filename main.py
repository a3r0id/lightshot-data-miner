from requests import get
from string import ascii_lowercase
from random import choice
from user_agent import generate_navigator
import pytesseract as tess
tess.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
from PIL import Image
from os import remove, getcwd
import threading
from json import dump, dumps, loads
import face_recognition
from datetime import datetime
from time import sleep

oof_backup = """{
    "good": [],
    "bad": [],
    "banned": []
}
"""

class images:
    found            = []
    processed        = 0
    success          = 0

class config:
    process_threads  = 10
    request_threads  = round(process_threads / 4)

class proxies:
    good             = []
    fresh_list       = []
    proxies          = {}
    T_INDEX          = 0

T_LOCK               = threading.Lock()   


class Proxies(object):
    def __init__(self) -> None:
        super().__init__()

        self.proxy_buffer = {}

        self.proxy_file = getcwd() + "/data/proxies.json"

    def get(self):
        T_LOCK.acquire()
        x = open(self.proxy_file)
        t = x.read()
        x.close()
        T_LOCK.release()    
        try:
            return loads(t)
        except:
            with open(self.proxy_file, 'w+') as f:
                f.write(oof_backup)
                print("%s was not JSON parsable! File re-formatted, please restart...")
                exit(1)

    def set(self, object):
        T_LOCK.acquire()
        with open(self.proxy_file, 'w+') as f:
            dump(object, f, indent=4)       
        T_LOCK.release()

# proxies.proxies = new Proxies();
proxies.proxies = Proxies()             

def proxyTestWorker():
    
    while True:

        proxy        = ""

        if (len(proxies.fresh_list)):
            proxy    = proxies.fresh_list.pop(0)
        else:
            continue
    
        address      = proxy.split(":")[0]
        port         = int(proxy.split(":")[1])

        proxified    = {
            'http':  f'http://{address}:{port}',
            'https': f'http://{address}:{port}'
        }

        abort = False

        obj = proxies.proxies.get()
            
        for bad_prox in obj['bad']:
            if (bad_prox['string'] == proxy):
                abort = True
                break

        for banned_prox in obj['banned']:
            if (banned_prox['string'] == proxy):      
                abort = True
                break     

        if not abort:

            proxies.T_INDEX += 1

            try:

                r        = get("http://prnt.sc", proxies = proxified, timeout=4.9)
                time_    = r.elapsed.microseconds / 1000

                if r.status_code == 403:

                    p_obj = proxies.proxies.get()
                    p_obj.banned.append({"ban_time": str(datetime.now()), "proxy": proxified, "string": proxy})
                    proxies.proxies.set(p_obj)
                    print("[BANNED PROXY: %s INDEX: %s / %s]" % (proxy, proxies.T_INDEX, len(proxies.fresh_list)))
                    continue   

            except:

                p_obj = proxies.proxies.get()
                p_obj['bad'].append({"test_time": str(datetime.now()), "proxy": proxified, "string": proxy})
                proxies.proxies.set(p_obj)
                print("[BAD PROXY: %s INDEX: %s / %s]" % (proxy, proxies.T_INDEX, len(proxies.fresh_list)))
                continue

            p_obj = proxies.proxies.get()
            p_obj['good'].append({"test_time": str(datetime.now()), "elapsed_time": time_, "proxy": proxified, "string": proxy, "status_code": r.status_code})
            proxies.proxies.set(p_obj)
            print("[GOOD PROXY: %s ELAPSED: %s INDEX: %s / %s]" % (proxy, time_, proxies.T_INDEX, len(proxies.fresh_list)))


#            T_LOCK.acquire()
#            print(proxies.proxies.get())
#            T_LOCK.release()

def updateProxies():

    print("Requesting proxies:")

    r = get(
        "https://api.proxyscrape.com" \
        "/v2/" \
        "?request=getproxies" \
        "&protocol=http" \
        "&timeout=4999" \
        "&country=all" \
        "&ssl=yes" \
        "&anonymity=all" \
        "&simplified=true",
        timeout=5
    )
    
    if (r.ok):
        proxies.fresh_list = r.text.splitlines()
        print("[api.proxyscrape.com] [Status %s] [Proxies Found: %s]" % (r.status_code, len(proxies.fresh_list),))
    else:
        print("[api.proxyscrape.com] [Status: %s]" % (r.status_code))
        exit(1)

    threads      = []

    for _ in range(10):
        threads.append(threading.Thread(target=proxyTestWorker))

    for i in range(10):
        threads[i].start()  

#    for i in range(10):
#        threads[i].join()      

def getBestProxy():
    tries = 0
    while True:
        if (tries == 100):
            print("Failed to find any good proxies!!!")
            exit(1)
        if (not len(proxies.proxies.get()['good'])):
            tries += 1
            sleep(.5)
            print("WATING FOR GOOD PROXY...")
            continue
    
        proxy_list = proxies.proxies.get()['good']

        print("GETTING BEST PROX:")
        print(proxy_list)

        fastestProxy = min([proxy['elapsed_time'] for proxy in proxy_list])
        
        for proxy in proxy_list:
            if proxy['elapsed_time'] == fastestProxy:
                return proxy
    

alpha = list(ascii_lowercase) + [str(i) for i in range(10)]

def makeToken(size):
    buffer = ""
    for _ in range(size):
        buffer += choice(alpha)
    return buffer    

def process_image_worker():
    
    while True:

        if not len(images.found):
            continue

        job   = images.found.pop(0)

        fname = "images/%s.png" % job['token']

        UA    = generate_navigator()["user_agent"]

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

        bestProx = getBestProxy()['proxy']
        print("[IMAGE PROCCESSING] Starting Image: %s" % fname)

        try:
            re = get(job['url'], stream=True, allow_redirects=True, headers=headers, proxies=bestProx, timeout=4.9)
        except:
            print("[Image Proccessing] Worker Request Timed Out! [Proxy: %s]" % bestProx['http'])
            continue

        if re.status_code == 403:

            p_obj = proxies.proxies.proxies.get()
            nuGoodProxies = []
            for p in p_obj['good']:
                if (p['good']['proxy'] == bestProx):
                    p_obj.banned.append({"ban_time": str(datetime.now()), "proxy": bestProx, "string": bestProx['http']})
                else:
                    nuGoodProxies.append(p)    
            p_obj['good'] = nuGoodProxies    
            proxies.proxies.set(p_obj)    
            print("[Image Proccessing] Worker Request Got [Proxy: %s] Banned! [Image: %s] [Code: %s] " % ( bestProx['http'], fname, re.status_code,))
            continue

        if not re.ok:
            print("[Image Proccessing] Worker Request Bad Respone Status Code! [Image: %s] [Code: %s] [Proxy: %s]" % (fname, re.status_code, bestProx['http'],))
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

        
        
        if len(faces_found):
            T_LOCK.acquire()
            with open("data/faces.json", "a") as f:
                f.write(dumps(job) + "\n")
            T_LOCK.release()

        if len(text):
            T_LOCK.acquire()
            with open("data/text.json", "a") as f:
                f.write(dumps(job) + "\n")   
            T_LOCK.release()   

        remove(fname)
        print("[Image Proccessing] Worker Request Bad Respone Status Code! [Image: %s] [Code: %s] [Proxy: %s]" % (fname, re.status_code, bestProx['http'],))
        images.success += 1


def request_worker():
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
        
        try:
            r = get(url, headers=headers, proxies=getBestProxy()['proxy'])
        except:
            continue    

        if not r.ok:

            if (r.status_code == 403):
                print("Your IP address has been banned by prnt.sc!")
                continue

            print({"status_code": r.status_code, "url": url})
            continue
        
        try:
            # BYPASS ANTI BOT MEASURES BY SIMPLY JUST GRABGING THE IMAGE FROM THE STATIC HTML HEAD INSTEAD OF RELYING ON A VALID BODY LOAD + XHR
            imgUrl = r.text.split("<meta property=\"og:image\" content=\"")[1].split("\"")[0]
        except Exception as f:
            continue

        if "st." in imgUrl:
            continue
        #                                                             PROC. THREADS           TRAY COUNT         PROCESSED COUNT   IMG URL
        print("[Threads: %s Tray Count: %s Proccessed: %s ] -> %s" % (config.process_threads, len(images.found), images.processed, imgUrl,))

        images.found.append({"token": token, "url": imgUrl})        


if __name__ == "__main__":

    # INITIALLY REQUEST AND SORT PROXIES
    updateProxies()

    # UPDATES PROXIES IN BACKGROUND
    def prox():
        while True:
            sleep(60 * 10)
            updateProxies()

    print("[*i*] STARTING PROXY TESTING, THIS WILL TAKE A MOMENT...")
    proxThread = threading.Thread(target=prox)
    proxThread.start()
    #proxThread.join()

    print("[*i*] PROXY TESTING COMPLETED!")

    for i in range(config.process_threads):
        t = threading.Thread(target=process_image_worker)
        t.start()
    
    print("[*i*] Started %s Image Proccessing Threads" % config.process_threads)

    for i in range(config.request_threads):
        t = threading.Thread(target=request_worker)
        t.start()    

    print("[*i*] Started %s HTTP Request Threads" % config.process_threads)







