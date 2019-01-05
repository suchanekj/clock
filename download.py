import wget


def autorun():
    wget.download("http://trin-hosts.trin.cam.ac.uk/clock/data/2008/", "newdownload")
