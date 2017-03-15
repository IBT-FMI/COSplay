#! /usr/bin/env python3

import time
import os
import sys
import threading
import argparse

# It turns out that just because pyudev is installed doesn't mean that
# it can actually be used. So we only bother to try is we're running
# under linux.


USE_AUTOCONNECT = sys.platform == 'linux'

BUFFER_SIZE = 512

DEVS = []
DEFAULT_DEV = None
DEV_IDX = 1

DEV_LOCK = threading.RLock()

def add_device(dev):
    """Adds a device to the list of devices we know about."""
    global DEV_IDX, DEFAULT_DEV
    with DEV_LOCK:
        for idx in range(len(DEVS)):
            test_dev = DEVS[idx]
            if test_dev.dev_name_short == dev.dev_name_short:
                # This device is already in our list. Delete the old one
                if test_dev is DEFAULT_DEV:
                    DEFAULT_DEV = None
                del DEVS[idx]
                break
        if find_device_by_name(dev.name):
            # This name is taken - make it unique
            dev.name += '-%d' % DEV_IDX
        dev.name_path = '/' + dev.name + '/'
        DEVS.append(dev)
        DEV_IDX += 1
        if DEFAULT_DEV is None:
            DEFAULT_DEV = dev


def find_device_by_name(name):
    """Tries to find a board by board name."""
    if not name:
        return DEFAULT_DEV
    with DEV_LOCK:
        for dev in DEVS:
            if dev.name == name:
                return dev
    return None


def find_serial_device_by_port(port):
    """Tries to find a board by port name."""
    with DEV_LOCK:
        for dev in DEVS:
            if dev.is_serial_port(port):
                return dev
    return None


def num_devices():
    with DEV_LOCK:
        return len(DEVS)

def is_micropython_usb_device(port):
    """Checks a USB device to see if it looks like a MicroPython device.
    """
    if type(port).__name__ == 'Device':
        # Assume its a pyudev.device.Device
        if ('ID_BUS' not in port or port['ID_BUS'] != 'usb' or
            'SUBSYSTEM' not in port or port['SUBSYSTEM'] != 'tty'):
            return False
        usb_id = 'usb vid:pid={}:{}'.format(port['ID_VENDOR_ID'], port['ID_MODEL_ID'])
    else:
        # Assume its a port from serial.tools.list_ports.comports()
        usb_id = port[2].lower()
    # We don't check the last digit of the PID since there are 3 possible
    # values.
    if usb_id.startswith('usb vid:pid=f055:980'):
        return True
    # Check for Teensy VID:PID
    if usb_id.startswith('usb vid:pid=16c0:0483'):
        return True
    return False


def autoconnect():
    """Sets up a thread to detect when USB devices are plugged and unplugged.
       If the device looks like a MicroPython board, then it will automatically
       connect to it.
    """
    if not USE_AUTOCONNECT:
        return
    try:
        import pyudev
    except ImportError:
        return
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    connect_thread = threading.Thread(target=autoconnect_thread, args=(monitor,), name='AutoConnect')
    connect_thread.daemon = True
    connect_thread.start()


def autoconnect_thread(monitor):
    """Thread which detects USB Serial devices connecting and disconnecting."""
    monitor.start()
    monitor.filter_by('tty')

    epoll = select.epoll()
    epoll.register(monitor.fileno(), select.POLLIN)

    while True:
        try:
            events = epoll.poll()
        except InterruptedError:
            continue
        for fileno, _ in events:
            if fileno == monitor.fileno():
                usb_dev = monitor.poll()
                print('autoconnect: {} action: {}'.format(usb_dev.device_node, usb_dev.action))
                dev = find_serial_device_by_port(usb_dev.device_node)
                if usb_dev.action == 'add':
                    # Try connecting a few times. Sometimes the serial port
                    # reports itself as busy, which causes the connection to fail.
                    for i in range(8):
                        if dev:
                            connected = connect_serial(dev.port, dev.baud, dev.wait)
                        elif is_micropython_usb_device(usb_dev):
                            connected = connect_serial(usb_dev.device_node)
                        else:
                            connected = False
                        if connected:
                            break
                        time.sleep(0.25)
                elif usb_dev.action == 'remove':
                    print('')
                    print("USB Serial device '%s' disconnected" % usb_dev.device_node)
                    if dev:
                        dev.close()
                        break


def autoscan():
    """autoscan will check all of the serial ports to see if they have
       a matching VID:PID for a MicroPython board. If it matches.
    """
    for port in serial.tools.list_ports.comports():
        if is_micropython_usb_device(port):
            connect_serial(port[0])

class DeviceError(Exception):
    """Errors that we want to report to the user and keep running."""
    pass

def connect_serial(port, baud=115200, wait=0):
    """Connect to a MicroPython board via a serial port."""
    if not QUIET:
        print('Connecting to %s ...' % port)
    try:
        dev = DeviceSerial(port, baud, wait)
    except DeviceError as err:
        sys.stderr.write(str(err))
        sys.stderr.write('\n')
        return False
    add_device(dev)
    return True

