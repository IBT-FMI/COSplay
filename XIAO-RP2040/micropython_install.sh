#!/usr/bin/env bash

# This will need to be improved based on:
# https://github.com/orgs/micropython/discussions/11366

if ! wget "https://micropython.org/resources/firmware/sseeed_xiao_nrf52-20230426-v1.20.0.uf2" ; then
	echo "The hard-coded download link is outdated. This is to be expected."
	echo "Please find the current download link under `https://micropython.org/download/seeed_xiao_nrf52/`, and download the file to this directory."
fi
