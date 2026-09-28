"""Readable formula blocks with native prose and searchable transcriptions."""
from functools import lru_cache
from pathlib import Path
import re
from PIL import Image,ImageFont
import matplotlib
from powerpoint_app.domain.models import FormulaElement
from powerpoint_app.visuals.assets import formula_png
from powerpoint_app.rendering.math_markup import math_blocks,detail_sections,math_search_text


@lru_cache
def prose_font(size):
    path=Path('/mnt/c/Windows/Fonts/calibri.ttf')
    if not path.exists():path=Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'
    return ImageFont.truetype(str(path),round(size*4))


def wrapped_text(value,width,size=12):
    font=prose_font(size);limit=width*72*4*.97;lines=[]
    for paragraph in value.splitlines():
        line=''
        for word in paragraph.split():
            candidate=(line+' '+word).strip()
            if line and font.getlength(candidate)>limit:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    return '\n'.join(lines),max(1,len(lines))*size*1.32/72


def math_picture(r,slide,latex,x,y,w,size=18,name='math'):
    from powerpoint_app.rendering.reference import text
    asset=formula_png(FormulaElement(id=name,type='formula',latex=latex),r.root/'cache',r.theme)
    with Image.open(asset) as im:iw,ih=im.size
    scale=min(size/25,w*220/iw)
    if scale*25<16:raise ValueError(f'Ligningen {name} kræver mere bredde ved 16 pt: {latex}')
    width=iw/220*scale;height=max(ih/220*scale,.17)
    # White native text supplies Ctrl+F/PDF search without showing linear notation.
    text(r,slide,math_search_text(latex),x,y,w,height,7.5,'FFFFFF',name='math-source-'+name)
    shape=r._picture(slide,asset,x,y,width,height);shape.name=name;r._set_alt_text(shape,latex)
    return height


def rich_details(r,slide,element,x,y,w,h):
    from powerpoint_app.rendering.reference import text,CALCULATE
    start=y;count=0
    for label,content in detail_sections(element.text):
        text(r,slide,label,x,y,.59,.21,9,CALCULATE,True)
        for kind,value in math_blocks(content):
            name=element.id+'-'+str(count);count+=1
            if kind=='math':height=math_picture(r,slide,value,x+.65,y,w-.65,18,name)
            else:
                value,height=wrapped_text(value,w-.65)
                text(r,slide,value,x+.65,y,w-.65,height,12,name=name)
            y+=height+.045
        y+=.085
    if y-start>h+.01:
        raise ValueError(f'Matematikken i {element.id} kræver {y-start:.2f} tommer; kun {h:.2f} til rådighed')
    return y-start
