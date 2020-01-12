import re


def parse_line(line):
    desc = re.findall("/\\*.*\\*/", line)
    desc = desc[0].strip("*/ ")
    line = re.sub("/\\*.*\\*/", "", line)
    line = re.sub(" +", " ", line)
    line = line.strip().split(" ")
    start = int(line[0].strip("@"))
    name = line[1]
    width = int(line[2].strip(".$"))
    print("{: <92} {: >4} | {: >2} | {}".format(desc, start, width, name))

    return (start, width, name, desc)


def get_dicio(path):
    dicio = {
        "name": [],
        "start": [],
        "width": [],
        "desc": [],
    }
    with open(path, "r") as f:
        for line in f:
            if line.startswith("@"):
                start, width, name, desc = parse_line(line)
                dicio["name"].append(name)
                dicio["start"].append(start)
                dicio["width"].append(width)
                dicio["desc"].append(desc)

    return dicio
