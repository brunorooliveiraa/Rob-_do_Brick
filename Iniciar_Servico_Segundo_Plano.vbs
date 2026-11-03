Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonwPath = currentDir & "\.venv\Scripts\pythonw.exe"
scriptPath = currentDir & "\servico_garimpo.py"

If fso.FileExists(pythonwPath) Then
    WshShell.CurrentDirectory = currentDir
    WshShell.Run Chr(34) & pythonwPath & Chr(34) & " " & Chr(34) & scriptPath & Chr(34), 0, False
Else
    WshShell.CurrentDirectory = currentDir
    WshShell.Run "pythonw " & Chr(34) & scriptPath & Chr(34), 0, False
End If

Set WshShell = Nothing
Set fso = Nothing
