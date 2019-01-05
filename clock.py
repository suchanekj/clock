# Ideas for joining
# 1) just average of slopes
# 2) find intercept for interval, then add another data value for intercepts, do regression overall
# http://faculty.franklin.uga.edu/amandal/sites/faculty.franklin.uga.edu.amandal/files/Effective_Statistical_Methods_for_Big_Data_Analytics.pdf

import os
import shutil
import numpy as np
import time
from datetime import datetime
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# import download
import config

data = {}
loadedDataStart = config.startTime


def load_downloads(memory=180):
    global loadedDataStart
    global data
    loadedDataStart = config.startTime
    endTimestamp = int(time.time() + 1e6)
    for i in config.dataFormat:
        data[i] = np.empty(int((endTimestamp - config.startTime) / config.timeStep))
        data[i][:] = np.nan
    x = os.walk("downloads")
    for i in x:
        # print(i)
        for j in i[2]:
            if j[-1] == 't' and j[-2] == 'x':
                try:
                    # print(".")
                    # shutil.copyfile(i[0] + "\\" + j, "downloads\\" + j)
                    f = open(i[0] + "\\" + j, "r")
                    f = f.readlines()
                    name = j.split("20")[0]
                    print(j)
                    if j == "drift-history.txt":
                        for a in range(len(f)):
                            f[a] = f[a].split(' ')
                        driftHistory = f
                    elif len(j.split("20")) > 1:
                        for a in range(len(f)):
                            f[a] = list(map(float, f[a].split(' ')))
                        for line in f:
                            try:
                                timestamp = int(round((line[0] - config.startTime) / config.timeStep))
                                if timestamp < 0:
                                    continue
                                if (name == "clock" or name == "clockdata"):
                                    data["drift"][timestamp] = line[1]
                                    data["amplitude"][timestamp] = line[2]
                                elif (name == "sunshine"):
                                    data["sunshine"][timestamp] = line[1]
                                elif (name == "tilt"):
                                    data["tilt"][timestamp] = line[1]
                                elif (name == "bubble"):
                                    data["bubble0b"][timestamp] = line[1]
                                    data["bubble0t"][timestamp] = line[2]
                                elif (name == "twist"):
                                    data["twist"][timestamp] = line[1]
                                    data["twistphase"][timestamp] = line[2]
                                elif (name == "temphum"):
                                    data["outsidetemp"][timestamp] = line[1]
                                    data["outsidehum"][timestamp] = line[2]
                                elif (name == "weather"):
                                    data["airtemp"][timestamp] = line[1]
                                    data["humidity"][timestamp] = line[2]
                                    data["pressure"][timestamp] = line[3]
                                elif (name == "temp"):
                                    data["temp0"][timestamp] = line[1]
                                    data["temp1"][timestamp] = line[2]
                                    data["temp2"][timestamp] = line[3]
                                    data["temp3"][timestamp] = line[4]
                                    data["temp4"][timestamp] = line[5]
                                    data["temp5"][timestamp] = line[6]
                                    data["temp6"][timestamp] = line[7]
                            except Exception as e:
                                print(e)
                                pass
                    else:
                        print(j)
                except Exception as e:
                    print(e)
                    pass
    value = {}
    age = {}
    for i in config.dataFormat[1:]:
        age[i] = 0
        value[i] = 0
    for i in range(len(data[config.dataFormat[0]])):
        for j in config.dataFormat[1:]:
            if not np.isnan(data[j][i]):
                age[j] = memory
                value[j] = data[j][i]
            elif age[j] > 0:
                data[j][i] = value[j]
            age[j] -= 1

    for j in config.dataFormat[1:]:
        if len(j.split("_")) != 2:
            continue
        if j.split("_")[1] == "int":
            data[j][0] = data[j.split("_")[0]][0]
    for i in range(1, len(data[config.dataFormat[0]])):
        for j in config.dataFormat[1:]:
            if len(j.split("_")) != 2:
                continue
            if j.split("_")[1] == "int":
                if np.isnan(data[j.split("_")[0]][i]) and not np.isnan(data[j][i-1]):
                    data[j][i] = config.integrationFactor * data[j][i-1]
                elif not np.isnan(data[j.split("_")[0]][i]) and np.isnan(data[j][i-1]):
                    data[j][i] = data[j.split("_")[0]][i]
                elif not np.isnan(data[j.split("_")[0]][i]) and not np.isnan(data[j][i-1]):
                    data[j][i] = data[j.split("_")[0]][i] + config.integrationFactor * data[j][i-1]

    try:
        for i in range(1, len(driftHistory) - 1):
            try:
                if datetime.fromtimestamp(int(driftHistory[i][0])).strftime('%Y-%m-%d') !=\
                   datetime.fromtimestamp(int(driftHistory[i + 1][0])).strftime('%Y-%m-%d'):
                    continue
                timestamp1 = int(round((int(driftHistory[i + 1][0]) - 3600 - config.startTime) / config.timeStep))
                timestamp2 = int(round((int(driftHistory[i][0]) + 7200 - config.startTime) / config.timeStep))
                for j in range(timestamp1, timestamp2):
                    for a in config.dataFormat[1:]:
                        data[a][j] = np.nan
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
        pass
    for i in range(len(data[config.dataFormat[0]])):
        timestamp = i * config.timeStep + config.startTime
        if i == 0 or datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') !=\
                datetime.fromtimestamp(timestamp - config.timeStep).strftime('%Y-%m-%d'):
            if i != 0: f.close()
            f = open("data/" + datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') + ".txt", "w+")
        f.write(str(timestamp) + " ")
        for col in range(len(config.dataFormat)):
            f.write(str(data[config.dataFormat[col]][i]))
            if col != len(config.dataFormat) - 1:
                f.write(" ")
        f.write("\n")


def func(X, *arg):
    return sum([a * b for a, b in zip(X, arg[1:])]) + arg[0]


def denseGraph(start, end, plot=True):
    start = int(start)
    end = int(end)
    for i in config.dataFormat:
        data[i] = np.empty(int((end - start) / config.timeStep))

    j = 0
    for i in range(start, end, config.timeStep):
        if i == start or datetime.fromtimestamp(i).strftime('%Y-%m-%d') !=\
                datetime.fromtimestamp(i - config.timeStep).strftime('%Y-%m-%d'):
            f = open("data/" + datetime.fromtimestamp(i).strftime('%Y-%m-%d') + ".txt", "r")
            f = f.readlines()
            a = 0
        f[a] = list(map(float, f[a].split(' ')))

        skip = False
        for b in range(len(f[a]) - 1):
            data[config.dataFormat[b]][j] = f[a][b + 1]
            if np.isnan(f[a][b + 1]):
                skip = True
        a += 1
        if skip:
            continue
        j += 1

    for a in config.dataFormat:
        data[a] = data[a][0:j]

    X = tuple(np.array([a(data, i) for i in range(len(data[config.dataFormat[0]]) - 1)]) for a in config.fitable)
    minX = tuple(np.min(a) for a in X)
    maxX = tuple(np.max(a) for a in X)
    Y = np.array([config.value(data, i) for i in range(len(data[config.dataFormat[0]]) - 1)])
    minY = np.min(Y)
    maxY = np.max(Y)
    p0 = np.zeros(len(X) + 1)
    p1 = curve_fit(func, X, Y, p0)[0]

    print(Y)
    print("zero value: " + str(p1[0]))
    for i in range(len(config.fitableNames) - 10):
        print(config.fitableNames[i] + ": " + str(p1[i + 1]))
        plt.plot([minX[i], maxX[i]], [(minY + maxY) / 2 - (maxX[i] - minX[i]) / 2 * p1[1 + i],
                                      (minY + maxY) / 2 + (maxX[i] - minX[i]) / 2 * p1[1 + i]],
                 'g--', label = 'fit: a=%5.3f' % p1[1 + i])
        plt.plot(X[i], Y, 'bx', label = 'data')
        plt.show()
        plt.clf()


# download.autorun()
# load_downloads()
denseGraph(1532822400, 1532822400 + 3600 * 24 * 0.5) # 2018-07-29
