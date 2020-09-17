import cefpyco
import time
import sys
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactory Library
from common import common
from protocol import icnCefore

basicConfig(level=INFO)
logger = getLogger(__name__)

if __name__ == '__main__':

	args = sys.argv

	if len(args) != 4:
		print ("[Usage]: sudo python3 **.py [method (add or del), ip address, interest name]")
		sys.exit(1)

	method = args[1]
	src = args[2]

	fib = {"method": args[1], "src": src, "name": args[3]}

	icnCefore.updateFib(fib)


