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
for n=1,20 do controls({},{"Right"}) emu.frameadvance() end
client.screenshot(root.."bizhawk-campaign-desert.png")
-- Slot 1 fixture stores menu row 8 and a pre-selector (zero) stage field.
tap("Start") tap("Down")
for n=1,8 do tap("Right") end
tap("A")
client.screenshot(root.."bizhawk-campaign-stage-menu.png")
tap("Start")
for n=1,850 do controls({},{}) emu.frameadvance() end
for n=1,12 do controls({},{"Up"}) emu.frameadvance() end
client.screenshot(root.."bizhawk-campaign-carpets.png")
local f=assert(io.open(root.."bizhawk-campaign-test-complete.txt","w"))
f:write("Loaded user slot 1 read-only, continued to Desert, selected Rug Ride, and steered P2 up.\n") f:close()
client.exit()
