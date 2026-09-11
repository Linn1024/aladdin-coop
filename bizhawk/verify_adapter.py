"""Run the installed adapter headlessly and verify co-op save-state replay."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import probe
probe.CORE=Path(__file__).resolve().parent/'aladdin_coop_libretro.dll'
from probe import C,Probe,ROOT
import hashlib,json
p=Probe();audio=[]
@C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
def sound(data,n):audio.append(C.string_at(data,n*4));return n
p.callbacks.append(sound);p.core.retro_set_audio_sample_batch(sound)
for n in range(100):
    p.buttons[1]={7} if n<30 else set()
    p.run(1,{8} if 50<=n<70 else set())
initial=p.save()
def replay():
    video=[];audio.clear()
    for n in range(250):
        p.buttons[1]=({7} if n<70 else {10} if n==100 else {1} if 160<=n<170 else set())
        p.run(1,{7} if 10<=n<60 else {8} if 110<=n<130 else set())
        video.append(p.frame[0])
    return hashlib.sha256(b''.join(video)).hexdigest(),hashlib.sha256(b''.join(audio)).hexdigest()
a=replay();p.screenshot(ROOT/'bizhawk/replay-headless.png')
p.restore(initial);b=replay();assert a[0]==b[0],(a,b)
assert any(any(x) for x in audio),'Silent audio'
buf=C.create_string_buffer(initial)
assert not p.core.retro_unserialize(buf,31),'Accepted truncated state'
bad=bytearray(initial);bad[0]^=255;buf=C.create_string_buffer(bytes(bad))
assert not p.core.retro_unserialize(buf,len(bad)),'Accepted wrong state format'
p.core.retro_reset();p.buttons[1]=set();p.run(60)
p.screenshot(ROOT/'bizhawk/restarted-headless.png')
report={'video_replay_sha256':a[0],'audio_bit_exact':a[1]==b[1],'nonzero_audio':True,'state_bytes':len(initial),'invalid_states_rejected':True}
(ROOT/'bizhawk/adapter-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
p.core.retro_unload_game();p.core.retro_deinit()
