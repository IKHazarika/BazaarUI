#defining some useful functions to use later

def stars_and_bars(num_objects_remaining, num_bins_remaining, filled_bins=()):
    """
    The Stars and Bars (https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics)) problem can be thought of as
    1. Putting m-1 bars ("|") in amongst a row of n stars
    OR
    2. Putting n balls into m bins.

    This program lists all the possible combinations by doing so.
    """
    if num_bins_remaining > 1:
        # case 1: more than one bins left
        novel_arrangement = []  # receptacle to contain newly generated arrangements.
        for num_distributed_to_the_next_bin in range(0, num_objects_remaining + 1):
            # try putting in anything between 0 to num_objects_remaining of objects into the next bin.
            novel_arrangement.extend(
                stars_and_bars(
                    num_objects_remaining - num_distributed_to_the_next_bin,
                    num_bins_remaining - 1,
                    filled_bins=filled_bins + (num_distributed_to_the_next_bin,),
                )
                # one or multiple tuple enclosed in a list
            )
        return novel_arrangement
    else:
        # case 2: reached last bin. Termintae recursion.
        # return a single tuple enclosed in a list.
        return [
            filled_bins + (num_objects_remaining,),
        ]

print(stars_and_bars(5, 2))

############################################################################

#to start the game, we set the following parameters:
#number of players, number of commodities, number of factories, number of faces, starting money, total number of rolls
#number of factories for each commodity, number of factories for each player, inventory for each factory

totalRolls = 2
numPlayers = 2
numCommodities = 2
numFactories = 2
numFaces = 2
startingMoney = 1
factoryPerCommodity = [1, 1]
factoryPerPlayer = [1, 1]
inventoryList = [1, 1]

#each state of the game contains the following information:
#position of each player p: players -> factories
#ownership of each factory omega: factories -> players
#inventory of each factory and personal stock of each player: I: factories U players -> Z_+
#money of each player M: players -> Z_+

import numpy as np

commodityList = []
while len(commodityList) < numFactories:
    commodity = np.random.randint(numCommodities)
    if factoryPerCommodity[commodity] != 0:
        factoryPerCommodity[commodity] -= 1
        commodityList.insert(len(commodityList), commodity)
print('commodity list is')
print(commodityList)

positionList = []
for i in range(numPlayers):
    positionList.insert(len(positionList), 0)
print('position list is')
print(positionList)

ownerList = []
while len(ownerList) < numFactories:
    owner = np.random.randint(numPlayers)
    if factoryPerPlayer[owner] != 0:
        factoryPerPlayer[owner] -= 1
        ownerList.insert(len(ownerList), owner)
print('ownerList is')
print(ownerList)


inventoryList = []
for i in range(numFactories):
    inventoryList.insert(len(inventoryList), 1)
for i in range(numPlayers):
    inventoryList.insert(len(inventoryList), np.repeat(0, numCommodities))
print('inventory list is')
print(inventoryList)

moneyList = []
for i in range(numPlayers):
    moneyList.insert(len(moneyList), 1)
print('money list is')
print(moneyList)

consumptionList = np.repeat(0, numPlayers)

initialState = [positionList, ownerList, inventoryList, moneyList, consumptionList]

#############################################################################################

#Here we define the production functions and the utility functions
#For now, for the sake of simplicity, each production function is simply a Cobb-Douglas one, with equal powers, and roughly CRS. Same for the utility function

#distribution tells us how each factory's inventory is used, if there are 3 factories then:
#distribution = [[0,2,3,1], [2,2,3,1], [1,2,1,0]] for example, where the fourth entry for each commodity is consumption, the rest tell us how much to be used to produce the ith commodity

def productionFunction(distribution):
    outputList = np.repeat(0, numFactories + 1)
    for fac in range(numFactories + 1):
        myComm = numCommodities
        if fac != numFactories:
            myComm = commodityList[fac]
        inputVector = np.repeat(0, numCommodities)
        for otherFac in range(numFactories):
            otherFacCommodity = commodityList[otherFac]
            otherFacQuantity = distribution[otherFac][fac]
            inputVector[otherFacCommodity] += otherFacQuantity
        base = 1
        for comm in range(len(inputVector)):
            if comm != myComm:
                base *= inputVector[comm]
        base = np.around(base ** (1 / (numCommodities - 1)), 0)
        outputList[fac] = base
    return outputList

##############################################################################################

