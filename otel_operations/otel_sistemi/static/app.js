const API = '/api';
let user = null;

async function api(path, opts = {}) {
  const o = { headers: { 'Content-Type': 'application/json' }, ...opts };
  if (o.body && typeof o.body === 'object') o.body = JSON.stringify(o.body);
  const r = await fetch(API + path, o);
  return r.json();
}
const $ = id => document.getElementById(id);
const app = () => $('app');

function showMsg(txt, ok = true) {
  return `<div class="msg ${ok ? 'msg-ok' : 'msg-err'}">${txt}</div>`;
}

// ── LOGIN ──
function showLogin() {
  user = null;
  app().innerHTML = `
    <div style="display:flex;align-items:center;justify-content:center;min-height:90vh">
    <div class="card" style="width:100%">
      <h1>🏨 Otel Sistemi</h1>
      <input id="em" type="email" placeholder="E-posta">
      <input id="pw" type="password" placeholder="Şifre">
      <button class="btn btn-primary" onclick="doLogin()">Giriş Yap</button>
      <div id="lerr"></div>
    </div></div>`;
}

async function doLogin() {
  const d = await api('/login', { method: 'POST', body: { email: $('em').value, password: $('pw').value } });
  if (!d.success) { $('lerr').innerHTML = showMsg(d.message, false); return; }
  user = d.data;
  route();
}

function route() {
  if (!user) { showLogin(); return; }
  const r = user.role;
  if (r === 'manager') showManager();
  else if (r === 'receptionist') showReceptionist();
  else if (r === 'housekeeper') showHousekeeper();
  else if (r === 'customer') showCustomer();
}

function hdr(title) {
  return `<div class="header"><div><b>${title}</b><br><span>${user.name} ${user.surname}</span></div>
  <button class="btn btn-danger btn-sm" onclick="showLogin()">Çıkış</button></div>`;
}

// ── MANAGER ──
function showManager() {
  app().innerHTML = hdr('Yönetici Paneli') + `
  <div class="grid">
    <button class="btn btn-primary" onclick="mOccupancy()">📊 Doluluk</button>
    <button class="btn btn-primary" onclick="mRooms()">🛏 Odalar</button>
    <button class="btn btn-success" onclick="mStays()">🏠 Konaklamalar</button>
    <button class="btn btn-success" onclick="mAllRes()">📋 Rezervasyonlar</button>
    <button class="btn btn-warning" onclick="mStaff()">👥 Personel</button>
    <button class="btn btn-warning" onclick="mAddStaff()">➕ Personel Ekle</button>
    <button class="btn btn-secondary" onclick="mToggleUser()">🔒 Hesap Durumu</button>
    <button class="btn btn-secondary" onclick="mTasks()">🧹 Hizmet Talep</button>
    <button class="btn btn-primary" onclick="mAssign()">📌 Görev Ata</button>
    <button class="btn btn-primary" onclick="mRoomStatus()">🔧 Oda Durumu</button>
    <button class="btn btn-warning" onclick="mPayments()">💳 Ödemeler</button>
    <button class="btn btn-danger" onclick="mLogs()">📜 Loglar</button>
  </div><div id="mc"></div>`;
}

async function mOccupancy() {
  const d = await api('/occupancy');
  const r = d.data;
  $('mc').innerHTML = `<div class="card"><h2>Doluluk Raporu</h2>
    <p>Toplam: ${r.total} | Dolu: ${r.occupied} | Müsait: ${r.available} | Temizlik: ${r.cleaning}</p>
    <p style="font-size:24px;color:#f59e0b;text-align:center;margin-top:8px">%${r.occupancy_rate}</p></div>`;
}

async function mRooms() {
  const d = await api('/rooms');
  $('mc').innerHTML = '<div class="card"><h2>Tüm Odalar</h2>' +
    d.data.map(r => `<div class="list-item">Oda ${r.room_number} | Kat ${r.floor} | ${r.type_name} | <span class="badge ${r.status_name==='available'?'badge-green':r.status_name==='occupied'?'badge-red':'badge-yellow'}">${r.status_name}</span></div>`).join('') + '</div>';
}