class Device(object):

    def __init__(self, pyb):
        self.pyb = pyb
        self.has_buffer = False  # needs to be set for remote_eval to work
        self.has_buffer = self.remote_eval(test_buffer)
        if self.has_buffer:
            if DEBUG:
                print("Setting has_buffer to True")
        elif not self.remote_eval(test_unhexlify):
            raise ShellError('rshell needs MicroPython firmware with ubinascii.unhexlify')
        else:
            if DEBUG:
                print("MicroPython has unhexlify")
        self.root_dirs = ['/{}/'.format(dir) for dir in self.remote_eval(listdir, '/')]
        self.sync_time()
        self.name = self.remote_eval(board_name, self.default_board_name())

    def check_pyb(self):
        """Raises an error if the pyb object was closed."""
        if self.pyb is None:
            raise DeviceError('serial port %s closed' % self.dev_name_short)

    def close(self):
        """Closes the serial port."""
        if self.pyb and self.pyb.serial:
            self.pyb.serial.close()
        self.pyb = None

    def is_root_path(self, filename):
        """Determines if 'filename' corresponds to a directory on this device."""
        test_filename = filename + '/'
        for root_dir in self.root_dirs:
            if test_filename.startswith(root_dir):
                return True
        return False

    def is_serial_port(self, port):
        return False

    def read(self, num_bytes):
        """Reads data from the pyboard over the serial port."""
        self.check_pyb()
        try:
            return self.pyb.serial.read(num_bytes)
        except (serial.serialutil.SerialException, TypeError):
            # Write failed - assume that we got disconnected
            self.close()
            raise DeviceError('serial port %s closed' % self.dev_name_short)

    def remote(self, func, *args, xfer_func=None, **kwargs):
        """Calls func with the indicated args on the micropython board."""
        global HAS_BUFFER
        HAS_BUFFER = self.has_buffer
        args_arr = [remote_repr(i) for i in args]
        kwargs_arr = ["{}={}".format(k, remote_repr(v)) for k, v in kwargs.items()]
        func_str = inspect.getsource(func)
        func_str += 'output = ' + func.__name__ + '('
        func_str += ', '.join(args_arr + kwargs_arr)
        func_str += ')\n'
        func_str += 'if output is None:\n'
        func_str += '    print("None")\n'
        func_str += 'else:\n'
        func_str += '    print(output)\n'
        func_str = func_str.replace('TIME_OFFSET', '{}'.format(TIME_OFFSET))
        func_str = func_str.replace('HAS_BUFFER', '{}'.format(HAS_BUFFER))
        func_str = func_str.replace('BUFFER_SIZE', '{}'.format(BUFFER_SIZE))
        func_str = func_str.replace('IS_UPY', 'True')
        if DEBUG:
            print('----- About to send %d bytes of code to the pyboard -----' % len(func_str))
            print(func_str)
            print('-----')
        self.check_pyb()
        try:
            self.pyb.enter_raw_repl()
            self.check_pyb()
            output = self.pyb.exec_raw_no_follow(func_str)
            if xfer_func:
                xfer_func(self, *args, **kwargs)
            self.check_pyb()
            output, _ = self.pyb.follow(timeout=10)
            self.check_pyb()
            self.pyb.exit_raw_repl()
        except (serial.serialutil.SerialException, TypeError):
            self.close()
            raise DeviceError('serial port %s closed' % self.dev_name_short)
        if DEBUG:
            print('-----Response-----')
            print(output)
            print('-----')
        return output

    def remote_eval(self, func, *args, **kwargs):
        """Calls func with the indicated args on the micropython board, and
           converts the response back into python by using eval.
        """
        return eval(self.remote(func, *args, **kwargs))

    def status(self):
        """Returns a status string to indicate whether we're connected to
           the pyboard or not.
        """
        if self.pyb is None:
            return 'closed'
        return 'connected'

    def sync_time(self):
        """Sets the time on the pyboard to match the time on the host."""
        now = time.localtime(time.time())
        self.remote(set_time, (now.tm_year, now.tm_mon, now.tm_mday, now.tm_wday + 1,
                               now.tm_hour, now.tm_min, now.tm_sec, 0))

    def write(self, buf):
        """Writes data to the pyboard over the serial port."""
        self.check_pyb()
        try:
            return self.pyb.serial.write(buf)
        except (serial.serialutil.SerialException, BrokenPipeError, TypeError):
            # Write failed - assume that we got disconnected
            self.close()
            raise DeviceError('{} closed'.format(self.dev_name_short))


