## <!-- Meta Data ----- > ##
Version = '5.1.7'
Date = '4/28/25'

## <!-- Imports ----- > ##
import os
import json
import requests as rq
import time as t
import random as rx
import configparser as cfp
import webbrowser as web
import subprocess
import ctypes
import keyboard

## <!-- Variables ----- > ##
# dir & dat #
_dir = None
dat_dir = None
data = None
keys = None
key = None
con = None
pattyJ = None
pattyC = None
dat = None
COM = None

# webbrowser links #
Torn = "https://www.torn.com/"
City = f"{Torn}city.php"
Map = f"{Torn}city.php#map-cont"
Market = f"{Torn}page.php?sid=ItemMarket#/market/view=category&categoryName="
Museum = f"{Torn}museum.php"
PointsM = f"{Torn}pmarket.php"
PointsB = f"{Torn}page.php?sid=points"
Gym = f"{Torn}gym.php"

## <!-- Snippet Functions ----- > ##
def prints (*args) :
    for txt in args :
        print (txt)
        print ("")

def inputs (txt=str) :
    input (f"{txt}")
    print ("")

def check_admin():
    try:
        is_admin = os.name == 'nt' and ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        is_admin = False

    if is_admin:
        print("Script is running with administrative privileges.")
    else:
        print("Script is NOT running with administrative privileges.")

## <!-- Directory Path & Data Load ---- > ##
def base () :
    def pathing () :
        global _dir, dat_dir, dat
        _dir = os.path.dirname(os.path.abspath(__file__))
        dat_dir = os.path.join (_dir, 'data')
        if '/0/' in _dir or '\\0\\' in _dir :
            print ("Android Pathing Detected. dat set to False")
            dat = False
        elif 'C:/' in _dir or 'C:\\' in _dir :
            print ("Windows Pathing Detected. dat set to True")
            dat = True
        else :
            print ("Pathing Undetected. dat set to True")
            dat = True

    def datafiles (dat=bool) :
        global data, con, pattyJ, pattyC, keys
        if dat == False :
            pattyJ = os.path.join(_dir, 'dat.json')
            pattyC = os.path.join(_dir, 'bot.cfg')
        elif dat == True :
            pattyJ = os.path.join(dat_dir, 'dat.json')
            pattyC = os.path.join(dat_dir, 'bot.cfg')
        else :
            raise ValueError ("dat variable is still None! It MUST be True or Flase! True = PC, False = Android")
        with open (pattyJ, 'r') as f :
            data = json.load(f)
        con = cfp.ConfigParser()
        con.read(pattyC)
        keys = []
        for section in con.sections() :
            for key, value in con.items(section) :
                try :
                    if int(value) == int(value) :
                        keys.append(key)
                except ValueError :
                    continue
        return keys
    pathing ()
    datafiles (dat=dat)

## <!-- Data Handeling Functions ----- > ##
def KEY () :
    global keys
    if not keys :
        raise ValueError ("No Keys Available")
    else :
        return rx.choice(keys)

def Count(key):
    key_found = False
    for section in con.sections():
        if key in con[section]:
            key_found = True
            try:
                current_value = int(con[section][key])
                con[section][key] = str(current_value + 1)
            except ValueError:
                raise ValueError(f"Value for key '{key}' is not an integer.")
            break
    if not key_found:
        raise KeyError(f"Key '{key}' not found in configuration.")
    with open(pattyC, 'w') as file:
        con.write(file)

## <!-- Browser Handeling Functions ----- > ##
def Opera (url, x, y, width, height):
    cmd = f'start opera --window-size={width},{height} --window-position={x},{y} {url}'
    subprocess.run(cmd, shell=True)

def Open_Market (x) :
    categories = [
        'Alcohol',
        'Artifact',
        'Booster',
        'Candy',
        'Clothing',
        'Collectible',
        'Drug',
        'Energy%20Drink',
        'Enhancer',
        'Flower',
        'Jewelery',
        'Material',
        'Medical',
        'Other',
        'Plushie',
        'Special',
        'Supply%20Pack',
        'Temporary',
        'Tool'
    ]
    if not (1 <= x <= len(categories)):
        raise ValueError(f"Invalid category index: {x}. Must be between 1 and {len(categories)}.")
    cat_name = categories[x - 1]
    cat_url = f"{Market}{cat_name}"
    web.open_new_tab(cat_url)

def HOT (x) :
    if x == "r":  # Refresh
        fx = 'ctrl+r'
    elif x == "c":  # Close tab
        fx = 'ctrl+w'
    elif x == "t":  # New tab
        fx = 'ctrl+t'
    elif x == "zo":  # Zoom out
        fx = 'ctrl+-'
    elif x == "zi":  # Zoom in
        fx = 'ctrl+='
    elif x == "h":  # Open history
        fx = 'ctrl+h'
    elif x == "b":  # Open bookmarks
        fx = 'ctrl+b'
    elif x == "s":  # Save page
        fx = 'ctrl+s'
    elif x == "f":  # Find on page
        fx = 'ctrl+f'
    elif x == "n":  # New window
        fx = 'ctrl+n'
    elif x == "q":  # Quit browser
        fx = 'ctrl+shift+q'
    elif x == "w" : # Close Current Tab
        fx = 'ctrl+w'
    else:
        raise ValueError(f"Unknown hotkey action: {x}")
    keyboard.send(fx)

def Attack (ID) :
    fx = f"{Torn}loader.php?sid=attack&user2ID={ID}"
    web.open_new_tab(fx)

def Others (COM, ID) :
    Compare = f"{Torn}personalstats.php?ID=2353731,{ID}&stats=useractivity&from=1%20month"
    if COM == "c" :
        web.open_newtab(Compare)

##<!-- API Request Functions -----> ##
def Call (url) :
    apikey = f'{KEY()}'
    headers = {
        'accept': 'application/json',
        'Authorization': f'ApiKey {apikey}'
    }
    response = rq.get(url, headers=headers)
    if response.status_code != 200:
        raise rq.HTTPError(f"HTTP Error: {response.status_code} - {response.reason}")
    try:
        raw = response.json()
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response received.")
    Count(apikey)
    return raw

##<!-- Expiremental Browser Java Injection Functions -----> ##
def inject_highlight_script():
    script = """
    (function() {
        const thresholds = [
            { percentage: 50, color: 'red' },
            { percentage: 75, color: 'orange' },
            { percentage: 100, color: 'green' },
            { percentage: 125, color: 'blue' }
        ];
        function highlightItems() {
            const items = document.querySelectorAll('.market-item');
            items.forEach(item => {
                const priceElement = item.querySelector('.price');
                const marketValueElement = item.querySelector('.market-value');
                if (priceElement && marketValueElement) {
                    const price = parseFloat(priceElement.textContent.replace(/[^0-9.]/g, ''));
                    const marketValue = parseFloat(marketValueElement.textContent.replace(/[^0-9.]/g, ''));
                    if (!isNaN(price) && !isNaN(marketValue)) {
                        const percentage = (price / marketValue) * 100;
                        thresholds.forEach(threshold => {
                            if (percentage <= threshold.percentage) {
                                item.style.backgroundColor = threshold.color;
                            }
                        });
                    }
                }
            });
        }
        highlightItems();
    })();
    """
    encoded_script = script.replace(" ", "%20").replace("\n", "%20")
    url = f"javascript:{encoded_script}"
    web.open_new_tab(url)

## <!-- Script Run Function -----> ##
def run () :
    if __name__ == "__main__" :
        base ()
        check_admin ()
        input ("we did it!")
run ()
