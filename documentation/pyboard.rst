=======
Pyboard
=======


LEDs
====

Green, orange and blue:
    Pyboard tries to connect to software on host computer.

Orange:
    Pyboard is armed.

Green:
    Delivering sequence.

Blue:
    Stimulus active.

Red:
    Computer writes to filesystem of pyboard.

Red/Green flashing:
    An error occured while executing the scripts on the board.

.. _pyboardStandalone:

Standalone use
==============

The pyboard can also be used without COSplay on the host computer.
To enter this use case press the 'USR' button on the board, when the green,
orange and blue LED light up simultaneously.

To load sequences onto the pyboard copy them into the ``sequence_library``
folder on the board.

Delivered sequences will be stored in
``delivered_sequences/sequencesX/sequenceY.tsv``, where ``X`` and ``Y``
are numbers. A new folder ``delivered_sequences/sequencesX`` is created
for every reboot of the pyboard.

*NOTE:* You have to delete old sequences manually.

Sequence Errors
===============

First a consitency check on a selected sequence. If the period
is smaller than the pulse width, the board selects a new sequence.

In case the board misses a scheduled onset time or end time of a pulse,
an error message is displayed. Furthermore, all error messages are stored
in a file ``errors.txt`` in the same directory as ``sequence.tsv``.

If the board is operated in :math:`\mu s` accuracy mode, the earliest
possible on-set time for the first event is approximately 76:math:`\mu s`
due to computational overhead. For smaller on-set times an error will
be raised as described above.
In :math:`ms` mode this delay is negligible.

Runtime Errors
==============

For debugging purposes, exceptions are stored in ``exceptions.txt`` on
the board.

*NOTE:* Syntax errors are not handled, as they are raise before execution.
You can use a programme like 'screen', 'minicom' or 'picocom'.