async function mStays() {
  const d = await api('/reservations?status=checked_in');
  $('mc').innerHTML = '<div class="card"><h2>Aktif Konaklamalar</h2>' +
    (d.data.length ? d.data.map(x => `<div class="list-item">${x.customer_name} | Oda ${x.room_number} | Çıkış: ${x.check_out_date}</div>`).join('') : '<p>Aktif konaklama yok.</p>') + '</div>';
}

async function mAllRes() {
  const cats = {all:'Tümü',pending_payment:'Ödeme Bekleyen',active:'Onaylı',checked_in:'Aktif',completed:'Tamamlanan',cancelled:'İptal'};
  $('mc').innerHTML = `<div class="card"><h2>Rezervasyonlar</h2><div class="tabs" id="rtabs"></div><div id="rlist"></div></div>`;
  const tabsEl = $('rtabs');
  for(const [k,v] of Object.entries(cats)){
    const b = document.createElement('button'); b.className='tab'+(k==='all'?' active':''); b.textContent=v;
    b.onclick=()=>{tabsEl.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));b.classList.add('active');loadRes(k,'rlist');};
    tabsEl.appendChild(b);
  }
  loadRes('all','rlist');
}
async function loadRes(cat, target) {
  const url = cat==='all' ? '/reservations' : '/reservations?status='+cat;
  const d = await api(url);
  $(target).innerHTML = d.data.length ? d.data.map(x => `<div class="list-item">#${x.id} ${x.customer_name} | <span class="badge ${x.status==='checked_in'?'badge-green':x.status==='completed'?'badge-blue':x.status==='cancelled'?'badge-red':'badge-yellow'}">${x.status}</span> | ${x.check_in_date} → ${x.check_out_date}</div>`).join('') : '<p>Kayıt yok.</p>';
}

async function mStaff() {
  const d1 = await api('/users?role=receptionist');
  const d2 = await api('/users?role=housekeeper');
  const all = [...d1.data, ...d2.data];
  $('mc').innerHTML = '<div class="card"><h2>Personel</h2>' +
    all.map(s => `<div class="list-item">${s.name} ${s.surname} (${s.role}) <span class="badge ${s.is_active?'badge-green':'badge-red'}">${s.is_active?'Aktif':'Pasif'}</span></div>`).join('') + '</div>';
}

function mAddStaff() {
  $('mc').innerHTML = `<div class="card"><h2>Personel Ekle</h2>
    <input id="sn" placeholder="Ad"><input id="ss" placeholder="Soyad">
    <input id="se" placeholder="E-posta"><input id="sp" placeholder="Şifre">
    <select id="sr"><option value="receptionist">Resepsiyonist</option><option value="housekeeper">Kat Görevlisi</option></select>
    <button class="btn btn-success" onclick="doAddStaff()">Kaydet</button><div id="smsg"></div></div>`;
}
async function doAddStaff() {
  const d = await api('/users', { method:'POST', body:{ actor_id:user.id, name:$('sn').value, surname:$('ss').value, email:$('se').value, password:$('sp').value, role:$('sr').value }});
  $('smsg').innerHTML = showMsg(d.message, d.success);
}

async function mToggleUser() {
  const d1 = await api('/users?role=receptionist');
  const d2 = await api('/users?role=housekeeper');
  const d3 = await api('/users?role=customer');
  const all = [...d1.data, ...d2.data, ...d3.data];
  $('mc').innerHTML = `<div class="card"><h2>Hesap Durumu Değiştir (FR4)</h2>
    <select id="tu">${all.map(u=>`<option value="${u.id}">${u.name} ${u.surname} (${u.role}) - ${u.is_active?'Aktif':'Pasif'}</option>`).join('')}</select>
    <div class="grid"><button class="btn btn-success" onclick="doToggle(true)">Aktif Yap</button>
    <button class="btn btn-danger" onclick="doToggle(false)">Pasif Yap</button></div><div id="tmsg"></div></div>`;
}
async function doToggle(active) {
  const d = await api('/users/'+$('tu').value+'/toggle', { method:'PATCH', body:{ actor_id:user.id, is_active:active }});
  $('tmsg').innerHTML = showMsg(d.message, d.success);
  if(d.success) setTimeout(()=>mToggleUser(), 800);
}

async function mTasks() {
  const d = await api('/services');
  $('mc').innerHTML = '<div class="card"><h2>Hizmet Talepleri</h2>' +
    (d.data.length ? d.data.map(t => `<div class="list-item">#${t.id} Oda ${t.room_number} | ${t.service_type} | <span class="badge ${t.status==='completed'?'badge-green':t.status==='pending'?'badge-yellow':'badge-blue'}">${t.status}</span> | ${t.staff_name||'Atanmadı'}</div>`).join('') : '<p>Talep yok.</p>') + '</div>';
}

