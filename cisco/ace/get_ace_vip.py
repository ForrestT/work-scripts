import argparse, socket
from cisco import ACE

parser = argparse.ArgumentParser()

parser.add_argument('vip', help='IP Address or DNS name of VIP')
group1 = parser.add_mutually_exclusive_group(required=True)
group1.add_argument('-f', '--file', help='file to open')
group1.add_argument('-d', '--device', help='device to pull config from')

args = parser.parse_args()

vip = socket.gethostbyname(args.vip)
if args.file:
	ace_obj = ACE(args.file)
else:
	pass
ace_obj.getVIPconfig(vip)
ace_obj.displayVIP()
