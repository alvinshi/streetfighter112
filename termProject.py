#15112 Term Project
#Xiang Shi
#xiangs1
#Section J

import math
import socket
import random
from _thread import *
################################################################
#Music Core Module(Copied and Adapted from http://jugad2.blogspot.in/2015/ ##
#############10/play-list-of-wav-files-with-pyaudio.html #################
################################################################
import pyaudio
import wave
import sys
import os.path
import time

CHUNK_SIZE = 1024

def play_wav(wav_filename, chunk_size=CHUNK_SIZE):
    '''
    Play (on the attached system sound device) the WAV file
    named wav_filename.
    '''

    try:
        print('Trying to play file ' + wav_filename)
        wf = wave.open(wav_filename, 'rb')
    except IOError as ioe:
        sys.stderr.write('IOError on file ' + wav_filename + '\n' + \
        str(ioe) + '. Skipping.\n')
        return
    except EOFError as eofe:
        sys.stderr.write('EOFError on file ' + wav_filename + '\n' + \
        str(eofe) + '. Skipping.\n')
        return

    # Instantiate PyAudio.
    p = pyaudio.PyAudio()

    # Open stream.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(chunk_size)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk_size)

    # Stop stream.
    stream.stop_stream()
    stream.close()

    # Close PyAudio.
    p.terminate()

################################################################
####################### Music Control #############################
################################################################
def musicPlayer():
    while True:
        play_wav("music/Retribution.wav")
#the music was taken from http://www.tannerhelland.com/music-directory/

################################################################
######################### Test Zone ##############################
################################################################
def testLine_intersect():
    print(line_intersect((5,0),(0,0),(2,-2),(3,2)))

def testAll():
    test = False
    if test == True:
        testLine_intersect()

################################################################
######################## Test Zone End ###########################
################################################################

################################################################
###################### General Helper Function ######################
################################################################
def almostEqual(a,b,epsilon = 10**(-5)):
    return abs(a-b) <= epsilon

def line_intersect(a,b,c,d):
    #To test whether two line segments intersect with each other
    #the switch is important!
    if(a[0] > b[0]):
        (a,b) = (b,a)
    if (c[0] > d[0]):
        (c,d) = (d,c)
    if (a[0] - b[0] == 0 or c[0] - d[0] == 0):
        return False
    m0 = (a[1] - b[1]) / (a[0] - b[0])
    m1 = (c[1] - d[1]) / (c[0] - d[0])
    n0 = a[1] - m0 * a[0]
    n1 = c[1] - m1 * c[0]
    if (almostEqual(m0, m1)) and (not almostEqual(m0, n0)):
        return False
    xIntersect = (n1 - n0) / (m0 - m1)
    if (xIntersect >= a[0] and xIntersect <= b[0] and
        xIntersect >= c[0] and xIntersect <= d[0]):
        return True
    return False

def reverseString(s):
    return s[::-1]
################################################################
######################### Battle Statistics ##########################
################################################################
class BattleStats(object):
    def __init__(self):
        self.moveHistory = []
        #primary data
        self.totalMove = 0
        self.moveCount = {}
        self.moveCount["jab"] = 0
        self.moveCount["kick"] = 0
        self.moveCount["bomb"] = 0
        self.moveCount["squat"] = 0
        self.moveCount["jump"] = 0
        self.moveCount["defend"] = 0
        #secondary data
        self.moveRate = 0
        self.attackPropensity = 0
        self.defendPropensity = 0
        self.squatPropensity = 0
        self.jumpPropensity = 0
        self.bombPropensity = 0
        self.kickPropensity = 0
        self.jabPropensity = 0

    def update(self):
        #used to update the stats for both players
        if len(self.moveHistory) != 0:
            move = self.moveHistory[-1]
            self.totalMove += 1
            if ("jab" in move):
                self.moveCount["jab"] = self.moveCount.get("jab", 0) + 1
            elif ("kick" in move):
                self.moveCount["kick"] = self.moveCount.get("kick", 0) + 1
            elif ("jump" in move):
                self.moveCount["jump"] = self.moveCount.get("jump", 0) + 1
            else:
                self.moveCount[move] = self.moveCount.get(move, 0) + 1
            self.defendPropensity = self.moveCount["defend"] / self.totalMove
            self.squatPropensity = self.moveCount["squat"] / self.totalMove
            self.jumpPropensity = self.moveCount["jump"] / self.totalMove
            self.attackPropensity = (1 - self.defendPropensity -
                                     self.squatPropensity - self.jumpPropensity)
            if self.attackPropensity != 0:
                self.bombPropensity = (self.moveCount["bomb"] / self.totalMove /
                                       self.attackPropensity)
                self.jabPropensity = (self.moveCount["jab"] / self.totalMove /
                                      self.attackPropensity)
                self.kickPropensity = (self.moveCount["kick"] / self.totalMove /
                                       self.attackPropensity)

################################################################
####################### Fighter Class Zone #########################
################################################################