async function mAssign() {
  const p = await api('/services?status=pending');
  const s = await api('/users?role=housekeeper');
  if(!p.data.length){ $('mc').innerHTML='<div class="card"><p>Bekleyen görev yok.</p></div>'; return; }
  $('mc').innerHTML = `<div class="card"><h2>Görev Ata</h2>
    <select id="at">${p.data.map(t=>`<option value="${t.id}">Oda ${t.room_number} - ${t.service_type}</option>`).join('')}</select>
    <select id="as">${s.data.map(u=>`<option value="${u.id}">${u.name} ${u.surname}</option>`).join('')}</select>
    <button class="btn btn-success" onclick="doAssign()">Ata</button><div id="amsg"></div></div>`;
}
async function doAssign() {
  const d = await api('/services/'+$('at').value+'/assign', { method:'POST', body:{ actor_id:user.id, staff_id:parseInt($('as').value) }});
  $('amsg').innerHTML = showMsg(d.message, d.success);
  if(d.success) setTimeout(()=>mAssign(), 800);
}

async function mRoomStatus() {
  const d = await api('/rooms');
  $('mc').innerHTML = `<div class="card"><h2>Oda Durumu Değiştir</h2>
    <select id="rr">${d.data.map(r=>`<option value="${r.id}">Oda ${r.room_number} (${r.status_name})</option>`).join('')}</select>
    <select id="rs"><option value="available">Müsait</option><option value="maintenance">Bakımda</option><option value="cleaning">Temizlikte</option><option value="occupied">Dolu</option></select>
    <button class="btn btn-warning" onclick="doRoomSt()">Güncelle</button><div id="rmsg"></div></div>`;
}
async function doRoomSt() {
  const d = await api('/rooms/'+$('rr').value+'/status', { method:'PATCH', body:{ actor_id:user.id, status:$('rs').value }});
  $('rmsg').innerHTML = showMsg(d.message, d.success);
}

async function mPayments() {
  const d = await api('/payments');
  $('mc').innerHTML = '<div class="card"><h2>Ödeme Geçmişi</h2>' +
    (d.data.length ? d.data.map(p => `<div class="list-item">${p.customer_name} | ${p.amount} TL | ${p.paid_at?.substring(0,10)} | Kod: ${p.transaction_code?.substring(0,10)}...</div>`).join('') : '<p>Ödeme yok.</p>') + '</div>';
}

async function mLogs() {
  const cats = {all:'Tümü',auth:'Giriş',reservation:'Rezervasyon',checkin_checkout:'Check-in/out',service:'Hizmet',room:'Oda',user:'Kullanıcı'};
  $('mc').innerHTML = `<div class="card"><h2>İşlem Kayıtları</h2>
    <div class="tabs" id="ltabs"></div><div id="llist"></div></div>`;
  const tabsEl = $('ltabs');
  for(const [k,v] of Object.entries(cats)){
    const b = document.createElement('button');
    b.className = 'tab' + (k==='all'?' active':'');
    b.textContent = v;
    b.onclick = () => { tabsEl.querySelectorAll('.tab').forEach(t=>t.classList.remove('active')); b.classList.add('active'); loadLogs(k); };
    tabsEl.appendChild(b);
  }
  loadLogs('all');
}
async function loadLogs(cat) {
  const url = cat === 'all' ? '/logs?limit=100' : '/logs?limit=100&category='+cat;
  const d = await api(url);
  $('llist').innerHTML = d.data.length ? d.data.map(l => `<div class="list-item">[${l.logged_at?.substring(0,16)}] ${l.user_name} → ${l.action}</div>`).join('') : '<p>Kayıt yok.</p>';
}

