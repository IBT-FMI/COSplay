=======
COSplay
=======

Overview
========

Contrast optimized stimulus player(COSplay) is a software for stimulus delivery in
stimulus-evoked fMRI experiments. It consists of two parts,
a programme, written in MicroPython, running on a microcontroller (PyBoard) delivering stimulus sequences
and a programme running on the MRI's computer monitoring the delivery.

Features
========

- TTL trigger from MRI scanner can be used
- 3 TTL output channels (3.3V) and 3 transistor channels
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

Insert the microSD into the Pyboard and connect it to the computer using the USB cable.
Copy all files in the pyboard folder to the SD card (``cp pyboard/* mount/point/of/the/sd``).

*NOTE:* You have to replace  ``mount/point/of/the/sd`` with the actual mount point of the sd card.
Of course you can also copy the files without using the terminal.

If you want to use the pyboard standalone you can continue reading at :ref:`pyboardStandalone`.

In order to grant the user permission to access the microcontroller a new udev rule is needed.
Run the script ``grant_permissions_for_pyboard`` inside the ``scripts`` folder to creat the rule (``./scripts/grant_permissions_for_pyboard``).
You will need root privileges to run the script. You can remove the rule using the ``remove_permissions_for_pyboard`` script.

The following installs a module that can be used in Python programs (``import cosplay``).

If you only want to use the programme as is, an installation is not mandatory. 
You can you can simply run the executable cli.py (``./cosplay/cli.py``).

Setuptools
----------

The module can be installed using setuptools.
Run ``python setup.py install`` inside the COSplay folder.

*NOTE:* If you have multiple python versions installed on your system,
you might have to change ``python`` to e.g. ``python3`` in the command above.

References
==========
* MicroPython: https://micropython.org/
* PyBoard: http://docs.micropython.org/en/latest/pyboard/pyboard/quickref.html
* Python: http://www.python.org/
* PySerial: http://pyserial.readthedocs.io/en/latest/pyserial.html
* Setuptools: https://setuptools.readthedocs.io/en/latest/
