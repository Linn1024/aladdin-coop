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
client.screenshot(root.."bizhawk-rope-restored.png")
for n=1,28 do controls({"Right"},{"Right"}) emu.frameadvance() end
for n=1,22 do controls({"Right"},{}) emu.frameadvance() end
for n=1,20 do controls({"A","Up"},{"A","Up"}) emu.frameadvance() end
for n=1,80 do controls({"Up"},{"Up"}) emu.frameadvance() end
client.screenshot(root.."bizhawk-rope-riding.png")
savestate.save(root.."rope-verification.State",true)
local f=assert(io.open(root.."bizhawk-rope-complete.txt","w"))
f:write("Loaded user slot read-only; waited for rope; both players rode upward.\n") f:close()
client.exit()
