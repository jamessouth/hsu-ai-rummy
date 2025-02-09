import requests
from fastapi import FastAPI
import fastapi
from pydantic import BaseModel
import uvicorn
import os
import signal
import logging
from funcs import *
# import pytest

"""
By Todd Dole, Revision 1.2
Written for Hardin-Simmons CSCI-4332 Artificial Intelligence
Revision History
1.0 - API setup
1.1 - Very basic test player
1.2 - Bugs fixed and player improved, should no longer forfeit
"""


base_rank_order = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
ace_hi_rank_order = base_rank_order+["A"]
ace_lo_rank_order = ["A"]+base_rank_order
aceHiOrder = {key: i for i, key in enumerate(ace_hi_rank_order)}
aceLoOrder = {key: i for i, key in enumerate(ace_lo_rank_order)}

DEBUG = True
PORT = 11000
USER_NAME = "danny"
# TODO - change your method of saving information from the very rudimentary method here
hand = []  # list of cards in our hand
discard = []  # list of cards organized as a stack
discards = []  # list of cards oppo/dealer have discarded
melds = []  # sets/runs laid down
cannot_discard = ""

# set up the FastAPI application
app = FastAPI()


@app.get("/")
async def root():
    ''' Root API simply confirms API is up and running.'''
    return {"status": "Running"}


class GameInfo(BaseModel):
    # data class used to receive data from API POST
    game_id: str
    opponent: str
    hand: str


@app.post("/start-2p-game/")
async def start_game(game_info: GameInfo):
    ''' Game Server calls this endpoint to inform player a new game is starting. '''
    # TODO - Your code here - replace the lines below
    global hand
    global discard
    hand = game_info.hand.split(" ")
    # hand.sort()
    logging.info("2p game started, ace hi hand is " +
                 str(getOrderedHand(hand, aceHiOrder)))
    logging.info("2p game started, ace lo hand is " +
                 str(getOrderedHand(hand, aceLoOrder)))
    logging.info("2p game started, dict hand is "+str(getDictHand(hand)))
    return {"status": "OK"}


class HandInfo(BaseModel):
    # data class used to receive data from API POST
    hand: str


@app.post("/start-2p-hand/")
async def start_hand(hand_info: HandInfo):
    ''' Game Server calls this endpoint to inform player a new hand is starting, continuing the previous game. '''
    # TODO - Your code here
    global hand
    global discard
    global discards
    discard = []
    discards = []
    hand = hand_info.hand.split(" ")
    # hand.sort()
    logging.info("2p game started, ace hi hand is " +
                 str(getOrderedHand(hand, aceHiOrder)))
    logging.info("2p game started, ace lo hand is " +
                 str(getOrderedHand(hand, aceLoOrder)))
    logging.info("2p game started, dict hand is "+str(getDictHand(hand)))
    return {"status": "OK"}


def process_events(event_text):
    ''' Shared function to process event text from various API endpoints '''
    # TODO - Your code here. Everything from here to end of function
    global hand
    global discard
    global discards
    for event_line in event_text.splitlines():
        logging.info("evline: "+event_line)

        if ((USER_NAME + " draws") in event_line or (USER_NAME + " takes") in event_line):
            logging.info("In draw, hand is "+str(hand))
            # logging.info("Drew "+event_line.split(" ")[-1])
            hand.append(event_line.split(" ")[-1])
            hand.sort()
            logging.info("Hand is now "+str(hand))
            logging.info("Drew a "+event_line.split(" ")
                         [-1]+", hand is now: "+str(hand))
        if ("discards" in event_line):  # add a card to discard pile
            newcard = event_line.split(" ")[-1]
            discard.insert(0, newcard)
            discards.append(newcard)
            logging.info("discards: "+str(discards))
        if ("takes" in event_line):  # remove a card from discard pile
            newcard = event_line.split(" ")[-1]
            discards.remove(newcard)
            discard.pop(0)
        if " Ends:" in event_line:
            logging.info(event_line)


class UpdateInfo(BaseModel):
    # data class used to receive data from API POST
    game_id: str
    event: str


@app.post("/update-2p-game/")
async def update_2p_game(update_info: UpdateInfo):
    '''
        Game Server calls this endpoint to update player on game status and other players' moves.
        Typically only called at the end of game.
    '''
    # TODO - Your code here - update this section if you want
    process_events(update_info.event)
    logging.info(update_info.event)
    return {"status": "OK"}


@app.post("/draw/")
async def draw(update_info: UpdateInfo):
    ''' Game Server calls this endpoint to start player's turn with draw from discard pile or draw pile.'''
    global cannot_discard
    # TODO - Your code here - everything from here to end of function
    process_events(update_info.event)
    if len(discard) < 1:  # If the discard pile is empty, draw from stock
        cannot_discard = ""
        return {"play": "draw stock"}
    if any(discard[0][0] in s for s in hand):
        # if our hand contains a matching card, take it
        cannot_discard = discard[0]
        return {"play": "draw discard"}
    return {"play": "draw stock"}  # Otherwise, draw from stock


def get_of_a_kind_count(hand):
    # how many 1 of a kind, 2 of a kind, etc in our hand
    of_a_kind_count = [0, 0, 0, 0]
    last_val = hand[0][0]
    count = 0
    for card in hand[1:]:
        cur_val = card[0]
        if cur_val == last_val:
            count += 1
        else:
            of_a_kind_count[count] += 1
            count = 0
        last_val = cur_val
    of_a_kind_count[count] += 1  # Need to get the last card fully processed
    return of_a_kind_count


