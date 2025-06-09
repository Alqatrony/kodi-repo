import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
import requests

addon = xbmcaddon.Addon()
api_url = addon.getSetting("api_url")
user_id = addon.getSetting("user_id")
auth_token = addon.getSetting("auth_token")

def search(item):
    headers = {
        'x-user-id': user_id,
        'x-auth-token': auth_token
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        subs = response.json()
        results = []
        for sub in subs:
            results.append({
                'label': sub.get('title', 'Subtitle'),
                'file': sub.get('file_url')
            })
        return results

    except Exception as e:
        xbmc.log(f"[SubdlBridge] Error: {str(e)}", xbmc.LOGERROR)
        return []

def run():
    results = search({})
    for result in results:
        list_item = xbmcgui.ListItem(label=result['label'])
        xbmcplugin.addDirectoryItem(handle=0, url=result['file'], listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(0)

if __name__ == '__main__':
    run()