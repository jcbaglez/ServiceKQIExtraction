from calibration import *


def getPos(side, filename):
    c = calibration()

    # pos  = c.getPositionsFromRecording("createGame")
    if side == "Server":
        places = ["Default", "Play", "Custom", "Rift","Training","ToolPractice", "Confirm", "Start", "Random", "Select", "CloseLol1", "CloseLol2",
                  "CloseLol3", "CloseLol4"]
    elif side == "Client":
        places = ["Setting",
                  "Resolution", "720p", "1080p", "1440p", "4K",
                  "FPS", "30FPS", "60FPS", '120FPS',
                  "Audio", "Stereo", "5.1", "7.1",
                  "VideoDecoder", "VideoDecoder_automatic", "Software_decoding", "Hardware_decoding",
                  "VideoCodec", "VideoCodec_automatic", "H.264", "H.265", "HDR",
                  "Return", "Sirio", "LoL",
                  '5 mbps', '10 mbps', '15 mbps', '20 mbps', '25 mbps', '30 mbps', '35 mbps', '40 mbps',
                  '45 mbps', '50 mbps', '75 mbps', '80 mbps', '90 mbps',
                  '100 mbps', '120 mbps', '125 mbps', '150 mbps', "QuitGame", "ConfirmQuitGame", "CloseMoonlight"]
    else:
        places = ["pruebafield"]
    pos = c.getPositionsFromList(places, filename)
    print(pos)

# print("--------------Client----------------")
# getPos('Client', "client_conf.json")
#getPos('Server','server.json')
print("------------Server 720p ------------")
getPos('Server','server.json')
# print("------------Server 1080p ------------")
# getPos('Server','coord_1080p.json')
# print("------------Server 1440p ------------")
# getPos('Server','coord_1440p.json')
# print("------------Server 4k ------------")
# getPos('Server','coord_4k.json')