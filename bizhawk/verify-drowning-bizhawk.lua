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
for n=1,90 do controls({},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-drowning-recovered.png")
savestate.save(root.."drowning-verification.State",true)
local f=assert(io.open(root.."bizhawk-drowning-complete.txt","w"))
f:write("Loaded drowned-player slot read-only and advanced 90 frames.\n") f:close()
client.exit()
