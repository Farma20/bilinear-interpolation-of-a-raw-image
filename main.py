import numpy as np
import cv2

#преобразование raw файла в массив с интенсивностью света для дальнейшей работы с ним
def openRaw(path, bpp, width, height):
    a = np.fromfile(open(path), np.dtype(bpp), width * height).reshape(height, width)
    print(a.shape)
    return a

#вычитание уровня черного
def applyBLC(raw, blcR, blcGr, blcGb, blcB):
    correctedRaw = np.zeros(raw.shape, dtype=np.uint32)
    correctedRaw[0::2, 1::2] = raw[0::2, 1::2] - blcGr
    correctedRaw[0::2, 0::2] = raw[0::2, 0::2] - blcR
    correctedRaw[1::2, 0::2] = raw[1::2, 0::2] - blcGb
    correctedRaw[1::2, 1::2] = raw[1::2, 1::2] - blcB
    correctedRaw[correctedRaw < 0] = 0
    return correctedRaw.astype('u2')

#разбиваем иходный массив с интесивностями цвета на три цветовых канала(RGB), ориентируясь на матрицу Байера
def Decomposition(ravIMG):
    rChn = np.zeros(ravIMG.shape, dtype=np.uint32)
    rChn[1::2, 1::2] = ravIMG[1::2, 1::2]

    gChn = np.zeros(ravIMG.shape, dtype=np.uint32)
    gChn[0::2, 1::2] = ravIMG[0::2, 1::2]
    gChn[1::2, 0::2] = ravIMG[1::2, 0::2]

    bChn = np.zeros(ravIMG.shape, dtype=np.uint32)
    bChn[0::2, 0::2] = ravIMG[0::2, 0::2]

    return rChn.astype('u2'), gChn.astype('u2'), bChn.astype('u2')

#производим билинейную интерполяцию (получаем значения интенсивности света RGB цветов там, где их не было)
def BiInterpolation(channel, color):
    if color == 'r':
        for i in range(len(channel)):
            if i % 2 != 0:
                for j in range(0, len(channel[i]), 2):
                    channel = Сonvolution(channel, i, j)
            else:
                for j in range(len(channel[i])):
                    channel = Сonvolution(channel, i, j)

    if color == 'g':
        for i in range(len(channel)):
            if i % 2 != 0:
                for j in range(1, len(channel[i]), 2):
                    channel = Сonvolution(channel, i, j)
            else:
                for j in range(0, len(channel[i]), 2):
                    channel = Сonvolution(channel, i, j)

    if color == 'b':
        for i in range(len(channel)):
            if i % 2 != 0:
                for j in range(len(channel[i])):
                    channel = Сonvolution(channel, i, j)
            else:
                for j in range(1, len(channel[i]), 2):
                    channel = Сonvolution(channel, i, j)

    return channel

#Операция свертки, испоьзуемая в билинейной интерполяции для получения нового значения света
def Сonvolution(channel, i, j):
    count = 0
    if i - 1 < 0:
        up = 0
    else:
        up = channel[i - 1][j]
        count += 1

    if i + 1 == len(channel):
        down = 0
    else:
        down = channel[i+1][j]
        count += 1

    if j - 1 < 0:
        left = 0
    else:
        left = channel[i][j - 1]
        count += 1

    if j + 1 == len(channel[i]):
        right = 0
    else:
        right = channel[i][j + 1]
        count += 1
    if count == 0:
        count = 1
    channel[i][j] = (up + down + left + right)/count

    return channel

# Соединяем 3 цветовых канала в один трехмерный массив
def GetImgColor(rChn, gChn, bChn):
    imgColor = np.zeros((len(rChn), len(rChn[0]), 3), dtype=np.uint32)
    for i in range(len(imgColor)):
        for j in range(len(imgColor[i])):
            imgColor[i][j][0] = rChn[i][j]
            imgColor[i][j][1] = gChn[i][j]
            imgColor[i][j][2] = bChn[i][j]

    return imgColor.astype('u2')

#Функция восстановления цвета
def Demosaic(ravIMG):
    redChannel, greenChannel, blueChannel = Decomposition(ravIMG)
    redChannel = BiInterpolation(redChannel, 'r')
    greenChannel = BiInterpolation(greenChannel, 'g')
    blueChannel = BiInterpolation(blueChannel, 'b')

    imgColor = GetImgColor(redChannel, greenChannel, blueChannel)

    print(imgColor.shape)
    return imgColor


def main():
    imgWidth = 2592
    imgHeight = 1944
    scaleTo = (1280, 800)
    raw = openRaw('sfr.2592x1944p5184b14.raw', 'u2', imgWidth, imgHeight)
    raw = applyBLC(raw, 800, 800, 800, 800)
    rawDemosaic = np.copy(raw)
    rawDemosaic = Demosaic(rawDemosaic)
    rawDemosaic = cv2.resize(rawDemosaic, scaleTo, interpolation=cv2.INTER_LINEAR)

    cv2.imshow('Original', rawDemosaic << 2)

    cv2.waitKey(0)


main()