def get_count(hand, card):
    count = 0
    for check_card in hand:
        if check_card[0] == card[0]:
            count += 1
    return count


@app.post("/lay-down/")
async def lay_down(update_info: UpdateInfo):
    ''' Game Server calls this endpoint to conclude player's turn with melding and/or discard.'''
    # TODO - Your code here - everything from here to end of function
    global hand
    global discard
    global cannot_discard
    process_events(update_info.event)

    logging.info("MELDS: "+str(melds))
    play_string = ""
    meld_str = ""
    meld = getRun(getOrderedHand(hand, aceLoOrder), aceLoOrder)
    if meld != []:
        meld_str = ' '.join(meld)
        play_string += "meld "+meld_str
    elif meld == []:
        meld = getRun(getOrderedHand(hand, aceHiOrder), aceHiOrder)
        if meld != []:
            meld_str = ' '.join(meld)
            play_string += "meld "+meld_str
        else:
            play_string = ""
    if play_string != "":
        melds.append(meld_str)
        logging.info("Meldorun: "+play_string)

        # return {"play":play_string}

    play_string = "meld "
    meld_str = ""
    altHand = [c for c in hand]
    for rank, count in getDictHand(altHand).items():
        if count > 2:
            altHand = [c for c in altHand if c[0] != rank]
            meld_str = ' '.join([c for c in altHand if c[0] == rank])
            play_string += "meld "+meld_str
            melds.append(meld_str)
            logging.info("Meldoset: "+play_string)
            break

        # return {"play":play_string}

    of_a_kind_count = get_of_a_kind_count(hand)
    if (of_a_kind_count[0]+(of_a_kind_count[1]*2)) > 1:
        logging.info("Need to discard")
        # Too many unmeldable cards, need to discard

        # If we have a 1 of a kind, discard the highest

        if (of_a_kind_count[0] > 0):
            logging.info("Discarding a single card")
            # logging.info("Discarding a single card")

            # edge case - the last card is 1 of a kind
            if (hand[-1][0] != hand[-2][0]):
                logging.info("Discarding last card " + hand[-1])
                return {"play": "discard " + hand.pop()}

            for i in range(len(hand)-2, -1, -1):
                if (i == 0):
                    logging.info("Discarding first card "+hand[0])
                    return {"play": "discard "+hand.pop(0)}
                if hand[i][0] != hand[i-1][0] and hand[i][0] != hand[i+1][0]:
                    logging.info("Discarding middle card "+hand[i])
                    return {"play": "discard "+hand.pop(i)}

        elif (of_a_kind_count[1] >= 1):
            logging.info(
                "Discarding two of a kind, cannot_discard = "+cannot_discard)
            for i in range(len(hand)-1, -1, -1):
                if (hand[i] != cannot_discard and get_count(hand, hand[i]) == 2):
                    logging.info("Discarding dc pair "+hand[i])
                    return {"play": "discard " + hand.pop(i)}

            logging.info("Discarding who " + hand[i])
            return {"play": "discard " + hand.pop(i)}

    # We should be able to meld.

    # First, find the card we discard - if needed
    discard_string = ""
    logging.info("of a kind count: "+str(of_a_kind_count))

    if (of_a_kind_count[0] > 0):
        if hand[-1][0] != hand[-2][0]:
            discard_string = " discard " + hand.pop()
        else:
            for i in range(len(hand)-2, -1, -1):
                if (i == 0):
                    discard_string = " discard " + hand.pop(0)
                    break
                if hand[i][0] != hand[i - 1][0] and hand[i][0] != hand[i + 1][0]:
                    discard_string = " discard " + hand.pop(i)
                    break

    # generate our list of meld
    play_string = ""
    last_card = ""
    while (len(hand) > 0):
        card = hand.pop(0)
        if (str(card)[0] != last_card):
            play_string += "meld "
        play_string += str(card) + " "
        last_card = str(card)[0]

    # remove the extra space, and add in our discard if any
    play_string = play_string[:-1]
    play_string += discard_string

    logging.info("Playing: "+play_string)
    return {"play": play_string}


@app.get("/shutdown")
async def shutdown_API():
    ''' Game Server calls this endpoint to shut down the player's client after testing is completed.  Only used if DEBUG is True. '''
    os.kill(os.getpid(), signal.SIGTERM)
    logging.info("Player client shutting down...")
    return fastapi.Response(status_code=200, content='Server shutting down...')


''' Main code here - registers the player with the server via API call, and then launches the API to receive game information '''
if __name__ == "__main__":

    if (DEBUG):
        url = "http://127.0.0.1:16200/test"

        # TODO - Change logging.basicConfig if you want
        logging.basicConfig(filename="DevRummyPlayer.log", format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    else:
        url = "http://127.0.0.1:16200/register"
        # TODO - Change logging.basicConfig if you want
        logging.basicConfig(filename="RummyPlayer.log", format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARNING)

    payload = {
        "name": USER_NAME,
        "address": "127.0.0.1",
        "port": str(PORT)
    }

    try:
        # Call the URL to register client with the game server
        response = requests.post(url, json=payload)
    except Exception as e:
        logging.info("Failed to connect to server.  Please contact Mr. Dole.")
        exit(1)

    if response.status_code == 200:
        logging.info("Request succeeded.")
        logging.info("Response:", response.json())  # or response.text
    else:
        logging.info("Request failed with status:", response.status_code)
        logging.info("Response:", response.text)
        exit(1)

    # run the client API using uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT)
