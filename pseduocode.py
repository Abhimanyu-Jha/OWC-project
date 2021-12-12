t=0
simulation_time=0

class User:
    def __init__(self,position,ap_index,speed):
        self.position = position
        self.connectedAP=ap_index
        self.speed=speed

class AP:
    def __init__(self,position,index):
        self.position = position
        self.index = index

# Create Users and APs at different points in space
users=[User([0,0],0,5),User([0,0],0,5),User([0,0],0,5),User([0,0],0,5)]
APs=[AP([0,0],0),AP([0,0],1),AP([0,0],2),AP([0,0],3)]

while t<simulation_time:
    # for all users in the space calulcate gamma=ObjFunc(SINR +delta_SINR) for all APs, do this every after every delta_t seconds
    # this will be a 2D matrix where we store gamma values of all APs for all Users
    # if for any user, some other AP (handover_candidate) is providing better gamma than the AP its connected(original_AP) to
    # then evaluate if we should move the AP or do the handover aka "start ttt timer"
        # find position for AP(moving candidate) which would give an new_gamma>=handover_candidate_gamma+threshold (threshold should be >0 because otherwise if users moves by even a samll unit, it will again very likely find a better AP)
            # this is the position on an imaginary circle with user as center and radius as distance between user and handover_candidate
            # the position is that point on this circle which is closest to all other Users connected to the original_AP
        # is this new position causing other Users to have an SINR lower than some threshold? -> then do handover instead
        # is this new position causing original_AP to move some distance d>d_max? -> then do handover instead
        # if all is good, move the AP to new position and repeat steps.
    t+=1


def objectiveFunction(AP,users):
    # SINR OF AP at person's location
    # SINR of AP at person's location, ttt time in the future
    return None