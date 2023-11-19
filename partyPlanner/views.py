from django.shortcuts import render
from django.http import JsonResponse
from django.apps import apps
import json
from django.views.decorators.csrf import csrf_exempt
from . import TSP
from LangChain import DuoLangChain
from gplace import GPlaceFinder
# Create your views here.
# export OPENAI_API_KEY=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
tokenDict = {}


messageDict = {}

class locationObj:
    name = ""
    image = ""
    def __init__(self, name_in, image_in):
        self.name = name_in
        self.image = image_in

def test(request):
    context = {'data': request.is_secure()}
    return render(request, 'home.html', context)

@csrf_exempt
def newMessage(request):
    body = json.load(request)
    response = "testMsg"

    if body['sessionToken'] not in tokenDict:
        model, opening_msg = DuoLangChain.construct()
        tokenDict[body['sessionToken']] = model
        return JsonResponse({'msg': opening_msg})
    else:
        model = tokenDict[body['sessionToken']]
        response, done = model.invoke(body['userMessage'])
        if (done):
            messageDict['lastMessage'] = response
        return JsonResponse({'msg': response, 'done': done})
        
@csrf_exempt
def finalPlan(request):
    body = json.load(request)
    startLocation = f"{body['lat']},{body['lng']}" 
    model = tokenDict[body['sessionToken']]
    allPlaces = model.places
    mode = model.mode
    gplace = GPlaceFinder()


    nonExclusiveData = []
    exclusiveData = []



    for place in allPlaces:
        excecData, nonExcData = gplace.query(place) # name, photo, location, addresss
        nonExclusiveData = nonExclusiveData + nonExcData
        exclusiveData = exclusiveData + excecData

        # non_exc = [x["name"] for x in nonExcData]
        # exc = [x["name"] for x in excecData]

        # nonExclusiveNames = nonExclusiveNames + non_exc
        # exclusiveNames = exclusiveNames + exc

        # non_excPic = [x["photo"] for x in nonExcData]
        # excPic = [x["photo"] for x in excecData]

        # nonExclusivePhotos = nonExclusivePhotos + non_excPic
        # exclusivePhotos = exclusivePhotos + excPic


    myDict = {
        'exclusive' : exclusiveData,
        'non_exclusive' : nonExclusiveData,
    }

    print(exclusiveData)
    print("----------------")
    print(nonExclusiveData)
    print("----------------")


    tspPath = TSP.bestTSP(myDict, mode, startLocation)[0]
    print(tspPath)
    print(len(exclusiveData))
    print(len(nonExclusiveData))
    
    output = []
    for point in tspPath:
        # print(point)
        places = {}
        places['waypoint'] = point['name']
        places['photoID'] = point['photo']
        output.append(places)
        # response.append(point['name'])
        # responseImg.append(point['photo'])
    # if len(tspPath) != 0:
    #     while (tspPath[0]['name'] != startLocation): # rotate elements so that first is always the start location
    #         # print(f"start:{startLocation} front{tspPath[0]}")
    #         tmp = tspPath[0]
    #         tspPath.pop(0)
    #         tspPath.append(tmp)
    #     response = [i['name'] for i in tspPath]

    # response = "testResponse"
    return JsonResponse({
        'places': output, 'mode' : mode, 'lastMessage' : messageDict['lastMessage']})



    
