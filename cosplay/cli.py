#"""Command line interface. Also executable as bash script."""

#!/bin/bash

''''true && for var in {6..1}; do which "python3.$var" >/dev/null 2>&1 && exec "python3.$var" "$0" $( echo "$@" | sed -- 's/--force//g' ); done # '''
''''which python2.7 >/dev/null 2>&1 && exec python2.7 "$0" $( echo "$@" | sed -- 's/--force//g' ) # '''
''''which python >/dev/null 2>&1 && (( $( python -c 'import sys; print(sys.version_info[1])' ) == 3 )) && (( $( python -c 'import sys; print(sys.version_info[1])' ) >=5 )) && exec python "$0" $( echo "$@" | sed -- 's/--force//g' ) # '''
''''which python >/dev/null 2>&1 && (( $( python -c 'import sys; print(sys.version_info[1])' ) == 2 )) && (( $( python -c 'import sys; print(sys.version_info[1])' ) ==7 )) && exec python "$0" $( echo "$@" | sed -- 's/--force//g' ) # '''
''''true && [[ $( echo "$@" | grep -c -- "--force" ) -eq 0 ]] && exec echo "Error: No supported python version found. (If you want to try to use the OS's default python version run this script with --force)" # '''
''''exec python "$0" $( echo "$@" | sed -- 's/--force//g' ) # '''

__author__ = "Aymanns Florian"

import argparse
try:
	import COSplay.server as server
except ImportError:
	import server

def return_parser():
	"""Return argparse argument parser."""
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
			help='Is needed to find the correct folder.',
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

	return parser

def main():
	"""Process arguments and pass them to server.main."""
	parser = return_parser()

	args = parser.parse_args()

	server.main(args)

if __name__ == '__main__':
	main()
