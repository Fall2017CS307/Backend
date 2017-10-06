from flask import jsonify

def apiDecorate(returnDict, status_code, response):
    apiReturn = {}
    apiReturn['api'] = "Datonate"
    apiReturn['version'] = 1.0
    apiReturn['status'] = status_code
    apiReturn['response'] = response
    for key,keyVal in returnDict.iteritems():
        apiReturn[key] = keyVal
    print response
    print status_code
    return jsonify(apiReturn)   