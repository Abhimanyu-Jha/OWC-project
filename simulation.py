import turtle
import random
import time
import numpy as np
random.seed(0)

# Setup Simulation Screen
wn = turtle.Screen()
wn.bgcolor("black")
wn.title("User Simulation")
AP_color_codes = ["red", "yellow", "green", "blue",
                  "orange", "purple", "pink", "white", "black"]
speedFactor = 0.01
ttt = 1000
hom = 0.001
wn.tracer(0)


class AP:
    def __init__(self, position, index, isWifi):
        self.position = position
        self.index = index
        self.turtle = turtle.Turtle()
        self.turtle.color(AP_color_codes[index])
        self.turtle.penup()
        self.turtle.shape("square" if (isWifi) else "triangle")
        self.turtle.speed(6)
        self.turtle.goto(position[0], position[1])


class User:
    def __init__(self, position, hostAP, speed):
        self.position = position
        self.hostAP = hostAP
        self.speed = speed
        self.turtle = turtle.Turtle()
        self.turtle.color(hostAP.turtle.color()[0])
        self.turtle.penup()
        self.turtle.shape("circle")
        self.turtle.speed(0)
        self.turtle.goto(position[0], position[1])
        self.turtle.dy = speed*random.choice([-1, 1])*speedFactor
        self.turtle.dx = speed*random.choice([-1, 1])*speedFactor

# function to calculate euclidean distance


def euclidieanDistance(pos1, pos2):
    return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5


l_AP1 = AP([-150, -150], 0, isWifi=False)
l_AP2 = AP([-150, 150], 1, isWifi=False)
l_AP3 = AP([150, -150], 2, isWifi=False)
l_AP4 = AP([150, 150], 3, isWifi=False)
w_AP5 = AP([0, 0], 4, isWifi=True)
aps = [l_AP1, l_AP2, l_AP3, l_AP4, w_AP5]

users = []
user_1 = User([-100, 0], hostAP=w_AP5, speed=2)
user_2 = User([80, 0], hostAP=w_AP5, speed=2)
user_3 = User([-100, -200], hostAP=w_AP5, speed=3)
users = [user_1, user_2, user_3]
# check closest AP, set as hostAP
for user in users:
    for ap in aps:
        user_pos = [user.turtle.xcor(), user.turtle.ycor()]
        og_dist = euclidieanDistance(user_pos, user.hostAP.turtle.pos())
        new_dist = euclidieanDistance(user_pos, ap.turtle.pos())
        if og_dist > new_dist:
            user.hostAP = ap
            user.turtle.color(ap.turtle.color()[0])


def drawPerimeter():
    pen = turtle.Turtle()
    pen.color("white")
    pen.penup()
    pen.speed(0)
    pen.goto(-300, -300)
    pen.pendown()
    pen.goto(-300, 300)
    pen.goto(300, 300)
    pen.goto(300, -300)
    pen.goto(-300, -300)
    pen.hideturtle()
    print("pen color is", pen.color()[0])


def signalStrength(pos1, pos2):
    if(euclidieanDistance(pos1, pos2) == 0):
        return 1000
    else:
        return euclidieanDistance(pos1, pos2)**-1


def SINR(tx_ap, user):
    # SINR between two positions
    user_pos = user.turtle.pos()
    signal = signalStrength(tx_ap.turtle.pos(), user_pos)
    interference = 0
    for ap in aps:
        if ap.index == tx_ap.index:
            continue
        interference += signalStrength(ap.turtle.pos(), user_pos)
    noise = 0
    return signal/(interference+noise)


def getOptimalPoint(center, radius, existing_users, currPos, d_max=200, wifi=True, radius_step_size=5, angle_step_size=10, min_SINR=0.1):
    # existing_users is a list of users connected to that AP which we are considering to move
    coords = []
    for r in np.arange(0, radius + radius_step_size/2, radius_step_size):
        for theta in np.arange(0, 360 + angle_step_size/2, angle_step_size):
            x = center[0] + r * np.cos(np.radians(theta))
            y = center[1] + r * np.sin(np.radians(theta))
            if euclidieanDistance([x, y], currPos) <= d_max:
                coords.append((x, y))

    optimalPoint = None
    optimalSumSINR = None
    for (x, y) in coords:
        newAp = AP([x, y], -1, isWifi=wifi)
        sumSINR = 0
        flag = True
        for user in existing_users:
            new_SINR = SINR(newAp, user)
            if new_SINR < min_SINR:
                flag = False
                break
            else:
                sumSINR += new_SINR

        if flag:
            if (optimalSumSINR is None) or (sumSINR > optimalSumSINR):
                optimalPoint = [x, y]
                optimalSumSINR = sumSINR

    return optimalPoint


# draw perimeter
drawPerimeter()


