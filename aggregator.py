import json
import time
from libbgg.apiv1 import BGG
import libbgg.apiv2

class AuctionGameData:
    def __init__(self, listId, itemId, user, gameName, gameId, userCountry, userState):
        self.listId = listId
        self.itemId = itemId
        self.user = user
        self.gameName = gameName
        self.gameId = gameId
        self.userCountry = userCountry
        self.userState = userState


    def export(self):
        return {
            'listId' : self.listId,
            'itemId' : self.itemId,
            'user' : self.user,
            'game' : self.gameName,
            'gameId' : self.gameId,
            'country' : self.userCountry,
            'state' : self.userState
        }

class AuctionData:
    def __init__(self):
        self.data = []

    def add(self, listId, itemId, user, gameName, gameId, userCountry, userState):
        self.data.append(AuctionGameData(listId, itemId, user,  gameName, gameId, userCountry, userState).export())
    def export(self):
        return self.data

def ExecuteGetGeekList(conn, listId):
    pulled = False
    watchdog = 0
    while (not pulled):
        try:
            time.sleep(3)
            return conn.get_geeklist(listId)
        except:
            watchdog += 1
            if (watchdog > 50):
                return None

def ExecuteGetUser(conn, username):
    pulled = False
    watchdog = 0
    while (not pulled):
        try:
            time.sleep(3)
            return conn.get_user(username)
        except:
            watchdog += 1
            if (watchdog > 50):
                return None

def RetrieveGeekList(conn, listId):
    results = ExecuteGetGeekList(conn, listId)
    if (results is None):
        return None
    watchdog = 0

    while ('message' in results):
        watchdog += 1
        if (watchdog > 50):
            return None
        results = ExecuteGetGeekList(conn, listId)

    return results['geeklist']

def RetrieveUser(conn, user):
    result = ExecuteGetUser(conn, user)
    if (result is None):
        return None
    watchdog = 0
    while ('message' in result):
        watchdog += 1
        if (watchdog > 50):
            return None
        result = ExecuteGetUser(conn, user)
    return result

def RetrieveAuctionGeeklists(conn_list, conn_user, metaAuctionId):
    metaList = RetrieveGeekList(conn_list, metaAuctionId)

    if (metaList is None):
        return None

    result = AuctionData()

    tracer = 0

    for metaItem in metaList['item']:

        tracer += 1
        if (tracer > 3):
            break

        if (metaItem['objecttype'] != 'geeklist'):
            continue
        auctionList = RetrieveGeekList(conn_list, metaItem['objectid'])
        if (auctionList is None):
            continue
        username = auctionList['username']['TEXT']
        userInfo = RetrieveUser(conn_user, username)
        country = ''
        if (userInfo is not None):
            userCountry = userInfo['user']['country']['value']
            userState = userInfo['user']['stateorprovince']['value']

        for item in auctionList['item']:
            user = item['username']
            itemId = item['id']
            gameName = item['objectname']
            gameId = item['objectid']
            result.add(metaItem['objectid'], itemId, user, gameName, gameId, userCountry, userState)

    return result

def main():
    metaAuctionId = 66420
    conn_list = BGG()
    conn_user = libbgg.apiv2.BGG()

    timeStarted = int(time.time())
    result = RetrieveAuctionGeeklists(conn_list, conn_user, metaAuctionId)
    timeCompleted = int(time.time())

    print json.dumps({'timeStarted' : timeStarted, 'timeCompleted' : timeCompleted, 'data' : result.export()})

if (__name__ == "__main__"):
    main()
