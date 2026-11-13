"""Ticket 06 offline regressions (Attempt-5 console swallow class): the console
echo handshake keeps at most one unacknowledged console command in flight, so a
later save() can never queue behind an unexecuted line of the OpenTTD dedicated
input loop. Studies of record:
.scratch/ramrom-product/research/03-attempt5-save-stall-forensics.md and
.scratch/ramrom-product/issues/06-console-echo-handshake.md."""

import ast
import asyncio
import io
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

import app.simulation.openttd.proof.road_mutation as road_mutation
from app.simulation.openttd.freight_native_network import paused_world_clock
from app.simulation.openttd.proof.road_mutation import console, console_ack

PAUSE_ECHO = "*** Game paused (manual)"
UNPAUSE_ECHO = "*** Game unpaused (manual)"


class DedicatedGameModel:
    """Model of OpenTTD 15.3 dedicated stdin handling (DedicatedHandleKeyInput
    in src/video/dedicated_v.cpp): one pump() is one input-loop iteration. A
    read(2) can collect two queued lines; getline then executes only the first
    and the rest stays inside the C++ streambuf, which the select() readiness
    check cannot see; such a hidden line executes only when new bytes reach
    fd 0 and make select() ready again (the sealed Attempt-5 stall)."""

    def __init__(self, stdout_path):
        self.stdout_path = stdout_path
        self.stream = io.BytesIO()
        self.readable = []  # lines on fd 0 not yet consumed by a read(2)
        self.hidden = []  # lines held inside the streambuf
        self.executed = 0

    def write(self, data):
        self.stream.write(data)
        self.readable.extend(data.decode().splitlines())

    def flush(self):
        pass

    def pump(self):
        if self.readable and self.hidden:
            # getline returns streambuf content before reading fd again.
            line = self.hidden.pop(0)
        elif self.readable:
            # One read(2) drains everything; getline executes only the first.
            self.hidden.extend(self.readable[1:])
            line = self.readable.pop(0)
            self.readable.clear()
        else:
            return
        self.execute(line)

    def execute(self, line):
        self.executed += 1
        if line in ("pause", "unpause"):
            echo = {"pause": PAUSE_ECHO, "unpause": UNPAUSE_ECHO}[line]
        elif (saved := re.fullmatch(r'save "(.+)"', line)) is not None:
            echo = "Saving map...\nMap successfully saved to '" + saved.group(1) + ".sav'."
        else:
            return
        with self.stdout_path.open("a") as log:
            log.write(echo + "\n")


class EchoingGame(DedicatedGameModel):
    """Healthy variant: the game services stdin by the end of each write, so
    every command acknowledges inside one poll cycle."""

    def write(self, data):
        DedicatedGameModel.write(self, data)
        self.pump()


class SilentGame(DedicatedGameModel):
    """Wedged variant: stdin is never serviced; no echo ever appears."""

    def pump(self):
        pass


class PauseOnlyGame(EchoingGame):
    """Answers one pause, then wedges: the unpause echo never arrives."""

    def pump(self):
        if self.executed >= 1:
            return
        DedicatedGameModel.pump(self)


class Backend:
    """Owned-backend stub carrying the health() poll contract of save()."""

    def __init__(self, game):
        self.process = SimpleNamespace(stdin=game)

    def health(self):
        pass


def prepared_for(tmp_path):
    """Fake prepared with the two real log files every fresh-tail poll needs."""
    stdout_path = tmp_path / "stdout.log"
    stderr_path = tmp_path / "stderr.log"
    stdout_path.write_bytes(b"")
    stderr_path.write_bytes(b"")
    return SimpleNamespace(
        directory=tmp_path,
        spec=SimpleNamespace(stdout_path=stdout_path, stderr_path=stderr_path),
    )


def tail(prepared):
    return prepared.spec.stdout_path.read_text(
        errors="replace"
    ) + prepared.spec.stderr_path.read_text(errors="replace")


def test_console_ack_returns_only_after_echo_observed(tmp_path):
    prepared = prepared_for(tmp_path)
    backend = Backend(EchoingGame(prepared.spec.stdout_path))

    asyncio.run(console_ack(backend, prepared, "pause", "Game paused (manual)"))

    assert PAUSE_ECHO in tail(prepared)
    assert backend.process.stdin.stream.getvalue() == b"pause\n"


def test_handshake_orders_capture_between_acknowledged_pause_and_resume(tmp_path):
    """T1 of record: the capture body cannot start before the pause echo is
    observed, and the context cannot exit before the unpause echo."""
    prepared = prepared_for(tmp_path)
    game = EchoingGame(prepared.spec.stdout_path)
    backend = Backend(game)
    diagnostic = {}
    ran = []

    async def drive():
        async with paused_world_clock(backend, prepared, diagnostic=diagnostic):
            assert PAUSE_ECHO in tail(prepared)
            ran.append("capture")

    asyncio.run(drive())
    assert ran == ["capture"]
    assert game.stream.getvalue() == b"pause\nunpause\n"
    assert UNPAUSE_ECHO in tail(prepared)
    assert diagnostic == dict(pause_pairs=1)


def test_console_ack_times_out_typed_and_never_retries(tmp_path):
    """T2 of record: a missing echo surfaces as the typed TimeoutError with the
    message of record, and the command is written exactly once."""
    prepared = prepared_for(tmp_path)
    game = SilentGame(prepared.spec.stdout_path)
    backend = Backend(game)

    async def drive():
        with pytest.raises(TimeoutError) as info:
            await console_ack(backend, prepared, "pause", "Game paused (manual)", timeout=0.1)

        assert str(info.value) == "console echo acknowledgement missing"

    asyncio.run(drive())
    assert game.stream.getvalue() == b"pause\n"


