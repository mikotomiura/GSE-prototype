// Read the ACM Digital Library result list of the coverage search and post it to `c_search.py acm-receive`
// (decision 38). Run in a tab open on https://dl.acm.org/ (after the site's own bot check has passed by itself),
// with QUERY set to the ACM query that `python3 c_search.py queries` prints, and PORT and TOKEN as the receiver prints
// them (`c_search.py acm-receive` accepts one POST to /TOKEN from the ACM origin, with the registered query).
// Reads every result page (50 records each) of the ACM Guide to Computing Literature and posts
// {query, started, finished, reported_count, records: [{href, title, type, date, venue}]}.
// Stops (throws) if a page has no result count, if the records read differ from the reported count, or if a record
// is listed twice.
async function acmExport(QUERY, PORT, TOKEN) {
  const base = 'https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=all&pageSize=50';
  const started = new Date().toISOString();
  const page = async (n) => {
    const u = `${base}&startPage=${n}&AllField=${encodeURIComponent(QUERY)}`;
    const d = new DOMParser().parseFromString(await (await fetch(u, {credentials: 'include'})).text(), 'text/html');
    const c = d.querySelector('.hitsLength');
    if (!c) throw new Error(`page ${n}: no result count`);
    const recs = [...d.querySelectorAll('li.search__item')].map(li => ({
      href: li.querySelector('.issue-item__title a')?.getAttribute('href') || '',
      title: li.querySelector('.issue-item__title')?.innerText?.trim() || '',
      type: li.querySelector('.issue-heading')?.innerText?.trim() || '',
      date: li.querySelector('.bookPubDate,.dot-separator span')?.innerText?.trim() || '',
      venue: li.querySelector('.issue-item__detail a')?.innerText?.trim() || '',
    }));
    return {count: parseInt(c.textContent.replace(/[^0-9]/g, ''), 10), recs};
  };
  const first = await page(0);
  let records = first.recs;
  for (let n = 1; records.length < first.count; n++) {
    await new Promise(r => setTimeout(r, 2000));
    const p = await page(n);
    if (!p.recs.length) break;
    records = records.concat(p.recs);
  }
  if (records.length !== first.count) throw new Error(`read ${records.length}, reported ${first.count}`);
  const hrefs = new Set(records.map(r => r.href));
  if (hrefs.size !== records.length) throw new Error(`${records.length - hrefs.size} records listed twice; pages overlap`);
  const body = JSON.stringify({query: QUERY, started, finished: new Date().toISOString(),
                               reported_count: first.count, records});
  const r = await fetch(`http://127.0.0.1:${PORT}/${TOKEN}`, {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                     body});
  return `${r.status} ${await r.text()} (${records.length} records)`;
}
