from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytube import Stream

from colorama import Fore


def print_logo():
    with open("logo.txt", "r") as f:
        logo = f.read()

    logo = logo.replace("{0}", Fore.RED)
    logo = logo.replace("{1}", Fore.WHITE)
    logo = logo.replace("{2}", Fore.YELLOW)

    print(logo + Fore.RESET)


def bytes_to_human_readable(b: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {unit}"
        b = b / 1024
    return "0 B"


def print_metadata(stream: Stream):
    st = f"\t{Fore.YELLOW}{stream.title} {Fore.WHITE}({stream.resolution})"
    st += (
        f"\n\t\t{Fore.CYAN}Type: {Fore.YELLOW}{stream.mime_type} "
        f"{Fore.CYAN}Size: {Fore.YELLOW}{stream.filesize} bytes ({bytes_to_human_readable(stream.filesize)}) "
        f"{Fore.CYAN}FPS: {Fore.YELLOW}{stream.fps} "
        f"{Fore.CYAN}Quality: {Fore.YELLOW}{stream.abr} "
        f"{Fore.CYAN}Codec: {Fore.YELLOW}{stream.video_codec} "
        f"{Fore.CYAN}Audio Codec: {Fore.YELLOW}{stream.audio_codec}{Fore.RESET}"
    )
    return st
