def DumpToEnv(outputData: dict, leadingKey: str = ''):
    envStr = ''
    for key in outputData:
        envKey: str = key.replace("-", "_").upper()
        if isinstance(outputData[key], dict):
            envKey = f'{leadingKey}{envKey}__'
            envStr += DumpToEnv(outputData[key], leadingKey=envKey)
        else:
            payload: str = outputData[key].replace("-", "_").upper()
            envStr += f'{leadingKey}{envKey}={payload.replace("-", "_").upper()}\n'
    return envStr


def MergeDictData(oldDict: dict, newDict: dict) -> dict:
    mergedDict = dict(oldDict)
    for key in newDict:
        if key in mergedDict:
            if isinstance(mergedDict[key], dict) and isinstance(newDict[key], dict):
                mergedDict[key] = MergeDictData(mergedDict[key], newDict[key])
            else:
                mergedDict[key] = newDict[key]
        else:
            mergedDict[key] = newDict[key]
    return mergedDict
