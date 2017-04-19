__author__ = "Aymanns Florian"

import argparse
from COSplay.server import run

def main():

	parser = argparse.ArgumentParser(prog="COSplay",
					description="Main program running on host computer for usage with a pyboard running COSplay")
	parser.add_argument('-v','--verbose',
			dest='verbose',
			action='store',
			type=int,
			help='Set the verbosity.',
			default='1')
	parser.add_argument('--vendor',
			dest='vendor',
			action='store',
			choices=['bruker'],
			type=str.lower,
			help='Is needed to find the correct folder. Program knows "bruker" (default="bruker")',
			default='bruker')
	parser.add_argument('--port',
			dest='port',
			action='store',
			type=str,
			help='Name of port pyboard is connected to. Generally not necessary as system should find the right port automatically.',
			default=None)
	parser.add_argument('--sequences',
			dest='sequences',
			action='store',
			type=str,
			help='Path to tsv files containing the sequences. This flag can be used if you did not save the sequences generated with COSgen in the default location or if you do not want to use the sequences generated most recently.',
			default=None)
	parser.add_argument('--storage_path',
			dest='storage_path',
			action='store',
			type=str,
			help='Path to directory where delivered sequences are stored. If not specified the sequence is stored in the folder of the most recent scan.',
			default=None)

	args = parser.parse_args()


	run(args)

if __name__ == '__main__':
	main()
