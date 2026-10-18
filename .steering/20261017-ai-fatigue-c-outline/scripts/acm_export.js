// Read the ACM Digital Library result list of the coverage search and post it to `c_search.py acm-receive`
// (decision 38). Run in a tab open on https://dl.acm.org/ (after the site's own bot check has passed by itself),
// with QUERY set to the ACM query that `python3 c_search.py queries` prints, and PORT and TOKEN as the receiver prints
// them (`c_search.py acm-receive` accepts one POST to /TOKEN from the ACM origin, with the registered query).
// Reads every result page (50 records each) of the ACM Guide to Computing Literature and posts
// {query, started, finished, reported_count, records: [{href, title, type, date, venue}]}.
// Stops (throws) if a page has no result count, if the reported count changes, or if the records united over the
// passes do not reach the reported count.
async function acmExport(QUERY, PORT, TOKEN) {
  const base = 'https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=all&pageSize=50';
  const started = new Date().toISOString();
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const page = async (n, sort) => {
    const u = `${base}&startPage=${n}${sort ? `&sortBy=${sort}` : ''}&AllField=${encodeURIComponent(QUERY)}`;
    let d, c;
    for (let t = 0; t < 2 && !c; t++) {   // a page without a count (the site's check) is read once more, 15 s later
      if (t) await wait(15000);
      d = new DOMParser().parseFromString(await (await fetch(u, {credentials: 'include'})).text(), 'text/html');
      c = d.querySelector('.hitsLength');
    }
    if (!c) throw new Error(`page ${n} (${sort || 'relevance'}): no result count`);
    const recs = [...d.querySelectorAll('li.search__item')].map(li => ({
      href: li.querySelector('.issue-item__title a')?.getAttribute('href') || '',
      title: li.querySelector('.issue-item__title')?.innerText?.trim() || '',
      type: li.querySelector('.issue-heading')?.innerText?.trim() || '',
      date: li.querySelector('.bookPubDate,.dot-separator span')?.innerText?.trim() || '',
      venue: li.querySelector('.issue-item__detail a')?.innerText?.trim() || '',
    }));
    window.__acmp = {n, sort, at: new Date().toISOString()};  // progress, readable from the console
    return {count: parseInt(c.textContent.replace(/[^0-9]/g, ''), 10), recs};
  };
  // The result order moves between pages (2026-10-18: one record on two pages, so another on none, and the same
  // record missing in two relevance-ordered passes). The whole list is read in up to three orders (relevance, then
  // the site's own sorts by publication date, ascending and descending) and the records are united by link; the
  // export is complete when the union reaches the reported count, and stops otherwise.
  const SORTS = ['', 'EpubDate_asc', 'EpubDate_desc'];
  const byHref = new Map();
  let count = null;
  const passes = [];
  for (let pass = 1; pass <= SORTS.length; pass++) {
    const sort = SORTS[pass - 1];
    const first = await page(0, sort);
    if (count === null) count = first.count;
    if (first.count !== count) throw new Error(`the reported count changed: ${count} -> ${first.count}`);
    let read = first.recs;
    for (let n = 1; read.length < count; n++) {
      await wait(8000);
      const p = await page(n, sort);
      if (p.count !== count) throw new Error(`the reported count changed on page ${n}: ${count} -> ${p.count}`);
      if (!p.recs.length) break;
      read = read.concat(p.recs);
    }
    read.forEach(r => { if (r.href && !byHref.has(r.href)) byHref.set(r.href, r); });
    passes.push({pass, sort: sort || 'relevance', read: read.length, unique_so_far: byHref.size});
    window.__acmpasses = passes;
    if (byHref.size >= count) break;
  }
  const records = [...byHref.values()];
  if (records.length !== count) throw new Error(`united ${records.length} records over ${passes.length} passes, reported ${count}`);
  const body = JSON.stringify({query: QUERY, started, finished: new Date().toISOString(),
                               reported_count: count, passes, records});
  window.__acmbody = body;  // kept, so that only the POST can be repeated if the receiver was not reachable
  const r = await fetch(`http://127.0.0.1:${PORT}/${TOKEN}`, {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                     body});
  return `${r.status} ${await r.text()} (${records.length} records)`;
}
