#!/usr/bin/env python3
"""Проверка подключенного оборудования на Raspberry Pi."""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
from typing import List


def run_command(cmd: List[str]) -> List[str]:
    if not shutil.which(cmd[0]):
        return []
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def list_paths(pattern: str) -> List[str]:
    return sorted(glob.glob(pattern))


def print_section(title: str, items: List[str]) -> None:
    print(f"\n=== {title} ===")
    if not items:
        print("Не найдено")
        return
    for item in items:
        print(f"- {item}")


def get_usb_devices() -> List[str]:
    return run_command(["lsusb"])


def get_block_devices() -> List[str]:
    lines = run_command(["lsblk", "-dno", "NAME,MODEL,SIZE,TRAN"])
    return [line for line in lines if line]


def get_i2c() -> List[str]:
    buses = list_paths("/dev/i2c-*")
    if buses:
        return buses
    return run_command(["i2cdetect", "-l"])


def get_serial() -> List[str]:
    devices = []
    patterns = [
        "/dev/ttyAMA*",
        "/dev/ttyS*",
        "/dev/ttyUSB*",
        "/dev/ttyACM*",
        "/dev/serial/by-id/*",
    ]
    for pattern in patterns:
        devices.extend(list_paths(pattern))
    return sorted(set(devices))


def get_spi() -> List[str]:
    return list_paths("/dev/spidev*")


def get_video() -> List[str]:
    return list_paths("/dev/video*")


def get_gpiochips() -> List[str]:
    return list_paths("/dev/gpiochip*")


def get_network() -> List[str]:
    interfaces = []
    base = "/sys/class/net"
    if not os.path.isdir(base):
        return interfaces

    for iface in sorted(os.listdir(base)):
        if iface == "lo":
            continue
        mac_path = os.path.join(base, iface, "address")
        state_path = os.path.join(base, iface, "operstate")
        mac = "unknown"
        state = "unknown"
        try:
            with open(mac_path, "r", encoding="utf-8") as f:
                mac = f.read().strip()
        except Exception:
            pass
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = f.read().strip()
        except Exception:
            pass
        interfaces.append(f"{iface} (MAC: {mac}, state: {state})")
    return interfaces


def main() -> None:
    print("Список подключенного оборудования Raspberry Pi")
    print_section("USB устройства", get_usb_devices())
    print_section("Блочные устройства (диски/SD/USB storage)", get_block_devices())
    print_section("I2C", get_i2c())
    print_section("SPI", get_spi())
    print_section("UART/Serial", get_serial())
    print_section("Видео устройства", get_video())
    print_section("GPIO chips", get_gpiochips())
    print_section("Сетевые интерфейсы", get_network())


if __name__ == "__main__":
    main()