class DeviceSerial(Device):

    def __init__(self, port, baud, wait):
        self.port = port
        self.baud = baud
        self.wait = wait

        if wait and not os.path.exists(port):
            toggle = False
            try:
                sys.stdout.write("Waiting %d seconds for serial port '%s' to exist" % (wait, port))
                sys.stdout.flush()
                while wait and not os.path.exists(port):
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    time.sleep(0.5)
                    toggle = not toggle
                    wait = wait if not toggle else wait -1
                sys.stdout.write("\n")
            except KeyboardInterrupt:
                raise DeviceError('Interrupted')

        self.dev_name_short = port
        self.dev_name_long = '%s at %d baud' % (port, baud)

        try:
            pyb = Pyboard(port, baudrate=baud, wait=wait)
        except PyboardError as err:
            print(err)
            sys.exit(1)

        # Bluetooth devices take some time to connect at startup, and writes
        # issued while the remote isn't connected will fail. So we send newlines
        # with pauses until one of our writes suceeds.
        try:
            # we send a Control-C which should kill the current line
            # assuming we're talking to tha micropython repl. If we send
            # a newline, then the junk might get interpreted as a command
            # which will do who knows what.
            pyb.serial.write(b'\x03')
        except serial.serialutil.SerialException:
            # Write failed. Now report that we're waiting and keep trying until
            # a write succeeds
            sys.stdout.write("Waiting for transport to be connected.")
            while True:
                time.sleep(0.5)
                try:
                    pyb.serial.write(b'\x03')
                    break
                except serial.serialutil.SerialException:
                    pass
                sys.stdout.write('.')
                sys.stdout.flush()
            sys.stdout.write('\n')

        # In theory the serial port is now ready to use
        Device.__init__(self, pyb)

    def default_board_name(self):
        return 'pyboard'

    def is_serial_port(self, port):
        return self.dev_name_short == port

    def timeout(self, timeout=None):
        """Sets the timeout associated with the serial port."""
        self.check_pyb()
        if timeout is None:
            return self.pyb.serial.timeout
        try:
            self.pyb.serial.timeout = timeout
        except:
            # timeout is a property so it calls code, and that can fail
            # if the serial port is closed.
            pass

def main():
    """The main program."""
    try:
        default_baud = int(os.getenv('COS_BAUD'))
    except:
        default_baud = 115200
    
    default_port = os.getenv('COS_PORT')
    if not default_port:
        default_port = '/dev/ttyACM0'
    
    global BUFFER_SIZE
    
    try:
        default_buffer_size = int(os.getenv('COS_BUFFER_SIZE'))
    except:
        default_buffer_size = BUFFER_SIZE
    parser = argparse.ArgumentParser(
        prog="COSplayHost",
        usage="%(prog)s [options] [command]",
        description="Conrol software for pyboard running COSplay.",
        epilog=("You can specify the default serial port using the " +
                "COS_PORT environment variable.")
    )
    parser.add_argument(
        "-b", "--baud",
        dest="baud",
        action="store",
        type=int,
        help="Set the baudrate used (default = %d)" % default_baud,
        default=default_baud
    )
    parser.add_argument(
        "--buffer-size",
        dest="buffer_size",
        action="store",
        type=int,
        help="Set the buffer size used for transfers (default = %d)" % default_buffer_size,
        default=default_buffer_size
    )
    parser.add_argument(
        "-p", "--port",
        dest="port",
        help="Set the serial port to use (default '%s')" % default_port,
        default=default_port
    )
    parser.add_argument(
        "-d", "--debug",
        dest="debug",
        action="store_true",
        help="Enable debug features",
        default=False
    )
    parser.add_argument(
        "--wait",
        dest="wait",
        type=int,
        action="store",
        help="Seconds to wait for serial port",
        default=0
    )
    parser.add_argument(
        "--timing",
        dest="timing",
        action="store_true",
        help="Print timing information about each command",
        default=False
    )
    parser.add_argument(
        '-V', '--version',
        dest='version',
        action='store_true',
        help='Reports the version and exits.',
        default=False
    )
    parser.add_argument(
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Turns off some output (useful for testing)",
        default=False
    )
    args = parser.parse_args(sys.argv[1:])

    if args.debug:
        print("Debug = %s" % args.debug)
        print("Port = %s" % args.port)
        print("Baud = %d" % args.baud)
        print("Wait = %d" % args.wait)
        print("Timing = %d" % args.timing)
        print("Quiet = %d" % args.quiet)
        print("Buffer_size = %d" % args.buffer_size)

    if args.version:
        print(__version__)
        return

    global DEBUG
    DEBUG = args.debug

    global QUIET
    QUIET = args.quiet

    BUFFER_SIZE = args.buffer_size
    print("before if args.port")
    if args.port:
        try:
            connect_serial(args.port, baud=args.baud, wait=args.wait)
        except DeviceError as err:
            print(err)
    else:
        autoscan()
    autoconnect()
    print("before if num devices")
    if num_devices() == 0:
        print('')
        print('No MicroPython boards connected')
        print('')
        while num_devices() == 0:
            time.sleep(0.1)
    print(num_devices())

main()
	
