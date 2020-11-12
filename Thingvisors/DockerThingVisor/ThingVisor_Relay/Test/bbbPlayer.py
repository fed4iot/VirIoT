import argparse, argcomplete
import sys, os
import requests
import time
import math

if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', action='store', dest='serverIP', 
                            help='HTTP vSilo Server Address (default: vm1) ', default='vm1')
        parser.add_argument('-p', action='store', dest='serverPort', 
                            help='HTTP vSilo Server Port (default: 31541) ', default='31541')
        parser.add_argument('-v', action='store', dest='vThingID', 
                            help='vThingID (default: relay-tv-jp/timestamp) ', default='relay-tv-jp/timestamp')
        parser.add_argument('-u', action='store', dest='startTime', 
                            help='Video start time in Unix Epoc Time (default: now) ', default='0')                          
        parser.add_argument('-f', action='store', dest='csvFileName', 
                            help='csvFile (default: None) ', default=None)
                            
        argcomplete.autocomplete(parser)
        args = parser.parse_args()
    except Exception:
        traceback.print_exc()

    serverIP = args.serverIP
    serverPort=args.serverPort
    startTime = int(args.startTime)
    vThingID = args.vThingID
    if startTime==0:
        startTime = time.time()
    segmentDuration = 4
    urlPrefix = "http://"+serverIP+":"+serverPort+"/vstream/"+vThingID+"/bbb_2000kbit/bunny_"

    csvFileName = args.csvFileName
    csvFile = None
    if csvFileName is not None:
        csvFile =  open(csvFileName, "w")

    
    maxSegmentNum = 150
    
    while True:
        try:
            now = time.time()
            currSegmentVirtual = (math.ceil((now-startTime)/segmentDuration))
            currSegmentProductionTime = startTime + currSegmentVirtual*segmentDuration
            time.sleep(currSegmentProductionTime - now)
            starttime = time.time()
            currSegment = (currSegmentVirtual%maxSegmentNum)+1
            uri =  urlPrefix + str(currSegment)+".m4s"
            print("%.4f Downloading segment %d " % (starttime, currSegment))
            r = requests.get(uri)
            l = len(r.content)
            stoptime = time.time()
            elapsed = stoptime - starttime
            rate = l*8.0/elapsed/1e6
            print("Downloaded %d kbytes at %f Mbit/s" % (l/1000,rate))
            if csvFile is not None:
                csvFile.write("%.4f \t %.4f \t %d \t %.4f \t %.4f \n" % (starttime, stoptime, currSegment, l/1000, rate))
                csvFile.flush()
            #time.sleep(segmentDuration - elapsed)
        except Exception as err:
            print("KeyboardInterrupt", err)
            if csvFile is not None:
                csvFile.close()
            time.sleep(1)
            os._exit(1)