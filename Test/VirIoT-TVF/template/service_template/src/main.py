import sys, socket, json
from logging import basicConfig, getLogger, DEBUG

#add import files

######

class SF():

    def __init__(self):

        #read config file
        with open('config.json', "r") as fp:
            setting = json.load(fp)

        self.host = setting["host"]
        self.port = setting["port"]
        self.segSize = setting["segSize"]
        self.logLevel = setting["logLevel"]

        if (self.logLevel == "debug"):
            basicConfig(level=DEBUG)
        self.logger = getLogger(__name__)

    #define service function
    def callServiceFunction(self):

        self.logger.debug("[callServiceFunction] start service function")

        #please write your own function
        ##self.revData: receved data from network function
        ##self.revData: byte type
        ##self.revData.decode(): string type 

        BODY = "dummy"
        ##########

        self.logger.debug("[callServiceFunction] complete")

        return BODY.encode()

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(10)

            while True:

                self.logger.debug("[callServiceFunction] waiting")
                clientsock, client_address = s.accept()

                try:
                    self.logger.debug("[callServiceFunction] accepted")

                    self.revData = b''

                    while True:

                        data = clientsock.recv(self.segSize)

                        if not data:
                            break
                        self.revData += data

                    self.logger.debug("[callServiceFunction] received")

                    self.logger.debug("[callServiceFunction] callServiceFunction")
            
                    result = self.callServiceFunction()

                    self.logger.debug("[callServiceFunction] send results")
                    clientsock.send(result)

                    self.logger.debug("[callServiceFunction] send complete")

                except Exception as e:
                    self.logger.debug("[callServiceFunction] error")
                    self.logger.debug(e)

                finally:
                    clientsock.close()

if __name__ == '__main__':

    sf = SF()
    sf.run()
