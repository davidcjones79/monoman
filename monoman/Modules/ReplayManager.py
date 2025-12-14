"""Recording and replay functionality for Monoman."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import orjson
import zstandard as zstd

from monoman.DataTypes import Snapshot


class RecordingWriter:
    """Writes snapshots to a compressed recording file."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Open compressed file for writing
        self._file = open(output_path, "wb")
        self._compressor = zstd.ZstdCompressor(level=3)
        self._stream = self._compressor.stream_writer(self._file)
        self._count = 0
        self._start_time = datetime.now()

    def write(self, snapshot: Snapshot) -> None:
        """Write a snapshot to the recording."""
        data = snapshot.to_dict()
        json_bytes = orjson.dumps(data)
        # Write length-prefixed JSON
        length = len(json_bytes)
        self._stream.write(length.to_bytes(4, "big"))
        self._stream.write(json_bytes)
        self._count += 1

    def close(self) -> None:
        """Close the recording file."""
        self._stream.close()
        self._file.close()

    @property
    def snapshot_count(self) -> int:
        """Get number of snapshots written."""
        return self._count

    @property
    def duration(self) -> float:
        """Get recording duration in seconds."""
        return (datetime.now() - self._start_time).total_seconds()

    def __enter__(self) -> "RecordingWriter":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class RecordingReader:
    """Reads snapshots from a compressed recording file."""

    def __init__(self, input_path: Path) -> None:
        self.input_path = input_path

        if not input_path.exists():
            raise FileNotFoundError(f"Recording file not found: {input_path}")

        self._file = open(input_path, "rb")
        self._decompressor = zstd.ZstdDecompressor()
        self._stream = self._decompressor.stream_reader(self._file)
        self._snapshots: list[Snapshot] = []
        self._current_index = 0
        self._loaded = False

    def load(self) -> None:
        """Load all snapshots into memory."""
        if self._loaded:
            return

        while True:
            try:
                # Read length prefix
                length_bytes = self._stream.read(4)
                if not length_bytes or len(length_bytes) < 4:
                    break

                length = int.from_bytes(length_bytes, "big")
                json_bytes = self._stream.read(length)

                if len(json_bytes) < length:
                    break

                data = orjson.loads(json_bytes)
                snapshot = Snapshot.from_dict(data)
                self._snapshots.append(snapshot)

            except Exception:
                break

        self._loaded = True

    def __iter__(self) -> Iterator[Snapshot]:
        """Iterate over all snapshots."""
        self.load()
        return iter(self._snapshots)

    def __len__(self) -> int:
        """Get number of snapshots."""
        self.load()
        return len(self._snapshots)

    def __getitem__(self, index: int) -> Snapshot:
        """Get snapshot by index."""
        self.load()
        return self._snapshots[index]

    @property
    def current(self) -> Snapshot | None:
        """Get current snapshot."""
        self.load()
        if 0 <= self._current_index < len(self._snapshots):
            return self._snapshots[self._current_index]
        return None

    def next(self) -> Snapshot | None:
        """Move to and return next snapshot."""
        self.load()
        if self._current_index < len(self._snapshots) - 1:
            self._current_index += 1
            return self.current
        return None

    def prev(self) -> Snapshot | None:
        """Move to and return previous snapshot."""
        self.load()
        if self._current_index > 0:
            self._current_index -= 1
            return self.current
        return None

    def seek(self, index: int) -> Snapshot | None:
        """Seek to specific snapshot index."""
        self.load()
        if 0 <= index < len(self._snapshots):
            self._current_index = index
            return self.current
        return None

    @property
    def position(self) -> int:
        """Get current position."""
        return self._current_index

    @property
    def duration(self) -> float:
        """Get recording duration in seconds."""
        self.load()
        if len(self._snapshots) < 2:
            return 0.0
        first = self._snapshots[0].timestamp
        last = self._snapshots[-1].timestamp
        return (last - first).total_seconds()

    @property
    def start_time(self) -> datetime | None:
        """Get recording start time."""
        self.load()
        if self._snapshots:
            return self._snapshots[0].timestamp
        return None

    @property
    def end_time(self) -> datetime | None:
        """Get recording end time."""
        self.load()
        if self._snapshots:
            return self._snapshots[-1].timestamp
        return None

    def close(self) -> None:
        """Close the recording file."""
        self._stream.close()
        self._file.close()

    def __enter__(self) -> "RecordingReader":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class ReplayManager:
    """Manages replay playback."""

    def __init__(self, recording_path: Path) -> None:
        self.reader = RecordingReader(recording_path)
        self.reader.load()
        self.is_playing = False
        self.playback_speed = 1.0

    @property
    def total_snapshots(self) -> int:
        """Get total number of snapshots."""
        return len(self.reader)

    @property
    def current_position(self) -> int:
        """Get current playback position."""
        return self.reader.position

    @property
    def current_snapshot(self) -> Snapshot | None:
        """Get current snapshot."""
        return self.reader.current

    def play(self) -> None:
        """Start playback."""
        self.is_playing = True

    def pause(self) -> None:
        """Pause playback."""
        self.is_playing = False

    def toggle_playback(self) -> bool:
        """Toggle playback state. Returns new state."""
        self.is_playing = not self.is_playing
        return self.is_playing

    def step_forward(self) -> Snapshot | None:
        """Step forward one snapshot."""
        return self.reader.next()

    def step_backward(self) -> Snapshot | None:
        """Step backward one snapshot."""
        return self.reader.prev()

    def seek(self, position: int) -> Snapshot | None:
        """Seek to specific position."""
        return self.reader.seek(position)

    def seek_percent(self, percent: float) -> Snapshot | None:
        """Seek to percentage of recording."""
        index = int((percent / 100) * (len(self.reader) - 1))
        return self.seek(index)

    def close(self) -> None:
        """Close the replay manager."""
        self.reader.close()


def get_recording_filename() -> str:
    """Generate a recording filename based on current timestamp."""
    now = datetime.now()
    return f"recording_{now.strftime('%Y%m%d_%H%M%S')}.monoman"


def cleanup_old_recordings(record_dir: Path, retention_hours: int) -> int:
    """Delete recordings older than retention period. Returns count deleted."""
    if not record_dir.exists():
        return 0

    cutoff = datetime.now().timestamp() - (retention_hours * 3600)
    deleted = 0

    for path in record_dir.glob("*.monoman"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                deleted += 1
        except OSError:
            continue

    return deleted
