param([Parameter(Mandatory=$true)][string]$WorkDir)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System; using System.Runtime.InteropServices;
public class NavWin {
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int L,T,R,B;}
 [StructLayout(LayoutKind.Sequential)] public struct POINT {public int X,Y;}
 [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a,uint b,bool v);
 [DllImport("user32.dll")] public static extern IntPtr SetFocus(IntPtr h);
 [DllImport("user32.dll")] public static extern void keybd_event(byte k,byte s,uint f,UIntPtr e);
 [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr c);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr FindWindow(string c,string t);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h,out RECT r);
 [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h,ref POINT p);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h,IntPtr a,int x,int y,int w,int v,uint f);
 [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
 public delegate bool EnumProc(IntPtr h,IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p,IntPtr l);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h,System.Text.StringBuilder s,int n);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,System.Text.StringBuilder s,int n);
}
'@
[void][NavWin]::SetProcessDPIAware()
[void][NavWin]::SetThreadDpiAwarenessContext([IntPtr](-4))
$started=@(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -eq 0
$app=$null;$deck=$null;$show=$null;$tests=@()
try {
 $app=New-Object -ComObject PowerPoint.Application;$app.AutomationSecurity=3;$app.Visible=-1
 $deck=$app.Presentations.Open((Join-Path $WorkDir 'EL-cheatsheet-BM4-navigation.pptx'),-1,0,-1)
 $deck.SlideShowSettings.ShowType=1
 foreach($slide in $deck.Slides){$slide.SlideShowTransition.AdvanceOnClick=0;$slide.SlideShowTransition.AdvanceOnTime=0}
 $deck.SlideShowSettings.RangeType=1;$deck.SlideShowSettings.StartingSlide=1;$deck.SlideShowSettings.EndingSlide=$deck.Slides.Count
 try {$deck.SlideShowSettings.ShowPresenterView=0}catch{}
 $show=$deck.SlideShowSettings.Run();$view=$show.View
 Write-Output ('Show geometry: '+$show.Left+','+$show.Top+','+$show.Width+','+$show.Height)
 Write-Output ('Native show: count='+$app.SlideShowWindows.Count+'; run=' +($null -ne $show)+'; current='+$view.Slide.SlideIndex)
 Start-Sleep -Milliseconds 1300
 $hwnd=[IntPtr]::Zero;$ready=[DateTime]::UtcNow.AddSeconds(2)
 while($hwnd -eq [IntPtr]::Zero -and [DateTime]::UtcNow -lt $ready){
  $hwnd=[NavWin]::FindWindow('screenClass',$null)
  if($hwnd -eq [IntPtr]::Zero){Start-Sleep -Milliseconds 200}
 }
 if($hwnd -eq [IntPtr]::Zero){
  $script:found=@();$pptPids=@(Get-Process POWERPNT | Select-Object -ExpandProperty Id)
  $callback=[NavWin+EnumProc]{param($h,$l)
   $pidValue=[uint32]0;[void][NavWin]::GetWindowThreadProcessId($h,[ref]$pidValue)
   if($pptPids -contains $pidValue){
    $c=New-Object System.Text.StringBuilder 256;$t=New-Object System.Text.StringBuilder 256
    [void][NavWin]::GetClassName($h,$c,256);[void][NavWin]::GetWindowText($h,$t,256)
    Write-Output ('Own PowerPoint window: '+$c.ToString()+'; '+$t.ToString())
    if($c.ToString() -match 'screen' -or $t.ToString() -match 'Slide Show|Diasshow|SlideShow'){$script:found+=@{h=$h;c=$c.ToString()}}
   };return $true
  }
  [void][NavWin]::EnumWindows($callback,[IntPtr]::Zero)
  if($script:found.Count -gt 0){$hwnd=$script:found[0].h}else{throw 'No native slideshow window'}
 }
 [void][NavWin]::ShowWindow($hwnd,9)
 [void][NavWin]::SetWindowPos($hwnd,[IntPtr](-1),0,0,0,0,0x0003)
 [void][NavWin]::BringWindowToTop($hwnd);[void][NavWin]::SetForegroundWindow($hwnd)
 Start-Sleep -Milliseconds 700
 $cases=Get-Content -Raw -Encoding UTF8 (Join-Path $WorkDir 'navigation-cases.json') | ConvertFrom-Json
 foreach($case in $cases){
  $view.GotoSlide([int]$case.source_page);$show.Activate();Start-Sleep -Milliseconds 1100
  $shape=$deck.Slides.Item([int]$case.source_page).Shapes.Item([string]$case.shape)
  $rect=New-Object NavWin+RECT;[void][NavWin]::GetClientRect($hwnd,[ref]$rect)
  $width=$rect.R-$rect.L;$height=$rect.B-$rect.T
  $scale=[Math]::Min($width/$deck.PageSetup.SlideWidth,$height/$deck.PageSetup.SlideHeight)
  $offsetX=($width-$deck.PageSetup.SlideWidth*$scale)/2;$offsetY=($height-$deck.PageSetup.SlideHeight*$scale)/2
  $x=[int]($offsetX+($shape.Left+$shape.Width/2)*$scale);$y=[int]($offsetY+($shape.Top+$shape.Height/2)*$scale)
  $show.Activate()
  $fgPid=[uint32]0;$fgThread=[NavWin]::GetWindowThreadProcessId([NavWin]::GetForegroundWindow(),[ref]$fgPid)
  $ownThread=[NavWin]::GetCurrentThreadId()
  [void][NavWin]::AttachThreadInput($ownThread,$fgThread,$true)
  [void][NavWin]::SetForegroundWindow($hwnd);[void][NavWin]::SetFocus($hwnd)
  [void][NavWin]::AttachThreadInput($ownThread,$fgThread,$false)
  if([NavWin]::GetForegroundWindow() -ne $hwnd){
   [NavWin]::keybd_event(0x12,0,0,[UIntPtr]::Zero);[NavWin]::keybd_event(0x12,0,2,[UIntPtr]::Zero)
   [void][NavWin]::SetForegroundWindow($hwnd)
  }
  $origin=New-Object NavWin+POINT;[void][NavWin]::ClientToScreen($hwnd,[ref]$origin)
  [void][NavWin]::SetCursorPos($origin.X+$x,$origin.Y+$y)
  Start-Sleep -Milliseconds 100
  Write-Output ($case.name+'; handle='+$hwnd+'; foreground='+[NavWin]::GetForegroundWindow()+'; cursor='+($origin.X+$x)+','+($origin.Y+$y))
  if([NavWin]::GetForegroundWindow() -ne $hwnd){throw 'Native slideshow cannot acquire foreground for physical link click'}
  [NavWin]::mouse_event(0x0002,0,0,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [NavWin]::mouse_event(0x0004,0,0,0,[UIntPtr]::Zero)
  $limit=[DateTime]::UtcNow.AddSeconds(5)
  while($view.Slide.SlideIndex -ne [int]$case.target_page -and [DateTime]::UtcNow -lt $limit){Start-Sleep -Milliseconds 60}
  $actual=$view.Slide.SlideIndex
  $tests+=@{case=$case.name;source=$case.source_page;shape=$case.shape;expected=$case.target_page;actual=$actual;click_x=$x;click_y=$y;method='Actual physical mouse down/up in foreground native Windows PowerPoint; per-monitor DPI coordinates; blank-click advance disabled only in test'}
  if($case.capture -or $actual -ne [int]$case.target_page){
   Start-Sleep -Milliseconds 300
   $point=New-Object NavWin+POINT;[void][NavWin]::ClientToScreen($hwnd,[ref]$point)
   $bitmap=New-Object System.Drawing.Bitmap($width,$height);$graphics=[System.Drawing.Graphics]::FromImage($bitmap)
   $graphics.CopyFromScreen($point.X,$point.Y,0,0,$bitmap.Size);$bitmap.Save((Join-Path $WorkDir ($case.name+'.png')),[System.Drawing.Imaging.ImageFormat]::Png)
   $graphics.Dispose();$bitmap.Dispose()
  }
  if($actual -ne [int]$case.target_page){throw ('Wrong native click target: '+$case.name+'; actual '+$actual+' expected '+$case.target_page+'; click='+$x+','+$y+'; client='+$width+','+$height)}
 }
 @{powerpoint=$app.Version;tested_clicks=$tests.Count;cases=$tests} | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $WorkDir 'native-navigation-tests.json')
 Write-Output ('Passed '+$tests.Count+' actual slideshow clicks.')
} finally {
 if($null -ne $show){try{$show.View.Exit()}catch{}}
 if($null -ne $deck){$deck.Close()}
 if($started -and $null -ne $app -and $app.Presentations.Count -eq 0){$app.Quit()}
}
