START_TIME = 1200000000
TIME_STEP = 30
INTEGRATION_FACTOR = 0.1 ** (1 / (24 * 3600 / TIME_STEP))
LAST_DAY_DOWNLOADED = "2018-12-04"
N_SIGMA_CUTOFF = 5

DATA_FORMAT = ["amplitude", "drift", "airtemp", "humidity", "pressure", "sunshine", "outsidetemp",
              "outsidehum", "temp0", "temp1", "temp2", "temp3", "temp4", "temp5", "temp6", "tilt", "twist",
              "twistphase", "bubble0b", "bubble0t", "sunshine_int", "airtemp_int", "humidity_int", "pressure_int"]

FITABLE = [
    lambda dat, i: dat["airtemp"][i],
    lambda dat, i: dat["humidity"][i],
    lambda dat, i: dat["pressure"][i],
    lambda dat, i: dat["sunshine"][i],
    lambda dat, i: dat["outsidetemp"][i],
    lambda dat, i: dat["outsidehum"][i],
    # lambda dat, i: dat["temp0"][i],
    # lambda dat, i: dat["temp1"][i],
    # lambda dat, i: dat["temp2"][i],
    # lambda dat, i: dat["temp3"][i],
    # lambda dat, i: dat["temp4"][i],
    # lambda dat, i: dat["temp5"][i],
    # lambda dat, i: dat["temp6"][i],
    # lambda dat, i: dat["sunshine_int"][i] * (1 - INTEGRATION_FACTOR),
    # lambda dat, i: dat["airtemp_int"][i] * (1 - INTEGRATION_FACTOR),
    # lambda dat, i: dat["pressure_int"][i] * (1 - INTEGRATION_FACTOR),
    # lambda dat, i: dat["humidity_int"][i] * (1 - INTEGRATION_FACTOR),
    lambda dat, i: (dat["airtemp"][i + 1] - dat["airtemp"][i]) / TIME_STEP,
    lambda dat, i: (dat["pressure"][i + 1] - dat["pressure"][i]) / TIME_STEP,
    lambda dat, i: (dat["humidity"][i + 1] - dat["humidity"][i]) / TIME_STEP
]

FITABLE_NAMES = [
    "airtemp",
    "humidity",
    "pressure",
    "sunshine",
    "outsidetemp",
    "outsidehum",
    # "temp0",
    # "temp1",
    # "temp2",
    # "temp3",
    # "temp4",
    # "temp5",
    # "temp6",
    # "sunshine_int",
    # "airtemp_int",
    # "humidity_int",
    # "pressure_int",
    "airtemp_d",
    "pressure_d",
    "humidity_d"
]

VALUE = lambda dat, i: (dat["drift"][i + 1] - dat["drift"][i]) * 24 * 3600 / TIME_STEP * 1000
