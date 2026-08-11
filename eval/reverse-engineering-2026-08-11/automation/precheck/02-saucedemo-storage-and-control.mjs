import { chromium } from '@playwright/test';
const b = await chromium.launch();
// 1. cart storage location
const ctx = await b.newContext();
const p = await ctx.newPage();
await p.goto('https://www.saucedemo.com/');
await p.fill('[data-test=username]','standard_user'); await p.fill('[data-test=password]','secret_sauce'); await p.click('[data-test=login-button]');
await p.waitForURL(/inventory/);
await p.click('[data-test=add-to-cart-sauce-labs-backpack]');
await p.click('[data-test=add-to-cart-sauce-labs-onesie]');
console.log('COOKIES:', JSON.stringify(await ctx.cookies()));
console.log('LOCALSTORAGE:', await p.evaluate(()=>JSON.stringify(localStorage)));
console.log('SESSIONSTORAGE:', await p.evaluate(()=>JSON.stringify(sessionStorage)));
// 2. tax on a different subtotal (metamorphic check on AC5)
await p.goto('https://www.saucedemo.com/checkout-step-one.html');
await p.fill('[data-test=firstName]','A'); await p.fill('[data-test=lastName]','B'); await p.fill('[data-test=postalCode]','C');
await p.click('[data-test=continue]');
console.log('TOTALS 2 items:', await p.locator('[data-test=subtotal-label]').textContent(), '|', await p.locator('[data-test=tax-label]').textContent(), '|', await p.locator('[data-test=total-label]').textContent());
// 3. seed session by cookie only — controllability probe
const ctx2 = await b.newContext();
await ctx2.addCookies([{name:'session-username',value:'standard_user',domain:'www.saucedemo.com',path:'/'}]);
const q = await ctx2.newPage();
const r2 = await q.goto('https://www.saucedemo.com/inventory.html');
console.log('COOKIE-SEEDED inventory status', r2.status(), 'url', q.url(), 'items', await q.locator('[data-test=inventory-item]').count());
// 4. seed cart by cookie
const ctx3 = await b.newContext();
await ctx3.addCookies([
  {name:'session-username',value:'standard_user',domain:'www.saucedemo.com',path:'/'},
  {name:'cart-contents',value:'[4]',domain:'www.saucedemo.com',path:'/'}]);
const s = await ctx3.newPage();
await s.goto('https://www.saucedemo.com/cart.html');
console.log('COOKIE-SEEDED cart badge:', await s.locator('[data-test=shopping-cart-badge]').count() ? await s.locator('[data-test=shopping-cart-badge]').textContent() : 'NONE', 'rows', await s.locator('[data-test=inventory-item]').count());
// 5. empty cart -> checkout reachable?
const ctx4 = await b.newContext();
await ctx4.addCookies([{name:'session-username',value:'standard_user',domain:'www.saucedemo.com',path:'/'}]);
const t = await ctx4.newPage();
await t.goto('https://www.saucedemo.com/cart.html');
await t.click('[data-test=checkout]');
console.log('EMPTY CART after checkout click url:', t.url());
await t.fill('[data-test=firstName]','A'); await t.fill('[data-test=lastName]','B'); await t.fill('[data-test=postalCode]','C'); await t.click('[data-test=continue]');
console.log('EMPTY CART step two url:', t.url(), 'totals:', await t.locator('[data-test=subtotal-label]').textContent().catch(()=>'n/a'));
await t.click('[data-test=finish]');
console.log('EMPTY CART finish url:', t.url(), 'header:', await t.locator('[data-test=complete-header]').textContent().catch(()=>'n/a'));
// 6. unauth page body
const ctx5 = await b.newContext(); const u = await ctx5.newPage();
const r5 = await u.goto('https://www.saucedemo.com/inventory.html');
console.log('UNAUTH status', r5.status(), 'url', u.url(), 'title', await u.title(), 'bodyStart', (await u.locator('body').innerText()).slice(0,200).replace(/\n/g,' / '));
// 7. login error field behaviour (AC6)
const p6 = await (await b.newContext()).newPage();
await p6.goto('https://www.saucedemo.com/');
await p6.fill('[data-test=username]','standard_user'); await p6.fill('[data-test=password]','wrong'); await p6.click('[data-test=login-button]');
console.log('AC6 username after fail:', JSON.stringify(await p6.inputValue('[data-test=username]')), 'password after fail:', JSON.stringify(await p6.inputValue('[data-test=password]')), 'err:', await p6.locator('[data-test=error]').textContent());
await b.close();
