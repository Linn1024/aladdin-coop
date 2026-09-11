local root="C:/TEMP2/aladdinGameCoop/bizhawk/"
client.speedmode(400)
client.setscreenshotosd(false)
client.unpause()
local function frame(keys)
 local pad={}
 for p=1,2 do for _,key in ipairs({"Start","Up","Down","Left","Right","A","B","Y","L"}) do pad["P"..p.." RetroPad "..key]=false end end
 for _,key in ipairs(keys or {}) do pad["P1 RetroPad "..key]=true end
 joypad.set(pad);emu.frameadvance()
end
savestate.load(root.."rope-verification.State",true)
client.unpause()
for i=1,15 do frame() end
frame({"Start"});frame();client.screenshot(root.."normal-pause-native.png")
frame({"A","B","Y"});frame();client.screenshot(root.."hidden-debug-native.png")
savestate.save(root.."pause-options-verification.State",true)
local f=io.open(root.."pause-options-native-complete.txt","w");f:write("Old native save loaded; normal pause and A+B+C debug captured.");f:close()
client.exit()