#The game starts with a dice roll, following which it is player 0's turn
#Player 0 first checks how many units of each commodity she has: that is, the sum of inventories of each commodity + the personal stock of that commodity
#She decides how much of each commodity to consume, and how much to use to produce another commodity
#She also chooses how much to offer to buy the firm she is on, and in case of rejection, how much to buy for how much
#The owner of the firm in question accepts the first or second offer, or rejects both
#Next dice roll happens
#The game continues

#When it stumbles upon a node with player N
#It should create 6 nodes with player as specified in the original node
#These 6 nodes would specify that after it, the next player should be whoever is the owner of its current tile

#When it stumbles upon a node with player i and action-that-generated-it an integer
#It should create one node each for each action, with player as specified in the original node
#These new nodes per action should specify that after them, the next player would be N

#When it stumbles upon a node with player i and action-that-generated-it is a tuple
#It should create three nodes with player specified in the original node
#Each node should specify that the next player is the grandparent's player + 1 modulo numPlayers

import itertools

nodes = [[-1, 'N', 'first roll', 1, 0, 1]] #each node is of the form [parent, player, action, probability, next player, rolls so far]
childlessNodes = [0]
states = [initialState]
numRolls = 0
whoseTurn = 0

for i in childlessNodes:
    if i < len(nodes):
        if i % 2000 == 0:
            print(i)
        if nodes[i][5] <= totalRolls:
            if nodes[i][1] == 'N':
                for j in range(numFaces):
                    newNode = [i, nodes[i][4], j + 1, 1 / numFaces, 0, nodes[i][5]]
                    childlessNodes.insert(len(childlessNodes), len(nodes))
                    newPositionList = states[i][0]
                    newOwnerList = states[i][1]
                    newInventoryList = states[i][2]
                    newMoneyList = states[i][3]
                    newConsumptionList = states[i][4]
                    newPositionList[nodes[i][4]] += j + 1
                    if newPositionList[nodes[i][4]] >= numFactories:
                        newPositionList[nodes[i][4]] = newPositionList[nodes[i][4]] - numFactories
                    nextPlayer = newOwnerList[newPositionList[nodes[i][4]]]
                    newNode[4] = nextPlayer
                    nodes.insert(len(nodes), newNode)
                    states.insert(len(states), [newPositionList, newOwnerList, newInventoryList, newMoneyList, newConsumptionList])
                    #childlessNodes.remove(i)
            
            if type(nodes[i][1]) is int and type(nodes[i][2]) is int:
                myState = states[i]
                ownedFactories = []
                for j in range(numFactories):
                    if myState[1][j] == nodes[i][1]:
                        ownedFactories.insert(len(ownedFactories), j)
                quantitiesOwned = np.repeat(0, numCommodities)
                for j in ownedFactories:
                    commodityOfConcern = commodityList[j]
                    quantitiesOwned[commodityOfConcern] += myState[2][j]
                for j in range(len(myState[2][numFactories + nodes[i][1]])):
                    quantitiesOwned[j] += myState[2][numFactories + nodes[i][1]][j]
                
                effectiveInventories = np.repeat(0, numCommodities + numFactories)
                for j in ownedFactories:
                    effectiveInventories[j] = myState[2][j]
                for j in range(len(myState[2][numFactories + nodes[i][1]])):
                    effectiveInventories[numFactories + j] = myState[2][numFactories + nodes[i][1]][j]
                
                #each action of the player is of the following form:
                #a tuple of length numFactories + numCommodities
                #each element of the tuple is another tuple, that distributes the available quantity of the commodities into consumption, and for the production in each factory, giving us the size of the tuple numFactories + 1
                #for example, if the quantities owned are [0, 3, 3] then an action could be
                #a = [[0,0,0,0], [1,2,0,0], [0,1,1,1]]
                #I adopt the convention where the last element is the consumption
                
                tempList = []
                for item in range(numCommodities + numFactories):
                    tempList.append([])
                for j in range(len(tempList)):
                    a = []
                    for k in range(effectiveInventories[j] + 1):
                        x = stars_and_bars(k, numFactories + 1)
                        a.insert(len(a), x)
                    for k in a:
                        for l in k:
                            tempList[j].insert(len(tempList[j]), l)
                
                for j in tempList:
                    toRemove = []
                    for k in j:
                        for l in range(len(k) - 1):
                            if k[l] > 0 and not(l in ownedFactories) and not(k in toRemove):
                                toRemove.append(k)
                    for k in toRemove:
                        j.remove(k)
                
                distributionList = []
                
                for element in itertools.product(*tempList):
                    distributionList.append(element)
                
                moneyAvailable = myState[3][nodes[i][1]]
                currentFactory = myState[0][nodes[i][1]]
                currentInventory = myState[2][currentFactory]
                
                offerList = []
                
                for j in range(moneyAvailable + 1):
                    for k in range(moneyAvailable + 1):
                        for l in range(currentInventory + 1):
                            offerList.append([j, k, l]) #offer is of the form [money offered to buy the factory, money offered to buy inventory, how much of the inventory]
                
                for j in offerList:
                    if j[1] == 0 and j[2] > 0:
                        offerList.remove(j)
                
                actionList = []
                
                for element in itertools.product(*[distributionList, offerList]):
                    actionList.append(element)
                
                nextPlayer = myState[1][myState[0][nodes[i][1]]]
                
                if nextPlayer != nodes[i][1]:
                    for j in actionList:
                        if nextPlayer == numPlayers:
                            nextPlayer = 0
                        newNode = [i, nextPlayer, j, 1, 'N', nodes[i][5]] #was i[5] before
                        nodes.append(newNode)
                        childlessNodes.insert(len(childlessNodes), len(nodes))
                        
                        """
                        quantitiesConsumed = []
                        for item in range(numCommodities):
                            quantitiesConsumed.append(0)
                        
                        for k in range(numFactories):
                            commodityOfConcern = commodityList[k]
                            quantitiesConsumed[commodityOfConcern] += j[0][k][-1]
                        for k in range(numFactories, numCommodities):
                            quantitiesConsumed[k] += j[0][k][-1]
                        """
                        newPositionList = states[i][0]
                        newOwnerList = states[i][1]
                        newInventoryList = states[i][2]
                        newMoneyList = states[i][3]
                        newConsumptionList = states[i][4]
                        
                        for k in range(numFactories):
                            newInventoryList[k] -= j[0][k][-1]
                        newOutput = productionFunction(j[0])
                        
                        for k in range(len(newOutput) - 1):
                            newInventoryList[k] = newOutput[k]
                        newConsumptionList[nodes[i][1]] = newOutput[-1]
                        
                        states.append([newPositionList, newOwnerList, newInventoryList, newMoneyList, newConsumptionList])
                    #childlessNodes.remove(i)
                
            
            if type(nodes[i][1]) is int and type(nodes[i][2]) is tuple:
                
                #case 1: the offer to buy the firm is accepted
                newPositionList = states[i][0]
                newOwnerList = states[i][1]
                newInventoryList = states[i][2]
                newMoneyList = states[i][3]
                newConsumptionList = states[i][4]
                
                buyer = nodes[nodes[i][0]][1]
                nextPlayer = buyer + 1
                if nextPlayer == numPlayers:
                    nextPlayer = 0
                nodes.append([i, 'N', 'Sell firm', 1, nextPlayer, nodes[i][5] + 1])
                offeredMoney = nodes[i][2][1][1]
                newMoneyList[buyer] -= offeredMoney
                newMoneyList[nodes[i][1]] += offeredMoney
                states.append([newPositionList, newOwnerList, newInventoryList, newMoneyList, newConsumptionList])
                
                #case 2: the offer to buy inventory is accepted
                newPositionList = states[i][0]
                newOwnerList = states[i][1]
                newInventoryList = states[i][2]
                newMoneyList = states[i][3]
                newConsumptionList = states[i][4]
                
                offeredMoney = nodes[i][2][1][1]
                newMoneyList[buyer] -= offeredMoney
                newMoneyList[nodes[i][1]] += offeredMoney
                offeredInventory = nodes[i][2][1][2]
                commodityOfConcern = commodityList[newPositionList[buyer]]
                newInventoryList[numFactories + buyer][commodityOfConcern] += offeredInventory
                nodes.append([i, 'N', 'Sell firm', 1, nextPlayer, nodes[i][5] + 1])
                states.append([newPositionList, newOwnerList, newInventoryList, newMoneyList, newConsumptionList])
                childlessNodes.append(len(nodes) - 1)
                
                #case 3: both the offers are rejected
                newPositionList = states[i][0]
                newOwnerList = states[i][1]
                newInventoryList = states[i][2]
                newMoneyList = states[i][3]
                newConsumptionList = states[i][4]
                
                nodes.append([i, 'N', 'Sell firm', 1, nextPlayer, nodes[i][5] + 1])
                states.append([newPositionList, newOwnerList, newInventoryList, newMoneyList, newConsumptionList])
                childlessNodes.append(len(nodes))
                
                #childlessNodes.remove(i)

print('len(nodes) is')
print(len(nodes))
print("nodes is")
print(nodes)
print("childlessNodes is")
print(childlessNodes)

##############################################################################################

