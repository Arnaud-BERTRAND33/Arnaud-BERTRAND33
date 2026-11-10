const {chromium}=require('playwright');
const [out,a,b,fps]=[process.argv[2],+process.argv[3],+process.argv[4],+process.argv[5]];
(async()=>{const br=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await br.newPage({viewport:{width:1920,height:1080}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://127.0.0.1:8765/film.html');await p.waitForFunction(()=>window.ready,null,{timeout:60000});
for(let f=a;f<b;f++){await p.evaluate(t=>window.seek(t),f/fps);
 await p.screenshot({path:`${out}/${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:94});
 if(f%100==0)console.log('frame',f);}
await br.close();console.log('done',a,b)})();