class Fighter(object):
    def __init__(self, user, control, data, level = 1):
        self.hp = 200
        self.y = data.groundLevel
        self.control = control
        #control by the user or the pc
        self.user = user
        if user == "player1":
            self.dir = 1
        elif user == "player2":
            self.dir = -1
        #track the current pose of the fighter
        #the timer controls the animation
        self.pose = None
        self.motionTimer = 0
        self.jumpTimer = 0
        self.jumpPose = None
        #init the starting position
        if user == 'player1':
            self.x = data.player1_start_pos_x
        elif user == 'player2':
            self.x = data.player2_start_pos_x
        self.level = level #level of difficulty, only apply to ai
        #init ai parameters if the fighter is controlled by pc
        self.aiInit()

    def aiInit(self):
        if self.control == "pc":
            self.motionRate = (self.level * 20) #motions per second
            self.moveToMotionRatio_default = 2
            self.squatRatio_default = 30
            self.jumpRatio_default = 30
            self.forwardRatio_default = 20
            self.backwardRatio_default = 20
            self.attackToDefendRatio_default = 2
            self.bombPercentage_default = 30
            self.jabPercentage_default = 30
            self.kickPercentage_default = 40

    def updateMoveHistory(self, data, jump = False):
        #to update the battle statistics
        if self.user == "player1":
            if jump:
                data.player1.moveHistory.append(self.jumpPose)
            else:
                data.player1.moveHistory.append(self.pose)
            data.player1.update()
        elif self.user == "player2":
            if jump:
                data.player2.moveHistory.append(self.jumpPose)
            else:
                data.player2.moveHistory.append(self.pose)
            data.player2.update()

    def moveForward(self,data):
        self.pose = "walkForward"

    def moveBackward(self,data):
        self.pose = "walkBackward"

    def coordinatesCalculator(self, data):
        #calculate the body coordinates based on the length of different body parts and
        #the angle between
        self.assX = self.x
        self.assY = self.y - max((self.shankL * math.cos(self.leftShank_angle_Y) +
                              self.thighL * math.cos(self.leftThigh_angle_Y)) * data.cmToPixel,
                                 (self.shankL * math.cos(self.rightShank_angle_Y) +
                              self.thighL * math.cos(self.rightThigh_angle_Y)) * data.cmToPixel)

        self.leftAssX = self.assX + (self.assWidth // 2 * math.sin(self.spine_angle_X)) * data.cmToPixel
        self.leftAssY = self.assY + (self.assWidth // 2 * math.cos(self.spine_angle_X)) * data.cmToPixel

        self.rightAssX = self.assX - (self.assWidth // 2  * math.sin(self.spine_angle_X)) * data.cmToPixel
        self.rightAssY = self.assY - (self.assWidth // 2 * math.cos(self.spine_angle_X)) * data.cmToPixel

        self.leftKneeX = self.assX + (self.thighL * math.sin(self.leftThigh_angle_Y)) * data.cmToPixel
        self.leftKneeY = self.assY + (self.thighL * math.cos(self.leftThigh_angle_Y)) * data.cmToPixel

        self.rightKneeX = self.assX + (self.thighL * math.sin(self.rightThigh_angle_Y)) * data.cmToPixel
        self.rightKneeY = self.assY + (self.thighL * math.cos(self.rightThigh_angle_Y)) * data.cmToPixel
        self.leftFootX = self.leftKneeX + (self.shankL * math.sin(self.leftShank_angle_Y)) * data.cmToPixel
        self.leftFootY = self.leftKneeY + (self.shankL * math.cos(self.leftThigh_angle_Y)) * data.cmToPixel

        self.rightFootX = self.rightKneeX + (self.shankL * math.sin(self.rightShank_angle_Y)) * data.cmToPixel
        self.rightFootY = self.rightKneeY + (self.shankL * math.cos(self.rightThigh_angle_Y)) * data.cmToPixel

        self.upperBodyX = self.assX + (self.bodyL * math.sin(self.spine_angle_Y)) * data.cmToPixel
        self.upperBodyY = self.assY - (self.bodyL * math.cos(self.spine_angle_Y)) * data.cmToPixel

        self.leftShoulderX = self.upperBodyX + (self.shoulderWidth // 2 * math.sin(self.spine_angle_X)) * data.cmToPixel
        self.leftShoulderY = self.upperBodyY + (self.shoulderWidth // 2 * math.cos(self.spine_angle_X)) * data.cmToPixel

        self.rightShoulderX = self.upperBodyX - (self.shoulderWidth // 2 * math.sin(self.spine_angle_X)) * data.cmToPixel
        self.rightShoulderY = self.upperBodyY - (self.shoulderWidth // 2 * math.cos(self.spine_angle_X)) * data.cmToPixel

        self.headX = self.upperBodyX + (self.headD // 2 * math.sin(self.head_angle_Y)) * data.cmToPixel
        self.headY = self.upperBodyY - (self.headD // 2 * math.cos(self.head_angle_Y)) * data.cmToPixel

        self.leftElbowX = self.leftShoulderX + (self.upperArmL * math.sin(self.leftUpperArm_angle_Y)) * data.cmToPixel
        self.leftElbowY = self.leftShoulderY + (self.upperArmL * math.cos(self.leftUpperArm_angle_Y)) * data.cmToPixel                             

        self.rightElbowX = self.rightShoulderX + (self.upperArmL * math.sin(self.rightUpperArm_angle_Y)) * data.cmToPixel
        self.rightElbowY = self.rightShoulderY + (self.upperArmL * math.cos(self.rightUpperArm_angle_Y)) * data.cmToPixel 

        self.leftHandX = self.leftElbowX + (self.foreArmL * math.sin(self.leftForeArm_angle_Y) * abs(math.sin(self.leftForeArm_angle_Z))) * data.cmToPixel
        self.leftHandY = self.leftElbowY + (self.foreArmL * math.cos(self.leftForeArm_angle_Y) * abs(math.cos(self.leftForeArm_angle_Z))) * data.cmToPixel 

        self.rightHandX = self.rightElbowX + (self.foreArmL * math.sin(self.rightForeArm_angle_Y)) * data.cmToPixel
        self.rightHandY = self.rightElbowY + (self.foreArmL * math.cos(self.rightForeArm_angle_Y)) * data.cmToPixel 

    def die(self, data):
        data.dyingTimer = 80
        self.motionTimer = 80
        self.pose = "die"

    #update the angles based on the pose and trigger the coordinateCalculator
    #if it is an attack move, the hit function will be triggered
    def stand(self, data):
        self.pose = 'stand'
        self.head_angle_Y = 50 / 180 * math.pi * self.dir
        
        self.leftUpperArm_angle_Y = 5 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 5/180 * math.pi * self.dir
        self.spine_angle_X = 85/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 20 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 30 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = - 20 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 20 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def bomb(self, data):
        self.pose = 'bomb'
        self.head_angle_Y = 0 / 180 * math.pi * self.dir

        self.leftUpperArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 90 / 180 * math.pi * self.dir

        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 10/180 * math.pi * self.dir
        self.spine_angle_X = 80/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 80 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 0 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = - 40 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = -40 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def beingHit(self, data, strength):
        if self.x - strength * self.dir >= 0 and self.x - strength * self.dir <= data.width:
            self.x -= strength * self.dir
        self.pose = "beingHit"
        self.motionTimer = 5
        self.head_angle_Y = 0 / 180 * math.pi * self.dir
        
        self.leftUpperArm_angle_Y = 5 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = -20/180 * math.pi * self.dir
        self.spine_angle_X = 120/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 10 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 10 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = - 10 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 10 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def jump(self, data):
        self.jumpPose = 'jump'
        self.leftUpperArm_angle_Y = 40 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 40 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 0/180 * math.pi * self.dir
        self.spine_angle_X = 90/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 40 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = -60 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = 15 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 0 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def jumpForward(self, data):
        self.jumpPose = 'jumpForward'
        self.leftUpperArm_angle_Y = 40 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 40 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 0/180 * math.pi * self.dir
        self.spine_angle_X = 90/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 40 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = -60 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = -40 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 60 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def jumpBackward(self, data):
        self.jumpPose = 'jumpBackward'
        self.leftUpperArm_angle_Y = 40 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 40 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 0/180 * math.pi * self.dir
        self.spine_angle_X = 90/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 40 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = -60 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = -40 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 60 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def squat(self, data):
        self.pose = 'squat'
        self.leftThigh_angle_Y = 75 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = -75 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = 75 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = -75 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)

    def jabSquat(self, data):
        self.pose = 'jabSquat'
        self.leftThigh_angle_Y = 75 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = -75 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = 75 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = -75 / 180 * math.pi  * self.dir

        self.leftUpperArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 90 / 180 * math.pi * self.dir

        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 5/180 * math.pi * self.dir
        self.spine_angle_X = 85/180 * math.pi * self.dir
        self.coordinatesCalculator(data)
        self.hit(data, 'jab1')

    def jab1(self, data):
        self.pose = 'jab1'
        self.head_angle_Y = 50 / 180 * math.pi * self.dir

        self.leftUpperArm_angle_Y = 65 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 90 / 180 * math.pi * self.dir

        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 5/180 * math.pi * self.dir
        self.spine_angle_X = 85/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 20 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 30 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = - 20 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 20 / 180 * math.pi  * self.dir

        self.coordinatesCalculator(data)
        self.hit(data, 'jab1')

    def jab2(self, data):
        self.pose = 'jab2'
        self.head_angle_Y = 10 / 180 * math.pi * self.dir
        
        self.leftUpperArm_angle_Y = 5 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir

        self.rightUpperArm_angle_Y = 70 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = 10/180 * math.pi * self.dir
        self.spine_angle_X = 80/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 30 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 0 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = - 30 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = -30 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)
        #have to compensate the shoulder width
        self.hit(data, 'jab2')


    def kick(self, data):
        self.pose = 'kick'
        self.head_angle_Y = -40 / 180 * math.pi * self.dir

        self.leftUpperArm_angle_Y = 5 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = -50/180 * math.pi * self.dir
        self.spine_angle_X = 130/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 130 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 130 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 0 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)
        self.hit(data, 'kick')

    def kickSquat(self, data):
        self.pose = 'kickSquat'
        self.leftThigh_angle_Y = 75 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 75 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = 75 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = -75 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)
        self.hit(data, 'kick')

    def jumpKick(self, data):
        self.pose = 'jumpKick'
        self.head_angle_Y = -20 / 180 * math.pi * self.dir

        self.spine_angle_Y = -20/180 * math.pi * self.dir
        self.spine_angle_X = 100/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 70 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 70 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = -25 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 55 / 180 * math.pi  * self.dir

        self.spine_angle_Y = 0/180 * math.pi * self.dir
        self.spine_angle_X = 90/180 * math.pi * self.dir
        
        self.coordinatesCalculator(data)
        self.hit(data, 'kick')

    def defend(self, data):
        self.pose = 'defend'
        self.head_angle_Y = 20 / 180 * math.pi * self.dir
        
        self.leftUpperArm_angle_Y = 65 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = -170 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 0 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 65 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = -175 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = -10/180 * math.pi * self.dir
        self.spine_angle_X = 100/180 * math.pi * self.dir
        self.coordinatesCalculator(data)

    def draw(self, canvas, data):
        #This function draws the character according to the body coordinates
        #It is used to synchronise the coordinates with the graphics
        if self.dir == 1:
            #Head
            (x0,x1,y0,y1) = (self.headX - self.headD // 2 * data.cmToPixel,
                             self.headY - self.headD // 2 * data.cmToPixel,
                             self.headX + self.headD // 2 * data.cmToPixel,
                             self.headY + self.headD // 2 * data.cmToPixel)
            canvas.create_oval(x0,x1,y0,y1, fill ="black")
            #leftArm
            canvas.create_line(self.leftHandX, self.leftHandY, self.leftElbowX, self.leftElbowY, width = 1, fill = "grey")
            canvas.create_line(self.leftShoulderX, self.leftShoulderY, self.leftElbowX, self.leftElbowY, width = 1, fill = "red")

            #body
            canvas.create_polygon([(self.leftShoulderX, self.leftShoulderY),
                                   (self.rightShoulderX, self.rightShoulderY),
                                   (self.rightAssX, self.rightAssY),
                                   (self.leftAssX, self.leftAssY)])           

            #shank
            canvas.create_line(self.leftKneeX, self.leftKneeY, self.leftFootX, self.leftFootY, width = 1, fill = "grey")
            canvas.create_line(self.rightKneeX, self.rightKneeY, self.rightFootX, self.rightFootY, width = 1, fill = "grey")
            
            #thigh
            canvas.create_polygon([(self.assX, self.assY), (self.leftAssX, self.leftAssY),
                                   (self.leftKneeX + 12 * self.dir, self.leftKneeY), (self.leftKneeX - 12 * self.dir, self.leftKneeY)], fill = "red")
            canvas.create_polygon([(self.leftAssX, self.leftAssY), (self.rightAssX, self.rightAssY),
                                   (self.rightKneeX - 12 * self.dir, self.rightKneeY), (self.rightKneeX + 12 * self.dir, self.rightKneeY)], fill = "firebrick")
            
            #rightArm
            canvas.create_line(self.rightHandX, self.rightHandY, self.rightElbowX, self.rightElbowY, width = 1, fill = "grey")
            canvas.create_line(self.rightShoulderX, self.rightShoulderY, self.rightElbowX, self.rightElbowY, width = 1, fill = "firebrick")
        else:
            #rightArm
            canvas.create_line(self.rightHandX, self.rightHandY, self.rightElbowX, self.rightElbowY, width = 1, fill = "grey")
            canvas.create_line(self.rightShoulderX, self.rightShoulderY, self.rightElbowX, self.rightElbowY, width = 1, fill = "firebrick")

            #Head
            (x0,x1,y0,y1) = (self.headX - self.headD // 2 * data.cmToPixel,
                             self.headY - self.headD // 2 * data.cmToPixel,
                             self.headX + self.headD // 2 * data.cmToPixel,
                             self.headY + self.headD // 2 * data.cmToPixel)
            canvas.create_oval(x0,x1,y0,y1, fill ="black")
            
            #body
            canvas.create_polygon([(self.leftShoulderX, self.leftShoulderY),
                                   (self.rightShoulderX, self.rightShoulderY),
                                   (self.rightAssX, self.rightAssY),
                                   (self.leftAssX, self.leftAssY)])

            #leftArm
            canvas.create_line(self.leftHandX, self.leftHandY, self.leftElbowX, self.leftElbowY, width = 1, fill = "grey")
            canvas.create_line(self.leftShoulderX, self.leftShoulderY, self.leftElbowX, self.leftElbowY, width = 1, fill = "red")


            #shank
            canvas.create_line(self.leftKneeX, self.leftKneeY, self.leftFootX, self.leftFootY, width = 1, fill = "grey")
            canvas.create_line(self.rightKneeX, self.rightKneeY, self.rightFootX, self.rightFootY, width = 1, fill = "grey")
            
            #thigh
            canvas.create_polygon([(self.leftAssX, self.leftAssY), (self.rightAssX, self.rightAssY),
                                   (self.rightKneeX - 12 * self.dir, self.rightKneeY), (self.rightKneeX + 12 * self.dir, self.rightKneeY)], fill = "firebrick")
            canvas.create_polygon([(self.rightAssX, self.rightAssY), (self.leftAssX, self.leftAssY),
                                   (self.leftKneeX + 12 * self.dir, self.leftKneeY), (self.leftKneeX - 12 * self.dir, self.leftKneeY)], fill = "red")

    def drawHPBar(self,canvas,data):
        if self.user == 'player1':
            canvas.create_rectangle(data.width//2 - data.midPanel//2 - 200-5,
                                    data.margin-5, data.width//2-data.midPanel//2+5, data.margin * 2+5,
                                    fill = "grey", width = 0)
            canvas.create_rectangle(data.width//2 - data.midPanel//2 - 200,
                                    data.margin, data.width//2-data.midPanel//2 - 200 + self.hp, data.margin * 2,
                                    fill = "red", width = 0)
        elif self.user == 'player2':
            canvas.create_rectangle(data.width//2 + data.midPanel//2 -5,
                                    data.margin-5, data.width//2 + data.midPanel//2+200 + 5, data.margin * 2+5,
                                    fill = "grey", width = 0)
            canvas.create_rectangle(data.width//2 + data.midPanel//2 + 200 - self.hp,
                                    data.margin, data.width//2 + data.midPanel//2 + 200, data.margin * 2,
                                    fill = "red", width = 0)

    #To test whether the attact move lands on the various body parts
    def hitHead(self, x0, y0, x1, y1, data):
        if (((x0 - self.headX) ** 2 + (y0 - self.headY) ** 2)
            <= ((self.headD //2 * data.cmToPixel) ** 2)):
            return True
        else:
            return False

    def hitBody(self,x0,y0,x1,y1):
        return (line_intersect((self.leftShoulderX, self.leftShoulderY),
                              (self.leftAssX, self.leftAssY),
                              (x0,y0),
                              (x1,y1)) or
                (line_intersect((self.rightShoulderX, self.rightShoulderY),
                                (self.rightAssX,self.rightAssY),
                                (x0,y0),
                                (x1,y1))) or
                (line_intersect((self.rightShoulderX, self.rightShoulderY),
                                (self.leftShoulderX,self.leftShoulderY),
                                (x0,y0),
                                (x1,y1))) or
                (line_intersect((self.rightAssX, self.rightAssY),
                                (self.leftAssX, self.leftAssY),
                                (x0,y0),
                                (x1,y1))))
                

    def hitThigh(self,x0,y0,x1,y1):
        return (line_intersect((self.leftAssX, self.leftAssY),
                              (self.leftKneeX, self.leftKneeY),
                              (x0,y0),
                              (x1,y1)) or
                (line_intersect((self.assX, self.assY),
                                (self.rightKneeX,self.rightKneeY),
                                (x0,y0),
                                (x1,y1))) or
                (line_intersect((self.assX, self.assY),
                                (self.leftKneeX,self.leftKneeY),
                                (x0,y0),
                                (x1,y1))) or
                (line_intersect((self.rightAssX, self.rightAssY),
                                (self.rightKneeX,self.rightKneeY),
                                (x0,y0),
                                (x1,y1))))

    def hitShank(self,x0,y0,x1,y1):
        return (line_intersect((self.leftKneeX, self.leftKneeY),
                              (self.leftFootX, self.leftFootY),
                              (x0,y0),
                              (x1,y1)) or
                (line_intersect((self.rightKneeX, self.rightKneeY),
                                (self.rightFootX,self.rightFootY),
                                (x0,y0),
                                (x1,y1))))

    def hit(self, data, move):
        #The main hit function
        (x0,y0,x1,y1) = (-1,-1,-1,-1)
        if move == "jab1":
            (x0,y0,x1,y1) = (self.leftShoulderX, self.leftShoulderY,
                             self.leftHandX, self.leftHandY)
        elif move == "jab2":
            (x0,y0,x1,y1) = (self.rightShoulderX, self.rightShoulderY,
                             self.rightHandX + self.dir * 10, self.rightHandY)
        elif move == "kick":
            (x0,y0,x1,y1) = (self.leftAssX, self.leftAssY,
                             self.leftFootX, self.leftFootY)
        for fighter in data.fighters:
            if (fighter.user != self.user and fighter.hp > 0
                and fighter.pose != "die"):
                if fighter.hitHead(x1,y1,x0,y0, data):
                    fighter.beingHit(data, self.strength*10)
                    if fighter.pose != "defend":
                        fighter.hp = max(fighter.hp - self.strength * 2, 0)
                elif fighter.hitBody(x0,y0,x1,y1):
                    fighter.beingHit(data, self.strength*10)
                    if fighter.pose != "defend":
                        fighter.hp = max(fighter.hp - self.strength * 2, 0)
                elif fighter.hitThigh(x0,y0,x1,y1):
                    fighter.beingHit(data, self.strength*10)
                    if fighter.pose != "defend":
                        fighter.hp = max(fighter.hp - self.strength * 2, 0)
                elif fighter.hitShank(x0,y0,x1,y1):
                    fighter.beingHit(data, self.strength*10)
                    fighter.hp = max(fighter.hp - self.strength, 0)

################################################################
########################## Al Module##############################
################################################################
    def ai(self, data):
        if self.level == 1:
            self.aiLevel1(data)
        elif self.level == 2:
            self.aiLevel2(data)
        elif self.level == 3:
            self.aiLevel3(data)

    def aiLevel1(self, data):
        self.valueLocaliser(data)
        self.randomAction(data)

    def aiLevel2(self, data):
        self.valueLocaliser(data)
        self.distanceConcious(data)
        self.bombConcious(data)
        self.randomAction(data)

    def aiLevel3(self, data):
        self.valueLocaliser(data)
        self.learningConcious(data)
        self.distanceConcious(data)
        self.bombConcious(data)
        self.randomAction(data)

    def valueLocaliser(self, data):
        #to localise the default parameter in order to modify them undestructively
        self.moveToMotionRatio = self.moveToMotionRatio_default
        self.squatRatio = self.squatRatio_default
        self.jumpRatio = self.jumpRatio_default
        self.forwardRatio = self.forwardRatio_default
        self.backwardRatio = self.backwardRatio_default
        self.attackToDefendRatio = self.attackToDefendRatio_default
        self.bombPercentage = self.bombPercentage_default
        self.jabPercentage = self.jabPercentage_default
        self.kickPercentage = self.kickPercentage_default

    def distanceConcious(self, data):
        currentD = abs(data.fighters[0].x - data.fighters[1].x)
        if currentD > 200:
            self.bombPercentage = self.bombPercentage + self.jabPercentage + self.kickPercentage
            self.jabPercentage = 0
            self.kickPercentage = 0
        elif currentD < 100:
            self.jabPercentage += self.bombPercentage//2
            self.kickPercentage += self.bombPercentage//2
            self.bombPercentage = 0

    def bombConcious(self, data):
        for bomb in data.bombs:
            if abs(bomb.x - self.x) <= self.shoulderWidth // 2 + 30 and bomb.direction == (-1) * (self.dir):
                self.moveToMotionRatio = 1
                self.attackToDefendRatio = 0
                self.jumpRatio +=self.backwardRatio
                self.backwardRatio = 0
                        
    def learningConcious(self, data):
        if self.isBombLover(data.player1):
            self.approach(data)
        elif self.isDefendLover(data.player1):
            self.approach(data)
            self.squatKicker(data)

    def isBombLover(self,a):
        return a.bombPropensity >= 0.4

    def isDefendLover(self,a):
        return a.defendPropensity >= 0.4

    def approach(self, data):
        currentD = abs(data.fighters[0].x - data.fighters[1].x)
        if currentD > 200:
            self.moveToMotionRatio = 1
            if self.dir == 1:
                self.forwardRatio += self.backwardRatio
                self.backwardRatio = 0
            elif self.dir == -1:
                self.backwardRatio += self.forwardRatio
                self.forwardRatio = 0
            self.jumpRatio += self.squatRatio // 2 + 1
            self.squatRatio = self.squatRatio // 2 - 1

    def squatKicker(self, data):
        currentD = abs(data.fighters[0].x - data.fighters[1].x)
        if currentD < 100:
            self.moveToMotionRatio = 3
            self.squatRatio += self.jumpRatio // 2 + self.forwardRatio // 2 + self.backwardRatio // 2
            self.jumpRatio = self.jumpRatio // 2
            self.forwardRatio = self.forwardRatio // 2
            self.backwardRatio = self.backwardRatio // 2
            self.kickPercentage += self.bombPercentage
            self.bombPercentage = 0

    
    def randomAction(self, data):
        if self.takeAction():
            type = self.chooseAction()
            if type == "move":
                type = self.chooseMove()
                if type == "squat":
                    keyPressedS(data, "pc", self.user)
                elif type == "jump":
                    keyPressedW(data, "pc", self.user)
                elif type == "forward":
                    keyPressedD(data, "pc", self.user)
                elif type == "backward":
                    keyPressedA(data, "pc", self.user)
            else:
                type = self.attackOrDefend()
                if type == "defend":
                    keyPressedL(data, "pc", self.user)
                else:
                    type = self.chooseAttack()
                    if type == "bomb":
                        keyPressedSpace(data, "pc", self.user)
                    elif type == "jab":
                        keyPressedJ(data, "pc", self.user)
                    elif type == "kick":
                        keyPressedK(data, "pc", self.user)

    def takeAction(self):
        a = random.randint(1,60)
        if a>= 1 and a<=self.motionRate:
            return True
        else: return False

    def chooseAction(self):
        a = random.randint(1, self.moveToMotionRatio + 1)
        if a == 1:
            return "move"
        else:
            return "motion"

    def chooseMove(self):
        a = random.randint(1,100)
        if a >= 1 and a <= self.squatRatio:
            return "squat"
        elif a > self.squatRatio and a <= self.squatRatio + self.jumpRatio:
            return "jump"
        elif (a > self.squatRatio + self.jumpRatio and
              a <= self.squatRatio + self.jumpRatio + self.forwardRatio):
            return "forward"
        elif (a > self.squatRatio + self.jumpRatio + self.forwardRatio
              and a <= 100):
            return "backward"

    def attackOrDefend(self):
        a = random.randint(1, self.attackToDefendRatio + 1)
        if a == 1:
            return "defend"
        else: return "attack"

    def chooseAttack(self):
        a = random.randint(1,100)
        if a >= 1 and a <= self.bombPercentage:
            return "bomb"
        elif (a > self.bombPercentage and
              (a <= self.bombPercentage + self.jabPercentage)):
            return "jab"
        elif a > self.bombPercentage + self.jabPercentage and a <= 100:
            return "kick"

################################################################
############################ Gouken #############################
################################################################
class Gouken(Fighter):
    def __init__(self, user, control, data, level=1):
        super().__init__(user, control, data, level)
        self.name = "Gouken"
        #body attributes
        self.height = 205
        self.headD = 25
        self.shoulderWidth = self.headD * 2.5
        self.assWidth = self.headD * 2
        self.bodyL = (self.height - self.headD) * (1/(data.goldenRatio + 1))
        
        self.armL = self.bodyL + 10
        self.upperArmL = self.armL // 2
        self.foreArmL = self.armL - self.upperArmL
        
        self.legL = self.height - self.headD - self.bodyL        
        self.thighL = self.legL // 2
        self.shankL = self.legL - self.thighL
        #fight attributes (user related)
        self.speed = 10
        self.explo = 6
        self.strength = 15
        #pose
        self.stand(data)
        self.coordinatesCalculator(data)

    def kick(self, data):
        #This override the general kick. The angle of the left thigh is smaller
        self.pose = 'kick'
        self.head_angle_Y = -40 / 180 * math.pi * self.dir

        self.leftUpperArm_angle_Y = 5 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Y = 135 / 180 * math.pi * self.dir
        self.leftForeArm_angle_Z = 45 / 180 * math.pi * self.dir
        
        self.rightUpperArm_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Y = 90 / 180 * math.pi * self.dir
        self.rightForeArm_angle_Z = 0 / 180 * math.pi * self.dir

        self.spine_angle_Y = -50/180 * math.pi * self.dir
        self.spine_angle_X = 130/180 * math.pi * self.dir

        self.leftThigh_angle_Y = 110 / 180 * math.pi * self.dir
        self.leftShank_angle_Y = 110 / 180 * math.pi * self.dir

        self.rightThigh_angle_Y = 0 / 180 * math.pi * self.dir
        self.rightShank_angle_Y = 0 / 180 * math.pi  * self.dir
        self.coordinatesCalculator(data)
        self.hit(data, 'kick')

    #This function is used to control all the animations of gouken
    def drawImage(self, canvas, data):
        if self.dir == 1:
            self.drawImageCore(canvas, data, data.goukenR)
        elif self.dir == -1:
            self.drawImageCore(canvas, data, data.goukenL)
            
    def drawImageCore(self, canvas, data, photoD):
        if self.pose == "dying":
            pass
        elif self.jumpPose == None:
            self.drawImageCore_groundMove(canvas, data, photoD)
        else:
            self.drawImageCore_skyMove(canvas, data, photoD)
          
    def drawImageCore_groundMove(self, canvas, data, photoD):
        if self.pose == "kick":
            if self.motionTimer == 4 or self.motionTimer == 3:
                image = photoD["kick"]
                canvas.create_image(self.x, self.y-95, image=image)
            else:
                image = photoD["kickPrep"]
                canvas.create_image(self.x, self.y-95, image=image)
        elif self.pose == "jab1" or self.pose == "jab2":
            if self.motionTimer > 1 and self.motionTimer < 5:
                image = photoD[self.pose]
                canvas.create_image(self.x, self.y-95, image=image)
            else:
                image = photoD["stand"]
                canvas.create_image(self.x, self.y-95, image=image)
        elif self.pose == "squat":
            image = photoD[self.pose]
            canvas.create_image(self.x, self.y-65, image=image)
        elif self.pose == "jabSquat":
            if self.motionTimer == 5 or self.motionTimer <= 1:
                image = photoD["squat"]
                canvas.create_image(self.x, self.y-65, image=image)
            else:
                image = photoD[self.pose]
                canvas.create_image(self.x, self.y-65, image=image)
        elif self.pose == "kickSquat":
            if self.motionTimer == 5 or self.motionTimer <= 1:
                image = photoD["kickSquatPrep"]
                canvas.create_image(self.x, self.y-65, image=image)
            else:
                image = photoD[self.pose]
                canvas.create_image(self.x, self.y-65, image=image)
        elif self.pose == "walkForward":
            if self.motionTimer == 4:
                canvas.create_image(self.x, self.y-95, image=photoD["walk1"])
            elif self.motionTimer == 3:
                canvas.create_image(self.x, self.y-95, image=photoD["walk2"])
            elif self.motionTimer == 2:
                canvas.create_image(self.x, self.y-95, image=photoD["walk3"])
            elif self.motionTimer <= 1:
                canvas.create_image(self.x, self.y-95, image=photoD["walk4"])
        elif self.pose == "walkBackward":
            if self.motionTimer == 4:
                canvas.create_image(self.x, self.y-95, image=photoD["walk4"])
            elif self.motionTimer == 3:
                canvas.create_image(self.x, self.y-95, image=photoD["walk4"])
            elif self.motionTimer == 2:
                canvas.create_image(self.x, self.y-95, image=photoD["walk3"])
            elif self.motionTimer <= 1:
                canvas.create_image(self.x, self.y-95, image=photoD["walk3"])
        elif self.pose == "bomb":
            if self.motionTimer <= 6 and self.motionTimer >= 5:
                canvas.create_image(self.x, self.y-95, image=photoD["bomb1"])
            elif self.motionTimer <= 4 and self.motionTimer >= 3:
                canvas.create_image(self.x, self.y-95, image=photoD["bomb2"])
            elif self.motionTimer <= 2:
                canvas.create_image(self.x, self.y-95, image=photoD["bomb3"])
        elif self.pose == "die":
            if self.motionTimer <= 80 and self.motionTimer >= 50:
                canvas.create_image(self.x, self.y-95, image=photoD["die1"])
            elif self.motionTimer < 50 and self.motionTimer >= 25:
                canvas.create_image(self.x, self.y-55, image=photoD["die2"])
            else:
                canvas.create_image(self.x, self.y-55, image=photoD["die3"])
        elif self.pose == "beingHit":
            if self.motionTimer >= 5:
                canvas.create_image(self.x, self.y-95, image=photoD["stand"])
            elif self.motionTimer >= 4:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
            elif self.motionTimer >= 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit2"])
            elif self.motionTimer < 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
        else:
            image = photoD[self.pose]
            canvas.create_image(self.x, self.y-95, image=image)

    def drawImageCore_skyMove(self, canvas, data, photoD):
        if self.pose == "beingHit":
            if self.motionTimer >= 5:
                canvas.create_image(self.x, self.y-95, image=photoD["stand"])
            elif self.motionTimer >= 4:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
            elif self.motionTimer >= 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit2"])
            elif self.motionTimer < 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
        if self.jumpPose == "jumpForward":
            if self.jumpTimer == 8:
                image = photoD["jumpForward1"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 7:
                image = photoD["jumpForward2"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 6 or self.jumpTimer == 5:
                image = photoD["jumpForward3"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 3 or self.jumpTimer == 4:
                image = photoD["jumpForward4"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 2:
                image = photoD["jumpForward5"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer <= 1:
                image = photoD["jumpForward6"]
                canvas.create_image(self.x, self.y - 95, image=image)

        elif self.jumpPose == "jumpBackward":
            if self.jumpTimer == 8:
                image = photoD["jumpBackward1"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 7 or self.jumpTimer == 6:
                image = photoD["jumpBackward2"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 4 or self.jumpTimer == 5:
                image = photoD["jumpBackward3"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 3 or self.jumpTimer == 2:
                image = photoD["jumpBackward4"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer <= 1:
                image = photoD["jumpBackward5"]
                canvas.create_image(self.x, self.y - 95, image=image)

        elif self.jumpPose == "jump":
            if self.jumpTimer == 8 or self.jumpTimer == 1:
                if self.pose == "jumpKick":
                    image = photoD["jumpKickPrep"]
                    canvas.create_image(self.x, self.y - 95, image=image)
                else:
                    image = photoD["jump1"]
                    canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 7 or self.jumpTimer == 2:
                if self.pose == "jumpKick":
                    image = photoD["jumpKick"]
                    canvas.create_image(self.x, self.y - 95, image=image)
                else:
                    image = photoD["jump2"]
                    canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer <= 6 and self.jumpTimer >= 3:
                if self.pose == "jumpKick":
                    image = photoD["jumpKick"]
                    canvas.create_image(self.x, self.y - 95, image=image)
                else:
                    image = photoD["jump3"]
                    canvas.create_image(self.x, self.y - 95, image=image)

################################################################
############################# Ryu ###############################
################################################################
class Ryu(Fighter):
    def __init__(self, user, control, data, level=1):
        super().__init__(user, control, data, level)
        self.name = "Ryu"
        #body attributes
        self.height = 190
        self.headD = 20
        self.shoulderWidth = self.headD * 2
        self.assWidth = self.headD * 1.8
        self.bodyL = (self.height - self.headD) * (1/(data.goldenRatio + 1))
        
        self.armL = self.bodyL
        self.upperArmL = self.armL // 2
        self.foreArmL = self.armL - self.upperArmL
        
        self.legL = self.height - self.headD - self.bodyL        
        self.thighL = self.legL // 2
        self.shankL = self.legL - self.thighL
        #fight attributes (user related)
        self.speed = 10
        self.explo = 10
        self.strength = 10
        #pose
        self.stand(data)
        self.coordinatesCalculator(data)

    def drawImage(self, canvas, data):
        if self.dir == 1:
            self.drawImageCore(canvas, data, data.ryuR)
        elif self.dir == -1:
            self.drawImageCore(canvas, data, data.ryuL)
            

    def drawImageCore(self, canvas, data, photoD):
        if self.pose == "dying":
            pass
        elif self.jumpPose == None:
            self.drawImageCore_groundMove(canvas, data, photoD)
        else:
            self.drawImageCore_skyMove(canvas, data, photoD)
          
    def drawImageCore_groundMove(self, canvas, data, photoD):
        if self.pose == "kick":
            if self.motionTimer == 4 or self.motionTimer == 3:
                image = photoD["kick"]
                canvas.create_image(self.x, self.y-95, image=image)
            else:
                image = photoD["kickPrep"]
                canvas.create_image(self.x, self.y-95, image=image)
        elif self.pose == "jab1" or self.pose == "jab2":
            if self.motionTimer > 1 and self.motionTimer < 5:
                image = photoD[self.pose]
                canvas.create_image(self.x, self.y-95, image=image)
            else:
                image = photoD["stand"]
                canvas.create_image(self.x, self.y-95, image=image)
        elif self.pose == "squat":
            image = photoD[self.pose]
            canvas.create_image(self.x, self.y-65, image=image)
        elif self.pose == "jabSquat":
            if self.motionTimer == 5 or self.motionTimer <= 1:
                image = photoD["squat"]
                canvas.create_image(self.x, self.y-65, image=image)
            else:
                image = photoD[self.pose]
                canvas.create_image(self.x, self.y-65, image=image)
        elif self.pose == "kickSquat":
            if self.motionTimer == 5 or self.motionTimer <= 1:
                image = photoD["kickSquatPrep"]
                canvas.create_image(self.x, self.y-65, image=image)
            else:
                image = photoD[self.pose]
                canvas.create_image(self.x, self.y-65, image=image)
        elif self.pose == "walkForward":
            if self.motionTimer == 4:
                canvas.create_image(self.x, self.y-95, image=photoD["walk1"])
            elif self.motionTimer == 3:
                canvas.create_image(self.x, self.y-95, image=photoD["walk2"])
            elif self.motionTimer == 2:
                canvas.create_image(self.x, self.y-95, image=photoD["walk3"])
            elif self.motionTimer <= 1:
                canvas.create_image(self.x, self.y-95, image=photoD["walk4"])
        elif self.pose == "walkBackward":
            if self.motionTimer == 4:
                canvas.create_image(self.x, self.y-95, image=photoD["walk4"])
            elif self.motionTimer == 3:
                canvas.create_image(self.x, self.y-95, image=photoD["walk4"])
            elif self.motionTimer == 2:
                canvas.create_image(self.x, self.y-95, image=photoD["walk3"])
            elif self.motionTimer <= 1:
                canvas.create_image(self.x, self.y-95, image=photoD["walk3"])
        elif self.pose == "bomb":
            if self.motionTimer <= 6 and self.motionTimer >= 5:
                canvas.create_image(self.x, self.y-95, image=photoD["bomb1"])
            elif self.motionTimer <= 4 and self.motionTimer >= 3:
                canvas.create_image(self.x, self.y-95, image=photoD["bomb2"])
            elif self.motionTimer <= 2:
                canvas.create_image(self.x, self.y-95, image=photoD["bomb3"])
        elif self.pose == "die":
            if self.motionTimer <= 80 and self.motionTimer >= 50:
                canvas.create_image(self.x, self.y-95, image=photoD["die1"])
            elif self.motionTimer < 50 and self.motionTimer >= 25:
                canvas.create_image(self.x, self.y-55, image=photoD["die2"])
            else:
                canvas.create_image(self.x, self.y-55, image=photoD["die3"])
        elif self.pose == "beingHit":
            if self.motionTimer >= 5:
                canvas.create_image(self.x, self.y-95, image=photoD["stand"])
            elif self.motionTimer >= 4:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
            elif self.motionTimer >= 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit2"])
            elif self.motionTimer < 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
        else:
            image = photoD[self.pose]
            canvas.create_image(self.x, self.y-95, image=image)

    def drawImageCore_skyMove(self, canvas, data, photoD):
        if self.pose == "beingHit":
            if self.motionTimer >= 5:
                canvas.create_image(self.x, self.y-95, image=photoD["stand"])
            elif self.motionTimer >= 4:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
            elif self.motionTimer >= 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit2"])
            elif self.motionTimer < 2:
                canvas.create_image(self.x, self.y-95, image=photoD["getHit1"])
        if self.jumpPose == "jumpForward":
            if self.jumpTimer == 8:
                image = photoD["jumpForward1"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 7:
                image = photoD["jumpForward2"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 6 or self.jumpTimer == 5:
                image = photoD["jumpForward3"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 3 or self.jumpTimer == 4:
                image = photoD["jumpForward4"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 2:
                image = photoD["jumpForward5"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer <= 1:
                image = photoD["jumpForward6"]
                canvas.create_image(self.x, self.y - 95, image=image)

        elif self.jumpPose == "jumpBackward":
            if self.jumpTimer == 8:
                image = photoD["jumpBackward1"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 7 or self.jumpTimer == 6:
                image = photoD["jumpBackward2"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 4 or self.jumpTimer == 5:
                image = photoD["jumpBackward3"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 3 or self.jumpTimer == 2:
                image = photoD["jumpBackward4"]
                canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer <= 1:
                image = photoD["jumpBackward5"]
                canvas.create_image(self.x, self.y - 95, image=image)

        elif self.jumpPose == "jump":
            if self.jumpTimer == 8 or self.jumpTimer == 1:
                if self.pose == "jumpKick":
                    image = photoD["jumpKickPrep"]
                    canvas.create_image(self.x, self.y - 95, image=image)
                else:
                    image = photoD["jump1"]
                    canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer == 7 or self.jumpTimer == 2:
                if self.pose == "jumpKick":
                    image = photoD["jumpKick"]
                    canvas.create_image(self.x, self.y - 95, image=image)
                else:
                    image = photoD["jump2"]
                    canvas.create_image(self.x, self.y - 95, image=image)
            elif self.jumpTimer <= 6 and self.jumpTimer >= 3:
                if self.pose == "jumpKick":
                    image = photoD["jumpKick"]
                    canvas.create_image(self.x, self.y - 95, image=image)
                else:
                    image = photoD["jump3"]
                    canvas.create_image(self.x, self.y - 95, image=image)

################################################################
######################## Bomb Class Zone #########################
################################################################
class Bomb(object):
    def __init__(self, x, y, direction, launcher):
        self.bombTimer = 0
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 15
        self.velocity = self.speed * self.direction
        self.launcher = launcher
        self.explode = False

    def hit(self, data):
        markingLine = [(self.x, self.y+5, self.x + self.direction * 10, self.y+5),
                       (self.x, self.y-5, self.x + self.direction * 10, self.y -5)]
        for line in markingLine:
            for fighter in data.fighters:
                if fighter.pose == "die": return False
                if (fighter.hitHead(line[0],line[1],line[2],line[3], data) or
                    fighter.hitBody(line[0],line[1],line[2],line[3])):
                    if fighter.pose != "defend" and fighter.hp > 0:
                        fighter.hp = max(fighter.hp - 10, 0)
                        fighter.beingHit(data, 10)
                        data.explosions.append([self.x, self.y, 7])
                    try:
                        data.bombs.remove(self)
                    except:
                        return
                    return
        return False

    def timerFiredGame_bomb(self, data):
        if self.x >= data.width+50 or self.x <= -50:
            data.bombs.remove(self)
        self.bombTimer += 1
        if self.hit(data) != False:
            pass
        else:
            self.x += self.velocity

    def drawBomb(self, canvas, data):
        if not self.explode:
            if self.direction == 1:
                if self.launcher == "Ryu":
                    if self.bombTimer <= 2:
                        canvas.create_image(self.x, self.y, anchor = E, image = data.bombR["ryuBomb1"])
                    elif self.bombTimer <= 4:
                        canvas.create_image(self.x, self.y, anchor = E, image = data.bombR["ryuBomb2"])
                    elif self.bombTimer <= 6:
                        canvas.create_image(self.x, self.y, anchor = E, image = data.bombR["ryuBomb3"])
                    else:
                        canvas.create_image(self.x, self.y, anchor = E, image = data.bombR["ryuBomb4"])
                elif self.launcher == "Gouken":
                    if self.bombTimer <= 4:
                        canvas.create_image(self.x, self.y, anchor = E, image = data.bombR["goukenBomb1"])
                    else:
                        canvas.create_image(self.x, self.y, anchor = E, image = data.bombR["goukenBomb2"])
                    
            elif self.direction == -1:
                if self.launcher == "Ryu":
                    if self.bombTimer <= 2:
                        canvas.create_image(self.x, self.y, anchor = W, image = data.bombL["ryuBomb1"])
                    elif self.bombTimer <= 4:
                        canvas.create_image(self.x, self.y, anchor = W, image = data.bombL["ryuBomb2"])
                    elif self.bombTimer <= 6:
                        canvas.create_image(self.x, self.y, anchor = W, image = data.bombL["ryuBomb3"])
                    else:
                        canvas.create_image(self.x, self.y, anchor = W, image = data.bombL["ryuBomb4"])
                elif self.launcher == "Gouken":
                    if self.bombTimer <= 4:
                        canvas.create_image(self.x, self.y, anchor = W, image = data.bombL["goukenBomb1"])
                    else:
                        canvas.create_image(self.x, self.y, anchor = W, image = data.bombL["goukenBomb2"])


from tkinter import *
################################################################
############################# init ################################
################################################################
def init(data):
    data.pause = False
    data.mode = 'welcome'
    data.music = True
    data.player = "player1"
    data.multiplayer = False
    if data.mode == 'welcome':
        initWelcome(data)

def initMultiplayerStage1(data):
    data.multiplayer = True
    HOST = ''
    PORT = 50014
    data.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data.server.connect((HOST, PORT))
    print('connected to server')

def initMultiplayerStage2(data):
    data.stages = []
    data.stages.append(("North Korea", PhotoImage(file = "image/stage/Stage_NorthKorea.gif")))
    data.stages.append(("Air Force Base", PhotoImage(file = "image/stage/Stage_AirforceBase.gif")))
    data.stages.append(("ChinaTown", PhotoImage(file = "image/stage/Stage_ChinaTown.gif")))
    data.stages.append(("Kenya", PhotoImage(file = "image/stage/Stage_Kenya.gif")))
    data.stages.append(("Practise Room", PhotoImage(file = "image/stage/Stage_PractiseRoom.gif")))
    data.stages.append(("the Great Wall", PhotoImage(file = "image/stage/Stage_theGreatWall.gif")))
    data.round = 3
    data.stageChosen = 0
    if data.player == "player1":
        data.userChar = "RYU"
    else:
        data.userChar = "GOUKEN"

def initWelcome(data):
    data.timerDelay = 1000
    data.photo = {}

def initMode(data):#Will init the resources for credit and help too
    data.timerDelay = 1000
    data.photo = {}
    data.photo["background"] = PhotoImage(file = "image/menu_background.gif")
    data.photo["common_background"] = PhotoImage(file = "image/level_background.gif")
    data.photo["credit"] = PhotoImage(file = "image/credit_panda.gif")
    data.photo["help"] = PhotoImage(file = "image/help_shifu.gif")

def initRound(data):
    data.round = 3

def initStage(data):
    data.timerDelay = 50
    data.leftArrowLightTimer = 0
    data.rightArrowLightTimer = 0
    data.stageChosen = 0
    data.stages = []
    data.stages.append(("North Korea", PhotoImage(file = "image/stage/Stage_NorthKorea.gif")))
    data.stages.append(("Air Force Base", PhotoImage(file = "image/stage/Stage_AirforceBase.gif")))
    data.stages.append(("ChinaTown", PhotoImage(file = "image/stage/Stage_ChinaTown.gif")))
    data.stages.append(("Kenya", PhotoImage(file = "image/stage/Stage_Kenya.gif")))
    data.stages.append(("Practise Room", PhotoImage(file = "image/stage/Stage_PractiseRoom.gif")))
    data.stages.append(("the Great Wall", PhotoImage(file = "image/stage/Stage_theGreatWall.gif")))

def initLevel(data):
    data.aiLevel = 1
    data.photo["level_background"] = PhotoImage(file = "image/level_background.gif")

def initCharacter(data):
    data.description = False
    data.userChar = "RYU"
    data.photo["ryu"] = PhotoImage(file = "image/characterSelection/ryu.gif")
    data.photo["gouken"] = PhotoImage(file = "image/characterSelection/gouken.gif")

def initGameMode(data, player1V = 0, player2V = 0):
    initGameControl(data)
    initOthers(data)
    initDisplayParameters(data)
    initStats(data, player1V, player2V)
    initFighters(data)

def initGameControl(data):
    data.opening = True
    data.winner = None
    data.dyingTimer = -1
    data.timerDelay = 50
    data.realTimer = 0
    data.countDown = 120

def initDisplayParameters(data):
    data.margin = 15
    data.midPanel = 100
    data.cmToPixel = data.width / 1280 * 2
    data.groundLevel = data.height * 9/10
    data.player1_start_pos_x = data.width * 1/4
    data.player2_start_pos_x = data.width * 3/4
    data.countDown_pos_x = data.width//2
    data.countDown_pos_y = data.height * 1/10
    data.goldenRatio = (1 + 5 ** (1/2))/2

def initFighters(data):
    data.fighters = []
    data.ryuR = {}
    data.ryuL = {}
    initRyuR(data)
    initRyuL(data)
    data.goukenR = {}
    data.goukenL = {}
    initGoukenR(data)
    initGoukenL(data)
    if not data.multiplayer:
        if data.userChar == "RYU":
            data.fighters.append(Ryu('player1', 'user', data))
            data.fighters.append(Gouken('player2', 'pc', data, data.aiLevel))
        else:
            data.fighters.append(Gouken('player1', 'user', data))
            data.fighters.append(Ryu('player2', 'pc', data, data.aiLevel))
    else:
        data.fighters.append(Ryu('player1', 'user', data))
        data.fighters.append(Gouken('player2', 'user', data))
        
def initOthers(data):
    data.testing = False
    data.bombR = {}
    data.bombL = {}
    data.bombs = []
    initBombR(data)
    initBombL(data)
    data.explosion = {}
    initExplosion(data)
    data.explosions = []
    data.otherPhoto = {}
    data.otherPhoto["KO"] = PhotoImage(file = "image/KO.gif")
    data.otherPhoto["projector_screen"] = PhotoImage(file = "image/projector_screen.gif")

def initStats(data, player1V, player2V):
    data.stats = False
    data.player1 = BattleStats()
    data.player2 = BattleStats()
    data.player1V = player1V
    data.player2V = player2V
    data.currentRound = player1V + player2V +1
    data.player1VStr = ""
    data.player2VStr = ""
    for i in range(data.round//2 + 1):
        if player1V == 0:
            data.player1VStr += "- "
        else:
            data.player1VStr += "V "
            player1V -= 1
        if player2V == 0:
            data.player2VStr += "- "
        else:
            data.player2VStr += "V "
            player2V -= 1


def initRyuR(data):
    data.ryuR["stand"] = PhotoImage(file = "image/ryu/r/stand.gif")
    data.ryuR["jab1"] = PhotoImage(file = "image/ryu/r/jab1.gif")
    data.ryuR["jab2"] = PhotoImage(file = "image/ryu/r/jab2.gif")
    data.ryuR["kick"] = PhotoImage(file = "image/ryu/r/kick.gif")
    data.ryuR["kickPrep"] = PhotoImage(file = "image/ryu/r/kickprep.gif")
    data.ryuR["squat"] = PhotoImage(file = "image/ryu/r/squat.gif")
    data.ryuR["jabSquat"] = PhotoImage(file = "image/ryu/r/jabSquat.gif")
    data.ryuR["kickSquat"] = PhotoImage(file = "image/ryu/r/kickSquat.gif")
    data.ryuR["kickSquatPrep"] = PhotoImage(file = "image/ryu/r/kickSquatPrep.gif")
    data.ryuR["defend"] = PhotoImage(file = "image/ryu/r/defend.gif")
    data.ryuR["jump1"] = PhotoImage(file = "image/ryu/r/jump1.gif")
    data.ryuR["jump2"] = PhotoImage(file = "image/ryu/r/jump2.gif")
    data.ryuR["jump3"] = PhotoImage(file = "image/ryu/r/jump3.gif")
    data.ryuR["walk1"] = PhotoImage(file = "image/ryu/r/walk1.gif")
    data.ryuR["walk2"] = PhotoImage(file = "image/ryu/r/walk2.gif")
    data.ryuR["walk3"] = PhotoImage(file = "image/ryu/r/walk3.gif")
    data.ryuR["walk4"] = PhotoImage(file = "image/ryu/r/walk4.gif")
    data.ryuR["jumpForward1"] = PhotoImage(file = "image/ryu/r/jumpForward1.gif")
    data.ryuR["jumpForward2"] = PhotoImage(file = "image/ryu/r/jumpForward2.gif")
    data.ryuR["jumpForward3"] = PhotoImage(file = "image/ryu/r/jumpForward3.gif")
    data.ryuR["jumpForward4"] = PhotoImage(file = "image/ryu/r/jumpForward4.gif")
    data.ryuR["jumpForward5"] = PhotoImage(file = "image/ryu/r/jumpForward5.gif")
    data.ryuR["jumpForward6"] = PhotoImage(file = "image/ryu/r/jumpForward6.gif")
    data.ryuR["jumpBackward1"] = PhotoImage(file = "image/ryu/r/jumpBackward1.gif")
    data.ryuR["jumpBackward2"] = PhotoImage(file = "image/ryu/r/jumpBackward2.gif")
    data.ryuR["jumpBackward3"] = PhotoImage(file = "image/ryu/r/jumpBackward3.gif")
    data.ryuR["jumpBackward4"] = PhotoImage(file = "image/ryu/r/jumpBackward4.gif")
    data.ryuR["jumpBackward5"] = PhotoImage(file = "image/ryu/r/jumpBackward5.gif")
    data.ryuR["jumpKick"] = PhotoImage(file = "image/ryu/r/jumpKick.gif")
    data.ryuR["jumpKickPrep"] = PhotoImage(file = "image/ryu/r/jumpKickPrep.gif")
    data.ryuR["bomb1"] = PhotoImage(file = "image/ryu/r/bomb1.gif")
    data.ryuR["bomb2"] = PhotoImage(file = "image/ryu/r/bomb2.gif")
    data.ryuR["bomb3"] = PhotoImage(file = "image/ryu/r/bomb3.gif")
    data.ryuR["die1"] = PhotoImage(file = "image/ryu/r/die1.gif")
    data.ryuR["die2"] = PhotoImage(file = "image/ryu/r/die2.gif")
    data.ryuR["die3"] = PhotoImage(file = "image/ryu/r/die3.gif")
    data.ryuR["getHit1"] = PhotoImage(file = "image/ryu/r/getHit1.gif")
    data.ryuR["getHit2"] = PhotoImage(file = "image/ryu/r/getHit2.gif")

    
def initRyuL(data):
    data.ryuL["stand"] = PhotoImage(file = "image/ryu/l/stand.gif")
    data.ryuL["jab1"] = PhotoImage(file = "image/ryu/l/jab1.gif")
    data.ryuL["jab2"] = PhotoImage(file = "image/ryu/l/jab2.gif")
    data.ryuL["kick"] = PhotoImage(file = "image/ryu/l/kick.gif")
    data.ryuL["kickPrep"] = PhotoImage(file = "image/ryu/l/kickprep.gif")
    data.ryuL["squat"] = PhotoImage(file = "image/ryu/l/squat.gif")
    data.ryuL["jabSquat"] = PhotoImage(file = "image/ryu/l/jabSquat.gif")
    data.ryuL["kickSquat"] = PhotoImage(file = "image/ryu/l/kickSquat.gif")
    data.ryuL["kickSquatPrep"] = PhotoImage(file = "image/ryu/l/kickSquatPrep.gif")
    data.ryuL["defend"] = PhotoImage(file = "image/ryu/l/defend.gif")
    data.ryuL["jump1"] = PhotoImage(file = "image/ryu/l/jump1.gif")
    data.ryuL["jump2"] = PhotoImage(file = "image/ryu/l/jump2.gif")
    data.ryuL["jump3"] = PhotoImage(file = "image/ryu/l/jump3.gif")
    data.ryuL["walk1"] = PhotoImage(file = "image/ryu/l/walk1.gif")
    data.ryuL["walk2"] = PhotoImage(file = "image/ryu/l/walk2.gif")
    data.ryuL["walk3"] = PhotoImage(file = "image/ryu/l/walk3.gif")
    data.ryuL["walk4"] = PhotoImage(file = "image/ryu/l/walk4.gif")
    data.ryuL["jumpForward1"] = PhotoImage(file = "image/ryu/l/jumpForward1.gif")
    data.ryuL["jumpForward2"] = PhotoImage(file = "image/ryu/l/jumpForward2.gif")
    data.ryuL["jumpForward3"] = PhotoImage(file = "image/ryu/l/jumpForward3.gif")
    data.ryuL["jumpForward4"] = PhotoImage(file = "image/ryu/l/jumpForward4.gif")
    data.ryuL["jumpForward5"] = PhotoImage(file = "image/ryu/l/jumpForward5.gif")
    data.ryuL["jumpForward6"] = PhotoImage(file = "image/ryu/l/jumpForward6.gif")
    data.ryuL["jumpBackward1"] = PhotoImage(file = "image/ryu/l/jumpBackward1.gif")
    data.ryuL["jumpBackward2"] = PhotoImage(file = "image/ryu/l/jumpBackward2.gif")
    data.ryuL["jumpBackward3"] = PhotoImage(file = "image/ryu/l/jumpBackward3.gif")
    data.ryuL["jumpBackward4"] = PhotoImage(file = "image/ryu/l/jumpBackward4.gif")
    data.ryuL["jumpBackward5"] = PhotoImage(file = "image/ryu/l/jumpBackward5.gif")
    data.ryuL["jumpKick"] = PhotoImage(file = "image/ryu/l/jumpKick.gif")
    data.ryuL["jumpKickPrep"] = PhotoImage(file = "image/ryu/l/jumpKickPrep.gif")
    data.ryuL["bomb1"] = PhotoImage(file = "image/ryu/l/bomb1.gif")
    data.ryuL["bomb2"] = PhotoImage(file = "image/ryu/l/bomb2.gif")
    data.ryuL["bomb3"] = PhotoImage(file = "image/ryu/l/bomb3.gif")
    data.ryuL["die1"] = PhotoImage(file = "image/ryu/l/die1.gif")
    data.ryuL["die2"] = PhotoImage(file = "image/ryu/l/die2.gif")
    data.ryuL["die3"] = PhotoImage(file = "image/ryu/l/die3.gif")
    data.ryuL["getHit1"] = PhotoImage(file = "image/ryu/l/getHit1.gif")
    data.ryuL["getHit2"] = PhotoImage(file = "image/ryu/l/getHit2.gif")

def initGoukenR(data):
    data.goukenR["stand"] = PhotoImage(file = "image/gouken/r/stand.gif")
    data.goukenR["jab1"] = PhotoImage(file = "image/gouken/r/jab1.gif")
    data.goukenR["jab2"] = PhotoImage(file = "image/gouken/r/jab2.gif")
    data.goukenR["kick"] = PhotoImage(file = "image/gouken/r/kick.gif")
    data.goukenR["kickPrep"] = PhotoImage(file = "image/gouken/r/kickprep.gif")
    data.goukenR["squat"] = PhotoImage(file = "image/gouken/r/squat.gif")
    data.goukenR["jabSquat"] = PhotoImage(file = "image/gouken/r/jabSquat.gif")
    data.goukenR["kickSquat"] = PhotoImage(file = "image/gouken/r/kickSquat.gif")
    data.goukenR["kickSquatPrep"] = PhotoImage(file = "image/gouken/r/kickSquatPrep.gif")
    data.goukenR["defend"] = PhotoImage(file = "image/gouken/r/defend.gif")
    data.goukenR["jump1"] = PhotoImage(file = "image/gouken/r/jump1.gif")
    data.goukenR["jump2"] = PhotoImage(file = "image/gouken/r/jump2.gif")
    data.goukenR["jump3"] = PhotoImage(file = "image/gouken/r/jump3.gif")
    data.goukenR["walk1"] = PhotoImage(file = "image/gouken/r/walk1.gif")
    data.goukenR["walk2"] = PhotoImage(file = "image/gouken/r/walk2.gif")
    data.goukenR["walk3"] = PhotoImage(file = "image/gouken/r/walk3.gif")
    data.goukenR["walk4"] = PhotoImage(file = "image/gouken/r/walk4.gif")
    data.goukenR["jumpForward1"] = PhotoImage(file = "image/gouken/r/jumpForward1.gif")
    data.goukenR["jumpForward2"] = PhotoImage(file = "image/gouken/r/jumpForward2.gif")
    data.goukenR["jumpForward3"] = PhotoImage(file = "image/gouken/r/jumpForward3.gif")
    data.goukenR["jumpForward4"] = PhotoImage(file = "image/gouken/r/jumpForward4.gif")
    data.goukenR["jumpForward5"] = PhotoImage(file = "image/gouken/r/jumpForward5.gif")
    data.goukenR["jumpForward6"] = PhotoImage(file = "image/gouken/r/jumpForward6.gif")
    data.goukenR["jumpBackward1"] = PhotoImage(file = "image/gouken/r/jumpBackward1.gif")
    data.goukenR["jumpBackward2"] = PhotoImage(file = "image/gouken/r/jumpBackward2.gif")
    data.goukenR["jumpBackward3"] = PhotoImage(file = "image/gouken/r/jumpBackward3.gif")
    data.goukenR["jumpBackward4"] = PhotoImage(file = "image/gouken/r/jumpBackward4.gif")
    data.goukenR["jumpBackward5"] = PhotoImage(file = "image/gouken/r/jumpBackward5.gif")
    data.goukenR["jumpKick"] = PhotoImage(file = "image/gouken/r/jumpKick.gif")
    data.goukenR["jumpKickPrep"] = PhotoImage(file = "image/gouken/r/jumpKickPrep.gif")
    data.goukenR["bomb1"] = PhotoImage(file = "image/gouken/r/bomb1.gif")
    data.goukenR["bomb2"] = PhotoImage(file = "image/gouken/r/bomb2.gif")
    data.goukenR["bomb3"] = PhotoImage(file = "image/gouken/r/bomb3.gif")
    data.goukenR["die1"] = PhotoImage(file = "image/gouken/r/die1.gif")
    data.goukenR["die2"] = PhotoImage(file = "image/gouken/r/die2.gif")
    data.goukenR["die3"] = PhotoImage(file = "image/gouken/r/die3.gif")
    data.goukenR["getHit1"] = PhotoImage(file = "image/gouken/r/getHit1.gif")
    data.goukenR["getHit2"] = PhotoImage(file = "image/gouken/r/getHit2.gif")

def initGoukenL(data):
    data.goukenL["stand"] = PhotoImage(file = "image/gouken/l/stand.gif")
    data.goukenL["jab1"] = PhotoImage(file = "image/gouken/l/jab1.gif")
    data.goukenL["jab2"] = PhotoImage(file = "image/gouken/l/jab2.gif")
    data.goukenL["kick"] = PhotoImage(file = "image/gouken/l/kick.gif")
    data.goukenL["kickPrep"] = PhotoImage(file = "image/gouken/l/kickprep.gif")
    data.goukenL["squat"] = PhotoImage(file = "image/gouken/l/squat.gif")
    data.goukenL["jabSquat"] = PhotoImage(file = "image/gouken/l/jabSquat.gif")
    data.goukenL["kickSquat"] = PhotoImage(file = "image/gouken/l/kickSquat.gif")
    data.goukenL["kickSquatPrep"] = PhotoImage(file = "image/gouken/l/kickSquatPrep.gif")
    data.goukenL["defend"] = PhotoImage(file = "image/gouken/l/defend.gif")
    data.goukenL["jump1"] = PhotoImage(file = "image/gouken/l/jump1.gif")
    data.goukenL["jump2"] = PhotoImage(file = "image/gouken/l/jump2.gif")
    data.goukenL["jump3"] = PhotoImage(file = "image/gouken/l/jump3.gif")
    data.goukenL["walk1"] = PhotoImage(file = "image/gouken/l/walk1.gif")
    data.goukenL["walk2"] = PhotoImage(file = "image/gouken/l/walk2.gif")
    data.goukenL["walk3"] = PhotoImage(file = "image/gouken/l/walk3.gif")
    data.goukenL["walk4"] = PhotoImage(file = "image/gouken/l/walk4.gif")
    data.goukenL["jumpForward1"] = PhotoImage(file = "image/gouken/l/jumpForward1.gif")
    data.goukenL["jumpForward2"] = PhotoImage(file = "image/gouken/l/jumpForward2.gif")
    data.goukenL["jumpForward3"] = PhotoImage(file = "image/gouken/l/jumpForward3.gif")
    data.goukenL["jumpForward4"] = PhotoImage(file = "image/gouken/l/jumpForward4.gif")
    data.goukenL["jumpForward5"] = PhotoImage(file = "image/gouken/l/jumpForward5.gif")
    data.goukenL["jumpForward6"] = PhotoImage(file = "image/gouken/l/jumpForward6.gif")
    data.goukenL["jumpBackward1"] = PhotoImage(file = "image/gouken/l/jumpBackward1.gif")
    data.goukenL["jumpBackward2"] = PhotoImage(file = "image/gouken/l/jumpBackward2.gif")
    data.goukenL["jumpBackward3"] = PhotoImage(file = "image/gouken/l/jumpBackward3.gif")
    data.goukenL["jumpBackward4"] = PhotoImage(file = "image/gouken/l/jumpBackward4.gif")
    data.goukenL["jumpBackward5"] = PhotoImage(file = "image/gouken/l/jumpBackward5.gif")
    data.goukenL["jumpKick"] = PhotoImage(file = "image/gouken/l/jumpKick.gif")
    data.goukenL["jumpKickPrep"] = PhotoImage(file = "image/gouken/l/jumpKickPrep.gif")
    data.goukenL["bomb1"] = PhotoImage(file = "image/gouken/l/bomb1.gif")
    data.goukenL["bomb2"] = PhotoImage(file = "image/gouken/l/bomb2.gif")
    data.goukenL["bomb3"] = PhotoImage(file = "image/gouken/l/bomb3.gif")
    data.goukenL["die1"] = PhotoImage(file = "image/gouken/l/die1.gif")
    data.goukenL["die2"] = PhotoImage(file = "image/gouken/l/die2.gif")
    data.goukenL["die3"] = PhotoImage(file = "image/gouken/l/die3.gif")
    data.goukenL["getHit1"] = PhotoImage(file = "image/gouken/l/getHit1.gif")
    data.goukenL["getHit2"] = PhotoImage(file = "image/gouken/l/getHit2.gif")

def initBombR(data):
    data.bombR["ryuBomb1"] = PhotoImage(file = "image/bomb/r/ryuBomb1.gif")
    data.bombR["ryuBomb2"] = PhotoImage(file = "image/bomb/r/ryuBomb2.gif")
    data.bombR["ryuBomb3"] = PhotoImage(file = "image/bomb/r/ryuBomb3.gif")
    data.bombR["ryuBomb4"] = PhotoImage(file = "image/bomb/r/ryuBomb4.gif")
    data.bombR["goukenBomb1"] = PhotoImage(file = "image/bomb/r/goukenBomb1.gif")
    data.bombR["goukenBomb2"] = PhotoImage(file = "image/bomb/r/goukenBomb2.gif")

def initBombL(data):
    data.bombL["ryuBomb1"] = PhotoImage(file = "image/bomb/l/ryuBomb1.gif")
    data.bombL["ryuBomb2"] = PhotoImage(file = "image/bomb/l/ryuBomb2.gif")
    data.bombL["ryuBomb3"] = PhotoImage(file = "image/bomb/l/ryuBomb3.gif")
    data.bombL["ryuBomb4"] = PhotoImage(file = "image/bomb/l/ryuBomb4.gif")
    data.bombL["goukenBomb1"] = PhotoImage(file = "image/bomb/l/goukenBomb1.gif")
    data.bombL["goukenBomb2"] = PhotoImage(file = "image/bomb/l/goukenBomb2.gif")

def initExplosion(data):
    data.explosion["explosion1"] = PhotoImage(file = "image/explosion/explosion1.gif")
    data.explosion["explosion2"] = PhotoImage(file = "image/explosion/explosion2.gif")
    data.explosion["explosion3"] = PhotoImage(file = "image/explosion/explosion3.gif")

def initGameOver(data):
    data.photo = {}
    data.photo["win"] = PhotoImage(file = "image/win.gif")
    data.photo["lose"] = PhotoImage(file = "image/lose.gif")



################################################################
######################## Mouse Pressed ###########################
################################################################

def mousePressed(event, data):
    # use event.x and event.y
    pass

################################################################
########################## Key Pressed ###########################
################################################################
def keyPressed(event, data):
    if event.keysym == "Escape":
        data.mode = "welcome"
        initWelcome(data)
    elif event.char == "0":
        data.music = not data.music
        print("changed")
    if data.mode == "welcome":
        keyPressedWelcome(event,data)
    elif data.mode == "mode":
        keyPressedMode(event, data)
    elif data.mode == "credit" or data.mode == "help":
        if event.keysym == "BackSpace":
            data.mode = "mode"
            initMode(data)
    elif data.mode == "stage":
        keyPressedStage(event, data)
    elif data.mode == "level":
        keyPressedLevel(event, data)
    elif data.mode == "round":
        keyPressedRound(event, data)
    elif data.mode == "game":
        keyPressedGame(event, data)
    elif data.mode == "gameOver":
        keyPressedGameOver(event, data)
    elif data.mode == "character":
        keyPressedCharacter(event, data)
        
    if data.mode == "multiplayer" or data.mode == "game":
        ms = str(event.char) + "\n" + str(event.keysym) + "\n" + str(data.player)
        data.server.send(bytes(ms, 'UTF-8'))
        

def keyPressedGameOver(event, data):
    data.mode = "welcome"

def keyPressedWelcome(event,data):
    if event.keysym != "Escape" and event.keysym != "BackSpace":
        data.mode = 'mode'
        initMode(data)

def keyPressedMode(event, data):
    if event.char == "s":
        data.mode = "stage"
        initStage(data)
    if event.char == "c":
        data.mode = "credit"
    if event.char == "h":
        data.mode = "help"
    if event.keysym == "BackSpace":
        data.mode = "welcome"
        init(data)
    if event.char == "m":
        data.mode = "multiplayer"
        try:
            initMultiplayerStage1(data)
            start_new_thread(handleServerMsg, (data,))
        except:
            data.mode = "mode"

#The server module is heavily modified based on the example given by Rohan during the mini-lecture series
def handleServerMsg(data):
    while True:
        data.msg = data.server.recv(1000).decode('UTF-8')
        print(data.msg)
        msgList = []
        if data.msg == "player1":
            data.player = "player1"
        elif data.msg == "player2":
            data.player = "player2"
        elif data.msg == "start":
            initMultiplayerStage2(data)
            initGameMode(data)
            data.mode = "game"
        elif data.msg == "player2start":
            data.player = "player2"
            initMultiplayerStage2(data)
            initGameMode(data)
            data.mode = "game"
        elif data.mode == "game" and data.msg != "player1" and data.msg != "player2" and data.msg != "start":
            for ms in data.msg.splitlines():
                msgList.append(ms)
            if msgList[2] != data.player: #No repeating motion
                if msgList[0] == "p":
                    data.pause = not data.pause
                elif msgList[0] == "t":
                    data.testing = not data.testing
                elif msgList[0] == "1":
                    data.stats = not data.stats
                if msgList[0] == "j":
                    keyPressedJ(data, "user", msgList[2])
                if msgList[0] == "k":
                    keyPressedK(data, "user", msgList[2])
                if msgList[0] == "l":
                    keyPressedL(data, "user", msgList[2])
                if msgList[0] == "s":
                    keyPressedS(data, "user", msgList[2])
                if msgList[0] == "d":
                    keyPressedD(data, "user", msgList[2])                   
                if msgList[0] == "a":
                    keyPressedA(data, "user", msgList[2])
                if msgList[0] == "w":
                    keyPressedW(data, "user", msgList[2])
                if msgList[1] == "space":
                    keyPressedSpace(data, "user", msgList[2])

def keyPressedStage(event, data):
    if event.keysym == "Left":
        data.leftArrowLightTimer = 5
        if data.stageChosen == 0:
            data.stageChosen = len(data.stages) - 1
        else:
            data.stageChosen -= 1
    elif event.keysym == "Right":
        data.rightArrowLightTimer = 5
        if data.stageChosen == len(data.stages) - 1:
            data.stageChosen = 0
        else:
            data.stageChosen += 1
    elif event.keysym == "space":
        data.mode = "character"
        initCharacter(data)
    elif event.keysym == "BackSpace":
        data.mode = "mode"
        initMode(data)

def keyPressedLevel(event, data):
    if event.keysym == "Left":
        data.leftArrowLightTimer = 5
        if data.aiLevel > 1:
            data.aiLevel -= 1
    elif event.keysym == "Right":
        data.rightArrowLightTimer = 5
        if data.aiLevel < 3:
            data.aiLevel += 1
    elif event.keysym == "space":
        data.mode = "round"
        initRound(data)
    elif event.keysym == "BackSpace":
        data.mode = "character"
        initCharacter(data)

def keyPressedCharacter(event, data):
    if event.keysym == "Left" or event.keysym == "Right":
        if event.keysym == "Left":
            data.leftArrowLightTimer = 5
        else:
            data.rightArrowLightTimer = 5
        if data.userChar == "RYU":
            data.userChar = "GOUKEN"
        else:
            data.userChar = "RYU"
    elif event.char == "d":
        data.description = not data.description
    elif event.keysym == "space":
        data.mode = "level"
        initLevel(data)
    elif event.keysym == "BackSpace":
        data.mode = "stage"
        initStage(data)

def keyPressedRound(event, data):
    if event.keysym == "Left":
        data.leftArrowLightTimer = 5
        if data.round > 1:
            data.round -= 2
    elif event.keysym == "Right":
        data.rightArrowLightTimer = 5
        data.round += 2
    elif event.keysym == "space":
        data.mode = "game"
        initGameMode(data)
    elif event.keysym == "BackSpace":
        data.mode = "level"
        initLevel(data)

#so that the AI can reuse these functions
def keyPressedJ(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.user == player:
            if fighter.pose == 'jump':
                fighter.motionTimer = 5
                fighter.jabUp(data)
            elif fighter.pose == "squat":
                fighter.motionTimer = 5
                fighter.jabSquat(data)
            elif fighter.pose != 'jab1':
                fighter.motionTimer = 5
                fighter.jab1(data)
            elif fighter.pose == 'jab1':
                fighter.motionTimer = 5
                fighter.jab2(data)
            fighter.updateMoveHistory(data, False)

def keyPressedK(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.user == player:
            if fighter.jumpPose == "jump":
                fighter.jumpKick(data)
            elif fighter.pose == "squat":
                fighter.motionTimer = 5
                fighter.kickSquat(data)
            elif fighter.y == data.groundLevel:
                fighter.motionTimer = 5
                fighter.kick(data)
            fighter.updateMoveHistory(data, False)

def keyPressedL(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.user == player:
            fighter.motionTimer = 4
            fighter.defend(data)
            fighter.updateMoveHistory(data, False)

def keyPressedS(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.user == player:
            fighter.motionTimer = 4
            fighter.squat(data)
            fighter.updateMoveHistory(data, False)

def keyPressedD(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.user == player:
            fighter.motionTimer = 4
            fighter.moveForward(data)
            #fighter.updateMoveHistory(data, False)

def keyPressedA(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.user == player:
            fighter.motionTimer = 4
            fighter.moveBackward(data)
            #fighter.updateMoveHistory(data, False)

def keyPressedW(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.y == data.groundLevel and fighter.user == player:
            fighter.jumpTimer = 8
            if fighter.pose == "walkForward":
                fighter.jumpForward(data)
            elif fighter.pose == "walkBackward":
                fighter.jumpBackward(data)
            else:
                fighter.jump(data)
            fighter.updateMoveHistory(data, True)

def keyPressedSpace(data, target, player):
    for fighter in data.fighters:
        if fighter.control == target and fighter.y == data.groundLevel and fighter.user == player:
            fighter.motionTimer = 6
            fighter.bomb(data)
            fighter.updateMoveHistory(data, False)

def keyPressedGame(event,data):
    if event.char == "p":
        data.pause = not data.pause
    elif event.char == "t":
        data.testing = not data.testing
    elif event.char == "1":
        data.stats = not data.stats
    if not data.pause and data.dyingTimer == -1:
        for fighter in data.fighters:
            if fighter.control == "user":
                if (fighter.motionTimer == 0 or
                    fighter.pose == "squat" or
                    fighter.pose == "walkForward" or
                    fighter.pose == "walkBackward" or
                    fighter.pose == "jab1"):
                    #To ensure that the move will not override the previous move too fast
                    if event.char == "j":
                        keyPressedJ(data, "user", data.player)
                    if event.char == "k":
                        keyPressedK(data, "user", data.player)
                    if event.char == "l":
                        keyPressedL(data, "user", data.player)
                    if event.char == "s":
                        keyPressedS(data, "user", data.player)
                    if event.char == "d":
                        keyPressedD(data, "user", data.player)                   
                    if event.char == "a":
                        keyPressedA(data, "user", data.player)
                    if event.char == "w":
                        keyPressedW(data, "user", data.player)
                    if event.keysym == "space":
                        keyPressedSpace(data, "user", data.player)

################################################################
########################### Timer Fired ###########################
################################################################
def timerFired(data):
    if data.mode == 'game':
        if not data.pause:
            timerFiredGame(data)
    elif data.mode == "stage":
        timerFiredArrow(data)
    elif data.mode == "level":
        timerFiredArrow(data)
    elif data.mode == "character":
        timerFiredArrow(data)
        
def timerFiredArrow(data):
    if data.leftArrowLightTimer != 0:
        data.leftArrowLightTimer -= 1
    if data.rightArrowLightTimer != 0:
        data.rightArrowLightTimer -= 1

def timerFiredGame(data):
    if not data.pause and not data.stats:
        timerFiredGame_timerControl(data)
        if data.realTimer > 60:
            timerFiredGame_checkWinner(data)
            timerFiredGame_jumpControl(data)
            timerFiredGame_motionControl(data)
            timerFiredGame_directionControl(data)
            timerFiredGame_bombControl(data)
            timerFiredGame_explosions(data)
            timerFiredGame_aiControl(data)

def timerFiredGame_timerControl(data):
        data.realTimer += 1
        if data.realTimer > 60 and data.realTimer % 20 == 0 and data.countDown != 0:
            data.countDown -= 1

def timerFiredGame_aiControl(data):
    if data.dyingTimer == -1:
        for fighter in data.fighters:
            if fighter.control == "pc":
                if fighter.pose != "die":
                    if (fighter.motionTimer == 0 or
                        fighter.pose == "squat" or
                        fighter.pose == "walkForward" or
                        fighter.pose == "walkBackward"):
                        fighter.ai(data)

def timerFiredGame_checkWinner(data):
    if len(data.fighters) > 0:       
        if data.dyingTimer == 1:
            if data.winner != None:
                initGameOver(data)
                data.mode = "gameOver"
            else:
                initGameMode(data, data.player1V, data.player2V)
                
        elif data.dyingTimer > 0:
            data.dyingTimer -= 1
        else:
            timerFiredGame_checkWinner_checkHp(data)
            timerFiredGame_checkWinner_checkTimer(data)

def timerFiredGame_checkWinner_checkTimer(data):
    if data.countDown <= 0:
        if data.fighters[0].hp > data.fighters[1].hp:
            timerFiredGame_checkWinner_die(0)
        else:
            timerFiredGame_checkWinner_die(1, data)

def timerFiredGame_checkWinner_die(n, data):
        data.fighters[n].die(data)
        if data.fighters[1-n].user == "player1":
            data.player1V += 1
            if data.player1V == data.round // 2 + 1:
                data.winner = data.fighters[1-n]
        elif data.fighters[1-n].user == "player2":
            data.player2V += 1
            if data.player2V == data.round // 2 + 1:
                data.winner = data.fighters[1-n]

def timerFiredGame_checkWinner_checkHp(data):            
    if data.fighters[0].hp <= 0:
        timerFiredGame_checkWinner_die(0, data)
    elif data.fighters[1].hp <= 0:
        timerFiredGame_checkWinner_die(1, data)

def timerFiredGame_jumpControl(data):
    for fighter in data.fighters:
        if fighter.jumpTimer != 0:
            if fighter.jumpTimer > 4:
                timerFiredGame_jumpControl_jump(fighter, data)
            elif fighter.jumpTimer <= 4:
                timerFiredGame_jumpControl_land(fighter, data)
            fighter.jumpTimer -= 1
        if fighter.jumpTimer == 0:
            fighter.jumpPose = None

def timerFiredGame_jumpControl_jump(fighter, data):
    if fighter.jumpPose == "jump":
        fighter.y -= 50
        fighter.coordinatesCalculator(data)
    elif fighter.jumpPose == "jumpForward":
        fighter.y -= 50
        fighter.x += 40
        if fighter.x < 0:
            fighter.x = 0
        elif fighter.x > data.width:
            fighter.x = data.width
        fighter.coordinatesCalculator(data)
    elif fighter.jumpPose == "jumpBackward":
        fighter.y -= 50
        fighter.x -= 40
        if fighter.x < 0:
            fighter.x = 0
        elif fighter.x > data.width:
            fighter.x = data.width
        fighter.coordinatesCalculator(data)

def timerFiredGame_jumpControl_land(fighter, data):
    if fighter.jumpPose == "jump":
        fighter.y += 50
        fighter.coordinatesCalculator(data)
    elif fighter.jumpPose == "jumpForward":
        fighter.y += 50
        fighter.x += 40
        if fighter.x < 0:
            fighter.x = 0
        elif fighter.x > data.width:
            fighter.x = data.width
        fighter.coordinatesCalculator(data)
    elif fighter.jumpPose == "jumpBackward":
        fighter.y += 50
        fighter.x -= 40
        if fighter.x < 0:
            fighter.x = 0
        elif fighter.x > data.width:
            fighter.x = data.width
        fighter.coordinatesCalculator(data)

def timerFiredGame_motionControl(data):
    for fighter in data.fighters:
        if fighter.motionTimer > 0:
            fighter.motionTimer -= 1
            if fighter.pose == "walkForward":
                if (fighter.x + fighter.speed < data.width) and (
                    fighter.x + fighter.speed > 0):
                    fighter.x += fighter.speed
                    fighter.coordinatesCalculator(data)
            elif fighter.pose == "walkBackward":
                if (fighter.x - fighter.speed < data.width) and (
                    fighter.x - fighter.speed > 0):           
                    fighter.x -= fighter.speed
                    fighter.coordinatesCalculator(data)
        elif fighter.motionTimer == 0:
            if fighter.y == data.groundLevel:
                fighter.stand(data)

def timerFiredGame_directionControl(data):                
    if len(data.fighters) == 2:
        #ensure two fighters are always face to face
        if data.fighters[0].x < data.fighters[1].x:
            data.fighters[0].dir = 1
            data.fighters[1].dir = -1
        elif data.fighters[0].x > data.fighters[1].x:
            data.fighters[0].dir = -1
            data.fighters[1].dir = 1

def timerFiredGame_bombControl(data):
    for fighter in data.fighters:
        if fighter.pose == "bomb" and fighter.motionTimer == 2:
            data.bombs.append(Bomb(fighter.leftHandX + 20 * fighter.dir, fighter.leftHandY, fighter.dir, fighter.name))
    for bomb in data.bombs:
        bomb.timerFiredGame_bomb(data)

def timerFiredGame_explosions(data):
    for explosion in data.explosions:
        explosion[2] -= 1
        if explosion[2] <= 0:
            data.explosions.remove(explosion)

################################################################
############################ RedrawAll ###########################
################################################################

def redrawAll(canvas, data):
    if data.mode == 'welcome':
        redrawAllWelcome(canvas,data)
    if data.mode == 'mode':
        redrawAllMode(canvas,data)
    if data.mode == 'game':
        redrawAllGame(canvas,data)
    if data.mode == 'gameOver':
        redrawAllGameOver(canvas, data)
    if data.mode == 'stage':
        redrawAllStage(canvas, data)
    if data.mode == 'level':
        redrawAllLevel(canvas, data)
    if data.mode == 'round':
        redrawAllRound(canvas, data)
    if data.mode == "credit":
        redrawAllCredit(canvas, data)
    if data.mode == "help":
        redrawAllHelp(canvas, data)
    if data.mode == "character":
        redrawAllCharacter(canvas, data)
    if data.mode == "multiplayer":
        redrawAllMultiplayer(canvas, data)

def redrawAllMultiplayer(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.photo["common_background"])
    canvas.create_text(data.width//2, data.height//2 + 2, text = "Waiting For the Next Player...", font = "Impact 45", fill = "Black")
    canvas.create_text(data.width//2, data.height//2, text = "Waiting for the Next Player...", font = "Impact 45", fill = "White")

    

def redrawAllCharacter(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.photo["common_background"])
    if data.description:
        redrawAllCharacter_description(canvas, data)
    else:
        if data.userChar == "RYU":
            canvas.create_image(data.width//2, data.height//2 + 170, image = data.photo["ryu"])
        else:
            canvas.create_image(data.width//2, data.height//2 + 30, image = data.photo["gouken"])
        canvas.create_text(data.width//2, data.height//2 + 2, text = data.userChar, font = "Impact 45", fill = "Black")
        canvas.create_text(data.width//2, data.height//2, text = data.userChar, font = "Impact 45", fill = "White")
    canvas.create_text(data.width//2, data.height//2 - 121, text = "SELECT YOUR CHARACTER", font = "YuppySC 20", fill = "Black")
    canvas.create_text(data.width//2, data.height//2 - 120, text = "SELECT YOUR CHARACTER", font = "YuppySC 20", fill = "White")
    redrawArrow(canvas, data)
    canvas.create_text(data.width//2, data.height//2 - 95, text = "Press D for his story", fill = "Black")
    canvas.create_text(data.width//2, data.height//2 - 93, text = "Press D for his story", fill = "White")
    canvas.create_text(data.width//2, data.height - 43, text = "Use LEFT and RIGHT to browse", fill = "White")
    canvas.create_text(data.width//2, data.height - 23, text = "Press SPACE to Select", fill = "White")




def redrawAllCharacter_description(canvas, data):
    if data.userChar == "RYU":
        canvas.create_image(data.width//2, data.height//2 + 170, image = data.photo["ryu"])
        canvas.create_text(data.width//2, data.height//2 - 37, text = '"The answer lies in the heart of battle."', font = "YuppySC 20", fill = "Black")
        canvas.create_text(data.width//2, data.height//2 - 35, text = '"The answer lies in the heart of battle."', font = "YuppySC 20", fill = "White")
        description = "Being highly focused on his training, Ryu aimed to \nbecome the strongest he can. However, his powers also \nattract several criminals who want to use him for their \nplans, such as M.Bison"
        canvas.create_text(data.width/2, data.height//2 + 17, text = description, fill = "Black")
        canvas.create_text(data.width/2, data.height//2 + 15, text = description, fill = "White")
    else:
        canvas.create_image(data.width//2, data.height//2 + 30, image = data.photo["gouken"])
        quote = '"Concentrate not on destroying your foe,\nbut on attaining your own victory."'
        canvas.create_text(data.width//2, data.height//2 - 47, text = quote, font = "YuppySC 20", fill = "Black")
        canvas.create_text(data.width//2, data.height//2 - 45, text = quote, font = "YuppySC 20", fill = "White")
        description = "Gouken and Akuma learned a murderous martial art \nstyle from their master, Goutesu. It included the special \ntechnique the Hadouken. After Goutetsu was killed by \nAkuma, Gouken refined these techniques, eliminating \nthe murderous energy they possessed. He would then \nteach his new style to two students, Ryu and Ken"
        canvas.create_text(data.width/2, data.height//2 + 35, text = description, fill = "Black")
        canvas.create_text(data.width/2, data.height//2 + 33, text = description, fill = "White")


def redrawAllHelp(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.photo["common_background"])
    canvas.create_image(data.width//2, data.height//2 + 20, image = data.photo["help"])
    canvas.create_text(data.width//2, data.height//2 - 140, text = "HELP", font = "Impact 40", fill = "White")
    canvas.create_text(data.width//2-200, data.height//2 - 140, text = "GAME CONTROL", font = "YuppySC 20", fill = "White")
    redrawAllHelp_gameControlName(canvas, data)
    redrawAllHelp_gameControlKeys(canvas,data)
    canvas.create_text(data.width//2+200, data.height//2 - 140, text = "OTHERS", font = "YuppySC 20", fill = "White")
    redrawAllHelp_othersName(canvas, data)
    redrawAllHelp_othersKeys(canvas, data)

def redrawAllHelp_othersName(canvas, data):
    canvas.create_text(410, data.height//2 - 110, anchor = W, text = "DURING THE GAME:", fill = "White")
    canvas.create_text(410, data.height//2 - 90, anchor = W, text = "Pause/Unpause:", fill = "White")
    canvas.create_text(410, data.height//2 - 70, anchor = W, text = "Turn On/Off Stats Center:", fill = "White")
    canvas.create_text(410, data.height//2 - 40, anchor = W, text = "IN ANY MENU:", fill = "White")
    canvas.create_text(410, data.height//2 - 20, anchor = W, text = "Back to the previous page:", fill = "White")
    canvas.create_text(410, data.height//2 + 10, anchor = W, text = "AT ANY TIME:", fill = "White")
    canvas.create_text(410, data.height//2 + 30, anchor = W, text = "To the Welcome page:", fill = "White")

def redrawAllHelp_othersKeys(canvas, data):
    canvas.create_text(580, data.height//2 - 90, anchor = W, text = "p", fill = "White")
    canvas.create_text(580, data.height//2 - 70, anchor = W, text = "1", fill = "White")
    canvas.create_text(580, data.height//2 - 20, anchor = W, text = "Delete", fill = "White")
    canvas.create_text(580, data.height//2 +30, anchor = W, text = "Escape", fill = "White")

def redrawAllHelp_gameControlName(canvas, data):
    canvas.create_text(40, data.height//2 - 110, anchor = W, text = "Jump:", fill = "White")
    canvas.create_text(40, data.height//2 - 90, anchor = W, text = "Crounch:", fill = "White")
    canvas.create_text(40, data.height//2 - 70, anchor = W, text = "Forward:", fill = "White")
    canvas.create_text(40, data.height//2 - 50, anchor = W, text = "Backward:", fill = "White")
    canvas.create_text(40, data.height//2 - 30, anchor = W, text = "Punch:", fill = "White")
    canvas.create_text(40, data.height//2 - 10, anchor = W, text = "Double Punch:", fill = "White")
    canvas.create_text(40, data.height//2 + 10, anchor = W, text = "Crounching Punch:", fill = "White")
    canvas.create_text(40, data.height//2 + 30, anchor = W, text = "Kick:", fill = "White")
    canvas.create_text(40, data.height//2 + 50, anchor = W, text = "Jumping Kick:", fill = "White")
    canvas.create_text(40, data.height//2 + 70, anchor = W, text = "Crounching Kick:", fill = "White")
    canvas.create_text(40, data.height//2 + 90, anchor = W, text = "Jump For/Backward:", fill = "White")
    canvas.create_text(40, data.height//2 + 110, anchor = W, text = "Defend:", fill = "White")
    canvas.create_text(40, data.height//2 + 130, anchor = W, text = "Hadoken:", fill = "White")

def redrawAllHelp_gameControlKeys(canvas, data):
    canvas.create_text(170, data.height//2 - 110, anchor = W, text = "W", fill = "White")
    canvas.create_text(170, data.height//2 - 90, anchor = W, text = "S", fill = "White")
    canvas.create_text(170, data.height//2 - 70, anchor = W, text = "D", fill = "White")
    canvas.create_text(170, data.height//2 - 50, anchor = W, text = "A", fill = "White")
    canvas.create_text(170, data.height//2 - 30, anchor = W, text = "J", fill = "White")
    canvas.create_text(170, data.height//2 - 10, anchor = W, text = "J + J", fill = "White")
    canvas.create_text(170, data.height//2 + 10, anchor = W, text = "S + J", fill = "White")
    canvas.create_text(170, data.height//2 + 30, anchor = W, text = "K", fill = "White")
    canvas.create_text(170, data.height//2 + 50, anchor = W, text = "W + K", fill = "White")
    canvas.create_text(170, data.height//2 + 70, anchor = W, text = "S + K", fill = "White")
    canvas.create_text(170, data.height//2 + 90, anchor = W, text = "W + D/A", fill = "White")
    canvas.create_text(170, data.height//2 + 110, anchor = W, text = "L", fill = "White")
    canvas.create_text(170, data.height//2 + 130, anchor = W, text = "Space", fill = "White")

def redrawAllCredit(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.photo["common_background"])
    canvas.create_image(data.width//2, data.height//2 + 150, image = data.photo["credit"])
    canvas.create_text(data.width//2, data.height//2 - 140, text = "CREDIT", font = "Impact 40", fill = "White")
    canvas.create_text(data.width//2, data.height//2 - 100, text = "Produced by:", font = "Impact 20", fill = "White")
    canvas.create_text(data.width//2, data.height//2 - 80, text = "Xiang (Alvin) Shi", fill = "White")
    canvas.create_text(data.width//2, data.height//2 - 50, text = "Thanks To", font = "Impact 20", fill = "White")
    canvas.create_text(data.width//2, data.height//2 - 30, text = "Rogultgot for the street fighter sprite sheet", fill = "White")
    canvas.create_text(data.width//2, data.height//2 - 15, text = "Tannerhelland.com for the background music", fill = "White")
    canvas.create_text(data.width//2, data.height//2, text = "Street Fighter Wiki for streetfighter related pictures and writeup", fill = "White")
    canvas.create_text(data.width//2, data.height//2 + 15, text = "Vasudev Ram for the music module", fill = "White")

def redrawAllLevel(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.photo["level_background"])
    canvas.create_text(data.width//2, data.height//2 - 121, text = "SELECT YOUR DIFFICULTY", font = "YuppySC 20", fill = "Black")
    canvas.create_text(data.width//2, data.height//2 - 120, text = "SELECT YOUR DIFFICULTY", font = "YuppySC 20", fill = "White")
    if data.aiLevel == 1:
        word = "DUMBASS"
    elif data.aiLevel == 2:
        word = "MEDIOCRE"
    elif data.aiLevel == 3:
        word = "INSANE"
    canvas.create_text(data.width//2, data.height//2 + 2, text = word, font = "Impact 45", fill = "Black")
    canvas.create_text(data.width//2, data.height//2, text = word, font = "Impact 45", fill = "White")
    canvas.create_text(data.width//2, data.height - 43, text = "Use LEFT and RIGHT to browse", fill = "Black")
    canvas.create_text(data.width//2, data.height - 23, text = "Press SPACE to Select", fill = "Black")
    redrawArrow(canvas, data)

def redrawAllRound(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.photo["level_background"])
    canvas.create_text(data.width//2, data.height//2 - 121, text = "SELECT THE ROUNDS", font = "YuppySC 20", fill = "Black")
    canvas.create_text(data.width//2, data.height//2 - 120, text = "SELECT THE ROUNDS", font = "YuppySC 20", fill = "White")
    canvas.create_text(data.width//2, data.height//2 + 2, text = str(data.round)+" ROUNDS", font = "Impact 45", fill = "Black")
    canvas.create_text(data.width//2, data.height//2, text = str(data.round)+" ROUNDS", font = "Impact 45", fill = "White")
    canvas.create_text(data.width//2, data.height - 43, text = "Use LEFT and RIGHT to browse", fill = "Black")
    canvas.create_text(data.width//2, data.height - 23, text = "Press SPACE to Select", fill = "Black")
    redrawArrow(canvas, data)

    
def redrawAllStage(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.stages[data.stageChosen][1])
    canvas.create_text(data.width//2, data.height//2 - 121, text = "SELECT YOUR STAGE", font = "YuppySC 20", fill = "Black")
    canvas.create_text(data.width//2, data.height//2 - 120, text = "SELECT YOUR STAGE", font = "YuppySC 20", fill = "White")
    canvas.create_text(data.width//2, data.height//2 + 2, text = data.stages[data.stageChosen ][0], font = "Impact 45", fill = "Black")
    canvas.create_text(data.width//2, data.height//2, text = data.stages[data.stageChosen ][0], font = "Impact 45", fill = "White")
    canvas.create_text(data.width//2, data.height - 43, text = "Use LEFT and RIGHT to browse", fill = "Black")
    canvas.create_text(data.width//2, data.height - 23, text = "Press SPACE to Select", fill = "Black")
    redrawArrow(canvas, data)

def redrawArrow(canvas, data):
    if data.leftArrowLightTimer == 0:
        colorLeft = "white"
    else:
        colorLeft = "orange"
    if data.rightArrowLightTimer == 0:
        colorRight = "white"
    else:
        colorRight = "orange"
    canvas.create_line(data.width // 2 + 247, data.height // 2 + 3, data.width // 2 + 197, data.height // 2 - 47, width = 10, fill = "black")
    canvas.create_line(data.width // 2 + 247, data.height // 2 - 3, data.width // 2 + 197, data.height // 2 + 47, width = 10, fill = "black")
    canvas.create_line(data.width // 2 + 250, data.height // 2 + 3, data.width // 2 + 200, data.height // 2 - 47, width = 10, fill = colorRight)
    canvas.create_line(data.width // 2 + 250, data.height // 2 - 3, data.width // 2 + 200, data.height // 2 + 47, width = 10, fill = colorRight)
    canvas.create_line(data.width // 2 - 247, data.height // 2 - 3, data.width // 2 - 197, data.height // 2 + 47, width = 10, fill = "black")
    canvas.create_line(data.width // 2 - 247, data.height // 2 + 3, data.width // 2 - 197, data.height // 2 - 47, width = 10, fill = "black")
    canvas.create_line(data.width // 2 - 250, data.height // 2 - 3, data.width // 2 - 200, data.height // 2 + 47, width = 10, fill = colorLeft)
    canvas.create_line(data.width // 2 - 250, data.height // 2 + 3, data.width // 2 - 200, data.height // 2 - 47, width = 10, fill = colorLeft)
    
def redrawAllWelcome(canvas,data):
    data.photo["background"] = PhotoImage(file = "image/welcome_page.gif")
    background = data.photo["background"]
    canvas.create_image(0, 0,anchor = NW, image=background)
    canvas.create_text(data.width//2, data.height - 114, text = "Street Fighter", font = "impact 83", fill = "Black")
    canvas.create_text(data.width//2, data.height - 115, text = "Street Fighter", font = "impact 80", fill = "White")
    canvas.create_text(data.width//2, data.height -53, text = "112 Special Edition", font = "Impact 25", fill = "Black")
    canvas.create_text(data.width//2, data.height -55, text = "112 Special Edition", font = "Impact 25", fill = "Red")
    canvas.create_line(90,data.height - 53, data.width//2 -100,data.height -53, fill = "black", width = 3)
    canvas.create_line(data.width - 90,data.height - 53, data.width//2 + 100,data.height -53, fill = "black", width = 3)
    canvas.create_line(90,data.height - 55, data.width//2 -100,data.height -55, fill = "red", width = 3)
    canvas.create_line(data.width - 90,data.height - 55, data.width//2 + 100,data.height -55, fill = "red", width = 3)
    canvas.create_text(data.width//2, data.height - 23, text = "Press any key to Start",font = "YuppySC 15", fill = "White")
    canvas.create_text(data.width//2, data.height - 24, text = "Press any key to Start",font = "YuppySC 15", fill = "Black")

def redrawAllMode(canvas, data):
    background = data.photo["background"]
    canvas.create_image(0, 0,anchor = NW, image=background)
    canvas.create_text(data.width//2-2, data.height//2-40, text = "Single Player Mode", font = "Calibri 35")
    canvas.create_text(data.width//2, data.height//2-43, text = "Single Player Mode", font = "Calibri 35", fill = "white")
    canvas.create_text(data.width//2-139, data.height//2-43, text = "S", font = "Calibri 35", fill = "orange")
    canvas.create_text(data.width//2-2, data.height//2 + 5, text = "Multi-Player Mode", font = "Calibri 35")
    canvas.create_text(data.width//2, data.height//2 + 2, text = "Multi-Player Mode", font = "Calibri 35", fill = "white")
    canvas.create_text(data.width//2 - 127, data.height//2 + 2, text = "M", font = "Calibri 35", fill = "orange")
    canvas.create_text(data.width//2-2, data.height//2 + 50, text = "Help", font = "Calibri 35")
    canvas.create_text(data.width//2, data.height//2 + 47, text = "Help", font = "Calibri 35", fill = "white")
    canvas.create_text(data.width//2-24, data.height//2 + 47, text = "H", font = "Calibri 35", fill = "orange")
    canvas.create_text(data.width//2-2, data.height//2 + 95, text = "Credit", font = "Calibri 35")
    canvas.create_text(data.width//2, data.height//2 + 92, text = "Credit", font = "Calibri 35", fill = "white")
    canvas.create_text(data.width//2-35, data.height//2 + 92, text = "C", font = "Calibri 35", fill = "orange")
    canvas.create_text(data.width//2, data.height - 23, text = "Press the leading letter to Enter")

def redrawAllGame(canvas, data):
    drawBattleField(canvas, data)
    drawInfo(canvas, data)
    for fighter in data.fighters:
        fighter.drawHPBar(canvas, data)
        fighter.drawImage(canvas, data)
        if data.testing:
            fighter.draw(canvas, data)
    for bomb in data.bombs:
        bomb.drawBomb(canvas, data)
    drawExplosions(canvas,data)
    drawOpening(canvas, data)
    drawKO(canvas, data)
    if data.stats:
        drawStatsSheet(canvas, data)
    if data.pause:
        drawPause(canvas, data)

def drawPause(canvas, data):
    canvas.create_text(data.width//2, data.height//2, text = "PAUSED", font = "impact 50", fill = "red")


def drawStatsSheet(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.otherPhoto["projector_screen"])
    canvas.create_text(data.width // 2, data.margin * 2, text = "Data Center", font = "Impact 20", fill = "white")
    canvas.create_text(data.width // 2 - 100, data.margin * 2, text = "PLAYER 1", font = "Impact 17", fill = "grey")
    canvas.create_text(data.width // 2 + 100, data.margin * 2, text = "PLAYER 2", font = "Impact 17", fill = "grey")
    canvas.create_text(data.width // 2, data.margin * 5, text = "JUMP", font = "Impact 30", fill = "white")
    canvas.create_text(data.width // 2, data.margin * 8, text = "SQUAT", font = "Impact 30", fill = "white")
    canvas.create_text(data.width // 2, data.margin * 11, text = "DEFEND", font = "Impact 30", fill = "white")
    canvas.create_text(data.width // 2, data.margin * 14, text = "ATTACK", font = "Impact 30", fill = "white")
    canvas.create_text(data.width // 2, data.margin * 16.5, text = "KICK", font = "Impact 25", fill = "grey")
    canvas.create_text(data.width // 2, data.margin * 19, text = "JAB", font = "Impact 25", fill = "grey")
    canvas.create_text(data.width // 2, data.margin * 21.5, text = "BOMB", font = "Impact 25", fill = "grey")

    canvas.create_rectangle(data.width // 2 - 60, data.margin * 5 - 10, data.width // 2 - 60 - int(data.player1.defendPropensity * 300), data.margin * 5 + 10, fill = "red", width = 0)
    canvas.create_rectangle(data.width // 2 - 60, data.margin * 8 - 10, data.width // 2 - 60 - int(data.player1.squatPropensity * 300), data.margin * 8 + 10, fill = "orange", width = 0)
    canvas.create_rectangle(data.width // 2 - 60, data.margin * 11 - 10, data.width // 2 - 60 - int(data.player1.defendPropensity * 300), data.margin * 11 + 10, fill = "yellow", width = 0)
    canvas.create_rectangle(data.width // 2 - 60, data.margin * 14 - 10, data.width // 2 - 60 - int(data.player1.attackPropensity * 300), data.margin * 14 + 10, fill = "green", width = 0)
    canvas.create_rectangle(data.width // 2 - 60, data.margin * 16.5 - 7, data.width // 2 - 60 - int(data.player1.kickPropensity * 300), data.margin * 16.5 + 7, fill = "blue", width = 0)
    canvas.create_rectangle(data.width // 2 - 60, data.margin * 19 - 7, data.width // 2 - 60 - int(data.player1.jabPropensity * 300), data.margin * 19 + 7, fill = "purple", width = 0)
    canvas.create_rectangle(data.width // 2 - 60, data.margin * 21.5 - 7, data.width // 2 - 60 - int(data.player1.bombPropensity * 300), data.margin * 21.5 + 7, fill = "grey", width = 0)

    canvas.create_rectangle(data.width // 2 + 60, data.margin * 5 - 10, data.width // 2 + 60 + int(data.player2.defendPropensity * 300), data.margin * 5 + 10, fill = "red", width = 0)
    canvas.create_rectangle(data.width // 2 + 60, data.margin * 8 - 10, data.width // 2 + 60 + int(data.player2.squatPropensity * 300), data.margin * 8 + 10, fill = "orange", width = 0)
    canvas.create_rectangle(data.width // 2 + 60, data.margin * 11 - 10, data.width // 2 + 60 + int(data.player2.defendPropensity * 300), data.margin * 11 + 10, fill = "yellow", width = 0)
    canvas.create_rectangle(data.width // 2 + 60, data.margin * 14 - 10, data.width // 2 + 60 + int(data.player2.attackPropensity * 300), data.margin * 14 + 10, fill = "green", width = 0)
    canvas.create_rectangle(data.width // 2 + 60, data.margin * 16.5 - 7, data.width // 2 + 60 + int(data.player2.kickPropensity * 300), data.margin * 16.5 + 7, fill = "blue", width = 0)
    canvas.create_rectangle(data.width // 2 + 60, data.margin * 19 - 7, data.width // 2 + 60 + int(data.player2.jabPropensity * 300), data.margin * 19 + 7, fill = "purple", width = 0)
    canvas.create_rectangle(data.width // 2 + 60, data.margin * 21.5 - 7, data.width // 2 + 60 + int(data.player2.bombPropensity * 300), data.margin * 21.5 + 7, fill = "grey", width = 0)

def drawKO(canvas, data):
    if data.dyingTimer >= 0:
        canvas.create_image(data.width//2, data.height//2, image = data.otherPhoto["KO"])


def drawOpening(canvas, data):
    if data.realTimer > 5 and data.realTimer <= 20:
        canvas.create_text(data.width//2, data.height//2, text = "ROUND " + str(data.currentRound), font = "impact 50", fill = "red")
    if data.realTimer > 25 and data.realTimer <= 40:
        canvas.create_text(data.width//2, data.height//2, text = "READY", font = "impact 50", fill = "red")
    if data.realTimer > 45 and data.realTimer <= 55:
        canvas.create_text(data.width//2, data.height//2, text = "FIGHT", font = "impact 60", fill = "red")
        canvas.create_rectangle(0,data.height//2 - 30, data.width//2-100, data.height//2 + 30, width = 0, fill = "red")
        canvas.create_rectangle(data.width//2+100,data.height//2 - 30, data.width, data.height//2 + 30, width = 0, fill = "red")
    if data.realTimer > 55 and data.realTimer <= 60:
        canvas.create_rectangle(0,data.height//2 - 30, (data.width//2-100) * (60-data.realTimer)//5, data.height//2 + 30, width = 0, fill = "red")
        canvas.create_rectangle(data.width//2+100+(data.width//2-100) * (data.realTimer-55)//5,data.height//2 - 30, data.width, data.height//2 + 30, width = 0, fill = "red")


def drawExplosions(canvas,data):
    for explosion in data.explosions:
        (x,y) = (explosion[0], explosion[1])
        if explosion[2] >= 5:
            canvas.create_image(x,y,image = data.explosion["explosion1"])
        elif explosion[2] >= 3:
            canvas.create_image(x,y,image = data.explosion["explosion2"])
        elif explosion[2] < 3:
            canvas.create_image(x,y,image = data.explosion["explosion3"])

def drawBattleField(canvas, data):
    photo = data.stages[data.stageChosen][1]
    canvas.create_image(0, 0,anchor = NW, image=photo)

    
def drawInfo(canvas, data):
    #countDown
    canvas.create_text(data.width//2, data.margin*1.5, text = data.countDown, font ="impact 32", fill = "black")
    canvas.create_text(data.width//2, data.margin*1.5, text = data.countDown, font ="impact 30", fill = "red")
    #currentRound
    canvas.create_text(data.width//2, data.margin*3, text = "Round " + str(data.currentRound))
    #currentWin
    canvas.create_text(data.width//2 + 50, data.margin*3, anchor = W, text = data.player2VStr)
    canvas.create_text(data.width//2 - 50, data.margin*3, anchor = E, text = reverseString(data.player1VStr))


def redrawAllGameOver(canvas, data):
    if data.winner.user == data.player:
        canvas.create_image(0, 0, anchor = NW, image = data.photo["win"])
        canvas.create_text(data.width//2, data.height//2 + 2, text = "YOU WON", font = "impact 60", fill = "Grey")
        canvas.create_text(data.width//2, data.height//2, text = "YOU WON", font = "impact 60", fill = "White")
    elif data.winner.user != data.player:
        canvas.create_image(0, 0, anchor = NW, image = data.photo["lose"])
        canvas.create_text(data.width//2, data.height//2 + 2, text = "YOU LOST", font = "impact 60", fill = "Grey")
        canvas.create_text(data.width//2, data.height//2, text = "YOU LOST", font = "impact 60")

####################################
# use the run function as-is
#The following code was taken from the 15112 course website
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 50 # milliseconds
    init(data)
    try:
        start_new_thread(musicPlayer,())
    except:
        pass
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
    
goRun = True
if goRun:
    run(640, 360)

testAll()
m
