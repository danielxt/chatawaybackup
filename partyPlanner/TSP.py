import json
import urllib.request
import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
import copy


endpoint = "https://maps.googleapis.com/maps/api/directions/json?"
API_KEY = "AIzaSyD_uCvYRugvLnWNqBQ1nkzY8Tw96KHTrc0"

# returns travel duration in seconds between 2 points depending on mode of transport
def twoPointDuration(origin, destination, mode):
    nav_request = f'origin={origin}&destination={destination}&mode={mode}&key={API_KEY}'
    request = endpoint + nav_request
    response = urllib.request.urlopen(request).read()
    directions = json.loads(response)
    routes = directions['routes']
    if len(routes) == 0:
        return float('inf')
    legs = routes[0]['legs']

    return legs[0]['duration']['value']


# returns adjacency matrix of duration between all points in SECONDS
def buildAM(locations, mode): 
    # 1. clean up input so + instead of spaces
    copyLocations = copy.deepcopy(locations)
    for i in range(len(copyLocations)):
        copyLocations[i] = copyLocations[i].replace(" ", "+")
    
    # 2. build the am
    AM = [[float('inf') for _ in range(len(copyLocations))] for _ in range(len(copyLocations))]
    for startIndex in range(len(copyLocations)):
        for endIndex in range(len(copyLocations)):
            if (startIndex != endIndex):
                AM[startIndex][endIndex] = twoPointDuration(copyLocations[startIndex], copyLocations[endIndex], mode)
            else:
                AM[startIndex][endIndex] = float('inf')

    return AM


# takes in dist of 2 lists: 'exlusive', 'non_exclusive', transport mode and start location
# user will visit all non exclusive locations, ONE exclusie location, and the start location
# returns min permutation, duration tuple
def bestTSP(inputDict, mode, startLocation):
    
    locationList = []
    bestPerm = []
    bestDuration = float('inf')

    finalPerm = []
    if len(inputDict['exclusive']) == 0:
        for nonExcData in inputDict['non_exclusive']: # go to all non exc
            locationList.append(nonExcData['name'])

            finalPerm.append(nonExcData)

            locationList.append(startLocation) # come back to start
            finalPerm.append({'name' : startLocation, 'photo' : ""})

            AM = np.array(buildAM(locationList, mode))
            permutation, duration = solve_tsp_dynamic_programming(AM)
            if (duration < bestDuration):
                bestDuration = duration
                bestPerm = [finalPerm[i] for i in permutation]
                # bestPerm = [locationList[i] for i in permutation]
            
            locationList = [] # clear for next iteration
            finalPerm = []
    else:
        for excData in inputDict['exclusive']: 
            locationList.append(excData['name']) # only go to 1 exlusive location
            finalPerm.append(excData)

            for nonExcData in inputDict['non_exclusive']: # go to all non exc
                locationList.append(nonExcData['name'])
                finalPerm.append(nonExcData)

            locationList.append(startLocation) # come back to start
            finalPerm.append({'name' : startLocation, 'photo' : ""})

            AM = np.array(buildAM(locationList, mode))
            permutation, duration = solve_tsp_dynamic_programming(AM)
            if (duration < bestDuration):
                bestDuration = duration
                bestPerm = [finalPerm[i] for i in permutation]
                # bestPerm = [locationList[i] for i in permutation]
            
            locationList = [] # clear for next iteration
            finalPerm = []

    return bestPerm, bestDuration


if __name__ == '__main__':
    # simulate input to func
    acceptedModes = ["driving", "walking", "bicycling", "transit"]
    startLocation = "Bob and Betty Beyster Building"
    myDict = {
        'exclusive' : [],
        'non_exclusive' : [{'name': 'Supino Pizzeria New Center', 'address': '6519 Woodward Ave, Detroit, MI 48202, USA', 'location': {'latitude': 42.3693506, 'longitude': -83.07299809999999}, 'photo': 'places/ChIJvdoAh0HTJIgRIpnHvXRsWx8/photos/AcJnMuEQStvjTV6NgeeBESAM1Y_FPakYNZ9-X9wQ10HBM3lb5gPNeRdFq4aDtah8ypjsu6IHvukAvXquU4ljD6OJZbiVj7Vjw5uGULVsU2psjSQOYEqzeRMbasiE96DRmmSPnIYMeGXRRZxPj5xhMlFMxXQ1tg8IwO9VzljL'}, {'name': '42.3068,-83.7059', 'photo': ''}]
    }
    tspPath = bestTSP(myDict, acceptedModes[0], startLocation)[0]
    output = []
    for point in tspPath:
        # print(point)
        places = {}
        places['waypoint'] = point['name']
        places['photoID'] = point['photo']
        output.append(places)
    print(output)