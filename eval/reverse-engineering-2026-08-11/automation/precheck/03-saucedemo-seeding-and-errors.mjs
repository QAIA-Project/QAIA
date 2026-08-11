import { chromium } from '@playwright/test';
const b = await chromium.launch();
// declarative seeding: cookie + localStorage via addInitScript
const ctx = await b.newContext();
await ctx.addCookies([{name:'session-username',value:'standard_user',domain:'www.saucedemo.com',path:'/'}]);
await ctx.addInitScript(() => window.localStorage.setItem('cart-contents','[4,2]'));
const p = await ctx.newPage();
await p.goto('https://www.saucedemo.com/cart.html');
console.log('SEEDED badge:', await p.locator('[data-test=shopping-cart-badge]').textContent().catch(()=>'NONE'), 'rows:', await p.locator('[data-test=inventory-item]').count());
console.log('SEEDED names:', await p.locator('[data-test=inventory-item-name]').allTextContents());
// sort options
await p.goto('https://www.saucedemo.com/inventory.html');
console.log('SORT options:', await p.locator('[data-test=product-sort-container] option').allTextContents());
console.log('SORT values:', await p.evaluate(()=>Array.from(document.querySelectorAll('[data-test=product-sort-container] option')).map(o=>o.value)));
console.log('names az:', await p.locator('[data-test=inventory-item-name]').allTextContents());
console.log('prices default:', await p.locator('[data-test=inventory-item-price]').allTextContents());
await p.selectOption('[data-test=product-sort-container]','lohi');
console.log('prices lohi:', await p.locator('[data-test=inventory-item-price]').allTextContents());
console.log('badge after sort:', await p.locator('[data-test=shopping-cart-badge]').textContent());
// locked out
const q = await (await b.newContext()).newPage();
await q.goto('https://www.saucedemo.com/');
await q.fill('[data-test=username]','locked_out_user'); await q.fill('[data-test=password]','secret_sauce'); await q.click('[data-test=login-button]');
console.log('LOCKED err:', await q.locator('[data-test=error]').textContent(), 'url', q.url());
// empty username
await q.goto('https://www.saucedemo.com/'); await q.fill('[data-test=password]','secret_sauce'); await q.click('[data-test=login-button]');
console.log('NOUSER err:', await q.locator('[data-test=error]').textContent());
await q.goto('https://www.saucedemo.com/'); await q.fill('[data-test=username]','standard_user'); await q.click('[data-test=login-button]');
console.log('NOPASS err:', await q.locator('[data-test=error]').textContent());
// unknown user vs known user wrong password - AC4 message equality
await q.goto('https://www.saucedemo.com/'); await q.fill('[data-test=username]','no_such_user_xyz'); await q.fill('[data-test=password]','secret_sauce'); await q.click('[data-test=login-button]');
console.log('UNKNOWNUSER err:', await q.locator('[data-test=error]').textContent());
await b.close();
