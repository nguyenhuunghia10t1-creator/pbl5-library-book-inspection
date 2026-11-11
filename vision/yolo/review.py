"""Generate an offline visual review page; approvals are explicit human input."""
import argparse
import base64
import csv
import json
from pathlib import Path
import cv2
from . import CLASSES


def create_review(prepared):
    root = Path(prepared)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    with (root / "review.csv").open(encoding="utf-8-sig", newline="") as stream:
        reviews = {r["image_id"]: r for r in csv.DictReader(stream)}
    rows = []
    for row in manifest["records"]:
        image = cv2.imread(str(root / "images" / row["image_file"]))
        if image is None:
            raise ValueError("Unreadable prepared image")
        h, w = image.shape[:2]
        for line in row["labels"]:
            c, x, y, bw, bh = map(float, line.split())
            a, b = (int((x-bw/2)*w), int((y-bh/2)*h)), (int((x+bw/2)*w), int((y+bh/2)*h))
            color = (200, 160, 40) if c == 0 else (30, 50, 240)
            cv2.rectangle(image, a, b, color, 2)
            cv2.putText(image, CLASSES[int(c)], (a[0], max(12, a[1]-2)), cv2.FONT_HERSHEY_SIMPLEX, .4, color, 1)
        scale = min(1., 640 / max(h, w))
        thumb = cv2.resize(image, (round(w * scale), round(h * scale)))
        encoded = base64.b64encode(cv2.imencode(".jpg", thumb, [cv2.IMWRITE_JPEG_QUALITY, 75])[1]).decode()
        rows.append({"id": row["image_id"], "negative": row["negative_candidate"], "image": encoded,
                     "raw": "images/" + row["image_file"], "review": reviews[row["image_id"]]})
    html = '''<!doctype html><html lang="vi"><meta charset="utf-8"><title>Rà nhóm sách và nhãn</title>
<style>body{font:16px system-ui;background:#eef2f5;margin:20px;color:#172433}header{position:sticky;top:0;background:white;padding:12px;border:1px solid #ccd;z-index:1}h1{font-size:24px;margin:0}#cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:16px}article{background:white;padding:10px}article[hidden]{display:none}img{width:100%;cursor:zoom-in}img.zoom{position:fixed;inset:0;margin:auto;width:auto;max-width:98vw;max-height:98vh;z-index:2;cursor:zoom-out}input,select{font:inherit;max-width:95%;margin:5px}small{display:block;overflow-wrap:anywhere}button{font:inherit;padding:8px}strong{color:#9c2f00}</style>
<header><h1>Rà dataset 5 nhãn</h1><p>Gán cùng group_id cho cùng cuốn/thiết kế bìa ở mọi góc chụp. Chỉ duyệt khi đã xem nhãn; ảnh không có lỗi cần duyệt mẫu âm riêng. Các mục chưa rõ giữ pending.</p>
<p>Bấm ảnh để phóng to nhãn; mở ảnh gốc để kiểm vùng bị che. Tải CSV trước khi đóng trang; thay đổi không tự ghi xuống tệp.</p>
<button id="export">Tải review.csv</button> <label>Nạp review.csv đã lưu <input id="import" type="file" accept=".csv"></label><label>Hiện <select id="filter"><option value="all">Tất cả</option><option value="negative">Ứng viên mẫu âm</option><option value="pending">Chưa duyệt</option></select></label><span id="count"></span></header><main id="cards"></main>
<script>const rows=__DATA__;const cards=document.getElementById('cards');
for(const row of rows){let card=document.createElement('article');card.dataset.id=row.id;card.dataset.negative=String(row.negative);card.innerHTML=`<img src="data:image/jpeg;base64,${row.image}" loading="lazy"><small>${row.id}</small><a href="${encodeURI(row.raw)}" target="_blank">Xem ảnh gốc</a><br><label>Nhóm sách <input class="group" placeholder="VD: book_001"></label><br><label>Nhãn <select class="label"><option value="pending">Chờ kiểm</option><option value="approved">Đã duyệt</option><option value="rejected">Còn nghi vấn</option></select></label><br>${row.negative?'<strong>Cần xác nhận không có bốn lỗi</strong><select class="negative"><option value="pending">Chờ kiểm</option><option value="approved">Đã duyệt mẫu âm</option><option value="rejected">Còn nghi vấn</option></select>':'<span>Không phải mẫu âm</span>'}`;card.querySelector('.group').value=row.review.group_id;card.querySelector('.label').value=row.review.label_review;if(row.negative)card.querySelector('.negative').value=row.review.negative_review;card.querySelector('img').onclick=e=>e.target.classList.toggle('zoom');cards.appendChild(card)}
function filter(){let n=0;const v=document.getElementById('filter').value;for(const c of cards.children){c.hidden=(v==='negative'&&c.dataset.negative!=='true')||(v==='pending'&&c.querySelector('.label').value==='approved');if(!c.hidden)n++}document.getElementById('count').textContent=' '+n+'/'+rows.length+' ảnh'}
document.getElementById('filter').onchange=filter;filter();
const q=s=>'"'+String(s).replaceAll('"','""')+'"';
document.getElementById('export').onclick=()=>{let lines=['image_id,group_id,label_review,negative_review'];for(const c of cards.children)lines.push([c.dataset.id,c.querySelector('.group').value,c.querySelector('.label').value,c.querySelector('.negative')?.value||'not_needed'].map(q).join(','));let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.join('\\r\\n')+'\\r\\n'],{type:'text/csv;charset=utf-8'}));a.download='review.csv';a.click();URL.revokeObjectURL(a.href)};
function parseCSV(text){let result=[],row=[],field='',quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++}else quoted=!quoted}else if(c===','&&!quoted){row.push(field);field=''}else if((c==='\\r'||c==='\\n')&&!quoted){if(c==='\\r'&&text[i+1]==='\\n')i++;row.push(field);result.push(row);row=[];field=''}else field+=c}if(quoted)throw Error('CSV chưa đóng dấu ngoặc kép');if(field||row.length){row.push(field);result.push(row)}return result}
document.getElementById('import').onchange=async e=>{if(!e.target.files.length)return;try{const parsed=parseCSV((await e.target.files[0].text()).replace(/^\\uFEFF/,''));if(parsed.shift().join(',')!=='image_id,group_id,label_review,negative_review')throw Error('Sai cột CSV');const byid=new Map([...cards.children].map(c=>[c.dataset.id,c]));const seen=new Set();for(const v of parsed){if(v.length!==4||!byid.has(v[0])||seen.has(v[0])||!['pending','approved','rejected'].includes(v[2])||!['pending','approved','rejected','not_needed'].includes(v[3]))throw Error('CSV có dòng sai hoặc trùng');seen.add(v[0])}if(seen.size!==rows.length)throw Error('CSV thiếu ảnh');for(const v of parsed){const c=byid.get(v[0]);c.querySelector('.group').value=v[1];c.querySelector('.label').value=v[2];if(c.querySelector('.negative'))c.querySelector('.negative').value=v[3]}filter()}catch(err){alert(err.message)}};
</script></html>'''.replace('__DATA__', json.dumps(rows, ensure_ascii=True).replace('<', '\\u003c'))
    page = root / "review.html"
    page.write_text(html, encoding="utf-8")
    return page


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", required=True)
    print(create_review(parser.parse_args().prepared))
