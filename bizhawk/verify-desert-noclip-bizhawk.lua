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
for n=1,60 do controls({"Right"},{"Right"}) emu.frameadvance() end
for n=1,1200 do controls({},{}) emu.frameadvance() end
-- The restored original story interlude waits for the game's Start button.
tap("Start")
for n=1,800 do controls({},{}) emu.frameadvance() end
tap("Start") tap("A") tap("Start")
for n=1,1000 do controls({"Right"},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-desert-noclip-crossing.png")
savestate.save(root.."desert-noclip-regression.State",true)
client.unpause()
for n=1,200 do controls({"Right"},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-desert-noclip-after.png")
savestate.load(root.."desert-noclip-regression.State",true)
client.unpause()
for n=1,200 do controls({"Right"},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-desert-noclip-replay.png")
tap("Start") tap("A") tap("Start")
for n=1,600 do controls({},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-desert-noclip-handoff.png")
local f=assert(io.open(root.."bizhawk-desert-noclip-complete.txt","w"))
f:write("Completed Desert noclip crossing, save/load, and handoff.\n") f:close()
client.exit()
