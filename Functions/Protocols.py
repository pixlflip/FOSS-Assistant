# file for any and all protocols used
import os
import datetime

# import pytube
# from pytube import YouTube
currentDirectory = os.getcwd()


# Burn it all to the ground. Leave nothing
def vex(path, passes=7):
    with open(path, "ba+") as delfile:
        length = delfile.tell()
        for i in range(passes):
            delfile.seek(0)
            delfile.write(os.urandom(length))
    os.remove(path)


# Returns String array of Byte array provided
def byteToStr(bytesToConvert):
    # Format data into str from byte
    convertedBytes = bytesToConvert.decode()
    # split message into parts
    request = convertedBytes.split(':')
    part1 = request[0].split(',')
    part2 = request[1].split(',')
    part3 = request[2].split(',')
    # return multidimensional array
    return part1, part2, part3


def loadStartupParameters():
    # check/verify all needed parameters exist
    if not os.path.isfile('/Functions/Program/startup.txt'):
        print("Failed Startup. Initializing Setup Protocol")
        firstTimeSetup()  # run first time setup

    # once verified go ahead and startup
    file = open(currentDirectory + '/Functions/Program/startup.txt')
    returnList = []
    for line in file:
        returnList.append(line)
    return returnList


def debugLog(msg):
    file = open(currentDirectory + '/Functions/Program/log.txt', "a")  # append mode
    x = datetime.datetime.now()
    xy = x.__str__().replace(" ", "")
    file.write("\n" + xy + "," + msg)
    file.close()


""" Eventually this with tie in to a neural network to make it easier. This method just makes it easier to skip the step
of speech intent if a command already has been correctly assigned from client based application """


# Finds intent of query and returns it as a numeric value + rest of array
def findIntentFromText(messageArray):
    command = messageArray[0]
    # massive if statement for now to gather intent. Don't touch the rest of the array in this function
    if command.__contains__("send") and command.__contains__("email"):
        # send email command code 1
        return 1

    elif command.__contains__("wiki"):
        # wikipedia search command code 2
        return 2

    elif command.__contains__("journal") and command.__contains__("new") and command.__contains__("entry"):
        # add entry to Journal command code 3
        return 3

    elif command.__contains__("bomb"):
        # this will do something dramatic eventually. Code 4
        return 4

    elif command.__contains__("youtube") and command.__contains__("download"):
        # download youtube link to memory. Code 5
        return 5

    elif command.__contains__("help"):
        return 6

    # ========================== MUSIC COMMANDS ==========================
    elif command.__contains__("rickroll"):
        # rickroll. A classic!
        return 7

    elif command.__contains__("music") and command.__contains__("all"):
        # play all music in no order
        return 8

    elif command.__contains__("backup") and command.__contains__("all"):
        # backup
        return 9

    elif command.__contains__("music") and command.__contains__("artist"):
        # play all music from one artist
        return 10

    elif command.__contains__("music") and command.__contains__("playlist"):
        # play playlist
        return 12

    else:
        return 0


# Downloads links provided to Youtube in highest possible resolution... at least in theory
"""def youtubeVideoDownload(links):
    for link in links:
        yt = pytube.YouTube(link)
        stream = yt.streams.first()
        stream.download()"""


# setup entire smart assistant
def firstTimeSetup():
    print("================ Best Enterprise Assistant Server Setup ================")
    startupParams = []
    profileParams = []
    # get info from user
    startupParams.append(input("= Please Give me a Name: "))
    startupParams.append(input("= Enter the full directory path to the folder you keep Music in: "))
    startupParams.append(input("= Enter the full directory path to the folder you keep Video in: "))
    startupParams.append(input("= Enter the full directory path to the folder you keep your Journal in: "))
    print("=========================================================================")
    print("Setup of base functions complete. Enter info for admin profile please. ")
    profileParams.append(input("= Enter your First Name: ").lower().replace(' ', ''))
    profileParams.append(input("= Enter your Password: "))
    profileParams.append(input("= Enter your Email Address: "))
    profileParams.append(input("= Enter your Password for Email Above: "))
    profileParams.append(input("= Enter this device's classification (mobile, work): "))

    # create startup file
    open('/Functions/Program/startup.txt', 'x')
    with open('/Functions/Program/startup.txt', 'w') as f:
        for line in startupParams:
            f.write(line)
    # create startup file
    open('/Functions/Profiles/' + profileParams[0], 'x')
    with open('/Functions/Profiles/' + profileParams[0], 'w') as f:
        for line in profileParams:
            f.write(line)