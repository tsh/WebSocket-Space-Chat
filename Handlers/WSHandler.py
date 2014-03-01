import sys
import uuid
import json

import tornado

from Objects import Ship

class WSHandler(tornado.websocket.WebSocketHandler):
    #array to store connected users
    users = []
    ships = {}

    def open(self):
        WSHandler.users.append(self)
        #assign unique id to each ship
        WSHandler.uid = str(uuid.uuid4())
        ship = Ship(WSHandler.uid)
        WSHandler.ships[WSHandler.uid] = ship
        d = {
            "messageType": "uid",
            "id": WSHandler.uid
        }
        jObj = json.dumps(d)
        self.write_message(jObj)
        print "OPEN: ",WSHandler.ships

        #send new user already connected ships
        conShips = {"messageType": "connectedShips", "ships": []}
        for k in WSHandler.ships.keys():
            sh = WSHandler.ships[k]
            conShips["ships"].append({
                "shipId": sh.getUID(),
                "x": sh.getX(),
                "y": sh.getY()
            })
        print "Sending ships: ",conShips
        self.write_message(json.dumps(conShips))


    def on_message(self, message):
        #READ and parse client message and react according to message type
        messageObject = json.loads(message)

        if messageObject["messageType"] == "shipPosition":
            try:
                ship = WSHandler.ships[messageObject['uid']]
                vx = messageObject["vx"]
                vy = messageObject["vy"]
                ship.computeShipPosition(vx,vy)
                response = {
                    "messageType": "shipPosition",
                    "id": ship.getUID(),
                    "x": ship.getX(),
                    "y": ship.getY()
                }
                WSHandler.notifyUsers(response)
            except:
                print sys.exc_info()

        elif messageObject["messageType"] == "getID":
            ship = Ship(WSHandler.uid)
            WSHandler.ships[WSHandler.uid] = ship
            d = {
                "messageType": "uid",
                "id": WSHandler.uid
            }
            jObj = json.dumps(d)
            self.write_message(jObj)


    def on_close(self):
        WSHandler.users.remove(self)
        del WSHandler.ships[WSHandler.uid]
        print "Close: ",WSHandler.ships
        print "-------CLOSED--------"

    @classmethod
    def notifyUsers(cls, message):
        for user in cls.users:
            user.write_message(message)
