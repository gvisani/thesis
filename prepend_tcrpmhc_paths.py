import re, glob

for path in glob.glob('/Users/gianmarcovisani/Desktop/thesis/*tcrpmhc.tex'):
    content = open(path).read()
    new = re.sub(r'(\\includegraphics(?:\[.*?\])?)\{', r'\1{tcrpmhc/figures/', content)
    count = content.count('\\includegraphics')
    open(path, 'w').write(new)
    print(f'{path.split("/")[-1]}: {count} paths updated')