// ── RECEPTIONIST ──
function showReceptionist() {
  app().innerHTML = hdr('Resepsiyon Paneli') + `
  <div class="grid">
    <button class="btn btn-primary" onclick="rAvail()">🛏 Müsait Odalar</button>
    <button class="btn btn-success" onclick="rActive()">🏠 Aktif Konakla</button>
    <button class="btn btn-warning" onclick="rAddCust()">👤 Müşteri Ekle</button>
    <button class="btn btn-primary" onclick="rAddRes()">📝 Rezervasyon</button>
    <button class="btn btn-success" onclick="rPay()">💳 Ödeme Al</button>
    <button class="btn btn-warning" onclick="rCheckin()">🔑 Check-in</button>
    <button class="btn btn-danger" onclick="rCheckout()">🚪 Check-out</button>
    <button class="btn btn-secondary" onclick="rAllRes()">📋 Tüm Rez.</button>
  </div><div id="rc"></div>`;
}

async function rAvail() {
  const today = new Date().toISOString().split('T')[0];
  const d = await api('/rooms/available?check_in='+today+'&check_out='+today);
  $('rc').innerHTML = '<div class="card"><h2>Müsait Odalar</h2>' +
    d.data.map(r => `<div class="list-item">Oda ${r.room_number} | ${r.type_name} | ${r.base_price} TL/gece</div>`).join('') + '</div>';
}

async function rActive() {
  const d = await api('/reservations?status=checked_in');
  $('rc').innerHTML = '<div class="card"><h2>Aktif Konaklamalar</h2>' +
    (d.data.length ? d.data.map(x => `<div class="list-item">#${x.id} ${x.customer_name} | Oda ${x.room_number} | Çıkış: ${x.check_out_date}</div>`).join('') : '<p>Yok.</p>') + '</div>';
}

function rAddCust() {
  $('rc').innerHTML = `<div class="card"><h2>Müşteri Ekle</h2>
    <input id="cn" placeholder="Ad"><input id="cs" placeholder="Soyad">
    <input id="ce" placeholder="E-posta"><input id="cp" placeholder="Şifre">
    <input id="ct" placeholder="Telefon">
    <button class="btn btn-success" onclick="doAddCust()">Kaydet</button><div id="cmsg"></div></div>`;
}
async function doAddCust() {
  const d = await api('/users', { method:'POST', body:{ actor_id:user.id, name:$('cn').value, surname:$('cs').value, email:$('ce').value, password:$('cp').value, role:'customer', phone:$('ct').value }});
  $('cmsg').innerHTML = showMsg(d.message, d.success);
}

async function rAddRes() {
  const c = await api('/users?role=customer');
  $('rc').innerHTML = `<div class="card"><h2>Rezervasyon Oluştur</h2>
    <select id="rc2">${c.data.map(u=>`<option value="${u.id}">${u.name} ${u.surname}</option>`).join('')}</select>
    <label style="font-size:12px;color:#94a3b8">Giriş Tarihi</label><input id="ri" type="date">
    <label style="font-size:12px;color:#94a3b8">Çıkış Tarihi</label><input id="ro" type="date">
    <input id="ra" type="number" placeholder="Yetişkin" value="1">
    <button class="btn btn-primary" onclick="doAddRes()">Oluştur</button><div id="rrmsg"></div></div>`;
}
async function doAddRes() {
  const d = await api('/reservations', { method:'POST', body:{ actor_id:user.id, customer_id:parseInt($('rc2').value), check_in:$('ri').value, check_out:$('ro').value, adult_count:parseInt($('ra').value) }});
  $('rrmsg').innerHTML = showMsg(d.message, d.success);
}

