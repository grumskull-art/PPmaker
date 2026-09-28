"""One math-markup parser for native slides, offline HTML and search text."""
import re
from copy import deepcopy


def math_blocks(source):
    if source.count('$') % 2:
        raise ValueError('Uafsluttet matematikmarkering: '+source)
    parts=source.split('$')
    return [('math' if i%2 else 'text',s.strip()) for i,s in enumerate(parts) if s.strip()]


def math_search_text(source):
    """Linear, searchable transcription; Latin I stays Latin I."""
    source=source.replace('{,}', ',')
    for _ in range(8):
        source=re.sub(r'\\(?:mathrm|mathit|mathbf)\{([^{}]*)\}',r'\1',source)
        source=re.sub(r'\\(?:dfrac|frac)\{([^{}]*)\}\{([^{}]*)\}',r'(\1)/(\2)',source)
        source=re.sub(r'\\sqrt\{([^{}]*)\}',r'√(\1)',source)
    symbols={'Delta':'Δ','Phi':'Φ','Psi':'Ψ','eta':'η','alpha':'α','gamma':'γ',
             'rho':'ρ','mu':'μ','varepsilon':'ε','theta':'θ','omega':'ω','pi':'π',
             'Omega':'Ω','cdot':'·','times':'×','sum':'Σ','ne':'≠','approx':'≈',
             'ge':'≥','le':'≤','infty':'∞','circ':'°','cos':'cos','sin':'sin'}
    source=re.sub(r'\\([A-Za-z]+)',lambda m:symbols.get(m[1],'' if m[1] in ('left','right','quad','qquad') else m[1]),source)
    return re.sub(r'\s+',' ',source.replace(r'\,',' ').replace(r'\;',' ').replace('{','').replace('}','')).strip()


def markup_search_text(source):
    return '\n'.join(math_search_text(s) if kind=='math' else s for kind,s in math_blocks(source))


def detail_sections(source):
    parts=re.split(r'(?m)^(TRIN|ENH\.|PAS PÅ|EKS\.)  ',source)
    if len(parts)==1:return [('',source)]
    return [(parts[i],parts[i+1].strip()) for i in range(1,len(parts),2)]


def serif_current_runs(frame):
    """Native/searchable current labels also use a barred Latin I."""
    for paragraph in frame.paragraphs:
        for run in list(paragraph.runs):
            parts=re.split(r'(?<![A-Za-z])(I)(?=[^A-Za-z]|$|[kx]\b|total\b|middel\b)',run.text)
            if len(parts)==1:continue
            for part in parts:
                if not part:continue
                clone=deepcopy(run._r);clone.t.text=part
                if part=='I':clone.get_or_add_rPr().get_or_add_latin().typeface='Cambria Math'
                run._r.addprevious(clone)
            run._r.getparent().remove(run._r)
