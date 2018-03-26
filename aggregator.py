import json
import time
from libbgg.apiv1 import BGG
import libbgg.apiv2

class AuctionGameData:
    def __init__(self, itemId, user, gameName, gameId, country):
        self.itemId = itemId
        self.user = user
        self.gameName = gameName
        self.gameId = gameId
        self.country = country

    def export(self):
        return {
            'itemId' : self.itemId,
            'user' : self.user,
            'game' : self.gameName,
            'gameId' : self.gameId,
            'country' : self.country
        }

class AuctionData:
    def __init__(self):
        self.data = []

    def add(self, itemId, user, gameName, gameId,country):
        self.data.append(AuctionGameData(itemId, user,  gameName, gameId, country).export())
    def export(self):
        return json.dumps(
            {
                'completionTime' : int(time.time()),
                'data' : self.data
            }
        )

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

    for item in metaList['item']:

        tracer += 1
        if (tracer > 3):
            break

        if (item['objecttype'] != 'geeklist'):
            continue
        auctionList = RetrieveGeekList(conn_list, item['objectid'])
        if (auctionList is None):
            continue
        username = auctionList['username']['TEXT']
        userInfo = RetrieveUser(conn_user, username)
        country = ''
        if (userInfo is not None):
            country = userInfo['user']['country']['value']

        for item in auctionList['item']:
            user = item['username']
            itemId = item['id']
            gameName = item['objectname']
            gameId = item['objectid']
            result.add(itemId, user, gameName, gameId, country)

    return result

def main():
    metaAuctionId = 66420
    conn_list = BGG()
    conn_user = libbgg.apiv2.BGG()

    result = RetrieveAuctionGeeklists(conn_list, conn_user, metaAuctionId)

    print result.export()

if (__name__ == "__main__"):
    main()
