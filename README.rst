COSplay
=======

.. image:: http://joss.theoj.org/papers/3ee7ef4edc7b537e19f89225d1d96139/status.svg
  :target: http://joss.theoj.org/papers/3ee7ef4edc7b537e19f89225d1d96139
  :alt: Journal of Open Source Software Publication Status
.. image:: https://readthedocs.org/projects/cosplay/badge/?version=latest
  :target: http://cosplay.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. image:: https://travis-ci.org/IBT-FMI/COSplay.svg?branch=master
  :target: https://travis-ci.org/IBT-FMI/COSplay

COSplay (Contrast optimized stimulus player) is a Python based software solution for the deliveriy of stimulus sequences in stimulus evoked fMRI experiments.
It is fully compatible with the stimulus sequence optimization package COSgen_.
The software is best used in conjunction with a COSplayer, an open source device, assembly instructions for which can be found `here`__.

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
- Setuptools_ 20.7 or newer

Hardware
--------

- PyBoard 1.1
- microSD (recommended)
- USB cable (A to micro-B)

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
