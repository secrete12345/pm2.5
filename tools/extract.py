import ijson

with open("stations.json", "rb") as f:
    for station in ijson.items(f, "stations.item"):
        area = station.get("areaTH")
        if area:
            print(area)