async function rPay() {
  const r = await api('/reservations?status=pending_payment');
  if(!r.data.length){ $('rc').innerHTML='<div class="card"><p>Bekleyen ödeme yok.</p></div>'; return; }
  $('rc').innerHTML = `<div class="card"><h2>Ödeme Al</h2>
    <select id="pr" onchange="calcAmt()">${r.data.map(x=>`<option value="${x.id}">#${x.id} ${x.customer_name}</option>`).join('')}</select>
    <input id="pa" type="number" placeholder="Tutar (TL)">
    <input id="pn" placeholder="Kart Sahibi Adı">
    <input id="pl" placeholder="Son 4 Hane" maxlength="4">
    <button class="btn btn-success" onclick="doPay()">Öde</button><div id="pmsg"></div></div>`;
  calcAmt();
}
async function calcAmt() {
  const d = await api('/reservations/'+$('pr').value+'/amount');
  if(d.data?.amount) $('pa').value = d.data.amount;
}
async function doPay() {
  const l = $('pl').value;
  if(l.length!==4||!/^\d+$/.test(l)){ $('pmsg').innerHTML=showMsg('Son 4 hane 4 rakam olmalı',false); return; }
  const d = await api('/reservations/'+$('pr').value+'/pay', { method:'POST', body:{ actor_id:user.id, amount:parseFloat($('pa').value), card_holder_name:$('pn').value, card_last_four:l }});
  $('pmsg').innerHTML = showMsg(d.message, d.success);
}

async function rCheckin() {
  const r = await api('/reservations?status=active');
  if(!r.data.length){ $('rc').innerHTML='<div class="card"><p>Ödenmiş rezervasyon yok.</p></div>'; return; }
  $('rc').innerHTML = `<div class="card"><h2>Check-in</h2>
    <select id="cr" onchange="loadCiRooms()">${r.data.map(x=>`<option value="${x.id}" data-ci="${x.check_in_date}" data-co="${x.check_out_date}">#${x.id} ${x.customer_name}</option>`).join('')}</select>
    <select id="cm"></select>
    <button class="btn btn-success" onclick="doCheckin()">Check-in Yap</button><div id="cimsg"></div></div>`;
  loadCiRooms();
}
async function loadCiRooms() {
  const sel = $('cr'); const o = sel.options[sel.selectedIndex];
  const d = await api('/rooms/available?check_in='+o.dataset.ci+'&check_out='+o.dataset.co);
  $('cm').innerHTML = d.data.map(r=>`<option value="${r.id}">Oda ${r.room_number} (${r.type_name})</option>`).join('') || '<option>Oda yok</option>';
}
async function doCheckin() {
  const d = await api('/reservations/'+$('cr').value+'/checkin', { method:'POST', body:{ actor_id:user.id, room_id:parseInt($('cm').value) }});
  $('cimsg').innerHTML = showMsg(d.message + (d.data?.qr_code ? ' QR: '+d.data.qr_code.substring(0,12)+'...' : ''), d.success);
}

async function rCheckout() {
  const r = await api('/reservations?status=checked_in');
  if(!r.data.length){ $('rc').innerHTML='<div class="card"><p>Aktif konaklama yok.</p></div>'; return; }
  $('rc').innerHTML = `<div class="card"><h2>Check-out</h2>
    <select id="co2">${r.data.map(x=>`<option value="${x.id}">#${x.id} ${x.customer_name} Oda ${x.room_number}</option>`).join('')}</select>
    <button class="btn btn-danger" onclick="doCheckout()">Check-out Yap</button><div id="comsg"></div></div>`;
}
async function doCheckout() {
  const d = await api('/reservations/'+$('co2').value+'/checkout', { method:'POST', body:{ actor_id:user.id }});
  $('comsg').innerHTML = showMsg(d.message, d.success);
}

async function rAllRes() {
  const cats = {all:'Tümü',pending_payment:'Ödeme Bekleyen',active:'Onaylı',checked_in:'Aktif',completed:'Tamamlanan',cancelled:'İptal'};
  $('rc').innerHTML = `<div class="card"><h2>Rezervasyonlar</h2><div class="tabs" id="rrtabs"></div><div id="rrlist"></div></div>`;
  const tabsEl = $('rrtabs');
  for(const [k,v] of Object.entries(cats)){
    const b = document.createElement('button'); b.className='tab'+(k==='all'?' active':''); b.textContent=v;
    b.onclick=()=>{tabsEl.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));b.classList.add('active');loadRes(k,'rrlist');};
    tabsEl.appendChild(b);
  }
  loadRes('all','rrlist');
}

// ── HOUSEKEEPER ──
function showHousekeeper() {
  app().innerHTML = hdr('Kat Görevlisi Paneli') + `
  <div class="grid">
    <button class="btn btn-primary" onclick="hTasks()">📋 Görevlerim</button>
    <button class="btn btn-success" onclick="hChange()">✅ Durum Güncelle</button>
  </div><div id="hc"></div>`;
}

async function hTasks() {
  const d = await api('/services?assigned_to='+user.id);
  $('hc').innerHTML = '<div class="card"><h2>Görevlerim</h2>' +
    (d.data.length ? d.data.map(t => `<div class="list-item">#${t.id} Oda ${t.room_number} | ${t.service_type} | <span class="badge ${t.status==='completed'?'badge-green':t.status==='in_progress'?'badge-blue':'badge-yellow'}">${t.status}</span></div>`).join('') : '<p>Görev yok.</p>') + '</div>';
}

