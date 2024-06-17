import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplcyberpunk
import requests

from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

since = relativedelta(months=1)
since = datetime.utcnow() - since - timedelta(days=1)
since = since.isoformat()[:19] + 'Z'

page = 1
data = {}
while True:
    print(f"Getting page {page}")
    j = requests.get("https://api.github.com/repos/WorkingRobot/MyDalamudPlugins/commits", params = {
            "path": "plogon.json",
            "per_page": 100,
            "page": page,
            "since": since
        }).json()
    if len(j) == 0:
        break
    for commit in j:
        date = datetime.fromisoformat(commit["commit"]["committer"]["date"][:-1]).date()
        if date in data:
            continue
        print(f"Getting commit {commit['sha']} for {date}")
        repo = requests.get(f"https://raw.githubusercontent.com/WorkingRobot/MyDalamudPlugins/{commit['sha']}/plogon.json").json()
        data[date] = repo
    page += 1

plugin_names = set()
for date, repo in data.items():
    for plugin in repo:
        plugin_names.add(plugin['InternalName'])
plugin_names = sorted(plugin_names)

plot_dates = []
plot_counts = []
yesterday_counts = None

for date, repo in sorted(data.items()):
    counts = [0] * len(plugin_names)
    for plugin in repo:
        counts[plugin_names.index(plugin['InternalName'])] = plugin['DownloadCount']
    if yesterday_counts is not None:
        new_counts = [a - b for a,b in zip(counts, yesterday_counts)]
        plot_dates.append(date)
        plot_counts.append(new_counts)
    yesterday_counts = counts

plt.style.use("cyberpunk")
plt.rcParams["font.family"] = "revert_back"
plt.rcParams["svg.hashsalt"] = "Graphs!"

fig, ax = plt.subplots(layout='constrained', figsize=(6,4))
locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
ax.plot(plot_dates, plot_counts, label=plugin_names)

ax.legend()
ax.set_title("Daily Download Count")

mplcyberpunk.add_underglow()

plt.savefig('downloads.svg', metadata={'Date': None})
