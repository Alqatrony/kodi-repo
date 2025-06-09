#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
from urllib.request import Request, urlopen

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

__cwd__ = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
__profile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__resource__ = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'lib'))
__temp__ = xbmcvfs.translatePath(os.path.join(__profile__, 'temp', ''))

sys.path.append(__resource__)

BASE_URL = "https://subdlbridge-api.onrender.com/api"

if not os.path.exists(__temp__):
    os.makedirs(__temp__)

def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log((u"### [%s] - %s" % (__scriptid__, msg)), level)

def get_auth_token():
    token = __addon__.getSetting('token')
    if not token:
        dialog = xbmcgui.Dialog()
        token = dialog.input('Enter Your SubdlBridge API Token', type=xbmcgui.INPUT_ALPHANUM)
        if token:
            __addon__.setSetting('token', token)
    return token

def get_user_id():
    uid = __addon__.getSetting('uid')
    if not uid:
        dialog = xbmcgui.Dialog()
        uid = dialog.input('Enter Your SubdlBridge User ID', type=xbmcgui.INPUT_ALPHANUM)
        if uid:
            __addon__.setSetting('uid', uid)
    return uid

def get_auth_headers():
    token = get_auth_token()
    uid = get_user_id()
    if not token or not uid:
        return None
    return {
        'x-auth-token': token,
        'x-user-id': uid
    }

def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = paramstring[1:]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

# HTTP GET JSON
def http_get_json(url, headers):
    req = Request(url, headers=headers)
    with urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

# HTTP GET Binary (for downloading subtitles)
def http_get_binary(url, headers):
    req = Request(url, headers=headers)
    with urlopen(req) as res:
        return res.read()

def fetch_subtitles():
    headers = get_auth_headers()
    if not headers:
        xbmcgui.Dialog().notification('SubdlBridge', 'Authentication credentials required', xbmcgui.NOTIFICATION_ERROR)
        return []
    try:
        return http_get_json(f"{BASE_URL}/subs", headers)
    except Exception as e:
        log(f"Failed to fetch subtitles: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('SubdlBridge', 'Failed to connect to API', xbmcgui.NOTIFICATION_ERROR)
        return []

def download_subtitle(subtitle_id):
    headers = get_auth_headers()
    if not headers:
        return None
    try:
        content = http_get_binary(f"{BASE_URL}/subs/{subtitle_id}/download", headers)
        subtitle_path = os.path.join(__temp__, f"{subtitle_id}.srt")
        with open(subtitle_path, 'wb') as f:
            f.write(content)
        return subtitle_path
    except Exception as e:
        log(f"Failed to download subtitle: {e}", xbmc.LOGERROR)
        return None
    
def download(subtitle_id):
    subtitle_path = download_subtitle(subtitle_id)
    if subtitle_path:
        subs = fetch_subtitles()
        sub = next((s for s in subs if s.get('id') == subtitle_id), None)
        title = sub.get('title', 'Subtitle') if sub else 'Subtitle'
        
        list_item = xbmcgui.ListItem(label=title)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=subtitle_path, listitem=list_item, isFolder=False)

LANG_MAP = {
    'arabic': 'ar',
    'german': 'de',
    'french': 'fr',
    'spanish': 'es',
    'italian': 'it',
    'english': 'en',
    'portuguese': 'pt',
    'russian': 'ru',
    'japanese': 'ja',
    'chinese': 'zh',
    'afrikaans': 'af',
    'albanian': 'sq',
    'amharic': 'am',
    'armenian': 'hy',
    'azerbaijani': 'az',
    'basque': 'eu',
    'belarusian': 'be',
    'bengali': 'bn',
    'bosnian': 'bs',
    'bulgarian': 'bg',
    'catalan': 'ca',
    'cebuano': 'ceb',
    'corsican': 'co',
    'croatian': 'hr',
    'czech': 'cs',
    'danish': 'da',
    'dutch': 'nl',
    'esperanto': 'eo',
    'estonian': 'et',
    'filipino': 'fil',  
    'finnish': 'fi',
    'frisian': 'fy',
    'galician': 'gl',
    'georgian': 'ka',
    'greek': 'el',
    'gujarati': 'gu',
    'haitian creole': 'ht',
    'hausa': 'ha',
    'hawaiian': 'haw',
    'hebrew': 'he',
    'hindi': 'hi',
    'hmong': 'hmn',
    'hungarian': 'hu',
    'icelandic': 'is',
    'igbo': 'ig',
    'indonesian': 'id',
    'irish': 'ga',
    'javanese': 'jv',
    'kannada': 'kn',
    'kazakh': 'kk',
    'khmer': 'km',
    'kinyarwanda': 'rw',
    'korean': 'ko',
    'kurdish (kurmanji)': 'ku',
    'kyrgyz': 'ky',
    'lao': 'lo',
    'latin': 'la',
    'latvian': 'lv',
    'lithuanian': 'lt',
    'luxembourgish': 'lb',
    'macedonian': 'mk',
    'malagasy': 'mg',
    'malay': 'ms',
    'malayalam': 'ml',
    'maltese': 'mt',
    'maori': 'mi',
    'marathi': 'mr',
    'mongolian': 'mn',
    'myanmar (burmese)': 'my',
    'nepali': 'ne',
    'norwegian': 'no',
    'odia (oriya)': 'or',
    'pashto': 'ps',
    'persian (farsi)': 'fa',
    'polish': 'pl',
    'punjabi (gurmukhi)': 'pa',
    'romanian': 'ro',
    'samoan': 'sm',
    'scottish gaelic': 'gd',
    'serbian': 'sr',
    'sesotho': 'st',
    'shona': 'sn',
    'sindhi': 'sd',
    'sinhala (sinhalese)': 'si',
    'slovak': 'sk',
    'slovenian': 'sl',
    'somali': 'so',
    'sundanese': 'su',
    'swahili': 'sw',
    'swedish': 'sv',
    'tajik': 'tg',
    'tamil': 'ta',
    'tatar': 'tt',
    'telugu': 'te',
    'thai': 'th',
    'tibetan': 'bo',
    'tigrinya': 'ti',
    'turkish': 'tr',
    'turkmen': 'tk',
    'ukrainian': 'uk',
    'urdu': 'ur',
    'uyghur': 'ug',
    'uzbek': 'uz',
    'vietnamese': 'vi',
    'welsh': 'cy',
    'xhosa': 'xh',
    'yiddish': 'yi',
    'yoruba': 'yo',
    'zulu': 'zu',
}

def search(item):
    subs = fetch_subtitles()
    for sub in subs:
        lang = sub.get('lang', 'Unknown')
        title = sub.get('title', 'Unknown')
        lang_code = LANG_MAP.get(lang.lower(), 'en')
        
        list_item = xbmcgui.ListItem(label=lang, label2=title)
        list_item.setArt({'icon': '0', 'thumb': lang_code})
        list_item.setProperty('sync', 'false')
        list_item.setProperty('hearing_imp', 'false')
        url = f"plugin://{__scriptid__}/?action=download&subtitle_id={sub['id']}"
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False)

def main():
    params = get_params()
    if params.get('action') == 'search':
        item = {
            'temp': False,
            'rar': False,
            'title': params.get('searchstring', ''),
            'tvshow': params.get('tvshow', ''),
            'year': params.get('year', ''),
            'season': params.get('season', ''),
            'episode': params.get('episode', ''),
        }
        search(item)
    elif params.get('action') == 'download':
        subtitle_id = params.get('subtitle_id', '')
        if subtitle_id:
            download(subtitle_id)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if __name__ == '__main__':
    main()