def wallBounceCheck(user):
    # wall bounce
    if user.turtle.ycor() < -300 or user.turtle.ycor() > 300:
        user.turtle.dy *= -1

    if user.turtle.xcor() > 300 or user.turtle.xcor() < -300:
        user.turtle.dx *= -1


def objectiveFunction(ap, user):
    return SINR(ap, user) + (SINR(ap, user) - SINR(ap, user))/ttt


def moveAP(ap, targetPos):
    DX = targetPos[0]-ap.turtle.xcor()-20
    DY = targetPos[1]-ap.turtle.ycor()-20
    steps = 700  # inversely proportional to speed
    ctr = 0
    while(ctr < steps):
        wn.update()
        ap.turtle.setx(ap.turtle.xcor()+(DX/steps))
        ap.turtle.sety(ap.turtle.ycor()+(DY/steps))

        if ap.turtle.xcor() > 300:
            ap.turtle.setx(300)
        if ap.turtle.xcor() < -300:
            ap.turtle.setx(-300)

        if ap.turtle.ycor() > 300:
            ap.turtle.sety(300)
        if ap.turtle.ycor() < -300:
            ap.turtle.sety(-300)

        ctr += 1
        # keep users moving while we move AP
        for _user in users:
            _user.turtle.setx(_user.turtle.xcor()+_user.turtle.dx)
            _user.turtle.sety(_user.turtle.ycor()+_user.turtle.dy)
            wallBounceCheck(_user)


t = 0

while True:
    wn.update()
    for user in users:
        # move users acc to their speeds
        user.turtle.setx(user.turtle.xcor()+user.turtle.dx)
        user.turtle.sety(user.turtle.ycor()+user.turtle.dy)
        user_pos = user.turtle.pos()

        # if for any user, some other AP (handover_candidate) is providing better SINR than the AP its connected(original_AP) to, then evaluate(make Decision) if we should move the AP or do the handover
        SINR_host = SINR(user.hostAP, user)
        # print("SINR_host",SINR_host)
        # print("user",user.speed)
        for ap in aps:
            if SINR(ap, user) >= SINR_host + hom:
                print("handover test")
                if(ap.index == user.hostAP.index):
                    continue
                else:
                    # start ttt
                    makeDecision = True
                    tc = 0

                    while(tc < ttt):
                        print(tc)
                        if not(SINR(ap, user) >= SINR_host + hom):
                            makeDecision = False
                            break
                        wn.update()
                        for _user in users:
                            # keep users moving while we evaluate ttt
                            _user.turtle.setx(
                                _user.turtle.xcor()+_user.turtle.dx)
                            _user.turtle.sety(
                                _user.turtle.ycor()+_user.turtle.dy)
                            wallBounceCheck(_user)
                        tc += 1

                    if(makeDecision):
                        # find targetAP
                        objFuncVals = [objectiveFunction(
                            _ap, user) for _ap in aps]
                        targetAP = aps[objFuncVals.index(max(objFuncVals))]
                        print("Need to see handover or move AP")
                        # see whether to handover to this targetAP or move hostAP

                        # find position for AP(moving candidate) which would give an new_gamma>=handover_candidate_gamma+threshold (threshold should be >0 because otherwise if users moves by even a samll unit, it will again very likely find a better AP)

                        # this is the position within an imaginary circle with user as center and radius as distance between user and handover_candidate
                        # the position is that point on this circle which is closest to all other Users connected to the original_AP
                        dist_from_target_AP = euclidieanDistance(
                            targetAP.turtle.pos(), user_pos)
                        dist_from_host_AP = euclidieanDistance(
                            user.hostAP.turtle.pos(), user_pos)
                        host_AP_users = [
                            _user for _user in users if _user.hostAP.index == user.hostAP.index]
                        getOptimalPoint(center=user.turtle.pos(), radius=dist_from_target_AP,
                                        existing_users=host_AP_users, currPos=user.hostAP.turtle.pos())
                        # is this new position causing other Users to have an SINR lower than some threshold? -> then do handover instead
                        # is this new position causing original_AP to move some distance d>d_max? -> then do handover instead
                        # if all is good, move the AP to new position and repeat steps.

                        print("ap.index", targetAP.index)

                        choiceVar = random.choice([-1, 1])
                        # choiceVar=1

                        if choiceVar == 1:
                            # Move AP
                            moveAP(user.hostAP, user.turtle.pos())
                        else:
                            # Handover
                            user.hostAP = targetAP
                            user.turtle.color(ap.turtle.color()[0])
                    else:
                        # do nothing
                        print("False Alarm, AP_candidate didnt pass ttt test")

        # random direction change every 3s (interval)
        if(t % 3000 == 0):
            user.turtle.dx *= random.choice([-1, 1])
            user.turtle.dy *= random.choice([-1, 1])

        # wall bounce
        wallBounceCheck(user)
    t += 1


wn.mainloop()
