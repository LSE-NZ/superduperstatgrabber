import riotwatcher
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import pandas as pd
import os
from datetime import timedelta 
from datetime import datetime
import time
import tkinter as tk
from tkinter import ttk
import json
import requests

with open('api_key.json','r') as f:
    api_key = str(json.load(f))

lol_watcher = LolWatcher(api_key=api_key
#rate_limiter=)
)

def puuid_from_ign(cus_reg,cus_name,cus_tag):
    print("Added account",cus_name,cus_tag,cus_reg)

accounts_lib = {'neckless': ['euw1','_J-2ueCR5fA3h616PW1x66e5FR0BNhm8WkA4w7QYA21u9rmD-Yddsmk4fBvfcERdV0qqEatf6KbYkA']}

with open('accounts.json', 'r') as f:
        data = json.load(f)

acc_buffer = {}

def update_buffer():
    acc_buffer.update(data)
    accounts_lib.update(acc_buffer)

update_buffer()

def acc_to_list(new_name,new_region,new_puuid):
    update_buffer()
    accounts_lib.update(acc_buffer)
    accounts_lib.update({new_name: [new_region, new_puuid]})

    j = json.dumps(accounts_lib,indent=4)
    
    with open (file='accounts.json', mode = 'w') as f:
        f.write(j)
        f.close
        print('Account added')

def read_data():
    with open('match_data.json','r') as f:
        specific_data = json.load(f)
        print(specific_data)
read_data()

def get_data(region,puuid,match_list):
    data_dict = {'games':{}}
    data_dict.clear
    
    for match in match_list:
        game_data = lol_watcher.match.by_id(region=region,match_id=match)
        data_dict['games'].update(game_data)
        d = json.dumps(data_dict,indent=4, separators=[',',':'])
        with open (file='match_data.json',mode='a') as f:
            print('writting')
            f.write(d)
            f.close


def search(name,count):

    with open('accounts.json','r') as f:
        account_data = json.load(f)
    region = account_data[name][0]
    puuid = account_data[name][1]
    try:
        match_list = lol_watcher.match.matchlist_by_puuid(region=region,puuid=puuid,count=count)
        get_data(region=region,puuid=puuid,match_list=match_list)
    except KeyError:
        print('Select an account')
        
def gui_main():
    app = tk.Tk()
    app.title("Stats Grabber")
    app.geometry("400x400")

    def set_api():
        api = tk.Toplevel()
        api.geometry('400x400')
        api.title("Enter API Key")

        def set_api_key(api_key):

            j = json.dumps(api_key)
            with open('api_key.json', 'w') as f:
                f.write(j)
            api.withdraw()
        
        api_entry = tk.Entry(api)
        api_entry.place(x=100,y=50)
        api_set_btn = tk.Button(api,text='Set API Key',command=lambda:set_api_key(api_key=api_entry.get()))
        api_set_btn.place(x=100,y=100)


    def custom_input():
        ci = tk.Toplevel()
        ci.geometry("400x400")
        ci.title("Custom Input")
        
        def pass_acc():
            acc_to_list(new_name=name_entry.get(),new_region=region_entry.get(),new_puuid=puuid_entry.get())
            with open('accounts.json','r') as f:
                data2 = json.load(f)
                sel_acc['values'] = list(data2.keys())
            ci.withdraw()

        name_entry = tk.Entry(ci)
        name_entry.place(x = 50, y = 50)
        region_entry = tk.Entry(ci)
        region_entry.place(x = 50, y = 70)
        puuid_entry = tk.Entry(ci)
        puuid_entry.place(x = 50, y = 90)
        add_acc_btn = tk.Button(ci,text="Add Account",command=lambda:(pass_acc())).place(x=50,y=110)

    sel_acc = ttk.Combobox(app,values=list(data.keys()))
    sel_acc.place(x=100,y=100)
    sel_acc.set("Choose Account")

    var = tk.StringVar()
    var.set('neckless')

    input_acc = tk.Entry(app)
    input_acc.place(x=150,y=150)
        
    sel_acc = ttk.Combobox(app,values=list(data.keys()))
    sel_acc.place(x=100,y=100)

    search_acc_btn = tk.Button(app,text="Search",command=lambda:search(name=sel_acc.get(), count=input_acc.get()))
    search_acc_btn.place(x=100,y=120)

    new_acc_btn = tk.Button(app,text="New Account",command=lambda:custom_input()).place(x=50,y=50)

    api_btn = tk.Button(app,text='API Key',command=lambda:set_api())
    api_btn.place(x=100,y=200)
    
    app.mainloop()

gui_main()