=======
COSplay
=======

Overview
========

Contrast optimized stimulus player (COSplay) is a software for stimulus delivery in stimulus-evoked fMRI experiments.
It consists of two parts, a program, written in MicroPython, running on a microcontroller (PyBoard) delivering stimulus sequences and a program running on the MRI's computer monitoring the delivery.

Features
========

- TTL trigger from MRI scanner can be used
- 2 TTL output channels (~4.2V)
- 2 transistor channels (up to ~3.3V)
- 2 TTL output channels with variable amplitude
- Microcontroller can be used standalone (c.f. :ref:`pyboard`)
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

- PyBoard 1.1 with MicroPython firmware 1.8.7 or newer
- USB cable (A to micro-B)
- microSD (recommended)
- Additional I/O circuitry (see components and diagram: :ref:`cosplayer`)

Installation
============

Download the package via Git (``git clone https://github.com/IBT-FMI/COSplay.git``) or download and unarchive it manually, or from your terminal (``wget https://github.com/IBT-FMI/COSplay/archive/master.zip && unzip master.zip``)

Open a terminal and go to the COSplay folder you downloaded.

Insert the microSD into the Pyboard and connect it to the computer using the USB cable.
Copy all files in the pyboard folder to the SD card (``cp -rf pyboard/* mount/point/of/the/sd``).

*NOTE:* You have to replace  ``mount/point/of/the/sd`` with the actual mount point of the SD card.
Of course you can also copy the files without using the terminal.

If you want to use the pyboard standalone you can continue reading at :ref:`pyboard`.

In order to grant the user permission to access the microcontroller, a new udev rule is needed.
Run the script ``grant_permissions_for_pyboard`` from inside the ``scripts`` folder to create the rule (``./scripts/grant_permissions_for_pyboard``).
You will need root privileges to run the script. You can remove the rule using the ``remove_permissions_for_pyboard`` script.

The following section instructions install a module that can be used in Python programs (via e.g. ``import cosplay``).

If you only want to use the program as is, an installation is not mandatory. 
You can simply run the executable cli.py (``./cosplay/cli.py``).

Setuptools
----------

The module can be installed using setuptools.
Run ``python setup.py install`` inside the COSplay folder.
After installation you can start COSplay using the command ``COSplay``.
Also, the scripts for the udev rules can be executed directly via the commands ``grant_permissions_for_pyboard`` and ``remove_permissions_for_pyboard`` after this installation.

*NOTE:* If you have multiple Python versions installed on your system,
you might have to change ``python`` to e.g. ``python3`` in the command above.

References
==========
* MicroPython: https://micropython.org/
* PyBoard: http://docs.micropython.org/en/latest/pyboard/pyboard/quickref.html
* Python: http://www.python.org/
* PySerial: http://pyserial.readthedocs.io/en/latest/pyserial.html
* Setuptools: https://setuptools.readthedocs.io/en/latest/
