import csv

RELEASE_DATA = {}

with open("/etc/os-release") as f:
    reader = csv.reader(f, delimiter="=")
    for row in reader:
        if row:
            RELEASE_DATA[row[0]] = row[1]

if RELEASE_DATA["ID"] in ["debian", "raspbian"]:
    with open("/etc/debian_version") as f:
        DEBIAN_VERSION = f.readline().strip()
    major_version = DEBIAN_VERSION.split(".")[0]
    version_split = RELEASE_DATA["VERSION"].split(" ", maxsplit=1)
    if version_split[0] == major_version:
        # Just major version shown, replace it with the full version
        RELEASE_DATA["VERSION"] = " ".join([DEBIAN_VERSION] + version_split[1:])

print("{} {}".format(RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"]))