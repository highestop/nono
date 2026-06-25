#!/usr/bin/env node
/**
 * Tests for articles/core.js pure logic functions.
 * Run: node articles/__tests__/test-core.js
 */

const { buildTagIndex, getFilteredFiles, processArticles, extractTitle, escapeHtml } = require('../core.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (e) {
    failed++;
    console.log(`  ✗ ${name}: ${e.message}`);
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg);
}

function assertDeepEqual(actual, expected, msg) {
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a !== e) throw new Error(`${msg}: expected ${e}, got ${a}`);
}

// ---------------------------------------------------------------------------
// buildTagIndex
// ---------------------------------------------------------------------------

console.log('buildTagIndex:');

test('builds tag index and metadata', () => {
  const articles = {
    '2099-01-01': [
      { file: 'a.md', title: 'Article A', tags: ['AI', 'Agent'] },
      { file: 'b.md', title: 'Article B', tags: ['AI'] },
    ]
  };
  const { allTags, articleMeta } = buildTagIndex(articles);
  assert(allTags['AI'].size === 2, `AI tag should have 2 articles, got ${allTags['AI'].size}`);
  assert(allTags['Agent'].size === 1, `Agent tag should have 1 article`);
  assert(articleMeta['2099-01-01/a.md'].title === 'Article A', 'metadata title mismatch');
});

test('skips -en.md files for tag counting', () => {
  const articles = {
    '2099-01-01': [
      { file: 'x-123.md', title: '中文', tags: ['AI'] },
      { file: 'x-123-en.md', title: 'English', tags: [] },
    ]
  };
  const { allTags, articleMeta } = buildTagIndex(articles);
  assert(allTags['AI'].size === 1, 'AI tag should count only main file');
  assert(!allTags['AI'].has('2099-01-01/x-123-en.md'), '-en file should not be in tag index');
  assert(articleMeta['2099-01-01/x-123-en.md'], '-en file should still be in metadata');
});

test('handles empty articles', () => {
  const { allTags, articleMeta } = buildTagIndex({});
  assertDeepEqual(allTags, {}, 'allTags should be empty');
  assertDeepEqual(articleMeta, {}, 'articleMeta should be empty');
});

test('handles items with no tags', () => {
  const articles = {
    '2099-01-01': [
      { file: 'a.md', title: 'No Tags' },
    ]
  };
  const { allTags, articleMeta } = buildTagIndex(articles);
  assertDeepEqual(allTags, {}, 'allTags should be empty');
  assert(articleMeta['2099-01-01/a.md'].tags.length === 0, 'tags should default to []');
});

// ---------------------------------------------------------------------------
// getFilteredFiles
// ---------------------------------------------------------------------------

console.log('\ngetFilteredFiles:');

test('returns all files when no tags selected', () => {
  const items = [
    { file: 'a.md', tags: ['AI'] },
    { file: 'b.md', tags: ['Agent'] },
  ];
  const result = getFilteredFiles(items, new Set());
  assertDeepEqual(result, ['a.md', 'b.md'], 'should return all files');
});

test('filters by single tag', () => {
  const items = [
    { file: 'a.md', tags: ['AI', 'Agent'] },
    { file: 'b.md', tags: ['Agent'] },
    { file: 'c.md', tags: ['AI'] },
  ];
  const result = getFilteredFiles(items, new Set(['AI']));
  assertDeepEqual(result, ['a.md', 'c.md'], 'should return AI-tagged files');
});

test('filters by multiple tags (intersection)', () => {
  const items = [
    { file: 'a.md', tags: ['AI', 'Agent'] },
    { file: 'b.md', tags: ['Agent'] },
    { file: 'c.md', tags: ['AI'] },
  ];
  const result = getFilteredFiles(items, new Set(['AI', 'Agent']));
  assertDeepEqual(result, ['a.md'], 'should return files with both tags');
});

test('returns empty when no files match', () => {
  const items = [
    { file: 'a.md', tags: ['AI'] },
  ];
  const result = getFilteredFiles(items, new Set(['Agent']));
  assertDeepEqual(result, [], 'should return empty');
});

// ---------------------------------------------------------------------------
// processArticles
// ---------------------------------------------------------------------------

console.log('\nprocessArticles:');

test('pairs bilingual files (cn first)', () => {
  const result = processArticles(['x-123.md', 'x-123-en.md']);
  assert(result.length === 1, `expected 1 entry, got ${result.length}`);
  assert(result[0].bilingual === true, 'should be bilingual');
  assert(result[0].cn === 'x-123.md', 'cn file mismatch');
  assert(result[0].en === 'x-123-en.md', 'en file mismatch');
});

test('pairs bilingual files (en first)', () => {
  const result = processArticles(['x-123-en.md', 'x-123.md']);
  assert(result.length === 1, `expected 1 entry, got ${result.length}`);
  assert(result[0].bilingual === true, 'should be bilingual');
  assert(result[0].cn === 'x-123.md', 'cn file mismatch');
  assert(result[0].en === 'x-123-en.md', 'en file mismatch');
});

test('standalone file (no pair)', () => {
  const result = processArticles(['wx-abc.md']);
  assert(result.length === 1, `expected 1 entry, got ${result.length}`);
  assert(result[0].bilingual === false, 'should not be bilingual');
  assert(result[0].file === 'wx-abc.md', 'file mismatch');
});

test('standalone -en file (no cn pair)', () => {
  const result = processArticles(['orphan-en.md']);
  assert(result.length === 1, `expected 1 entry, got ${result.length}`);
  assert(result[0].bilingual === false, 'should not be bilingual');
  assert(result[0].file === 'orphan-en.md', 'file mismatch');
});

test('mixed bilingual and standalone files', () => {
  const result = processArticles(['wx-abc.md', 'x-1.md', 'x-1-en.md', 'xhs-def.md']);
  assert(result.length === 3, `expected 3 entries, got ${result.length}`);
  const bilingual = result.filter(e => e.bilingual);
  const standalone = result.filter(e => !e.bilingual);
  assert(bilingual.length === 1, 'should have 1 bilingual pair');
  assert(standalone.length === 2, 'should have 2 standalone files');
});

test('empty file list', () => {
  const result = processArticles([]);
  assertDeepEqual(result, [], 'should return empty');
});

// ---------------------------------------------------------------------------
// extractTitle
// ---------------------------------------------------------------------------

console.log('\nextractTitle:');

test('extracts # heading', () => {
  assert(extractTitle('# Hello World\n\nBody') === 'Hello World', 'title mismatch');
});

test('extracts ## heading if no # heading', () => {
  assert(extractTitle('## Sub Heading\n\nBody') === 'Sub Heading', 'should not match ## as title');
});

test('extracts first line if no heading', () => {
  assert(extractTitle('Just some text\nMore text') === 'Just some text', 'first line mismatch');
});

test('returns Untitled for empty string', () => {
  assert(extractTitle('') === 'Untitled', 'should return Untitled');
});

test('trims whitespace from title', () => {
  assert(extractTitle('#   Spaced Title  \n') === 'Spaced Title', 'should trim');
});

// ---------------------------------------------------------------------------
// escapeHtml
// ---------------------------------------------------------------------------

console.log('\nescapeHtml:');

test('escapes < > & "', () => {
  assert(escapeHtml('<b>"Tom & Jerry"</b>') === '&lt;b&gt;&quot;Tom &amp; Jerry&quot;&lt;/b&gt;', 'escape mismatch');
});

test('passes through safe strings', () => {
  assert(escapeHtml('Hello World') === 'Hello World', 'safe string should be unchanged');
});

// ---------------------------------------------------------------------------

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
