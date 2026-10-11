set -e
cd "$(dirname "$0")"
python3 prod.py >/dev/null
python3 -c "
import re;s=open('prod.html').read();s=s.replace('__MARK__',open('mark.png.b64').read()).replace('__ICON__',open('icon.png.b64').read());open('../prod-built.html','w').write(s)
sc=re.findall(r'<script>(.*?)</script>',s,re.S);open('../p.js','w').write(sc[-1])"
node --check ../p.js
cp ../prod-built.html test/index.html
echo built
