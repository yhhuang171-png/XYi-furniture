"""Synchronize Published public catalogue records; credentials are environment-only."""
import os,json,urllib.request,urllib.parse,html,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sync():
 token=os.environ['AIRTABLE_TOKEN'];base=os.environ['AIRTABLE_BASE_ID'];table=os.environ['AIRTABLE_TABLE_ID']
 records=[];offset=None
 while True:
  params={'filterByFormula':'{Status}="Published"','sort[0][field]':'Order','sort[0][direction]':'asc','pageSize':100}
  if offset:params['offset']=offset
  req=urllib.request.Request(f'https://api.airtable.com/v0/{base}/{table}?'+urllib.parse.urlencode(params),headers={'Authorization':'Bearer '+token})
  with urllib.request.urlopen(req,timeout=40) as resp:page=json.load(resp)
  records.extend(page.get('records',[]));offset=page.get('offset')
  if not offset:break
 assets=ROOT/'assets/catalogue';assets.mkdir(exist_ok=True)
 cards=[];items=[]
 def esc(v):return html.escape(str(v or ''),quote=True)
 for record in records:
  f=record.get('fields',{});attachments=f.get('Attachments') or []
  if not attachments:continue
  att=attachments[0];url=att['url'];host=urllib.parse.urlparse(url).hostname or ''
  if urllib.parse.urlparse(url).scheme!='https' or not(host.endswith('.airtableusercontent.com') or host.endswith('.airtable.com')):raise ValueError('Unexpected attachment host')
  with urllib.request.urlopen(url,timeout=60) as resp:
   kind=resp.headers.get_content_type();data=resp.read(25000001)
  ext={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp','image/gif':'.gif'}.get(kind)
  if not ext or len(data)>25000000:raise ValueError('Unsupported attachment')
  filename=hashlib.sha256(data).hexdigest()[:24]+ext
  image='/assets/catalogue/'+filename
  name=f.get('Name') or 'Product';desc=f.get('Description') or '';sku=f.get('SKU') or '';spec=f.get('Specs') or f.get('Specifications') or ''
  tags=[x.strip() for x in str(f.get('Tags') or '').split(',') if x.strip()]
  extra=(f'<div class="product-sku">SKU {esc(sku)}</div>' if sku else '')+(f'<div class="product-specs">{esc(spec)}</div>' if spec else '')
  anchor='catalogue-'+re.sub('[^a-zA-Z0-9_-]','',record['id'])
  cards.append(f'<article class="product-card" id="{anchor}"><div class="product-image"><img src="{image}" alt="{esc(name)}" loading="lazy"></div><div class="product-body"><div class="product-index">{len(cards)+1:02d} / Production</div><div class="line-badge">OEM-ready</div><h3>{esc(name)}</h3>{extra}<p>{esc(desc)}</p><div class="product-tags">'+''.join(f'<span>{esc(t)}</span>' for t in tags)+'</div><a class="product-link" href="#contact">Send Inquiry</a></div></article>')
  items.append((filename,data))
 if not cards:raise ValueError('No published products with images; keeping existing catalogue')
 p=ROOT/'index.html';source=p.read_text();opening='<div class="product-grid" id="production-grid">';start=source.index(opening)+len(opening)
 depth=1;end=None
 for match in re.finditer(r'</?div\b[^>]*>',source[start:]):
  depth+= -1 if match.group().startswith('</') else 1
  if depth==0:end=start+match.start();break
 if end is None:raise ValueError('Product grid boundary missing')
 for name,data in items:(assets/name).write_bytes(data)
 p.write_text(source[:start]+'\n<!-- Public catalogue synchronized from Airtable; no client-side credentials. -->\n'+'\n'.join(cards)+'\n'+source[end:])
 print(f'Synchronized {len(cards)} published products and their images.')
if __name__=='__main__':
 try:sync()
 except Exception as e:
  # Do not print response bodies, credential values or signed attachment URLs.
  print('Catalogue sync failed:',type(e).__name__)
  raise SystemExit(1)
