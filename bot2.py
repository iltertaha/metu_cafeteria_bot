


import json
import requests
import time
import urllib
import datetime
import io

from bs4 import BeautifulSoup

TOKEN = "512294390:AAFBkxoQCkrGleUtsgHhGQJFcQq-0UAYPG0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def get_updates(self, offset=None, timeout=50):
    method = 'getUpdates'
    params = {'timeout': timeout, 'offset': offset}
    resp = requests.get(self.api_url + method, params)
    result_json = resp.json()['result']
    return result_json



def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def send_image(botToken, imageFile, chat_id):
    command = 'curl -s -X POST https://api.telegram.org/bot' + botToken + '/sendPhoto -F chat_id=' + chat_id + " -F photo=@" + imageFile
    subprocess.call(command.split(' '))
    return

def sendImageRemoteFile(chat_id,img_url):
    url = "https://api.telegram.org/bot512294390:AAFBkxoQCkrGleUtsgHhGQJFcQq-0UAYPG0/sendPhoto";
    remote_image = requests.get(img_url)
    photo = io.BytesIO(remote_image.content)
    photo.name = 'img.png'
    files = {'photo': photo}
    data = {'chat_id' : chat_id}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)



def yemekhane_daily():
    now = datetime.datetime.now()
    bugun=now.strftime("%A")
    if bugun in ["Saturday","Sunday"]:
        return False
    url='http://kafeterya.metu.edu.tr/'

    r=requests.get(url)

    soup=BeautifulSoup(r.content,"lxml")
    yemeks=soup.find("body").find("div").find_all("p")
    food=[]
    for yemek in yemeks:
        food.append(yemek.get_text())

    return food


def yemekhane_menu_resim():
    image_list=[]
    url = "http://kafeterya.metu.edu.tr"
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html)
    for link in soup.find_all('img'):
        image_list.append(link.get('src'))

    image_list=list(filter(lambda x: x.startswith("images/yemekresim"),image_list))
    for i in image_list:
        print(i)
    return image_list

def handle_updates(updates):
    for update in updates["result"]:
        last_update_id = update['update_id']
        if update["message"]["text"]:
            text = update["message"]["text"]
        else:
            print("asd")
        chat = update["message"]["chat"]["id"]

        if text == "/done":
            send_message("Bot turned of", chat)
            new_offset = last_update_id + 1

        elif text == "/start":
            keyboard=build_keyboard(["a","b"])
            send_message("Hi,I'm boronabot for metu cafeteria.How can I help you?", chat,keyboard)
            new_offset = last_update_id + 1


        elif text == "/boronatoday":
            send_message("please wait.I'm checking the cafeteria menu",chat)
            time.sleep(2)
            send_message("Sorry,there is no borona for today",chat)
            send_image(TOKEN,"https://cdn.shopify.com/s/files/1/1061/1924/products/Sad_Face_Emoji_large.png",chat)
            new_offset = last_update_id + 1
        elif text.lower()=="yemekte ne var?":
            if yemekhane_daily():
                keyboard=build_keyboard(["Yemekte ne var?","resimli menu","Sevmediğim yemekler(coming soon)"])
                send_message("Menuyu bir kontrol edeyim",chat,keyboard)

                liste=yemekhane_daily()
                for i in range(5):
                    send_message(liste[i],chat)
                new_offset = last_update_id + 1
            else:
                send_message( "Haftasonlari yemek yok hocam.",chat)
                new_offset = last_update_id + 1


        elif text=="/boronafoto":
            sendImageRemoteFile(chat,"https://mobile.donanimhaber.com/store/4a/83/d7/4a83d7cc533653bdebc14c9f4371d1ad.jpg")
            new_offset = last_update_id + 1

        elif text==("resimli menu"):
            keyboard=build_keyboard(["resimli menu->ogle","resimli menu->aksam",])
            send_message("choose side",chat,keyboard)
            new_offset = last_update_id + 1

        elif text==("resimli menu->ogle"):
            image=yemekhane_menu_resim()
            for i in range(4):
                if(str(image[i])=="images/yemekresim/3389dae361af79b04c9c8e7057f60cc6.jpg"):
                    send_message("Bu yemek icin resim yok",chat)
                else:
                    sendImageRemoteFile(chat,"https://kafeterya.metu.edu.tr/"+str(image[i]))

        elif text==("resimli menu->aksam"):
            image=yemekhane_menu_resim()
            for i in range(4,8):
                if(str(image[i])=="images/yemekresim/3389dae361af79b04c9c8e7057f60cc6.jpg"):
                    send_message("Bu yemek icin resim yok",chat)
                else:
                    sendImageRemoteFile(chat,"https://kafeterya.metu.edu.tr/"+str(image[i]))

        elif text.startswith("Bugun yemekte"):

            liste1=yemekhane_daily()
            words=text.split()


            words1=words[2:-2]
            print(words)
            print(liste1)

            matching = [s for s in liste1 if words[2].upper() in s]


            if matching:
                for i in matching:
                    send_message("Bugunku menude bulunan: {} ".format(i),chat)

            else:
                send_message("Malesef",chat)

            new_offset = last_update_id + 1


        elif text.startswith("/"):
            new_offset = last_update_id + 1
            continue

        else:
            continue
            
      
        elif text=="/"):
            send_message("Lütfen komut girin.",chat)
    


        elif text==("/help"):
            keyboard=build_keyboard(["bugün yemekte {yemek} var mı","/boronafoto","resimli menu","Sevmediğim yemekler(coming soon)"])
            send_message("Komutlar şu şekilde",chat,keyboard)
            
            

def build_keyboard(items):
    keyboard = [[item] for item in items]
    _markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)





def main():


    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)



if __name__ == '__main__':
    main()
