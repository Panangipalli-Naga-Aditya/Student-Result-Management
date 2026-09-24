const $=s=>document.querySelector(s),app=$('#app');let user=null;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const csrf=()=>document.querySelector('meta[name=csrf-token]').content;
const size=b=>b>1048576?(b/1048576).toFixed(1)+' MB':Math.max(1,Math.round(b/1024))+' KB';
const fdate=d=>new Date(d).toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'});
function toast(m,t='ok'){const e=document.createElement('div');e.className='toast '+t;e.textContent=m;$('#toasts').append(e);setTimeout(()=>e.remove(),4000)}
async function api(url,opt={}){opt.headers={'X-CSRFToken':csrf(),...(opt.headers||{})};if(opt.json){opt.body=JSON.stringify(opt.json);opt.headers['Content-Type']='application/json';opt.method=opt.method||'POST'}
 const r=await fetch(url,opt),d=await r.json().catch(()=>({}));if(!r.ok)throw Object.assign(new Error(d.error||'Something went wrong.'),{status:r.status});return d}
const guard=async fn=>{try{await fn()}catch(e){toast(e.message,'err');if(e.status===401)location.hash='#/login'}};
function renderNav(){const l=(h,t)=>`<a href="#/${h}" class="${location.hash==='#/'+h?'on':''}">${t}</a>`;
 $('#nav').innerHTML=l('','Home')+l('results','Results')+l('upload','Upload Result')+l('mine','My Uploads')+l('about','About')+(user?(user.role==='admin'?l('admin','Faculty'):'')+`<span>👤 ${esc(user.name)}</span><button id="lo">Logout</button>`:l('login','Login')+l('register','Register'));
 const lo=$('#lo');if(lo)lo.onclick=()=>guard(async()=>{await api('/api/auth/logout',{method:'POST'});user=null;location.hash='#/';route()})}
const card=(r,own)=>`<div class="card"><b>${esc(r.student_name)}</b> <span class="muted">· ${esc(r.roll_number)}</span><h3>${esc(r.title)}</h3><div>${esc(r.subject)}</div>
<span class="pill">${r.file_type.toUpperCase()} • ${size(r.file_size)}</span><div class="muted">Uploaded: ${fdate(r.upload_date)}</div>
<div class="acts"><button class="btn sm" data-v="${r.id}">View</button><a class="btn sm ghost" href="/api/results/${r.id}/download">Download</a>${own||(user&&user.role==='admin')?`<button class="btn sm danger" data-d="${r.id}">Delete</button>`:''}</div></div>`;
const empty=`<div class="card empty"><h3>No results uploaded yet.</h3><p class="muted">Be the first student to share a result with the class.</p><a class="btn" href="#/upload">Upload Result</a></div>`;
function wire(reload){app.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>viewer(b.dataset.v));
 app.querySelectorAll('[data-d]').forEach(b=>b.onclick=()=>{if(confirm('Delete this result permanently?'))guard(async()=>{await api('/api/results/'+b.dataset.d,{method:'DELETE'});toast('Result deleted.');reload()})})}
async function viewer(id){await guard(async()=>{const{result:r}=await api('/api/results/'+id),u=`/api/results/${id}/view`;let h=`<h3>${esc(r.title)}</h3>`;
 if(r.file_type==='pdf')h+=`<iframe src="${u}"></iframe>`;else if(['jpg','jpeg','png','webp'].includes(r.file_type))h+=`<img src="${u}" alt="">`;
 else if(r.file_type==='txt'){h+=`<pre>${esc(await(await fetch(u)).text())}</pre>`}
 else h+=`<p>Preview unavailable for this file type.</p><a class="btn" href="/api/results/${id}/download">Download File</a>`;
 $('#mbody').innerHTML=h;$('#modal').hidden=false})}