def test_unpause_ack_timeout_is_recorded_body_error_kept(tmp_path, monkeypatch):
    real_ack = road_mutation.console_ack

    def fast_ack(backend, prepared, command, marker, **kwargs):
        kwargs["timeout"] = 0.1
        return real_ack(backend, prepared, command, marker, **kwargs)

    monkeypatch.setattr(road_mutation, "console_ack", fast_ack)
    prepared = prepared_for(tmp_path)
    game = PauseOnlyGame(prepared.spec.stdout_path)
    backend = Backend(game)
    diagnostic = {}

    async def drive():
        with pytest.raises(RuntimeError, match="pausing capture"):
            async with paused_world_clock(backend, prepared, diagnostic=diagnostic):
                raise RuntimeError("pausing capture failed")

    asyncio.run(drive())
    assert diagnostic["pause_resume_error"] == "console echo acknowledgement missing"
    assert "pause_pairs" not in diagnostic
    assert game.stream.getvalue() == b"pause\nunpause\n"


def console_issuers(path):
    tree = ast.parse(path.read_text())
    issuers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for sub in ast.walk(node):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Name)
                    and sub.func.id == "console"
                ):
                    issuers.add(node.name)
    return issuers


def test_no_unacknowledged_console_commands_on_attempt_path():
    """T3 of record (AST invariant): on the loop attempt path every
    owned-console command issues through save() or console_ack(), so at most
    one unacknowledged command is ever in flight. Bare console() issuers are
    confined to the sanctioned issuers here; the single start_ai bootstrap in
    run() is exempt because its completion is already awaited by the
    ROAD_PROOF_COMPANY_READY poll directly after it. Console issuers outside
    the attempt path (corridor_* bootstrap commands, freight_canonical_dispatch,
    canonical_fleet) are out of this ticket's scope."""
    openttd = Path(__file__).parents[1] / "app" / "simulation" / "openttd"
    sanctioned = {
        "freight_native_network.py": set(),  # no direct console() call at all
        "proof/road_mutation.py": {"console", "save", "console_ack", "run"},
    }
    for name, allowed in sanctioned.items():
        issuers = console_issuers(openttd / name)
        assert issuers <= allowed, (name, sorted(issuers), sorted(allowed))


def test_adjacency_swallow_reproduces_attempt5_loss(tmp_path):
    """T4 red of record: with the old fire-and-forget adjacency (unpause
    written, save written with no acknowledgement in between) one dedicated
    input read(2) consumed both lines, executed only the unpause and held the
    save line in the streambuf across every later input iteration; the save
    executed only after the failure-path third write, exactly the sealed
    stdout.log order of Attempt 5."""
    prepared = prepared_for(tmp_path)
    game = DedicatedGameModel(prepared.spec.stdout_path)
    backend = Backend(game)
    qualified = str(tmp_path / "qualified")
    failure = str(tmp_path / "failure")
    completion = "Map successfully saved to '"

    console(backend, "unpause")
    console(backend, 'save "' + qualified + '"')
    game.pump()
    assert UNPAUSE_ECHO in tail(prepared)
    for _ in range(6):
        game.pump()
        assert "Map successfully saved" not in tail(prepared)  # save line swallowed

    console(backend, 'save "' + failure + '"')  # the failure-path third write
    game.pump()
    game.pump()
    tail_text = tail(prepared)
    assert completion + qualified + ".sav'." in tail_text
    assert tail_text.index(completion + qualified) < tail_text.index(completion + failure)


def test_handshake_releases_save_only_after_unpause_echo(tmp_path):
    """T4 green of record: with the handshake the capture-exit unpause is
    acknowledged while it is still the only unacknowledged command in flight,
    and the following save is written only once the unpause echo is observed."""
    prepared = prepared_for(tmp_path)
    game = DedicatedGameModel(prepared.spec.stdout_path)
    backend = Backend(game)
    diagnostic = {}
    qualified = str(tmp_path / "qualified")

    async def pump_soon():
        await asyncio.sleep(0.02)
        game.pump()

    async def drive():
        ctx = paused_world_clock(backend, prepared, diagnostic=diagnostic)
        boot = asyncio.create_task(pump_soon())  # executes the pause echo in flight
        await ctx.__aenter__()
        await boot
        assert PAUSE_ECHO in tail(prepared)
        assert game.readable == []  # pause acknowledged; nothing in flight

        resume = asyncio.create_task(ctx.__aexit__(None, None, None))
        await asyncio.sleep(0.001)
        assert game.readable == ["unpause"]  # exactly one unacknowledged in flight
        assert UNPAUSE_ECHO not in tail(prepared)
        assert b'save "' not in game.stream.getvalue()  # no save joined the queue
        await pump_soon()
        await resume

        assert UNPAUSE_ECHO in tail(prepared)
        console(backend, 'save "' + qualified + '"')
        assert game.readable == ['save "' + qualified + '"']
        await pump_soon()
        assert "Map successfully saved to '" + qualified + ".sav'." in tail(prepared)
        transcript = game.stream.getvalue()
        assert transcript.index(b"unpause\n") < transcript.index(b'save "')
        assert diagnostic == dict(pause_pairs=1)

    asyncio.run(drive())
