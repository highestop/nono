/**
 * Core logic for articles reader.
 * Pure functions with no DOM dependencies — testable in Node.js.
 */

/**
 * Build tag index and article metadata from articles data.
 * @param {Object} articles - { folder: [{ file, title, tags }] }
 * @returns {{ allTags: Object<string, Set<string>>, articleMeta: Object<string, { title, tags }> }}
 */
function buildTagIndex(articles) {
  const allTags = {};
  const articleMeta = {};
  for (const [folder, items] of Object.entries(articles)) {
    for (const item of items) {
      const key = `${folder}/${item.file}`;
      articleMeta[key] = { title: item.title, tags: item.tags || [] };
      // Skip -en.md files for tag counting (English originals have no tags)
      if (item.file.endsWith('-en.md')) continue;
      for (const tag of (item.tags || [])) {
        if (!allTags[tag]) allTags[tag] = new Set();
        allTags[tag].add(key);
      }
    }
  }
  return { allTags, articleMeta };
}

/**
 * Filter files in a folder by selected tags.
 * @param {Array} items - [{ file, tags }]
 * @param {Set<string>} selectedTags
 * @returns {string[]} filtered file names
 */
function getFilteredFiles(items, selectedTags) {
  if (!selectedTags || selectedTags.size === 0) return items.map(i => i.file);
  return items
    .filter(item => {
      const tags = item.tags || [];
      return [...selectedTags].every(t => tags.includes(t));
    })
    .map(i => i.file);
}

/**
 * Merge bilingual pairs from a file list.
 * A bilingual pair is: "xxx.md" (Chinese, main) + "xxx-en.md" (English original)
 * @param {string[]} fileList
 * @returns {Array<{ cn?: string, en?: string, file?: string, bilingual: boolean }>}
 */
function processArticles(fileList) {
  const enSuffix = '-en.md';
  const enFiles = new Set(fileList.filter(f => f.endsWith(enSuffix)));
  const entries = [];
  const processed = new Set();

  for (const file of fileList) {
    if (processed.has(file)) continue;

    if (file.endsWith(enSuffix)) {
      const base = file.slice(0, -enSuffix.length);
      const cnFile = base + '.md';
      if (fileList.includes(cnFile)) {
        entries.push({ cn: cnFile, en: file, bilingual: true });
        processed.add(file);
        processed.add(cnFile);
      } else {
        entries.push({ file: file, bilingual: false });
        processed.add(file);
      }
    } else {
      const base = file.slice(0, -'.md'.length);
      const enFile = base + enSuffix;
      if (enFiles.has(enFile)) {
        entries.push({ cn: file, en: enFile, bilingual: true });
        processed.add(file);
        processed.add(enFile);
      } else {
        entries.push({ file: file, bilingual: false });
        processed.add(file);
      }
    }
  }

  return entries;
}

/**
 * Extract title from markdown content.
 * @param {string} md
 * @returns {string}
 */
function extractTitle(md) {
  const match = md.match(/^#\s+(.+)$/m);
  if (match) return match[1].trim();
  const firstLine = md.trim().split('\n')[0];
  return firstLine ? firstLine.replace(/^#+\s*/, '').trim() : 'Untitled';
}

/**
 * Escape HTML special characters.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Export for Node.js testing; no-op in browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { buildTagIndex, getFilteredFiles, processArticles, extractTitle, escapeHtml };
}
