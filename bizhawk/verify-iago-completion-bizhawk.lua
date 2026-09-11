local root="C:/TEMP2/aladdinGameCoop/bizhawk/"
client.speedmode(400)
client.setscreenshotosd(false)
client.unpause()
local function controls(a,b)
 local pad={}
 for p=1,2 do for _,key in ipairs({"Start","Up","Down","Left","Right","A","B","Y","L"}) do pad["P"..p.." RetroPad "..key]=false end end
 for _,key in ipairs(a or {}) do pad["P1 RetroPad "..key]=true end
 for _,key in ipairs(b or {}) do pad["P2 RetroPad "..key]=true end
 joypad.set(pad)
end
local function tap(key) controls({key},{}) emu.frameadvance() controls({},{}) emu.frameadvance() end
savestate.load("C:/TEMP2/Bizhawk/Libretro/State/aladdin_coop_libretro/Aladdin_(U)_[!].QuickSave1.State",true)
client.unpause()
for n=1,120 do controls({},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-iago-bonus.png")
for n=1,1200 do
 if n%30==0 then controls({"A","B","Start"},{}) else controls({},{}) end
 emu.frameadvance()
end
controls({},{}) emu.frameadvance()
client.screenshot(root.."bizhawk-iago-next-stage.png")
savestate.save(root.."iago-completion-verification.State",true)
client.exit()
