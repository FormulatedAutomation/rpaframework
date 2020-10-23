from collections import OrderedDict
import datetime
import getpass
import logging
import os
import platform
import signal
import socket
from typing import Any

from RPA.core.decorators import operating_system_required

if platform.system() == "Windows":
    import psutil
    from psutil._common import bytes2human
else:
    psutil = object
    bytes2human = object


class OperatingSystem:
    """RPA Framework library containing cross platform keywords for managing
    computer properties and actions.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @operating_system_required("Windows")
    def get_boot_time(
        self, as_datetime: bool = False, datetime_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Get computer boot time in seconds from Epoch or in datetime string.

        Example:
            ${boottime}  Get Boot Time
            ${boottime}  Get Boot Time   as_datetime=True
            ${boottime}  Get Boot Time   as_datetime=True  datetime_format=%d.%m.%Y

        Arguments:
            as_datetime (bool): if True returns datetime string, otherwise seconds,
                         defaults to False
            datetime_format (str): datetime string format, defaults to "%Y-%m-%d %H:%M:%S"

        Returns:
            seconds from Epoch or datetime string
        """
        btime = self.boot_time_in_seconds_from_epoch()
        if as_datetime:
            return datetime.datetime.fromtimestamp(btime).strftime(datetime_format)
        return btime

    @operating_system_required("Windows")
    def boot_time_in_seconds_from_epoch(self) -> str:
        """Get machine boot time

        Example:
            ${epoch}  Boot Time In Seconds From Epoch

        Returns:
            boot time in seconds from Epoch
        """
        return psutil.boot_time()

    def get_machine_name(self) -> str:
        """Get machine name

        Example:
            ${machine}  Get Machine Name

        Returns:
            machine name as string
        """
        return socket.gethostname()

    def get_username(self) -> str:
        """Get username of logged in user

        Example:
            ${user}  Get Username

        Returns:
            username as string
        """
        return getpass.getuser()

    @operating_system_required("Darwin", "Linux")
    def put_system_to_sleep(self) -> None:
        """Puts system to sleep mode

        Example:
            Put System To Sleep
        """
        if platform.system() == "Darwin":
            os.system("pmset sleepnow")
        if platform.system() == "Linux":
            os.system("systemctl suspend")

    @operating_system_required("Windows")
    def process_exists(self, process_name: str, strict: bool = True) -> Any:
        """Check if process exists by its name

        Example:
            ${process}  Process Exists  calc
            ${process}  Process Exists  calc  strict=False

        Arguments:
            process_name (str): search for this process
            strict (bool): defines how match is made, default `True`
                           which means that process name needs to be exact match
                           and `False` does inclusive matching

        Returns:
            process instance or False
        """
        for p in psutil.process_iter():
            p_name = p.name()
            if strict and process_name.lower() == p_name.lower():
                return p
            elif not strict and process_name.lower() in p_name.lower():
                return p
        return False

    @operating_system_required("Windows")
    def kill_process(self, process_name: str) -> bool:
        """Kill process by name

        Example:
            ${process}  Process Exists  calc  strict=False
            ${status}   Kill Process    ${process.name()}

        Arguments:
            process_name (str): name of the process

        Returns:
            `True` if succeeds `False` if not
        """
        p = self.process_exists(process_name)
        if p:
            p.terminate()
            return True
        return False

    @operating_system_required("Windows")
    def kill_process_by_pid(self, pid: int) -> None:
        """Kill process by pid

        Example:
            ${process}  Process Exists  calc  strict=False
            ${status}   Kill Process    ${process.pid}

        Arguments:
            pid (int): process identifier
        """
        os.kill(pid, signal.SIGTERM)

    @operating_system_required("Windows")
    def get_memory_stats(self, humanized: bool = True) -> dict:
        """Get computer memory stats and return those in bytes
        or in humanized memory format.

        Example:
            &{mem}     Get Memory Stats
            &{mem}     Get Memory Stats   humanized=False

        Arguments:
            humanized (bool): if `False` returns memory information in bytes,
                              defaults to `True`

        Returns:
            memory information in dictionary format
        """
        meminfo = psutil.virtual_memory()
        memdict = meminfo._asdict()
        if humanized:
            humandict = {}
            for key, val in memdict.items():
                if key == "percent":
                    humandict[key] = val
                else:
                    humandict[key] = bytes2human(val)
            return OrderedDict(humandict)
        return memdict
