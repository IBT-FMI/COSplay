COSplay
=======

.. image:: http://joss.theoj.org/papers/3ee7ef4edc7b537e19f89225d1d96139/status.svg
  :target: http://joss.theoj.org/papers/3ee7ef4edc7b537e19f89225d1d96139
  :alt: Journal of Open Source Software Publication Status
.. image:: https://readthedocs.org/projects/cosplay/badge/?version=latest
  :target: http://cosplay.readthedocs.io/en/latest
  :alt: Documentation Status

COSplay (Contrast optimized stimulus player) is a Python based software solution for the delivery of stimulus sequences in stimulus evoked experiments.
It is fully compatible with the stimulus sequence optimization package COSgen_.
The software is best used in conjunction with a COSplayer, an open source device, assembly instructions for which can be found `here`__.

Rationale and Use Case Example
------------------------------

In many research areas, the functioning of complex systems is probed by measuring stimulus-evoked responses.
COSplay can allow e.g. a neuroscientist to present milli-second accurate stimuli to a subject during a measurement procedure.
Commonly, stimulus train delivery is coordinated by in-house and/or proprietary solutions, which are often ill-documented, expensive, poorly reproducible, high-maintenance, and unsustainable.
Uniquely, COSplay permits stimulus train delivery via a small and portable device, capable of interfacing with proprietary measurement systems --- but in and of itself not containing any additional proprietary software or hardware!

Features
--------

- TTL trigger from MRI scanner can be used
- 2 transistor channels
- 2 TTL output channels (3.3V)
- 2 amplitude modulation channels
- Microcontroller can be used standalone (c.f. `Standalone use` section in the docs)
- Stimulus pulse delivery with  ms or μs accurary
- Random selection of a sequence from a sequence library
- Piping of sequence file to the directory of the latest scan on the MRI computer
- Error message forwarding to computer

Installation
------------

COSplay can be installed using Python's `setuptools`.

.. code-block:: console

   git clone https://github.com/IBT-FMI/COSplay.git
   cd COSplay
   python setup.py install --user

Dependencies
------------

- Python_ 2.7 or Python 3.5 and newer
- PySerial_ 3.3 or newer
- Setuptools_ 20.7 or newer

Hardware
--------

- PyBoard 1.1
- microSD (recommended)
- USB cable (A to micro-B)

Minimal Usage Example
---------------------

To execute a demo sequence on the COSplayer device, please follow the subsequent steps:

1. Install the package on a machine according to the instructions above.
2. Connect the COSplayer device to the machine. At this point the blue, orange, and green LEDs should light up, according to the `LED legend <https://cosplay.readthedocs.io/en/latest/pyboard.html#led-pattern-legend>`_.
3. Press the USR button twice. At this point the blue LED should light up, the red LED may also intermittently light up, according to whether data is being written on disk.
4. After the device is recognised by the host computer, navigate to the `sequence_library` directory.
5. Copy a file formatted according to the COSplay/BIDS standard into the directory. An example file is `provided in this repository <sequence.tsv>`_. All values are interpreted as SI base units, seconds and hertz, respectively --- with the exception of the amplitude (`see more <https://cosplay.readthedocs.io/en/latest/pyboard.html#circuit>`_).
6. After the file has copied and the red LED is no longer lit, safely remove the volume, and press the RST button.
7. Click the USR button once to select the standalone operation mode. At this point the LED lighting should transition from blue, orange, and green to none.
8. Click the USR button again to arm the device. At this point the orange LED should light up.
9. Click the USR button once more to trigger the sequence. At this point the green LED should light up, and, as stimulation is delivered, the blue LED should intermittently light up as well.

.. _Python: https://www.python.org/
.. _COSgen: https://github.com/IBT-FMI/COSgen
.. _COSplayer: https://figshare.com/articles/A_Guide_to_Assembling_the_COSplayer_an_Open_Source_Device_for_Microsecond-Range_Stimulus_Delivery_with_broad_Application_in_Biomedical_Engineering_and_fMRI/7227626
.. _PySerial: https://pypi.python.org/pypi/pyserial
.. _Setuptools: https://pypi.python.org/pypi/setuptools

__ COSplayer_


Contributing Guidelines
-----------------------

You can:

- Submit suggestions for improvements via the `GitHub Pull Request tracker <https://github.com/IBT-FMI/COSplay/pulls>`_.
- Report issues and seek help via the `GitHub Issue tracker <https://github.com/IBT-FMI/COSplay/issues>`_.
