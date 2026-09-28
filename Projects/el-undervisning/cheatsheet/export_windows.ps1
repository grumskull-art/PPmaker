param([Parameter(Mandatory=$true)][string]$WorkDir)
$ErrorActionPreference='Stop'
$started=@(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -eq 0
$app=New-Object -ComObject PowerPoint.Application
$app.AutomationSecurity=3;$app.Visible=-1;$deck=$null
$preview=Join-Path $WorkDir 'preview';[void](New-Item $preview -ItemType Directory -Force)
$bounds=@()
function Text-Bounds($shape,[int]$Page) {
 if($shape.Type -eq 6){for($j=1;$j -le $shape.GroupItems.Count;$j++){Text-Bounds $shape.GroupItems.Item($j) $Page}}
 elseif($shape.HasTable -eq -1){
  for($row=1;$row -le $shape.Table.Rows.Count;$row++){
   for($col=1;$col -le $shape.Table.Columns.Count;$col++){
    $cell=$shape.Table.Cell($row,$col).Shape
    $script:bounds+=@{page=$Page;name=($shape.Name+'-r'+$row+'c'+$col);width=$cell.Width;height=$cell.Height;text_width=$cell.TextFrame2.TextRange.BoundWidth;text_height=$cell.TextFrame2.TextRange.BoundHeight;margin_x=($cell.TextFrame.MarginLeft+$cell.TextFrame.MarginRight);margin_y=($cell.TextFrame.MarginTop+$cell.TextFrame.MarginBottom)}
   }
  }
 }
 elseif($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1){
  $script:bounds+=@{page=$Page;name=$shape.Name;width=$shape.Width;height=$shape.Height;text_width=$shape.TextFrame2.TextRange.BoundWidth;text_height=$shape.TextFrame2.TextRange.BoundHeight;margin_x=($shape.TextFrame.MarginLeft+$shape.TextFrame.MarginRight);margin_y=($shape.TextFrame.MarginTop+$shape.TextFrame.MarginBottom)}
 }
}
try {
 $deck=$app.Presentations.Open((Join-Path $WorkDir 'EL-cheatsheet-BM4-navigation.pptx'),-1,0,0)
 if([Math]::Abs($deck.PageSetup.SlideWidth-841.89) -gt 1 -or [Math]::Abs($deck.PageSetup.SlideHeight-595.28) -gt 1){throw 'Incorrect A4 page size'}
 for($i=1;$i -le $deck.Slides.Count;$i++){
  $slide=$deck.Slides.Item($i)
  $slide.Export((Join-Path $preview ('page-'+$i.ToString('00')+'.png')),'PNG',1782,1260)
  for($j=1;$j -le $slide.Shapes.Count;$j++){Text-Bounds $slide.Shapes.Item($j) $i}
 }
 $deck.SaveAs((Join-Path $WorkDir 'EL-cheatsheet-BM4-navigation.pdf'),32)
 @{powerpoint_version=$app.Version;pages=$deck.Slides.Count;width_pt=$deck.PageSetup.SlideWidth;height_pt=$deck.PageSetup.SlideHeight;text_bounds=$bounds;method='Native Microsoft PowerPoint Windows COM; read-only open, PNG render every page and PDF export'} | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $WorkDir 'windows-layout.json')
 Write-Output ('Exported and measured '+$deck.Slides.Count+' A4 pages in Windows PowerPoint.')
 $deck.Close();$deck=$null
} finally {if($null -ne $deck){$deck.Close()};if($started -and $app.Presentations.Count -eq 0){$app.Quit()}}
