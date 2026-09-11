local root="C:/TEMP2/aladdinGameCoop/bizhawk/"
client.speedmode(400)
client.setscreenshotosd(false)
client.unpause()
savestate.load("C:/TEMP2/Bizhawk/Libretro/State/aladdin_coop_libretro/Aladdin_(U)_[!].QuickSave1.State",true)
for n=1,60 do
  joypad.set({["P1 RetroPad Right"]=true,["P2 RetroPad Right"]=true})
  emu.frameadvance()
end
client.screenshot(root.."bizhawk-user-exit-complete.png")
local f=assert(io.open(root.."bizhawk-exit-test-complete.txt","w"))
f:write("Loaded user slot 1 read-only and walked both players right for 60 frames.\n")
f:close()
client.exit()
