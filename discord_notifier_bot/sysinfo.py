import datetime
import os
import time
from collections import defaultdict, namedtuple
from datetime import timedelta
from functools import lru_cache

# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def has_extra_cpu():
    try:
        import psutil
    except ImportError:
        return False
    return True


@lru_cache(maxsize=1)
def has_extra_gpu():
    try:
        import GPUtil
    except ImportError:
        return False
    return True


def get_cpu_info():
    if not has_extra_cpu():
        return None

    import psutil

    meminfo = psutil.virtual_memory()
    GB_div = 1024 ** 3

    info = (
        "```\n"
        + "\n".join(
            [
                f"Uptime:  {timedelta(seconds=int(time.time() - psutil.boot_time()))}",
                f"CPUs:    {psutil.cpu_count()}",
                f"RAM:     {meminfo.total / GB_div:.1f} GB",
                "",
                "Load:    1min: {0[0]:.1f}%, 5min: {0[1]:.1f}%, 15min: {0[2]:.1f}%".format(
                    [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
                ),
                f"Memory:  {(meminfo.used / meminfo.total) * 100:.1f}% [used: {meminfo.used / GB_div:.1f} / {meminfo.total / GB_div:.1f} GB] [available: {meminfo.available  / GB_div:.1f} GB]",
            ]
        )
        + "\n```"
    )

    return info


def get_disk_info():
    if not has_extra_cpu():
        return None

    import psutil
    from psutil._common import bytes2human

    info = ""

    disks = [
        disk
        for disk in psutil.disk_partitions(all=False)
        if "loop" not in disk.device and not disk.mountpoint.startswith("/boot")
    ]

    header = ("Device", "Mount", "Use", "Total", "Used", "Free")
    rows = list()
    for disk in disks:
        usage = psutil.disk_usage(disk.mountpoint)
        rows.append(
            (
                disk.device,
                disk.mountpoint,
                f"{usage.percent:.1f} %",
                bytes2human(usage.total),
                bytes2human(usage.used),
                bytes2human(usage.free),
                # disk.fstype,
            )
        )

    lengths = [
        max(len(row[field_idx]) for row in [header] + rows)
        for field_idx in range(len(rows[0]))
    ]

    info = (
        "```\n"
        + "\n".join(
            # header
            [
                # "| " +
                " | ".join(
                    [
                        f"{field:{field_len}s}"
                        for field, field_len in zip(header, lengths)
                    ]
                )
                # + " |"
            ]
            # separator
            + [
                # "| " +
                " | ".join(["-" * field_len for field_len in lengths])
                # + " |"
            ]
            # rows
            + [
                # "| " +
                " | ".join(
                    # text fields
                    [
                        f"{field:<{field_len}s}"
                        for field, field_len in list(zip(row, lengths))[:2]
                    ]
                    # values/number
                    + [
                        f"{field:>{field_len}s}"
                        for field, field_len in list(zip(row, lengths))[2:]
                    ]
                )
                # + " |"
                for row in rows
            ]
        )
        + "\n```"
    )

    return info


def get_gpu_info():
    if not has_extra_gpu():
        return None

    import GPUtil

    rows = list()
    fields = ["ID", "Util", "Mem", "Temp", "Memory (Used)"]  # , "Name"]
    rows.append(fields)

    for gpu in GPUtil.getGPUs():
        fields = [
            f"{gpu.id}",
            f"{gpu.load * 100:.0f} %",
            f"{gpu.memoryUtil * 100:.1f} %",
            f"{gpu.temperature:.1f} °C",
            f"{int(gpu.memoryUsed)} / {int(gpu.memoryTotal)} MB",
            # f"{gpu.name}",
        ]
        rows.append(fields)

    lengths = [
        max(len(row[field_idx]) for row in rows) for field_idx in range(len(rows[0]))
    ]

    info = (
        "```\n"
        + "\n".join(
            # header
            [
                # "| " +
                " | ".join(
                    [
                        f"{field:{field_len}s}"
                        for field, field_len in zip(rows[0], lengths)
                    ]
                )
                # + " |"
            ]
            # separator
            + [
                # "| " +
                " | ".join(["-" * field_len for field_len in lengths])
                # + " |"
            ]
            # rows
            + [
                # "| " +
                " | ".join(
                    [f"{field:>{field_len}s}" for field, field_len in zip(row, lengths)]
                )
                # + " |"
                for row in rows[1:]
            ]
        )
        + "\n```"
    )

    return info


def get_local_machine_name():
    return os.uname().nodename


def get_info_message(with_cpu=True, with_gpu=True):
    message = f"**Status of `{get_local_machine_name()}`**\n"
    message += f"Date: `{datetime.datetime.now()}`\n\n"

    if with_cpu and has_extra_cpu():
        message += "System information:"
        ret = get_cpu_info()
        if ret is not None:
            message += "\n" + ret + "\n"
        else:
            message += " N/A\n"

        message += "Disk information:"
        ret = get_disk_info()
        if ret is not None:
            message += "\n" + ret + "\n"
        else:
            message += " N/A\n"

    if with_gpu and has_extra_gpu():
        message += "GPU information:"
        ret = get_gpu_info()
        if ret is not None:
            message += "\n" + ret + "\n"
        else:
            message += " N/A\n"

    return message


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------


ObservableLimit = namedtuple(
    "ObservableLimit",
    (
        #: visible name of the check/limit/...
        "name",
        #: function that returns a numeric value
        "fn_retrieve",
        #: function that get current and threshold value (may be ignored)
        #: and returns True if current value is ok
        "fn_check",
        #: threshold, numeric (for visibility purposes)
        "threshold",
        #: message to send if check failed (e. g. resource exhausted)
        "message",
        #: badness increment for each failed check, None for default
        #: can be smaller than threshold to allow for multiple consecutive failed checks
        #: or same as threshold to immediatly notify
        "badness_inc",
        #: badness threshold if reached, a message is sent, None for default
        #: allows for fluctuations until message is sent
        "badness_threshold",
    ),
)


class BadCounterManager:
    """Manager that gathers badness values for keys with
    individual thresholds and increments."""

    def __init__(self, default_threshold=3, default_increase=3):
        self.bad_counters = defaultdict(int)
        self.default_increase = default_increase
        self.default_threshold = default_threshold

    def reset(self, name=None):
        """Reset counters etc. to normal/default levels."""
        if name is not None:
            self.bad_counters[name] = 0
        else:
            for name in self.bad_counters.keys():
                self.bad_counters[name] = 0

    def increase_counter(self, name, limit):
        """Increse the badness level and return True if threshold reached."""
        bad_threshold = (
            limit.badness_threshold
            if limit.badness_threshold is not None
            else self.default_threshold
        )
        bad_inc = (
            limit.badness_inc
            if limit.badness_inc is not None
            else self.default_increase
        )

        # increse value
        self.bad_counters[name] = min(bad_threshold, self.bad_counters[name] + bad_inc)

        return self.threshold_reached(name, limit)

    def decrease_counter(self, name, limit):
        """Decrease the badness counter and return True if normal."""
        if self.bad_counters[name] > 0:
            self.bad_counters[name] = max(0, self.bad_counters[name] - 1)

        return self.is_normal(name)

    def threshold_reached(self, name, limit):
        """Return True if the badness counter has reached the threshold."""
        bad_threshold = (
            limit.badness_threshold
            if limit.badness_threshold is not None
            else self.default_threshold
        )

        return self.bad_counters[name] >= bad_threshold

    def is_normal(self, name):
        """Return True if the badness counter is zero/normal."""
        return self.bad_counters[name] == 0


class NotifyBadCounterManager(BadCounterManager):
    """Manager that collects badness values and notification statuses."""

    def __init__(self, default_threshold=3, default_increase=3):
        super().__init__(
            default_threshold=default_threshold, default_increase=default_increase
        )
        self.notified = defaultdict(bool)

    def reset(self, name=None):
        super().reset(name=name)

        if name is not None:
            self.notified[name] = False
        else:
            for name in self.notified.keys():
                self.notified[name] = False

    def decrease_counter(self, name, limit):
        """Decrease the counter and reset the notification flag
        if the normal level has been reached.
        Returns True on change from non-normal to normal
        (for a one-time notification setup)."""
        was_normal_before = self.is_normal(name)
        has_notified_before = self.notified[name]
        is_normal = super().decrease_counter(name, limit)
        if is_normal:
            self.notified[name] = False
        # return True if changed, else False if it was already normal
        # additionally require a limit exceeded message to be sent, else ignore the change
        return was_normal_before != is_normal and has_notified_before

    def should_notify(self, name, limit):
        """Return True if a notification should be sent."""
        if not self.threshold_reached(name, limit):
            return False

        if not self.notified[name]:
            return True

    def mark_notified(self, name):
        """Mark this counter as already notified."""
        self.notified[name] = True


def make_observable_limits():
    if not has_extra_cpu():
        return dict()

    # ----------------------------------------------------

    import psutil

    def _get_loadavg():
        return [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]

    def _get_mem_util():
        mem = psutil.virtual_memory()
        return mem.used / mem.total * 100

    def _get_disk_paths():
        disks = [
            disk
            for disk in psutil.disk_partitions(all=False)
            if "loop" not in disk.device and not disk.mountpoint.startswith("/boot")
        ]
        paths = [disk.mountpoint for disk in disks]
        return paths

    def _get_disk_usage(path):
        return psutil.disk_usage(path).percent

    def _get_disk_free_gb(path):
        return psutil.disk_usage(path).free / 1024 / 1024 / 1024

    # ----------------------------------------------------

    limits = dict()

    limits["cpu_load_5min"] = ObservableLimit(
        name="CPU-Load-Avg-5min",
        fn_retrieve=lambda: _get_loadavg()[1],
        fn_check=lambda cur, thres: cur < thres,
        threshold=95.0,
        message="**CPU Load Avg [5min]** is too high! (value: `{cur_value}%`, threshold: `{threshold})`",
        # increase badness level by 1
        badness_inc=1,
        # notify, when badness counter reached 3
        badness_threshold=3,
    )
    limits["mem_util"] = ObservableLimit(
        name="Memory-Utilisation",
        fn_retrieve=lambda: _get_mem_util(),
        fn_check=lambda cur, thres: cur < thres,
        threshold=85.0,
        message="**Memory Usage** is too high! (value: `{cur_value}%`, threshold: `{threshold})`",
        # increase badness level by 1
        badness_inc=1,
        # notify, when badness counter reached 3
        badness_threshold=3,
    )

    for i, path in enumerate(_get_disk_paths()):
        limits[f"disk_util_perc{i}"] = ObservableLimit(
            name=f"Disk-Usage-{path}",
            fn_retrieve=lambda: _get_disk_usage(path),
            fn_check=lambda cur, thres: cur < thres,
            threshold=95.0,
            message=(
                f"**Disk Usage for `{path}`** is too high! "
                "(value: `{cur_value}%`, threshold: `{threshold})`"
            ),
            # use default increment amount
            badness_inc=None,
            # notify immediately
            badness_threshold=None,
        )
        # TODO: disable the static values test if system has less or not significantly more total disk space
        limits[f"disk_util_gb{i}"] = ObservableLimit(
            name=f"Disk-Space-Free-{path}",
            fn_retrieve=lambda: _get_disk_free_gb(path),
            fn_check=lambda cur, thres: cur > thres,
            # currently a hard-coded limit of 30GB (for smaller systems (non-servers) unneccessary?)
            threshold=30.0,
            message=(
                "No more **Disk Space for `{path}`**! "
                "(value: `{cur_value}GB`, threshold: `{threshold})`"
            ),
            # use default increment amount
            badness_inc=None,
            # notify immediately
            badness_threshold=None,
        )

    # TODO: GPU checks
    # NOTE: may be useful if you just want to know when GPU is free for new stuff ...

    return limits


# ---------------------------------------------------------------------------