$('#mclose').onclick=()=>{$('#modal').hidden=true;$('#mbody').innerHTML=''};$('#burger').onclick=()=>$('#nav').classList.toggle('open');
const views={
'':()=>{app.innerHTML=`<section class="hero"><div class="tag">⚛</div><h1>Physics Results Hub</h1><div class="tag">One Platform. Every Result. Shared with the Class.</div>
<p>A centralized academic platform designed to help students securely upload, organize, access and share physics-related results and documents.</p>
<a class="btn" href="#/upload">Upload Your Result</a><a class="btn ghost" href="#/results">Explore Results</a><div class="eq">∇·E = ρ/ε₀ &nbsp; ∇×B = μ₀J + μ₀ε₀ ∂E/∂t &nbsp; E = hν</div></section>`},
about:()=>{app.innerHTML=`<div class="card"><h2>About</h2><p>Physics Results Hub lets students of the class share results, lab reports, assignments and examination documents. Files are stored on the server, access is limited to authenticated users, and faculty can moderate uploads.</p></div>`},
login:()=>{app.innerHTML=`<form class="card form" id="f"><h2>Login</h2><label>Email / Roll Number</label><input name="identifier" required><label>Password</label><input type="password" name="password" required><p><button class="btn">Login</button></p></form>`;
 $('#f').onsubmit=e=>{e.preventDefault();guard(async()=>{user=(await api('/api/auth/login',{json:Object.fromEntries(new FormData(e.target))})).user;location.hash='#/results'})}},
register:()=>{app.innerHTML=`<form class="card form" id="f"><h2>Register</h2><label>Full Name</label><input name="name" required><label>Roll Number</label><input name="roll_number" required><label>Email</label><input type="email" name="email" required><label>Password</label><input type="password" name="password" minlength="8" required><label>Confirm Password</label><input type="password" name="confirm_password" required><p><button class="btn">Create account</button></p></form>`;
 $('#f').onsubmit=e=>{e.preventDefault();guard(async()=>{user=(await api('/api/auth/register',{json:Object.fromEntries(new FormData(e.target))})).user;toast('Welcome, '+user.name+'!');location.hash='#/results'})}},
results:async()=>{if(!user){toast('Please log in to upload a result.','err');return location.hash='#/login'}
 app.innerHTML=`<h2>Student Results</h2><div class="bar"><input id="q" placeholder="Search students, results, subjects or roll numbers…"><select id="subject"><option value="">All subjects</option><option>Engineering Physics</option><option>Physics Lab</option><option>Other</option></select>
<select id="type"><option value="">All types</option><option value="pdf">PDF</option><option value="word">Word</option><option value="excel">Excel</option><option value="powerpoint">PowerPoint</option><option value="text">Text</option><option value="image">Image</option></select>
<select id="date"><option value="">All dates</option><option value="today">Today</option><option value="week">This week</option><option value="month">This month</option></select>
<select id="sort"><option value="newest">Newest First</option><option value="oldest">Oldest First</option><option value="name">Student Name A–Z</option></select></div><div id="list" class="grid"></div>`;
 const load=()=>guard(async()=>{const p=new URLSearchParams();['q','subject','type','date','sort'].forEach(k=>{if($('#'+k).value)p.set(k,$('#'+k).value)});
  const{results}=await api('/api/results?'+p);$('#list').outerHTML=`<div id="list" class="grid">${results.map(r=>card(r,user.id===r.student_id)).join('')||''}</div>`;if(!results.length)$('#list').outerHTML=empty;wire(load)});
 let t;$('#q').oninput=()=>{clearTimeout(t);t=setTimeout(load,300)};['subject','type','date','sort'].forEach(k=>$('#'+k).onchange=load);load()},
mine:async()=>{if(!user){toast('Please log in to upload a result.','err');return location.hash='#/login'}
 app.innerHTML='<h2>My Uploads</h2><div id="list" class="grid"></div>';const load=()=>guard(async()=>{const{results}=await api('/api/user/uploads');$('#list').outerHTML=results.length?`<div id="list" class="grid">${results.map(r=>card(r,true)).join('')}</div>`:empty;wire(load)});load()},
upload:()=>{if(!user){toast('Please log in to upload a result.','err');return location.hash='#/login'}
 app.innerHTML=`<form class="card form" id="f"><h2>Upload Your Result</h2><label>Student Name</label><input value="${esc(user.name)}" disabled><label>Roll Number</label><input value="${esc(user.roll_number)}" disabled>
<label>Result Title</label><input name="title" placeholder="Physics Mid-Term Examination" required><label>Subject</label><select name="subject"><option>Engineering Physics</option><option>Physics Lab</option><option>Other</option></select>
<label>Description</label><textarea name="description" rows="3"></textarea><label>File</label>
<div class="drop" id="drop">Drag &amp; drop your file here or browse from your device.<input type="file" id="file" hidden accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.webp"></div>
<div id="fi" hidden><p id="fn"></p><div class="prog"><i id="pb"></i></div><button type="button" class="btn sm ghost" id="rep">Replace file</button> <button type="button" class="btn sm danger" id="rem">Remove file</button></div>
<p><button class="btn" id="pub">Publish Result</button></p></form>`;
 let file=null;const inp=$('#file'),set=f=>{file=f;$('#fi').hidden=!f;$('#drop').hidden=!!f;if(f)$('#fn').textContent=`${f.name} · ${f.name.split('.').pop().toUpperCase()} · ${size(f.size)}`;$('#pb').style.width='0'};
 $('#drop').onclick=()=>inp.click();$('#rep').onclick=()=>inp.click();$('#rem').onclick=()=>{inp.value='';set(null)};inp.onchange=()=>inp.files[0]&&set(inp.files[0]);
 const dr=$('#drop');['dragover','dragenter'].forEach(x=>dr.addEventListener(x,e=>{e.preventDefault();dr.classList.add('over')}));dr.addEventListener('dragleave',()=>dr.classList.remove('over'));dr.addEventListener('drop',e=>{e.preventDefault();dr.classList.remove('over');set(e.dataTransfer.files[0])});
 $('#f').onsubmit=e=>{e.preventDefault();if(!file)return toast('Please choose a file.','err');const fd=new FormData(e.target);fd.append('file',file);const x=new XMLHttpRequest();x.open('POST','/api/results');x.setRequestHeader('X-CSRFToken',csrf());
  x.upload.onprogress=p=>{$('#pb').style.width=(p.loaded/p.total*100)+'%'};x.onload=()=>{let d={};try{d=JSON.parse(x.responseText)}catch{}if(x.status===201){toast(d.message);location.hash='#/results'}else toast(d.error||'Upload failed.','err')};x.onerror=()=>toast('Network error.','err');x.send(fd)}},
admin:async()=>{if(!user||user.role!=='admin'){toast('You do not have permission to perform this action.','err');return location.hash='#/'}
 const load=()=>guard(async()=>{const d=await api('/api/admin/dashboard');app.innerHTML=`<h2>Faculty Administration</h2><div class="stats"><div class="card stat"><b>${d.total_students}</b>Total Students</div><div class="card stat"><b>${d.total_results}</b>Total Results</div><div class="card stat"><b>${d.uploaded_today}</b>Uploaded Today</div><div class="card stat"><b>${size(d.storage_bytes)}</b>Storage Used</div></div>
<h3>Recent uploads</h3><div class="tw"><table><tr><th>Student</th><th>Roll</th><th>Result</th><th>Subject</th><th>Date</th><th>File</th><th>Action</th></tr>${d.recent.map(r=>`<tr><td>${esc(r.student_name)}</td><td>${esc(r.roll_number)}</td><td>${esc(r.title)}</td><td>${esc(r.subject)}</td><td>${fdate(r.upload_date)}</td><td>${r.file_type.toUpperCase()}</td><td><button class="btn sm" data-v="${r.id}">View</button> <a class="btn sm ghost" href="/api/results/${r.id}/download">Download</a> <button class="btn sm danger" data-d="${r.id}">Delete</button></td></tr>`).join('')}</table></div>`;wire(load)});load()}};
async function route(){const k=location.hash.replace(/^#\/?/,'');renderNav();$('#nav').classList.remove('open');(views[k]||views[''])()}
addEventListener('hashchange',route);
(async()=>{try{user=(await api('/api/auth/me')).user}catch{}route()})();
// subtle physics particle background
const cv=$('#bg'),cx=cv.getContext('2d');let P=[];function rs(){cv.width=innerWidth;cv.height=innerHeight;P=Array.from({length:Math.min(60,innerWidth/18)},()=>({x:Math.random()*cv.width,y:Math.random()*cv.height,vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3}))}
function tick(){cx.clearRect(0,0,cv.width,cv.height);P.forEach((p,i)=>{p.x=(p.x+p.vx+cv.width)%cv.width;p.y=(p.y+p.vy+cv.height)%cv.height;cx.fillStyle='rgba(34,184,230,.35)';cx.beginPath();cx.arc(p.x,p.y,1.8,0,7);cx.fill();
 for(let j=i+1;j<P.length;j++){const d=Math.hypot(p.x-P[j].x,p.y-P[j].y);if(d<110){cx.strokeStyle=`rgba(34,184,230,${.12*(1-d/110)})`;cx.beginPath();cx.moveTo(p.x,p.y);cx.lineTo(P[j].x,P[j].y);cx.stroke()}}});requestAnimationFrame(tick)}
addEventListener('resize',rs);rs();tick();
