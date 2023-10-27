import requests, json, os

from PIL import Image
from datetime import datetime

if not os.path.exists("icons"):
    os.makedirs("icons")

with open("repos.json", "r") as f:
    plugins = json.load(f)

official_repo = requests.get("https://kamori.goats.dev/Plugin/PluginMaster").json()

def get_asset_by_type(assets, mime_type):
    for asset in assets:
        if asset['content_type'] == mime_type:
            return asset
    raise Exception("Could not find asset with valid mime type")

def get_github_download_count(username, repo):
    releases = requests.get(f"https://api.github.com/repos/{username}/{repo}/releases?per_page=100").json()
    download_count = 0
    for release in releases:
        try:
            asset = get_asset_by_type(release['assets'], "application/zip")
            download_count += asset['download_count']
        except:
            pass
    return download_count

def get_official_download_count(internal_name):
    for plugin in official_repo:
        if plugin['InternalName'] == internal_name:
            return plugin['DownloadCount']
    return 0

unofficial_icon = Image.open("unofficial.png").convert("RGBA")
def create_icon(icon_url, internal_name, is_unofficial):
    with Image.open(requests.get(icon_url, stream=True).raw) as base_icon:
        icon = base_icon.convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS)
        if is_unofficial:
            icon.alpha_composite(unofficial_icon)
        icon.save(f"icons/{internal_name}.png")
    return f"https://raw.githubusercontent.com/WorkingRobot/MyDalamudPlugins/main/icons/{internal_name}.png"

plogons = []
good_plogons = []

for plugin in plugins:
    release_info = requests.get(f"https://api.github.com/repos/{plugin['username']}/{plugin['repo']}/releases/latest").json()

    release_timestamp = int(datetime.fromisoformat(release_info['published_at'].replace('Z','+00:00')).timestamp())
    zip_asset = get_asset_by_type(release_info['assets'], "application/zip")
    config_asset = get_asset_by_type(release_info['assets'], "application/json")

    zip_download_url = zip_asset['browser_download_url']
    config_data = requests.get(config_asset['browser_download_url']).json()

    download_count = get_github_download_count(plugin['username'], plugin['repo'])
    if plugin.get('isOfficial'):
        download_count += get_official_download_count(config_data['InternalName'])

    config_data['IsHide'] = False
    config_data['IsTestingExclusive'] = False
    config_data['LastUpdate'] = release_timestamp
    config_data['DownloadCount'] = download_count
    config_data['DownloadLinkInstall'] = zip_download_url
    config_data['DownloadLinkUpdate'] = zip_download_url
    config_data['DownloadLinkTesting'] = zip_download_url
    icon_url = config_data['IconUrl']
    config_data['IconUrl'] = create_icon(icon_url, config_data['InternalName'], False)

    plogons.append(config_data.copy())

    if plugin.get('isOfficial'):
        config_data['Punchline'] = f"Unofficial/uncertified build of {config_data['Name']}. {config_data['Punchline']}"
        config_data['Name'] += ' (Unofficial)'
        config_data['InternalName'] += 'Unofficial'
        config_data['IconUrl'] = create_icon(icon_url, config_data['InternalName'], True)
        good_plogons.append(config_data.copy())

with open('plogon.json', 'w') as f:
    json.dump(plogons, f, indent=4)

with open('goodplogon.json', 'w') as f:
    json.dump(good_plogons, f, indent=4)