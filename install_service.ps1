C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy -preserveHostHeader:true /commit:apphost
.\nssm.exe install checkertool_#{Octopus.Environment.Name} "D:\Python\python.exe" "D:\Octopus\Applications\#{Octopus.Environment.Name}\Custom\CheckerTool\server.py"
.\nssm.exe set checkertool_#{Octopus.Environment.Name} AppDirectory D:\Octopus\Applications\#{Octopus.Environment.Name}\Custom\CheckerTool
.\nssm.exe start checkertool_#{Octopus.Environment.Name}