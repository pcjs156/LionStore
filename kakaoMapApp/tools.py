from math import radians, degrees, sin, cos, acos

zoomVal = "20 30 50 100 250 500 1000 2000 4000 8000 16000 32000 64000 128000".split(' ')
zoomLevel = {level:int(meter) for level, meter in zip(range(1, len(zoomVal)+1), zoomVal)}

# 위도 경도를 입력받아 미터 단위로 반환
def meterDistance(latLon1, latLon2):
    lat1, lon1 = latLon1
    lat2, lon2 = latLon2

    theta = lon1 - lon2
    dist = sin(radians(lat1)) * sin(radians(lat2)) + cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(theta))

    dist = acos(dist)
    dist = degrees(dist)
    dist = dist * 60 * 1.1515

    dist = dist * 1609.344

    return dist


def getZoomLevel(centerLatLon:list, infos:list, zoomRadius:int=5):
    distancePair = dict()
    # 판매처 : 거리 쌍
    for info in infos:
        distancePair[info] = meterDistance(centerLatLon, (info.seller.latitude, info.seller.longitude))
    
    # 가장 가까운 상위 (최대) 5개의 쌍
    distancePair = list(distancePair.items())
    distancePair = sorted(distancePair, key=lambda pair: pair[1])[:zoomRadius]
    # 그 중 가장 먼 판매처
    closestInfo, closestDistance = distancePair[-1]

    for i in range(1, len(zoomVal)+1):
        if zoomLevel[i] > closestDistance:
            ret = i-1
            break

    return ret if ret != 1 else 1