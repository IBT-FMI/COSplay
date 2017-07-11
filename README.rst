COSplay
=======

.. image:: https://readthedocs.org/projects/cosplay/badge/?version=latest
  :target: http://cosplay.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. image:: https://travis-ci.org/IBT-FMI/COSplay.svg?branch=master
  :target: https://travis-ci.org/IBT-FMI/COSplay

COSplay (Contrast optimized stimulus player) is a Python based software solution for the deliveriy of stimulus sequences in stimulus evoked fMRI experiments.
It is fully compatible with the stimulus sequence optimization package COSgen_. 

Features
--------

- TTL trigger from MRI scanner can be used
- 3 TTL output channels (3.3V) and 3 transistor channels
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

*Note:* `setuptools` will not manage any dependencies.
You will have to install Dependencies_ manually, e.g. using ``pip install pyserial``.

Dependencies
------------

- Python_ 2.7 or Python 3.5 and newer
- PySerial_ 3.3 or newer

Hardware
--------

- PyBoard 1.13
- microSD (recommended)
- USB cable (A to micro-B)

.. _Python: https://www.python.org/
.. _COSgen: https://github.com/IBT-FMI/COSgen
.. _PySerial: https://pypi.python.org/pypi/pyserial
