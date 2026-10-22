# Maintaining research summaries

The home page, topic directory, topic summaries, data catalog and summary PNGs share `web/src/content/research-reading.server.ts`. Review each conclusion against its named public evidence before changing it. Do not promote historical description or exploration to a trading claim because a file hash or accounting check passes.

Keep sample dates distinct from evidence version dates. Mixed-period studies must say so rather than infer a common return period. Link the main public chart inputs and retain each experiment's detailed sources in its report. The catalog lists selected key evidence, not an exhaustive data lineage. No raw vendor data belongs in the catalog.

Keep English and Chinese copy together. Low-turnover's detailed image continues to use the pinned reader dataset; other summary images use the same metadata as their page and directory. Images retain dates and limits and intentionally omit the page URL.

Microcap's earlier reviews remain inside a native disclosure with their original IDs. Fragment links open ancestor disclosures, including repeated clicks on the same fragment. The archive's open state persists within the browser session when switching language. Without JavaScript it can be opened manually.

Search processes only allowlisted public methods. It indexes every heading with the renderer's slug or retained legacy ID, up to 1,200 characters in the introductory section and 240 in each later section. This is section search, not full-text search. Keep the 250 KiB index gate and public-path checks enabled.

For changes, run the web unit checks, Pages build and static verification, and affected browser tests. Check a mobile layout and both PNG languages. Editorial changes must not overwrite frozen historical downloads or imply newly observed returns.
