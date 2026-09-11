"""Saved missing-rope regression: shared unlock, native spawn, ride and replay."""
from probe import *

p = Probe()
c = p.core
c.al_probe_player.restype = C.POINTER(C.c_ubyte)
fixture = ((ROOT/'diagnostics/rope-user.core').read_bytes(),
           (ROOT/'diagnostics/rope-user.extra').read_bytes())

def restore(state):
    p.restore(state[0])
    assert c.al_coop_restore(C.create_string_buffer(state[1]), len(state[1]))

def save():
    extra = C.create_string_buffer(c.al_coop_state_size())
    assert c.al_coop_save(extra, len(extra))
    return p.save(), extra.raw

def step(n=1, one=0, two=0):
    c.al_coop_buttons(0, one)
    c.al_coop_buttons(1, two)
    p.run(n)

def status():
    s = (C.c_uint*7)()
    c.al_coop_status(s)
    return list(s)

def ropes():
    r = p.ram()
    # Native template plus its stationary and riding object types.
    return [i for i in range(1, 25) if r[0x7e40+i*66] in (0x12, 0x84)
            and r[0x7e72+i*66:0x7e75+i*66] == bytes.fromhex('2064ba')]

restore(fixture)
start = status()
camera = p.ram()[0x7df6:0x7dfa]
assert p.ram()[0xceeb] == 0xba and p.ram()[0xf12a] == 255
step(90)
assert status()[3:] == start[3:]
assert abs(int.from_bytes(p.ram()[0x7df6:0x7df8], 'big') -
           int.from_bytes(camera[:2], 'big')) <= 4
assert p.ram()[0x7df8:0x7dfa] == camera[2:]
assert p.ram()[0xceeb] == 0, 'Pending rope trigger was never consumed'
assert len(ropes()) == 1, ropes()
ready = save()

def ride():
    step(28, one=1<<7, two=1<<7)
    step(22, one=1<<7)
    step(20, one=(1<<8)|(1<<4), two=(1<<8)|(1<<4))
    step(80, one=1<<4, two=1<<4)
    s = status()
    assert s[4] < 1450 and s[6] < 1450 and s[3:5] == s[5:7], s
    assert len(ropes()) == 1, 'Duplicate rope spawned'
    return s, hashlib.sha256(p.frame[0]).hexdigest()

a = ride()
restore(ready)
assert ride() == a
p.screenshot(ROOT/'diagnostics/verified-rooftop-rope.png')

# Missing flutes must not unlock ropes; old P2-only unlocks must migrate.
restore(fixture)
p.write(0xf12a, b'\0')
for player in (0, 1):
    c.al_probe_player(player)[0xf12a] = 0
step(90)
assert p.ram()[0xceeb] == 0xba and not ropes()
c.al_probe_player(1)[0xf12a] = 255
old_p2_only = save()
restore(old_p2_only)
assert p.ram()[0xf12a] == 255
step(90)
assert len(ropes()) == 1 and p.ram()[0xceeb] == 0

# Both context installations retain a shared unlock during ordinary gameplay.
for player in (0, 1):
    c.al_probe_player(player)[0xf12a] = 0
step(30)
assert p.ram()[0xf12a] == 255
print('PASS: saved rope restored without scrolling, both players ride, no duplicate,')
print('      deterministic replay, flute required, P2-only save migration, shared flag')
