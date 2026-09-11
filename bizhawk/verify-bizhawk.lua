local root = "C:/TEMP2/aladdinGameCoop/bizhawk/"
client.speedmode(400)
client.setscreenshotosd(false)
client.unpause()
local function controls(p1,p2)
  local b={}
  for p=1,2 do
    for _,name in ipairs({"Up","Down","Left","Right","A","B","Y","L","Start"}) do
      b["P"..p.." RetroPad "..name]=false
    end
  end
  for _,name in ipairs(p1 or {}) do b["P1 RetroPad "..name]=true end
  for _,name in ipairs(p2 or {}) do b["P2 RetroPad "..name]=true end
  joypad.set(b)
end
for n=0,89 do
  controls({},n<30 and {"Right"} or {})
  emu.frameadvance()
end
client.screenshot(root.."bizhawk-two-players.png")
savestate.save(root.."bizhawk-coop-test.State",true)
local function replay()
  for n=0,179 do
    local a=n<35 and {"Right"} or (n>=70 and n<90 and {"A"} or {})
    local b=n>=20 and n<55 and {"Right"} or (n==120 and {"L"} or {})
    controls(a,b)
    emu.frameadvance()
  end
end
replay()
client.screenshot(root.."bizhawk-replay1.png")
savestate.load(root.."bizhawk-coop-test.State",true)
replay()
client.screenshot(root.."bizhawk-replay2.png")
-- The debug menu must remain interactive while the game world is frozen.
controls({"Start"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
client.screenshot(root.."bizhawk-debug-menu.png")
savestate.save(root.."bizhawk-debug-test.State",true)
controls({"Down"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
controls({"A"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
client.screenshot(root.."bizhawk-debug-toggle.png")
savestate.load(root.."bizhawk-debug-test.State",true)
controls({},{}) emu.frameadvance()
client.screenshot(root.."bizhawk-debug-restored.png")
controls({"Up"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
controls({"Up"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
controls({"A"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
client.screenshot(root.."bizhawk-noclip-menu.png")
controls({"Start"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
for n=1,100 do controls({"Right","Up"},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-noclip-flight.png")
controls({"Start"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
controls({"A"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
controls({"Start"},{}) emu.frameadvance()
controls({},{}) emu.frameadvance()
for n=1,3 do controls({},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-noclip-handoff.png")
client.reboot_core()
for n=1,60 do controls({},{}) emu.frameadvance() end
client.screenshot(root.."bizhawk-restarted.png")
local f=assert(io.open(root.."bizhawk-test-complete.txt","w"))
f:write("Completed independent controls, native BizHawk save/load replay, and Reboot Core.\n")
f:close()
client.exit()
