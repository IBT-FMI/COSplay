.. _pyboard:

=======
Pyboard
=======

.. graphviz:: workflow.dot

LEDs
====

Green, orange and blue:
    Pyboard tries to connect to software on host computer.

Blue:
    Copy mode.

Orange:
    Pyboard is armed.

Green:
    Delivering sequence.

Green, Blue:
    Stimulus active.

Red:
    Computer writes to filesystem of pyboard.
    Warning! Do not unplug or reset the board in this state as files might be corrupted.

Red/Green flashing:
    An error occured while executing the scripts on the board.

Standalone use
==============

The pyboard can also be used without COSplay on the host computer.
To enter this use case press the 'USR' button on the board, when the green,
orange and blue LED light up simultaneously after the board started.

To load sequences onto the pyboard you need to enter the copy mode.
Double click the 'USR' button, when the green, orange and blue LED light up simultaneously after the board started. The board should now present it self to the computer as a mass storage device and the blue LED lights up. Copy the sequence files into the ``sequence_library`` folder on the board/SD.

*NOTE:* Do not forget to safely remove or unmount the board before restarting or disconnecting it, just like you would with any normal memory stick.

The board can be restarted by pressing the 'RST' button.

Delivered sequences will be stored in
``delivered_sequences/sequencesX/sequenceY.tsv``, where ``X`` and ``Y``
are numbers. A new folder ``delivered_sequences/sequencesX`` is created
for every reboot of the pyboard.

*NOTE:* You have to delete old sequences manually.

Sequence Errors
===============

Before deliverying a sequence the board checks its consistency.
If the period is smaller than the pulse width or the values in the out_channel column are not integers between 1 and 6, a SequenceError is raised.

In case the board misses a scheduled onset time or end time of a pulse,
an error message is displayed. Furthermore, all error messages are stored
in a file ``errors.txt`` in the same directory as ``sequence.tsv``.

If the board is operated in :math:`\mu s` accuracy mode, the earliest
possible on-set time for the first event is approximately :math:`320\mu s`
due to computational overhead. For smaller on-set times the board misses the scheduled time as described above.
In :math:`ms` mode this delay is negligible.

Runtime Errors
==============

For debugging purposes, exceptions are stored in ``exceptions.txt`` on
the board.

*NOTE:* Syntax errors are not handled, as they are raised before execution.
You can use a programme like 'screen', 'minicom' or 'picocom'.

Circuit
=======

The following figure shows the circuit used with the pyboard. BNC 1-3 can short circuit the incoming BNC. Ports 4-6 can deliver 3.3V TTL pulses.

.. image:: circuit.png

config.py
=========

Library path
------------

If one copies sequences to the board mamually, the path to the directory containing the sequences can be spcified in ``library_path``.

Accuracy
--------

``accuracy`` can be 'us' for :math:`\mu s`-mode or 'ms' for :math:`ms`-mode.

On values for out channels
--------------------------

The values in this section are the value a pin takes when a stimulus is delivered.
If no stimulus is to be delivered, the pin takes the oposite value.
