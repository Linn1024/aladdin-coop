"""Compare native object templates against single-player motion, frame for frame."""
exec(compile(open(__file__.replace('verify_object_physics.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
fixture=((ROOT/'diagnostics/physics-user.core').read_bytes(),
         (ROOT/'diagnostics/physics-user.extra').read_bytes())
rom=next(ROOT.glob('*.bin')).read_bytes()
a=0x7e40+15*66
for template in (0x1b819c,0x1b81d8,0x1b8034,0x1b8048,0x1b7bd4,0x1b8200):
    restore(fixture)
    for i in range(1,31):p.write(0x7e40+i*66,b'\0')
    # Decode the original 20-byte spawn template like native 1AE30A.
    t=rom[template:template+20];o=bytearray(66)
    o[:2]=t[:2];o[6:10]=t[2:6];o[10:14]=t[6:10]
    o[30:32]=t[10:12];o[32:36]=t[12:16]
    o[41]=t[16];o[53]=t[17];o[60]=t[18]
    o[2:4]=(1150).to_bytes(2,'big');o[4:6]=(1000).to_bytes(2,'big')
    p.write(a,o);step(2);initial=save();tracks=[]
    for native in (False,True):
        restore(initial)
        if native:c.al_coop_enable(0);p.write(0x863e,b'\0')
        track=[]
        for frame in range(60):
            step();r=p.ram()
            track.append((r[a],r[a+2:a+10],r[a+24:a+30]))
        tracks.append(track)
    assert tracks[0]==tracks[1], (hex(template),next((i,x,y) for i,(x,y) in enumerate(zip(*tracks)) if x!=y))
    # Require actual falling and a bounce, not just a static object comparison.
    assert len({t[1][2:4] for t in tracks[0]})>1
    velocities=[int.from_bytes(t[2][2:4],'big',signed=True) for t in tracks[0]]
    if o[60]&16:
        assert any(v>0 for v in velocities) and any(v<0 for v in velocities), (hex(template),velocities)
    restore(initial);step(60);expected=status(),hashlib.sha256(p.frame[0]).hexdigest()
    restore(initial);step(60);assert (status(),hashlib.sha256(p.frame[0]).hexdigest())==expected
    print('PASS: native falling/bouncing trajectory and replay',hex(template),flush=True)
