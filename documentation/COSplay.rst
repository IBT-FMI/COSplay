=======
COSplay
=======

Overview
========

Contrast optimized stimulus player(COSplay) is a software for stimulus delivery in
stimulus-evoked fMRI experiments. It consists of two part,
a programme, written in MicroPython, running on a microcontroller (PyBoard) delivering stimulus sequences
and a programme running on the MRI's computer monitoring the delivery.

Features
========

- TTL trigger from MRI scanner can be used
- Microcontroller can be used standalone (c.f. :ref:`pyboardStandalone`)
- Stimulus pulse delivery with  :math:`ms` or :math:`\mu s` accurary
- Random selection of a sequence from a sequence library
- Piping of sequence file to the directory of the latest scan on the MRI computer
- Error message forwarding to computer

Dependencies
============

- Python 2.7 or Python 3.5 and newer
- PySerial 3.3 or newer

Hardware
========

- PyBoard 1.1
- microSD
- USB cable (A to micro-B)

Installation
============

Open a terminal and go to the COSplay folder you downloaded.

Insert the microSD into the Pyboard and connected to the computer using the USB cable.
Copy all files in the pyboard folder to the SD card (``cp pyboard/* mount/point/of/the/sd``).

*NOTE:* You have to replave ``mount/point/of/the/sd`` with the actual mount point of the sd card.
Of course you can also copy the files without using the terminal.

In order to grant the user permission to access the microcontroller a new udev rule is needed.
Run the script ``grant_permissions_for_pyboard`` inside the ``scripts`` folder to creat the rule
(``./scripts/grant_permissions_for_pyboard``).
You will need root privileges to run the script.

The following installs a module that can be used in Python programs (``import COSplay``).

If you only want to use the programme as is, an installation is not mandatory. 
You can you can simply run the executable cli.py (``./path/to/COSplay/COSplay/cli.py``).

Setuptools
----------

The module can be installed using setuptools.
Run ``python setup.py install`` inside the COSplay folder.

*NOTE:* If you have multiple python versions installed on your system,
you might have to change ``python`` to e.g. ``python3`` in the comand above.

References
==========
* MicroPython: https://micropython.org/
* PyBoard: http://docs.micropython.org/en/latest/pyboard/pyboard/quickref.html
* Python: http://www.python.org/
* PySerial: http://pyserial.readthedocs.io/en/latest/pyserial.html
* Setuptools: https://setuptools.readthedocs.io/en/latest/
