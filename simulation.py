import turtle
import random
import time
random.seed(0)

# Setup Simulation Screen
wn= turtle.Screen()
wn.bgcolor("black")
wn.title("User Simulation")
AP_color_codes=["red","yellow","green","blue","orange","purple","pink","white","black"]
speedFactor=0.01
ttt=1000
hom=0.001
wn.tracer(0)

class AP:
    def __init__(self,position,index,isWifi):
        self.position = position
        self.index = index
        self.turtle=turtle.Turtle()
        self.turtle.color(AP_color_codes[index])
        self.turtle.penup()
        self.turtle.shape("square" if (isWifi) else "triangle")
        self.turtle.speed(0)
        self.turtle.goto(position[0],position[1])

class User:
    def __init__(self,position,hostAP,speed):
        self.position = position
        self.hostAP=hostAP
        self.speed=speed
        self.turtle=turtle.Turtle()
        self.turtle.color(hostAP.turtle.color()[0])
        self.turtle.penup()
        self.turtle.shape("circle")
        self.turtle.speed(0)
        self.turtle.goto(position[0],position[1])
        self.turtle.dy=speed*random.choice([-1, 1])*speedFactor
        self.turtle.dx=speed*random.choice([-1, 1])*speedFactor

# function to calculate euclidean distance
def euclidieanDistance(pos1,pos2):
    return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5

l_AP1=AP([-150,-150],0,isWifi=False)
l_AP2=AP([-150,150],1,isWifi=False)
l_AP3=AP([150,-150],2,isWifi=False)
l_AP4=AP([150,150],3,isWifi=False)
w_AP5=AP([0,0],4,isWifi=True)
aps=[l_AP1,l_AP2,l_AP3,l_AP4,w_AP5]

users=[]
user_1=User([-100,0],hostAP=w_AP5,speed=1)
user_2=User([80,0],hostAP=w_AP5,speed=2)
user_3=User([-100,-200],hostAP=w_AP5,speed=3)
users=[user_1,user_2,user_3]
# check closest AP, set as hostAP
for user in users:
    for ap in aps:
        user_pos=[user.turtle.xcor(),user.turtle.ycor()]
        og_dist=euclidieanDistance(user_pos,user.hostAP.position)
        new_dist=euclidieanDistance(user_pos,ap.position)
        if og_dist>new_dist:
            user.hostAP=ap
            user.turtle.color(ap.turtle.color()[0])

def drawPerimeter():
    pen=turtle.Turtle()
    pen.color("white")
    pen.penup()
    pen.speed(0)
    pen.goto(-300,-300)
    pen.pendown()
    pen.goto(-300,300)
    pen.goto(300,300)
    pen.goto(300,-300)
    pen.goto(-300,-300)
    pen.hideturtle()
    print("pen color is",pen.color()[0])


def signalStrength(pos1,pos2):
    return euclidieanDistance(pos1,pos2)**-1

def SINR(tx_ap,user):
    # SINR between two positions
    user_pos=user.turtle.pos()
    signal=signalStrength(tx_ap.position,user_pos)
    interference=0
    for ap in aps:
        if ap.index==tx_ap.index:
            continue
        interference+=signalStrength(ap.position,user_pos)
    noise=0
    return signal/(interference+noise)

# draw perimeter
drawPerimeter()

def wallBounceCheck(user):
    # wall bounce
    if user.turtle.ycor()<-300 or user.turtle.ycor()>300:
        user.turtle.dy*=-1

    if user.turtle.xcor()>300 or user.turtle.xcor()<-300:
        user.turtle.dx*=-1

def objectiveFunction(ap,user):
    return SINR(ap,user) + (SINR(ap,user) - SINR(ap,user))/ttt

t=0
while True:
    wn.update()
    for user in users:
        # move users acc to their speeds
        user.turtle.setx(user.turtle.xcor()+user.turtle.dx)
        user.turtle.sety(user.turtle.ycor()+user.turtle.dy)
        user_pos=user.turtle.pos()

        # if for any user, some other AP (handover_candidate) is providing better gamma than the AP its connected(original_AP) to, then evaluate(make Decision) if we should move the AP or do the handover 
        SINR_host=SINR(user.hostAP,user)
        # print("SINR_host",SINR_host)
        # print("user",user.speed)
        for ap in aps:
            if SINR(ap,user) >= SINR_host + hom:
                print("handover test")
                if(ap.index==user.hostAP.index):
                    continue
                else:
                    # start ttt
                    makeDecision=True
                    tc=0

                    while(tc<ttt):
                        print(tc)
                        if not(SINR(ap,user) >= SINR_host + hom):
                            makeDecision=False
                            break
                        wn.update()
                        for _user in users:
                            # keep users moving while we evaluate ttt
                            _user.turtle.setx(_user.turtle.xcor()+_user.turtle.dx)
                            _user.turtle.sety(_user.turtle.ycor()+_user.turtle.dy)
                            wallBounceCheck(_user)
                        tc+=1

                    if(makeDecision):
                        #find targetAP
                        objFuncVals=[objectiveFunction(_ap,user) for _ap in aps]
                        targetAP=aps[objFuncVals.index(max(objFuncVals))]

                        # see whether to handover to this targetAP or move targetAP
                        print("Need to see handover or move AP")
                        print("ap.index",targetAP.index)
                        user.hostAP=ap
                        user.turtle.color(ap.turtle.color()[0])
                    else:
                        # do nothing
                        print("False Alarm, AP_candidate didnt pass ttt test")

        #random direction change every 3s (interval)
        if(t%3000==0):
            user.turtle.dx*=random.choice([-1, 1])
            user.turtle.dy*=random.choice([-1, 1])

        # wall bounce
        wallBounceCheck(user)
    t+=1




wn.mainloop()