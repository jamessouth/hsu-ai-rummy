from collections import Counter


def getRun(hand, ord):
    res = [hand[0]]
    for i, x in enumerate(hand):
        if i != 0:
            if x[1] == hand[i-1][1]:  # same suit
                if ord[x[0]]-ord[hand[i-1][0]] == 1:  # rank diff of 1
                    res.append(x)
                else:  # diff != 1
                    if len(res) > 2:
                        return res
                    else:
                        res.clear()
                        res.append(x)
            else:  # diff suit
                if len(res) > 2:
                    return res
                else:
                    res.clear()
                    res.append(x)
    if len(res) > 2:
        return res
    else:
        return []


def getSafeDiscard(hand, dict, ordlo, ordhi, lastDiscard):
    lorun = getRun(getOrderedHand(hand, ordlo), ordlo)
    hirun = getRun(getOrderedHand(hand, ordhi), ordhi)
    ones = [x for x in hand if dict[x[0]] == 1]
    trueSingles = [
        x for x in ones if x not in lorun and x not in hirun and x != lastDiscard]
    if trueSingles == []:
        pairs = [x for x in hand if dict[x[0]] == 2]
        truePairs = [
            x for x in pairs if x not in lorun and x not in hirun and x != lastDiscard]
        if truePairs == []:
            trips = [x for x in hand if dict[x[0]] == 3]
            trueTrips = [
                x for x in trips if x not in lorun and x not in hirun and x != lastDiscard]
            if trueTrips == []:
                last = [x for x in trips if x != lastDiscard]
                return getRankOrderedHand(last, ordlo)[len(last)-1]
            else:
                return getRankOrderedHand(trueTrips, ordlo)[len(trueTrips)-1]
        else:
            return getRankOrderedHand(truePairs, ordlo)[len(truePairs)-1]
    else:
        return getRankOrderedHand(trueSingles, ordlo)[len(trueSingles)-1]


def getCardsPlayableOnMelds(melds, ord):
    res = []
    for meld in melds:
        first = meld[0]
        if first != meld[3]:
            suit = meld[1]
            last = meld[-2]
            print("run", suit, first, last)
            if first == "A":
                print("ace lo run")
                res.append(ord[ord.index(last)+1]+suit)
            elif last == "A":
                print("ace hi run")
                res.append(ord[ord.index(first)-1]+suit)
            else:
                print("mid run")
                res.append(ord[ord.index(last)+1]+suit)
                res.append(ord[ord.index(first)-1]+suit)
        else:
            print("set", first)
            if len(meld) > 9:
                print("4 cards")
            else:
                print("3 cards")
                for s in "CDHS":
                    if s not in meld[1]+meld[4]+meld[7]:
                        res.append(first+s)
    return res


def getDictHand(hand):
    return Counter(c[0] for c in hand)


def getOrderedHand(hand, ord):
    return sorted(sorted(hand, key=lambda c: ord[c[0]]), key=lambda c: c[1])


def getRankOrderedHand(hand, ord):
    return sorted(hand, key=lambda c: ord[c[0]])


# suitRankAceHi = [] # list of cards in our hand
# suitRankAceLo = [] # list of cards in our hand
# handDict = {} # dict of cards in our hand
# hand = [] # list of cards in our hand
# oppoHand = [] # list of cards in oppo hand
# oppoHandLen = 0 # number of cards in oppo hand
# discard = [] # list of cards organized as a stack
# stock = [] # list of cards in the stock
# cannot_discard = ""

# ['7C', 'TC', 'JC', 'QC', 'KC', '2D', '3D', '7D', 'QD', '2H', '7H', 'JH', 'QH', 'KH', 'AS', '2S', '7S', 'TS']

    # logging.info("discard is "+ discard[0])

    # def getSafeDiscard(hand, dict, ordlo, ordhi, lastDiscard):
    # # aces low for scoring so only ace low order used
    # maxval = -1
    # counter = 1
    # hiRank = ""
    # while counter < 3:
    #     for rank, count in dict.items():
    #         if count == counter:
    #             if ordlo[rank] > maxval:
    #                 maxval = ordlo[rank]
    #                 hiRank = rank
    #     l = [c for c in hand if c[0] == hiRank and c != lastDiscard and c not in getRun(
    #         hand, ordlo) and c not in getRun(hand, ordhi)]
    #     if l == []:
    #         counter += 1
    #         maxval = -1
    #         hiRank = ""
    #     else:
    #         return l[0]
    # return "TC"
