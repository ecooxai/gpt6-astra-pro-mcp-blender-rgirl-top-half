import {chromium} from 'playwright';
import fs from 'node:fs';
const url=process.env.PREVIEW_URL||'http://127.0.0.1:8793/';
const browser=await chromium.launch({headless:true,executablePath:'/home/dev/.local/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const results=[];
for(const device of [{name:'desktop',width:1440,height:1100},{name:'mobile',width:390,height:844}]){
 const page=await browser.newPage({viewport:{width:device.width,height:device.height},deviceScaleFactor:1}); const errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto(url,{waitUntil:'networkidle',timeout:60000});await page.waitForFunction(()=>window.__studio?.revision>0,{timeout:15000});
 await page.screenshot({path:`tests/${device.name}-studio.png`,fullPage:true});
 const checks=await page.evaluate(()=>({revision:window.__studio.revision,overflow:document.documentElement.scrollWidth>innerWidth,score:document.getElementById('score').textContent,imageLoaded:document.getElementById('main-image').naturalWidth>0,modelCredit:document.querySelector('.stage-credit').textContent,canvasHeight:document.getElementById('stage').clientHeight}));
 await page.click('#reference-open');checks.dialogOpened=await page.locator('#reference-dialog').evaluate(e=>e.open);await page.click('#reference-close');
 if(process.env.TEST_MODEL==='1'){
   await page.click('[data-view="orbit"]');await page.waitForFunction(()=>window.__studio.modelLoaded,{timeout:90000});await page.waitForTimeout(1200);
   checks.model=await page.evaluate(()=>({loaded:window.__studio.modelLoaded,bounds:window.__studio.modelBounds,errors:window.__studio.errors}));
   await page.click('#wireframe');checks.wireframe=await page.locator('#wireframe').getAttribute('aria-pressed');await page.click('#wireframe');
   await page.click('#rotate');checks.turntable=await page.locator('#rotate').getAttribute('aria-pressed');await page.click('#rotate');
   await page.screenshot({path:`tests/${device.name}-orbit.png`,fullPage:false});
 }
 results.push({device:device.name,...checks,errors});await page.close();
}
await browser.close();fs.writeFileSync('tests/browser-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results));
