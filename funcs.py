from collections import Counter


def getRun(hand, ord):
    res = [hand[0]]
    for i, x in enumerate(hand):
        if i != 0:
            if x[1] == hand[i-1][1]:  # same suit
                if ord[x[0]]-ord[hand[i-1][0]] == 1:  # rank diff of 1
                    res.append(x)
                else:  # diff != 1
                    res.clear()
                    res.append(x)
            else:  # diff suit
                if len(res) > 2:
                    return res
                else:
                    res.clear()
                    res.append(x)


def getDictHand(hand):
    return Counter(c[0] for c in hand)


def getOrderedHand(hand, ord):
    return sorted(sorted(hand, key=lambda c: ord[c[0]]), key=lambda c: c[1])

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
