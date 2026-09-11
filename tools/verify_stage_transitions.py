"""Inject native exit requests to verify routing; these are not boss victories."""
exec(compile(open(__file__.replace('verify_stage_transitions.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
next_stage={0:4,2:3,3:0,4:5,5:7,6:7,7:8,8:9,9:10,10:12,12:11}
out=[]
for level,target in next_stage.items():
    stage(level)
    p.write(0xf0e9,b'\xff')
    for n in range(2400):
        p.run(1,{3} if n%90==0 else set())
        if c.al_coop_ready() and c.al_coop_level()==target:break
    else:raise AssertionError((level,target,status(),c.al_coop_level()))
    out.append([level,target]);print('PASS: native stage routing',level,'->',target,flush=True)
stage(11);p.write(0xf0e9,b'\xff')
for n in range(1500):p.run(1,{3} if n%90==0 else set())
assert not c.al_coop_ready(),'Final stage should yield to the native ending'
p.screenshot(ROOT/'diagnostics/campaign-ending.png')
(ROOT/'diagnostics/stage-transition-verification.json').write_text(json.dumps({
 'native_routes':out,'final_stage_yields_to_native_ending':True,
 'method':'Injected exit flags at stage starts, not complete playthroughs.'
},indent=2)+'\n')
