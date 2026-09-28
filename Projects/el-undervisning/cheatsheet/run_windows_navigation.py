"""Exercise selected links with actual clicks in the Windows PowerPoint slideshow."""
from pathlib import Path
import hashlib,json,shutil,subprocess,time
from powerpoint_app.projects import load_plan
ROOT=Path(__file__).resolve().parent
plan=load_plan(ROOT/'slide-plan.json');positions={s.id:i+1 for i,s in enumerate(plan.slides)};cases=[]
def add(slide,link,name,capture=False):
 cases.append(dict(name=name,source_page=positions[slide.id],source_id=slide.id,shape='nav-'+link.id,target_page=positions[link.target_slide_id],target_id=link.target_slide_id,capture=capture))
home=next(s for s in plan.slides if s.layout=='lookup_start')
for link in home.navigation:add(home,link,link.id,capture=link.id=='group-current')
indexes=[s for s in plan.slides if any(n.placement=='row' for n in s.navigation)]
first=indexes[0];last=indexes[-1]
first_row=next(n for n in first.navigation if n.placement=='row');last_row=[n for n in last.navigation if n.placement=='row'][-1]
add(first,first_row,'first-index-first-row',True)
for n in first.navigation:
 if n.entry_id=='I01':add(first,n,'first-index-I01',True)
add(last,last_row,'last-index-last-row',True)
card=plan.slides[positions[first_row.target_slide_id]-1]
for n in card.navigation:add(card,n,'card-'+n.id)
add(first,next(n for n in first.navigation if n.id=='next-index'),'index-next')
add(last,next(n for n in last.navigation if n.id=='back-start'),'last-index-home')
ref=plan.slides[-1];add(ref,next(n for n in ref.navigation if n.id=='back-start'),'reference-home')
(ROOT/'review/navigation-cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
win_temp=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command','[IO.Path]::GetTempPath()'],text=True).strip()
wsl_temp=subprocess.check_output(['wslpath','-u',win_temp],text=True).strip();work=Path(wsl_temp)/('el-navigation-test-'+str(time.time_ns()));work.mkdir()
for name in ['EL-cheatsheet-BM4-navigation.pptx']:shutil.copyfile(ROOT/'exports'/name,work/name)
shutil.copyfile(ROOT/'test_navigation_windows.ps1',work/'test_navigation_windows.ps1');shutil.copyfile(ROOT/'review/navigation-cases.json',work/'navigation-cases.json')
win=win_temp.rstrip('\\')+'\\'+work.name
subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',win+'\\test_navigation_windows.ps1','-WorkDir',win],check=True)
report=json.loads((work/'native-navigation-tests.json').read_text(encoding='utf-8-sig'))
report['pptx_sha256']=hashlib.sha256((ROOT/'exports/EL-cheatsheet-BM4-navigation.pptx').read_bytes()).hexdigest()
report['plan_sha256']=hashlib.sha256((ROOT/'slide-plan.json').read_bytes()).hexdigest()
(ROOT/'review/native-navigation-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for f in work.glob('*.png'):shutil.copyfile(f,ROOT/'review'/('native-'+f.name))
print('Native click evidence:',ROOT/'review/native-navigation-tests.json')
