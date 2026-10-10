// JWT хранится только в памяти вкладки; обновление страницы требует нового входа.
let access = null, refresh = null, kind = 'clients', records = [], editing = null;
const $ = id => document.getElementById(id);
const schemas = {
  clients: [['full_name','ФИО','text'],['iin','ИИН (12 цифр)','text'],['phone','Телефон','text'],['email','Email','email']],
  accounts: [['client','Клиент','select'],['number','Номер счёта (KZ + 18 символов)','text'],['currency','Валюта','select'],['balance','Баланс','number']]
};
function message(text='', error=false){ $('message').textContent=text; $('message').classList.toggle('error',error); }
function signedOut(){ access=refresh=null; records=[]; $('workspace').hidden=true; $('login').hidden=false; $('logout').hidden=true; $('rows').replaceChildren(); $('request-log').textContent=''; }
function explain(data){ return typeof data==='object' ? Object.entries(data).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(', '):v}`).join('\n') : String(data); }
async function api(path, method='GET', body, retry=true){
  const r=await fetch('/api/'+path,{method,headers:{'Content-Type':'application/json',...(access?{'Authorization':'Bearer '+access}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const data=r.status===204?null:await r.json();
  if(r.status===401 && refresh && retry && !path.startsWith('auth/')){
    const rr=await fetch('/api/auth/refresh/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh})});
    const tokens=await rr.json();
    if(rr.ok){access=tokens.access;refresh=tokens.refresh||refresh;return api(path,method,body,false);}
    signedOut(); throw Error('Сессия истекла. Войдите снова.');
  }
  if(!path.startsWith('auth/')) $('request-log').textContent=`${method} /api/${path}\n${body?JSON.stringify(body,null,2):''}\nHTTP ${r.status}\n${data?JSON.stringify(data,null,2):''}`;
  if(!r.ok) throw Error(explain(data));
  return data;
}
async function safely(action){try{message();await action();}catch(e){message(e.message,true);}}
function cell(row,value){const td=document.createElement('td');td.textContent=value??'—';row.append(td);return td;}
async function load(){
  const data=await api(kind+'/?search='+encodeURIComponent($('search').value));records=data;
  const headers=kind==='clients'?['ID','ФИО','ИИН','Телефон','Email','Действия']:['ID','Клиент','Номер счёта','Валюта','Баланс','Действия'];
  const tr=document.createElement('tr');headers.forEach(h=>{const th=document.createElement('th');th.textContent=h;tr.append(th);});$('head').replaceChildren(tr);$('rows').replaceChildren();
  data.forEach(record=>{const row=document.createElement('tr');const keys=kind==='clients'?['id','full_name','iin','phone','email']:['id','client_name','number','currency','balance'];keys.forEach(k=>cell(row,record[k]));const actions=cell(row,'');
    for(const [text,fn,css] of [['Изменить',()=>openEditor(record),'secondary'],['Удалить',async()=>{if(confirm('Удалить запись №'+record.id+'?')){await api(`${kind}/${record.id}/`,'DELETE');await load();message('Запись удалена.');}},'danger']]){const b=document.createElement('button');b.textContent=text;b.className=css;b.onclick=()=>safely(fn);actions.append(b);} $('rows').append(row);
  });$('count').textContent=`Найдено записей: ${data.length}`;
}
async function openEditor(record=null){
  editing=record?.id??null;$('fields').replaceChildren();
  const clients=kind==='accounts'?await api('clients/'):[];
  if(kind==='accounts'&&!clients.length) throw Error('Сначала добавьте клиента.');
  for(const [key,title,type] of schemas[kind]){
    const label=document.createElement('label');label.textContent=title;
    const input=document.createElement(type==='select'?'select':'input');input.name=key;
    if(type==='select'){
      const options=key==='client'?clients.map(c=>[c.id,`${c.full_name} · ${c.iin}`]):['KZT','USD','EUR'].map(c=>[c,c]);
      for(const [value,text] of options){const o=document.createElement('option');o.value=value;o.textContent=text;input.append(o);}
    }else input.type=type;
    input.required=!['phone','email'].includes(key);
    if(key==='balance'){input.min='0';input.max='99999999999999.99';input.step='.01';input.value='0.00';}
    if(key==='iin'){input.pattern='[0-9]{12}';input.maxLength=12;input.inputMode='numeric';}
    if(key==='number'){input.pattern='KZ[0-9A-Z]{18}';input.maxLength=20;}
    if(record) input.value=record[key];label.append(input);$('fields').append(label);
  }
  $('editor-title').textContent=editing?'Изменение записи №'+editing:'Новая запись';$('editor').hidden=false;$('editor').scrollIntoView({behavior:'smooth'});
}
$('login-form').onsubmit=e=>{e.preventDefault();safely(async()=>{const tokens=await api('auth/token/','POST',Object.fromEntries(new FormData(e.target)));access=tokens.access;refresh=tokens.refresh;e.target.reset();$('login').hidden=true;$('workspace').hidden=false;$('logout').hidden=false;await load();});};
$('logout').onclick=()=>safely(async()=>{try{if(refresh)await api('auth/logout/','POST',{refresh});}finally{signedOut();}});
for(const type of ['clients','accounts']) $(type+'-tab').onclick=()=>safely(async()=>{kind=type;$('search').value='';$('editor').hidden=true;$('table-title').textContent=type==='clients'?'Клиенты':'Счета';for(const t of ['clients','accounts'])$(t+'-tab').setAttribute('aria-pressed',String(t===type));await load();});
$('search-form').onsubmit=e=>{e.preventDefault();safely(load);};$('new').onclick=()=>safely(()=>openEditor());$('cancel').onclick=()=>{$('editor').hidden=true;};
$('record-form').onsubmit=e=>{e.preventDefault();safely(async()=>{const body=Object.fromEntries(new FormData(e.target));if(body.client)body.client=Number(body.client);await api(kind+'/'+(editing?editing+'/':''),editing?'PUT':'POST',body);$('editor').hidden=true;await load();message('Запись сохранена в PostgreSQL.');});};
