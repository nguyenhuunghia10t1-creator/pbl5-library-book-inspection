// Minh họa vị trí camera và sách khi chưa có ảnh đầu vào.
function drawStation(canvas) {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const project = ([x, y, z]) => [355 + 1.12 * x - 0.90 * y, 222 + 0.35 * x + 0.46 * y - z];
  function path(points, color, fill, width = 2, close = false) {
    ctx.beginPath();
    points.map(project).forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
    if (close) ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineJoin = "round";
    ctx.stroke();
  }
  function block(x, y, z, w, d, h, top, side, edge) {
    const A = [x,y,z+h], B = [x+w,y,z+h], C = [x+w,y+d,z+h], D = [x,y+d,z+h];
    path([D,C,[x+w,y+d,z],[x,y+d,z]],edge,side,1.8,true);
    path([B,C,[x+w,y+d,z],[x+w,y,z]],edge,side,1.8,true);
    path([A,B,C,D],edge,top,1.8,true);
  }
  const edge = "#658079";
  for (const x of [-120,110]) {
    for (const y of [-38,27]) block(x,y,-22,9,9,25,"#394946","#293936",edge);
  }
  block(-156,-48,0,312,96,13,"#293b38","#233530",edge);
  for (let x=-150; x<151; x+=13) path([[x,-45,14],[x,45,14]],"#476159",null,1);
  block(-166,-49,13,333,5,4,"#587368","#283b36",edge);
  block(-166,46,13,333,5,4,"#587368","#283b36",edge);
  // Bìa, gáy và ruột sách.
  block(-46,-33,15,89,66,3,"#8fa887","#5c776a","#a4be95");
  block(-44,-32,18,85,63,8,"#929b83","#6e796a","#9dae95");
  block(-46,-33,26,89,66,3,"#a3bd78","#788b58","#c9df92");
  path([[-36,-32,30],[-36,32,30]],"#617a55",null,1.4);
  for (const y of [-16,-9]) path([[-25,y,30],[13,y,30]],"#687c52",null,2);
  block(-35,-76,12,9,8,119,"#465a53","#30423d",edge);
  block(-35,-76,125,12,79,7,"#597065","#344a40",edge);
  ctx.setLineDash([4,5]);
  for (const [x,y] of [[-49,-37],[46,-37],[-49,36],[46,36]]) path([[-23,0,109],[x,y,32]],"#648354",null,1.1);
  ctx.setLineDash([]);
  block(-44,-11,117,42,27,21,"#516b57","#3b503f","#9db195");
  block(-32,-3,110,15,12,7,"#8fa587","#46583e","#cde89a");
  path([[-27,16,126],[-16,16,126]],"#d8fa91",null,3);
}
const sketch = document.getElementById("stationSketch");
if (sketch) drawStation(sketch);

const operationLink = document.querySelector(".rail-active");
operationLink.addEventListener("click", () => {
  document.body.classList.remove("historyTab");
  document.getElementById("tabs").textContent = "Lịch sử";
});
