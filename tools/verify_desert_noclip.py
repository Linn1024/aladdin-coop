"""Regression: Desert bottom-edge streaming must never enter the native trap."""
from probe import *

p = Probe()
c = p.core
p.restore((ROOT / 'first-level.state').read_bytes())
c.al_coop_enable(1)
p.run(10)
assert c.al_coop_debug_stage(3)
for frame in range(2400):
    p.run(1, {3} if frame % 90 == 0 else set())
    if frame > 1 and c.al_coop_ready() and c.al_coop_level() == 3:
        break
else:
    raise AssertionError('Desert failed to load')
assert c.al_coop_debug(8)

def status():
    s = (C.c_uint * 7)()
    c.al_coop_status(s)
    return list(s)

def fly(frames, button):
    c.al_coop_buttons(0, 1 << button)
    for frame in range(frames):
        before = status()[1]
        p.run()
        assert status()[1] == before + 1, ('Frozen gameplay', status())
        ram = p.ram()
        camera_y = int.from_bytes(ram[0x7df8:0x7dfa], 'big')
        assert camera_y < 512 - 240, camera_y

# Starting height already pushes the camera to its bottom limit. The old
# code freezes at X3954 when the renderer reads row 32 of a 32-row map.
fly(1000, 7)
raw = p.save()
extra = C.create_string_buffer(c.al_coop_state_size())
assert c.al_coop_save(extra, len(extra))
fly(100, 7)
expected = status(), hashlib.sha256(p.frame[0]).hexdigest()
p.restore(raw)
assert c.al_coop_restore(extra, len(extra))
fly(100, 7)
assert (status(), hashlib.sha256(p.frame[0]).hexdigest()) == expected
fly(900, 7)
fly(200, 5)
fly(1900, 6)
fly(200, 4)
fly(1900, 7)
fly(200, 5)
assert c.al_coop_debug(8)
c.al_coop_buttons(0, 0)
p.run()
s = status()
assert s[3:5] == s[5:7], s
before = s[1]
p.run(120)
assert status()[1] > before, status()
print('PASS: Desert noclip edges, former freeze point, save replay, and handoff')
