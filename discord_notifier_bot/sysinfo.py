import datetime
import os
import time
from collections import namedtuple
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
    "ObservableLimit", ("name", "fn_retrieve", "fn_check", "threshold", "message")
)


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

    limits["cpu_load_1min"] = ObservableLimit(
        name="CPU-Load-1min",
        fn_retrieve=lambda: _get_loadavg()[1],
        fn_check=lambda cur, thres: cur < thres,
        threshold=90.0,
        message="**CPU Load Avg [5min]** is too high! (value: `{cur_value}%`, threshold: `{threshold})`",
    )
    limits["mem_util"] = ObservableLimit(
        name="Memory-Utilisation",
        fn_retrieve=lambda: _get_mem_util(),
        fn_check=lambda cur, thres: cur < thres,
        threshold=85.0,
        message="**Memory Usage** is too high! (value: `{cur_value}%`, threshold: `{threshold})`",
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
        )
        limits[f"disk_util_gb{i}"] = ObservableLimit(
            name=f"Disk-Space-Free-{path}",
            fn_retrieve=lambda: _get_disk_free_gb(path),
            fn_check=lambda cur, thres: cur > thres,
            threshold=30.0,
            message=(
                "No more **Disk Space for `{path}`**! "
                "(value: `{cur_value}GB`, threshold: `{threshold})`"
            ),
        )

    return limits


# ---------------------------------------------------------------------------
