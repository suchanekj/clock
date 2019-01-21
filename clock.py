import os
import shutil
import numpy as np
import time
from datetime import datetime
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# import download
from config import *

data = {}
loadedDataStart = START_TIME


def load_downloads(memory=180):
    global loadedDataStart
    global data
    loadedDataStart = START_TIME
    endTimestamp = int(time.time() + 1e6)
    for i in DATA_FORMAT:
        data[i] = np.empty(int((endTimestamp - START_TIME) / TIME_STEP))
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
                                timestamp = int(round((line[0] - START_TIME) / TIME_STEP))
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
    for i in DATA_FORMAT[1:]:
        age[i] = 0
        value[i] = 0
    for i in range(len(data[DATA_FORMAT[0]])):
        for j in DATA_FORMAT[1:]:
            if not np.isnan(data[j][i]):
                age[j] = memory
                value[j] = data[j][i]
            elif age[j] > 0:
                data[j][i] = value[j]
            age[j] -= 1

    for j in DATA_FORMAT[1:]:
        if len(j.split("_")) != 2:
            continue
        if j.split("_")[1] == "int":
            data[j][0] = data[j.split("_")[0]][0]
    for i in range(1, len(data[DATA_FORMAT[0]])):
        for j in DATA_FORMAT[1:]:
            if len(j.split("_")) != 2:
                continue
            if j.split("_")[1] == "int":
                if np.isnan(data[j.split("_")[0]][i]) and not np.isnan(data[j][i-1]):
                    data[j][i] = INTEGRATION_FACTOR * data[j][i-1]
                elif not np.isnan(data[j.split("_")[0]][i]) and np.isnan(data[j][i-1]):
                    data[j][i] = data[j.split("_")[0]][i]
                elif not np.isnan(data[j.split("_")[0]][i]) and not np.isnan(data[j][i-1]):
                    data[j][i] = data[j.split("_")[0]][i] + INTEGRATION_FACTOR * data[j][i-1]

    try:
        for i in range(1, len(driftHistory) - 1):
            try:
                if datetime.fromtimestamp(int(driftHistory[i][0])).strftime('%Y-%m-%d') !=\
                   datetime.fromtimestamp(int(driftHistory[i + 1][0])).strftime('%Y-%m-%d'):
                    continue
                timestamp1 = int(round((int(driftHistory[i + 1][0]) - 3600 - START_TIME) / TIME_STEP))
                timestamp2 = int(round((int(driftHistory[i][0]) + 7200 - START_TIME) / TIME_STEP))
                for j in range(timestamp1, timestamp2):
                    for a in DATA_FORMAT[1:]:
                        data[a][j] = np.nan
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
        pass
    for i in range(len(data[DATA_FORMAT[0]])):
        timestamp = i * TIME_STEP + START_TIME
        if i == 0 or datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') !=\
                datetime.fromtimestamp(timestamp - TIME_STEP).strftime('%Y-%m-%d'):
            if i != 0: f.close()
            f = open("data/" + datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') + ".txt", "w+")
        f.write(str(timestamp) + " ")
        for col in range(len(DATA_FORMAT)):
            f.write(str(data[DATA_FORMAT[col]][i]))
            if col != len(DATA_FORMAT) - 1:
                f.write(" ")
        f.write("\n")


def func(X, *arg):
    return sum([a * b for a, b in zip(X, arg[1:])]) + arg[0]


def denseGraph(start, end, plot=True):
    start = int(start)
    end = int(end)
    for i in DATA_FORMAT:
        data[i] = np.empty(int((end - start) / TIME_STEP))

    j = 0
    for i in range(start, end, TIME_STEP):
        if i == start or datetime.fromtimestamp(i).strftime('%Y-%m-%d') !=\
                datetime.fromtimestamp(i - TIME_STEP).strftime('%Y-%m-%d'):
            f = open("data/" + datetime.fromtimestamp(i).strftime('%Y-%m-%d') + ".txt", "r")
            f = f.readlines()
            a = 0
        f[a] = list(map(float, f[a].split(' ')))

        skip = False
        for b in range(len(f[a]) - 1):
            data[DATA_FORMAT[b]][j] = f[a][b + 1]
            if np.isnan(f[a][b + 1]):
                skip = True
        a += 1
        if skip:
            continue
        j += 1

    for a in DATA_FORMAT:
        data[a] = data[a][0:j]


    X = tuple(np.array([a(data, i) for i in range(len(data[DATA_FORMAT[0]]) - 1)]) for a in FITABLE)
    Y = np.array([VALUE(data, i) for i in range(len(data[DATA_FORMAT[0]]) - 1)])
    p0 = np.zeros(len(X) + 1)
    p1, pcov = curve_fit(func, X, Y, p0)

    # Remove readings caused by systematic error
    pstd = np.sqrt(np.diag(pcov))
    std = sum(pstd)  # probably wrong !!!!!!!!!!!!!!!!!!!!!!!!!
    print(std)
    Z = np.transpose(np.array(X))
    to_delete = []
    print(p1)
    for i in range(len(Y)):
        predicted = func(Z[i], *p1)
        # print(Z[i], predicted, Y[i])
        if abs(predicted - Y[i]) > std * N_SIGMA_CUTOFF / 100: # !!!!!!!!!!!!!!!!!!!!
            to_delete.append(i)
    Y = np.delete(Y, to_delete)
    X = list(X)
    for i in range(len(X)):
        X[i] = np.delete(X[i], to_delete)
    X = tuple(X)
    # print(X)
    print(len(to_delete))
    popt = curve_fit(func, X, Y, p0)[0]

    # print(Y)
    minX = tuple(np.min(a) for a in X)
    maxX = tuple(np.max(a) for a in X)
    minY = np.min(Y)
    maxY = np.max(Y)
    print("zero value: " + str(popt[0]))
    for i in range(len(FITABLE_NAMES)):
        print(FITABLE_NAMES[i] + ": " + str(popt[i + 1]))
        plt.plot([minX[i], maxX[i]], [(minY + maxY) / 2 - (maxX[i] - minX[i]) / 2 * popt[1 + i],
                                      (minY + maxY) / 2 + (maxX[i] - minX[i]) / 2 * popt[1 + i]],
                 'g--', label = 'fit: a=%5.3f' % popt[1 + i])
        plt.plot(X[i], Y, 'bx', label = 'data')
        plt.show()
        plt.clf()


# download.autorun()
# load_downloads()
denseGraph(1532822400, 1532822400 + 3600 * 24 * 1) # 2018-07-29