async function hChange() {
  const d = await api('/services?assigned_to='+user.id);
  const active = d.data.filter(t => t.status==='pending'||t.status==='in_progress');
  if(!active.length){ $('hc').innerHTML='<div class="card"><p>Aktif görev yok.</p></div>'; return; }
  $('hc').innerHTML = `<div class="card"><h2>Görev Durumu Güncelle</h2>
    <select id="ht">${active.map(t=>`<option value="${t.id}">#${t.id} Oda ${t.room_number} (${t.service_type})</option>`).join('')}</select>
    <button class="btn btn-warning" onclick="doHSt('in_progress')">Başladım</button>
    <button class="btn btn-success" onclick="doHSt('completed')">Tamamlandı</button>
    <button class="btn btn-danger" onclick="doHSt('cancelled')">İptal</button>
    <div id="hmsg"></div></div>`;
}
async function doHSt(st) {
  const d = await api('/services/'+$('ht').value+'/status', { method:'PATCH', body:{ actor_id:user.id, status:st }});
  $('hmsg').innerHTML = showMsg(d.message, d.success);
  if(d.success) setTimeout(()=>hChange(), 800);
}

// ── CUSTOMER ──
function showCustomer() {
  app().innerHTML = hdr('Müşteri Paneli') + `
  <div class="grid">
    <button class="btn btn-primary" onclick="cKey()">🔑 Oda Anahtarım</button>
    <button class="btn btn-success" onclick="cService('cleaning')">🧹 Temizlik İste</button>
    <button class="btn btn-warning" onclick="cService('room_service')">🍽 Oda Servisi</button>
    <button class="btn btn-secondary" onclick="cScan()">📷 QR Tara</button>
  </div><div id="cc"></div>`;
}

async function cKey() {
  const d = await api('/my-access', { method:'POST', body:{ customer_id:user.id }});
  if(!d.success){ $('cc').innerHTML='<div class="card"><p>'+d.message+'</p></div>'; return; }
  $('cc').innerHTML = `<div class="card"><h2>Oda ${d.data.room_number}</h2>
    <div id="qr-display"></div>
    <div class="code-text">${d.data.qr_code}</div>
    <p style="text-align:center;color:#94a3b8;font-size:13px">Çıkış: ${d.data.check_out_date}</p></div>`;
  new QRCode($('qr-display'), { text:d.data.qr_code, width:200, height:200, colorDark:'#e2e8f0', colorLight:'#1e293b' });
}

async function cService(type) {
  const d = await api('/services', { method:'POST', body:{ customer_id:user.id, service_type:type }});
  $('cc').innerHTML = `<div class="card">${showMsg(d.message, d.success)}</div>`;
}

function cScan() {
  $('cc').innerHTML = `<div class="card"><h2>QR Kod Tara</h2>
    <video id="vid" autoplay playsinline></video>
    <button class="btn btn-danger btn-sm" onclick="stopCam()">Kamerayı Kapat</button>
    <p style="margin-top:8px;text-align:center;color:#94a3b8">veya manuel girin:</p>
    <input id="mc2" placeholder="Erişim Kodu">
    <button class="btn btn-primary" onclick="verifyCode($('mc2').value)">Doğrula</button>
    <div id="vmsg"></div></div>`;
  startCam();
}

let camStream = null;
async function startCam() {
  try {
    camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode:'environment' } });
    $('vid').srcObject = camStream;
  } catch(e) { console.log('Kamera erişimi yok:', e); }
}
function stopCam() {
  if(camStream) { camStream.getTracks().forEach(t=>t.stop()); camStream=null; }
  const v=$('vid'); if(v) v.srcObject=null;
}

async function verifyCode(code) {
  if(!code){ $('vmsg').innerHTML=showMsg('Kod giriniz.',false); return; }
  const d = await api('/verify-access', { method:'POST', body:{ code }});
  $('vmsg').innerHTML = `<div class="card" style="margin-top:8px"><p>${d.message}</p>
    ${d.success ? '<p>Misafir: '+d.data.guest_name+'<br>Oda: '+d.data.room_number+'<br>Geçerli: '+d.data.valid_from+' → '+d.data.valid_until+'</p>' : ''}</div>`;
}

// Start
showLogin();
