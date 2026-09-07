"""Build the local/static gallery from request manifests. Standard library only."""
import hashlib
import html
import json
import struct
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ESC = html.escape

def verify_file(base, filename, expected, allowed=None):
    path = (base/filename).resolve()
    assert path.is_relative_to((allowed or base).resolve()), filename
    assert path.is_file(), path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    return path

def card(base, poster):
    output = verify_file(base, poster['output'], poster['output_sha256'], ROOT/'output')
    assert output.parent == ROOT/'output', output
    prompt = verify_file(base, poster['prompt'], poster['prompt_sha256'])
    for source in poster['inputs']:
        verify_file(base,source['path'],source['sha256'])
    header = output.read_bytes()[:24]
    assert header[:8] == b'\x89PNG\r\n\x1a\n'
    width, height = struct.unpack('>II', header[16:24])
    image = output.relative_to(ROOT).as_posix()
    prompt = prompt.relative_to(ROOT).as_posix()
    request = (base/'README.md').relative_to(ROOT).as_posix()
    metadata = (base/'metadata/request.json').relative_to(ROOT).as_posix()
    return f'''<article><a class="poster" href="{ESC(image)}"><img src="{ESC(image)}" width="{width}" height="{height}" loading="lazy" alt="{ESC(poster['title'])}"></a><div class="caption"><h3>{ESC(poster['title'])}</h3><nav aria-label="Материалы: {ESC(poster['title'])}"><a href="{ESC(image)}" download>Скачать PNG</a><a href="{ESC(prompt)}">Промпт</a><a href="{ESC(request)}">Весь запрос</a><a href="{ESC(metadata)}">Метаданные</a></nav></div></article>'''

def main():
    groups = {'bogorodskoe-preobrazhenskaya': [], 'domodedovskaya-orekhovo-borisovo': []}
    previous, initial = [], []
    requests = sorted((ROOT/'posters').glob('*/*/metadata/request.json'))
    count = 0
    for file in requests:
        base = file.parent.parent
        assert all((base/folder).is_dir() for folder in ['input','prompt','metadata'])
        manifest = json.loads(file.read_text())
        assert manifest['schema_version']==1
        assert manifest['path_base']=='request-directory'
        for poster in manifest['posters']:
            rendered = card(base,poster)
            if base.parent.name=='russian-architecture': initial.append((poster['id'],rendered))
            elif poster['latest']: groups[base.parent.name].append((poster['id'],rendered))
            else: previous.append((poster['id'],rendered))
            count += 1
    current_count = sum(len(v) for v in groups.values())
    sections=[]
    titles = {'bogorodskoe-preobrazhenskaya':'Богородское и Преображенская площадь',
              'domodedovskaya-orekhovo-borisovo':'Домодедовская, Орехово-Борисово и окрестности'}
    for slug, entries in groups.items():
        sections.append(f'<section id="{slug}"><h2>{titles[slug]}</h2><div class="grid">'+''.join(c for _,c in sorted(entries))+'</div></section>')
    for slug,title,entries in [('previous','Прежние версии',previous),('initial','Первый эксперимент: Нерль, Кижи и Наркомфин',initial)]:
        if not entries:
            continue
        sections.append(f'<details class="history" id="{slug}"><summary>{title} · {len(entries)}</summary><div class="grid">'+''.join(c for _,c in sorted(entries))+'</div></details>')
    page = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Окрестности — все плакаты</title><style>
:root{color-scheme:dark;background:#181a19;color:#eeeae1;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}*{box-sizing:border-box}body{margin:0}header,main,footer{max-width:1600px;margin:auto;padding:32px}header{padding-top:56px}h1{font-size:clamp(30px,4vw,56px);font-weight:550;letter-spacing:-.035em;margin:0 0 14px}p{line-height:1.6;color:#b8bbb4}header p{max-width:900px}.eyebrow{letter-spacing:.13em;font-size:12px;text-transform:uppercase;color:#cabea3;margin-bottom:14px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:32px 28px}.poster{display:block;background:#252826;line-height:0}.poster img{display:block;width:100%;height:auto}article{min-width:0}.caption{padding:18px 2px 24px}h2{font-size:28px;font-weight:550;margin:0 0 28px}h3{font-size:21px;font-weight:540;line-height:1.3;margin:0 0 8px}section{margin-bottom:48px;scroll-margin-top:24px}nav{display:flex;gap:14px 22px;flex-wrap:wrap;margin:14px 0}a{color:#e1c99a;text-underline-offset:4px}a:hover{color:#fff}a:focus-visible,summary:focus-visible{outline:2px solid #e1c99a;outline-offset:5px}.history{border-top:1px solid #353b35;padding:24px 0}.history summary{font-size:22px;cursor:pointer;margin-bottom:24px}footer{border-top:1px solid #353b35;color:#969d94;font-size:14px;line-height:1.6}@media(max-width:900px){.grid{grid-template-columns:1fr}header,main,footer{padding-left:18px;padding-right:18px}header{padding-top:34px}}
</style></head><body><header><div class="eyebrow">Окрестности · Московская серия</div><h1>Места и истории района</h1>'''
    page += f'<p>{current_count} финальных плакатов — по одной версии каждого сюжета. Все изображения собраны в общей папке output; промпты и метаданные — по запросам.</p>'
    page += '<nav aria-label="Разделы"><a href="#bogorodskoe-preobrazhenskaya">Богородское и Преображенская площадь</a><a href="#domodedovskaya-orekhovo-borisovo">Домодедовская и окрестности</a></nav></header><main>'
    page += ''.join(sections)+'</main><footer><a href="README.md">О проекте и структуре</a> · <a href="ARTWORK-LICENSE.md">Сведения о материалах</a></footer></body></html>'
    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key,value in attrs:
                if key in ('href','src') and value and not urlsplit(value).scheme and not value.startswith('#'):
                    assert (ROOT/unquote(urlsplit(value).path)).is_file(), value
    Links().feed(page)
    (ROOT/'index.html').write_text(page)
    print(f'Gallery verified: {len(requests)} requests, {current_count} current posters, {count} outputs; all hashes and local links pass.')

if __name__=='__main__':
    main()
