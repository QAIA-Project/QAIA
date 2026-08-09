// E2E IHM — maps QAIA Gherkin scenarios (US-004) to executable Playwright tests.
// Each test title cites its stable scenario ID + AC for requirement traceability.
// Cross-actor preconditions not under test are seeded declaratively via the API (T3/T4);
// the actor whose UI action IS the scenario under test always drives it through the real UI.
// Note: the SUT is a single-page app with no live-refresh/polling — a signed-in actor's
// lists only reflect data that existed at login time (or the app's own post-action refresh()).
// So every UI actor here logs in with `openActor` AFTER any API-seeded data it needs to see,
// rather than reloading an already-logged-in page (a reload would just show the login screen
// again — there is no session persistence across a hard reload in this demo SUT).
const { test, expect } = require('./fixtures');
const { apiLogin, apiCreateSubmittedReport, apiDecide, todayISO } = require('./helpers');

const B = process.env.BASE_URL || 'http://localhost:4500'; // honore BASE_URL comme la config (B1)

test.describe('ExpenseFlow — approval journey (US-004)', () => {

  test('@QAIA-US-004-001 @AC1 @AC2 @AC8 @P1 @smoke end-to-end: draft to first approval on a small report', async ({ employee, openActor, request }) => {
    const { reportsPage } = employee;
    await reportsPage.startDraft();
    await reportsPage.fillLine(0, { category: 'taxi', amount: 40.00, date: todayISO(), receipt: true });
    await reportsPage.submitDraft();
    await expect(reportsPage.mineCards()).toHaveCount(1);
    const id = (await reportsPage.mineCards().first().getAttribute('data-testid')).replace('report-', '');
    await expect(reportsPage.status(id)).toHaveText('submitted');

    // manager logs in AFTER the report exists, so their inbox reflects it (see file header note)
    const mgr = await openActor('manager@demo', 'Mona Manager');
    await expect(mgr.reportsPage.inbox.getByTestId('status-' + id)).toHaveText('submitted');
    await mgr.reportsPage.approveBtn(id).click();
    await expect(mgr.reportsPage.message).toContainText('approve');

    const empToken = await apiLogin(request, B, 'employee@demo');
    const check = await request.get(B + '/api/reports/' + id, { headers: { Authorization: 'Bearer ' + empToken } });
    expect((await check.json()).report.status).toBe('approved');
  });

  test('@QAIA-US-004-002 @AC1 @P2 a complete draft is submitted successfully', async ({ employee }) => {
    const { reportsPage } = employee;
    await reportsPage.startDraft();
    await reportsPage.fillLine(0, { category: 'meal', amount: 20.00, date: todayISO(), receipt: true });
    await reportsPage.submitDraft();
    await expect(reportsPage.mineCards()).toHaveCount(1);
    const id = (await reportsPage.mineCards().first().getAttribute('data-testid')).replace('report-', '');
    await expect(reportsPage.status(id)).toHaveText('submitted');
  });

  test('@QAIA-US-004-003 @AC1 @P2 a changes-requested report returns to draft', async ({ openActor, request }) => {
    const emp = await apiLogin(request, B, 'employee@demo');
    const { id } = await apiCreateSubmittedReport(request, B, emp, { lines: [{ category: 'meal', amount: 20, date: todayISO(), receipt: true }] });

    const mgr = await openActor('manager@demo', 'Mona Manager'); // logs in after the report exists
    await expect(mgr.reportsPage.inbox.getByTestId('status-' + id)).toHaveText('submitted');
    await mgr.reportsPage.decide(id, 'changes', 'please add a receipt scan');
    await expect(mgr.reportsPage.message).toContainText('changes-requested');

    const check = await request.get(B + '/api/reports/' + id, { headers: { Authorization: 'Bearer ' + emp } });
    expect((await check.json()).report.status).toBe('draft');
  });

  test('@QAIA-US-004-004 @AC1 @P2 an edited changes-requested draft is re-submitted', async ({ openActor, request }) => {
    const emp = await apiLogin(request, B, 'employee@demo');
    const { id } = await apiCreateSubmittedReport(request, B, emp, { lines: [{ category: 'meal', amount: 20, date: todayISO(), receipt: false }] });
    const mgr = await apiLogin(request, B, 'manager@demo');
    await apiDecide(request, B, mgr, id, 'changes-requested', 'please add a receipt scan');

    // employee logs in after the changes-requested/draft transition happened
    const empActor = await openActor('employee@demo', 'Elie Employee');
    await expect(empActor.reportsPage.editBtn(id)).toBeVisible();
    await empActor.reportsPage.editBtn(id).click();
    await empActor.reportsPage.fillLine(0, { category: 'meal (with receipt)', amount: 20.00, date: todayISO(), receipt: true });
    await empActor.reportsPage.submitDraft();
    await expect(empActor.reportsPage.status(id)).toHaveText('submitted');
  });

  test('@QAIA-US-004-038 @AC-list @P3 an employee with no reports sees an empty list', async ({ employee }) => {
    const { reportsPage } = employee;
    await expect(reportsPage.mine).toContainText('No reports');
  });
});
