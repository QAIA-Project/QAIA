// Option A (ADR 0003): read-only access to QAIA's skill content, for an external MCP client
// (Cursor, Copilot, ...) to read and follow the same way Claude Code reads a local skill file.
// No business logic here beyond "find the file, read it" -- the interpretation of the content
// is entirely up to the calling model, exactly as it already is inside Claude Code.
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(__dirname, '..', '..');
const PLUGINS_DIR = path.join(REPO_ROOT, 'plugins');

// Parses only the two frontmatter fields the shared contract requires every SKILL.md to have
// (name, description) -- see .github/workflows/ci.yml's own frontmatter check for the same
// two fields, kept in sync deliberately rather than re-deriving a separate notion of "valid".
function parseFrontmatter(text) {
  // Split on \r?\n: this repo is checked out with CRLF line endings on Windows (git
  // autocrlf) but LF elsewhere -- found by a real test failure (qaia-core/feedback
  // reporting no description) rather than assumed, matching the project's own convention
  // of verifying rather than guessing (see e.g. D65's regex fixes).
  const lines = text.split(/\r?\n/);
  if (lines[0] !== '---') return { name: null, description: null };
  const end = lines.indexOf('---', 1);
  // Un frontmatter non ferme rendait `end === -1`, et `slice(1, undefined)` prenait TOUT le
  // fichier comme frontmatter : `get('name')` retournait alors la premiere ligne commencant par
  // « name: » n'importe ou dans le corps. Un fichier sans frontmatter valide n'a pas de
  // frontmatter -- il ne faut pas en inventer un (B39).
  if (end === -1) return { name: null, description: null };
  const block = lines.slice(1, end);
  const get = (key) => {
    const line = block.find((l) => l.startsWith(`${key}:`));
    return line ? line.slice(key.length + 1).trim() : null;
  };
  return { name: get('name'), description: get('description') };
}

// Enumerates every SKILL.md under plugins/*/skills/*/ -- the exact same set the CI frontmatter
// check already validates, so "listed here" == "shipped in a real QAIA plugin", never a
// user-supplied or externally-reachable path.
export async function listSkills() {
  const plugins = await readdir(PLUGINS_DIR, { withFileTypes: true });
  const skills = [];
  for (const plugin of plugins) {
    if (!plugin.isDirectory()) continue;
    const skillsDir = path.join(PLUGINS_DIR, plugin.name, 'skills');
    let skillDirs;
    try {
      skillDirs = await readdir(skillsDir, { withFileTypes: true });
    } catch {
      continue; // a plugin without a skills/ dir is not an error here
    }
    for (const skillDir of skillDirs) {
      if (!skillDir.isDirectory()) continue;
      const skillPath = path.join(skillsDir, skillDir.name, 'SKILL.md');
      let content;
      try {
        content = await readFile(skillPath, 'utf8');
      } catch {
        continue;
      }
      const { name, description } = parseFrontmatter(content);
      skills.push({
        id: `${plugin.name}/${skillDir.name}`,
        plugin: plugin.name,
        name: name || skillDir.name,
        description: description || '',
      });
    }
  }
  return skills.sort((a, b) => a.id.localeCompare(b.id));
}

// Reads one skill's full content by its "plugin/skill-dir" id (exactly the id listSkills()
// returns -- never a free-form path). Resolves and re-checks the path stays inside plugins/
// before reading, so a client cannot escape via "../" even if it fabricates an id string.
export async function getSkillContent(id) {
  const [plugin, skillDir] = String(id).split('/');
  if (!plugin || !skillDir) {
    throw new Error('invalid skill id, expected "plugin/skill-dir" as returned by list_skills');
  }
  const skillPath = path.resolve(PLUGINS_DIR, plugin, 'skills', skillDir, 'SKILL.md');
  if (!skillPath.startsWith(PLUGINS_DIR + path.sep)) {
    throw new Error('resolved path escapes plugins/ -- refused');
  }
  return readFile(skillPath, 'utf8');
}

export async function getOutputContract() {
  return readFile(path.join(REPO_ROOT, 'docs', 'OUTPUT-CONTRACT.md'), 'utf8');
}
