import test from 'node:test';
import assert from 'node:assert/strict';
import { listSkills, getSkillContent, getOutputContract } from '../src/skills.js';
import { scoreFeature, validateManifest } from '../src/tools.js';
import { readdirSync, existsSync } from 'node:fs';

// The count is READ FROM DISK, never hard-coded. The previous version asserted
// `length >= 29` under a title claiming "all 29" — the repository had 35 by then, so the
// test passed while its title lied, and it would still have passed if the bridge had
// silently dropped six skills. `length >= N` is a one-sided assertion, and it is the exact
// defect class `qaia-score:automation-score` exists to flag in generated suites.
function countShippedSkills() {
  const root = new URL('../../plugins/', import.meta.url);
  let n = 0;
  for (const plugin of readdirSync(root, { withFileTypes: true })) {
    if (!plugin.isDirectory()) continue;
    const skillsDir = new URL(`${plugin.name}/skills/`, root);
    if (!existsSync(skillsDir)) continue;
    for (const skill of readdirSync(skillsDir, { withFileTypes: true })) {
      if (skill.isDirectory() && existsSync(new URL(`${plugin.name}/skills/${skill.name}/SKILL.md`, root))) n += 1;
    }
  }
  return n;
}

test('list_skills exposes every shipped skill, each with a name and description', async () => {
  const skills = await listSkills();
  const onDisk = countShippedSkills();
  assert.ok(onDisk > 0, 'no SKILL.md found on disk — the test cannot prove anything');
  assert.equal(skills.length, onDisk,
    `the bridge exposes ${skills.length} skills but ${onDisk} SKILL.md files exist`);
  for (const s of skills) {
    assert.ok(s.id.includes('/'), `id should be "plugin/skill-dir": ${s.id}`);
    assert.ok(s.name, `skill ${s.id} has no name`);
    assert.ok(s.description, `skill ${s.id} has no description`);
  }
});

test('get_skill_content reads a real skill end to end', async () => {
  const skills = await listSkills();
  const target = skills.find((s) => s.id === 'qaia-core/istqb-design');
  assert.ok(target, 'istqb-design should be listed');
  const content = await getSkillContent(target.id);
  assert.match(content, /istqb-design/);
  assert.match(content, /Domain Testing/); // D109 rename -- proves this reads the live file, not a cache
});

test('get_skill_content refuses a path-traversal id', async () => {
  await assert.rejects(() => getSkillContent('../../../../etc/passwd'), /refused|invalid/);
});

test('get_output_contract reads the real contract doc', async () => {
  const content = await getOutputContract();
  // Le numero de version est DELIBEREMENT hors de l'assertion. Il etait epingle a `contract 1.0`
  // et a fait rougir la CI au premier bump mineur (1.1, ADR 0008, 2026-08-11) -- alors que ce
  // test ne verifie pas la version : il verifie que le pont lit le vrai fichier. Epingler un
  // nombre qui bouge par conception, c'est la meme classe de faute que les cinq regles dupliquees
  // corrigees le 2026-08-09 : une seconde copie d'un fait qui finit par diverger.
  assert.match(content, /## Schema \(contract \d+\.\d+\)/);
  assert.match(content, /qaia-score/); // preuve que c'est le fichier vivant, pas un cache
});

test('score_feature: a well-formed feature scores reasonably and is NOT FAIL', async () => {
  const content = `Feature: demo
  @QAIA-DEMO-001 @ep @P1
  Scenario: valid input is accepted
    Given a valid input
    When it is submitted
    Then the response status is 200

  @QAIA-DEMO-002 @ep @negative @P1
  Scenario: invalid input is refused
    Given an invalid input
    When it is submitted
    Then the response status is 422
`;
  const result = await scoreFeature(content);
  assert.equal(result.scenarios, 2);
  assert.notEqual(result.gate, 'FAIL');
});

test('score_feature: an injected defect (hollow Then) is actually caught, not silently passed', async () => {
  // Mirrors the project's own verification convention (D65/D83 etc.): prove the wrapper
  // reports a real, unambiguous defect rather than trusting a clean-looking round-trip.
  const content = `Feature: demo
  @QAIA-DEMO-003 @ep @P1
  Scenario: something happens
    Given a thing
    When it happens
    Then it works
`;
  const result = await scoreFeature(content);
  assert.equal(result.gate, 'FAIL', `expected FAIL on a hollow Then, got ${result.gate}: ${JSON.stringify(result.findings)}`);
});

test('validate_manifest: a real, valid manifest passes', async () => {
  const manifest = {
    contract: '1.0',
    usId: 'US-TEST',
    title: 'test',
    status: 'draft',
    generatedAt: new Date(0).toISOString(),
    base: '.qaia',
    producers: [{ plugin: 'qaia-core', version: '0.2.18', skill: 'testbook-generate', at: new Date(0).toISOString() }],
    artifacts: [{ kind: 'feature', format: 'gherkin', path: 'testbooks/US-TEST/x.feature' }],
  };
  const result = await validateManifest(JSON.stringify(manifest));
  assert.equal(result.pass, true, `expected pass, got errors: ${JSON.stringify(result.errors)}`);
});

test('validate_manifest: an injected defect (bad status enum) is actually caught', async () => {
  const manifest = {
    contract: '1.0',
    usId: 'US-TEST',
    title: 'test',
    status: 'not-a-real-status',
    generatedAt: new Date(0).toISOString(),
    base: '.qaia',
    producers: [],
    artifacts: [],
  };
  const result = await validateManifest(JSON.stringify(manifest));
  assert.equal(result.pass, false);
  assert.ok(result.errors.some((e) => e.includes('status')), `expected a status error, got: ${JSON.stringify(result.errors)}`);
});
