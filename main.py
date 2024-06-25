from __future__ import annotations

import os
import threading
from pathlib import Path

from colorama import Fore
from pytube import Playlist, Stream, YouTube
from tqdm import tqdm

from utils import print_logo

if os.name == "nt":
    from colorama import just_fix_windows_console

    just_fix_windows_console()


class YTDownloader:
    def __init__(self, url: str, *, path: Path | str) -> None:
        self.url = url
        self.path = Path(path)

        self._stream = None

    @property
    def stream(self) -> Stream:
        if self._stream is None:
            self._stream = self._get_stream()

        return self._stream

    def _get_stream(self) -> Stream:
        video = YouTube(self.url)
        stream = video.streams.get_highest_resolution()
        if stream is None:
            stream = video.streams.get_lowest_resolution()

        assert stream is not None

        self._tqdm(stream)
        return stream

    def _tqdm(self, stream: Stream) -> Stream:

        name = stream.title
        string_limit = 64
        if len(name) > string_limit:
            start = name[: int(string_limit / 2)]
            end = name[-int(string_limit / 2) :]
            name = f"{start}...{end}"

        SIZE_OF_TAB = 8

        _bar = tqdm(
            total=stream.filesize,
            unit="bytes",
            unit_scale=True,
            desc=name,
            unit_divisor=1024,
            ascii=True,
            colour="CYAN",
            smoothing=0.3,
            dynamic_ncols=True,
            ncols=os.get_terminal_size().columns - SIZE_OF_TAB,
            bar_format="[*] {l_bar}{bar}| {n_fmt}/{total_fmt} %s[{elapsed}<{remaining}, {rate_fmt}{postfix}]%s"
            % (Fore.CYAN, Fore.RESET),
        )

        def progress(chunk, file_handle, bytes_remaining):
            _bar.update(len(chunk))

        def complete(file_handle):
            _bar.clear()
            _bar.close()

        stream.on_progress = progress
        stream.on_complete = complete
        return stream

    def download(self, *, overwrite_file: bool = False) -> None:
        stream = self.stream

        if not overwrite_file and (self.path / stream.title).exists():
            error = f"File already exists: {self.path / stream.title}"
            raise FileExistsError(error)

        stream.download(self.path, skip_existing=overwrite_file)

    def __hash__(self) -> int:
        return hash(self.url)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url!r})"

    def __str__(self) -> str:
        return self.url


class PlaylistDownloader:
    def __init__(self, url: str, *, path: Path | str) -> None:
        self.url = url
        self.path = Path(path)
        self.playlist = Playlist(self.url)

        self._threads = []

    def download(self, *, overwrite_file: bool = False) -> None:
        for ytd in self.capture():
            task = threading.Thread(target=ytd.download, kwargs={"overwrite_file": overwrite_file})
            self._threads.append(task)
            task.start()

        for task in self._threads:
            task.join()

    def capture(self):
        for url in self.playlist:
            yield YTDownloader(url, path=self.path)


if __name__ == "__main__":
    print_logo()
    url = input(f"{Fore.CYAN}[*] {Fore.YELLOW}Enter the URL: {Fore.RESET}")
    path = input(f"{Fore.CYAN}[*] {Fore.YELLOW}Enter the folder name: {Fore.RESET}")
    path = path.strip()
    if not path:
        print(
            f"{Fore.CYAN}[*] {Fore.YELLOW}Warning: {Fore.RESET}You did not enter a folder name. Using current directory."
        )

    if path and not os.path.exists(path):
        print(
            f"{Fore.CYAN}[*] {Fore.YELLOW}Warning: {Fore.RESET}Folder does not exist. Create folder {path}? [Y/n]",
            end=" ",
        )
        choice = input().strip().lower()
        if choice == "n":
            print(f"{Fore.CYAN}[*] {Fore.YELLOW}Exiting...{Fore.RESET}")
            exit(0)
        os.makedirs(path)

    if "playlist" in url:
        yt = PlaylistDownloader(url, path=path)
    elif "watch" in url:
        yt = YTDownloader(url, path=path)
    else:
        print(f"{Fore.CYAN}[*] {Fore.YELLOW}Invalid URL: {Fore.RESET}Please enter a valid URL.")
        exit(1)

    yt.download(overwrite_file=True)
