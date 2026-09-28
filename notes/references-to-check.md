# References to check

Every citation introduced into the report, with its verification status. The final pass is
mechanical: work this list top to bottom against primary sources.

**Status key** — `CONFIRMED` (primary source opened during this project; authors, title,
venue, year and identifier all match) · `INHERITED` (came from the submitted interim
bibliography, not yet re-checked against its primary source) · `UNVERIFIED` (needed for a
claim, not yet located; must **not** appear as a citation — use
`[CITATION NEEDED: <claim>]` in the text instead).

## Verified on 7 September 2026

| Key | Source | Status | Used in |
|---|---|---|---|
| `passeratpalmbach2025dphints` | Passerat-Palmbach J, Wadhwa S. Differentially Private aggregate hints in mev-share. arXiv:2508.14284; 19 Aug 2025. cs.CR | `CONFIRMED` | Ch 2 order-flow auctions; Ch 6 mitigations |
| `pennock2004dpm` | Pennock DM. A dynamic pari-mutuel market for hedging, wagering, and information aggregation. In: Proc. 5th ACM Conference on Electronic Commerce (EC'04). New York: ACM; 2004. p. 170–179. doi:10.1145/988772.988799 | `CONFIRMED` | Ch 2 scoring rules; Ch 3 Delphi pricing |
| `gebele2026semantic` | Gebele J, Matthes F. Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets. arXiv:2601.01706; 5 Jan 2026. | `CONFIRMED` | Ch 2 prediction-market arbitrage |
| `uma2026oracle` | UMA. How does UMA's oracle work. Protocol documentation. Accessed 7 Sep 2026. | `CONFIRMED` | Ch 2 optimistic oracles; Ch 3 Sapience resolution |
| `sapience2026relayer` | Sapience. Auction Relayer API, and the relayer implementation at `packages/relayer/src/handlers/escrow.ts` and `packages/sdk/types/escrow.ts`. MIT. Accessed 7 Sep 2026. | `CONFIRMED` | Ch 3 execution information flow; Ch 4 model |
| `gensyn2026sdk` | Gensyn. Delphi SDK documentation. Accessed 6–7 Sep 2026. | `CONFIRMED` | Ch 3 Delphi pricing and settlement routing |
| `glosten1985bidask` | Glosten LR, Milgrom PR. Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. Journal of Financial Economics. 1985;14(1):71–100. | `CONFIRMED` | Ch 2 microstructure; Ch 4 the expected sign of H1 |
| `kyle1985continuous` | Kyle AS. Continuous Auctions and Insider Trading. Econometrica. 1985;53(6):1315–1336. | `CONFIRMED` | Ch 2 microstructure; Ch 4 |
| `nakamura2026privacysubsidy` | Nakamura Y. The Privacy Subsidy in Glosten-Milgrom: Bid-Ask Spread and Welfare under Flip-Noise Direction Observation. arXiv:2605.19742; 19 May 2026. | `CONFIRMED` | Ch 2; Ch 4 positioning; Ch 6 mitigations |
| `gensyn2026delphi` | Jedamski D. Building Delphi: Pricing, Settlement, and Agentic Trading. Gensyn engineering blog, 7 May 2026. | `CONFIRMED` (URL fetched 4 Sep 2026; re-open before submission) | Ch 3 |
| `truebit2026orchestration` | Truebit. Orchestration Layer for Offchain Agents. Case study, 20 Aug 2026. | `CONFIRMED` (URL fetched 6 Sep 2026; re-open before submission) | Ch 3 |

### Corrections that came out of verification

- **The supervisor's paper is not a Financial Cryptography paper.** `references-seed.md`
  guessed "Likely Financial Cryptography and Data Security, 2025". It is a standalone arXiv
  preprint, arXiv:2508.14284, with **two** authors, Passerat-Palmbach and Wadhwa. Citing it
  as a conference paper would have been a fabricated venue in the supervisor's own entry.
- **arXiv:2601.01706 is real** and matches the interim's bibliography entry. It also gives a
  usable quantitative finding: of over 100,000 events analysed, roughly 6% appear
  concurrently across platforms, with prices diverging by 2–4% on average.

## The optimistic-oracle critique — resolved by reframing, not by citation

`references-seed.md` flagged the claim that UMA tokenholders are incentivised to vote with
the expected majority rather than the truth as "widely stated but must be properly
sourced". **No independent academic source was found.** The search returned UMA's own
documentation and UMA's own blog rebutting critics.

**Do not cite an academic critique that does not exist.** The report instead cites UMA's
primary documentation for the *mechanism*, and labels the inference as its own argument, in
line with `CLAUDE.md` §6: every claim is cited, measured, or labelled as an argument.

Verified from UMA's documentation, 7 September 2026:

- "Slashing and rewards incentivize stakers to vote for the most correct answer."
- "Casting votes in secret prevents lazy voters from copying other voters and dishonest
  voters from coordinating on an incorrect result."
- Disputes resolve when a minimum **65% majority** of staked UMA votes for a single outcome.
- Voting is **24-hour commit** followed by **24-hour reveal**.
- Both proposer and disputer post bonds, forfeited by the losing side.

The report's argument, labelled as argument: a mechanism that pays for agreement with the
resolved majority is a coordination device, and coordination devices track truth only while
the truth is the focal point. On a question whose wording is genuinely contested, the focal
point is whatever voters expect other voters to choose, which need not be the
best reading of the specification. UMA's design anticipates this and defends against
*coordination* (secret ballots, a 65% threshold, a one-week unstaking delay); none of those
defences addresses *ambiguity*, because they make it harder to agree on a lie rather than
easier to agree on a meaning. Chapter 3 makes this point and marks it as the report's own
reasoning about a documented mechanism, not as a reported finding.

## Inherited from the interim, still to re-check

Carried over in `report/bib/references.bib`. These were compiled for the interim
submission and are the most trustworthy unverified entries here, but the declaration says
every reference was checked against its primary source, so they must be.

| Key | Status |
|---|---|
| `daian2019flashboys` | `INHERITED` |
| `chitra2023uncertainty` | `INHERITED` |
| `ethereummev` | `INHERITED` |
| `wolfers2004prediction` | `INHERITED` |
| `hanson2007lmsr` | `INHERITED` |
| `saguillo2025forest` | `INHERITED` |
| `lui2025bittensor` | `INHERITED` |
| `numinousgithub` | `INHERITED` |
| `blanchard2017krum` | `INHERITED` — one sentence only, strategic ≠ Byzantine |

## Located but not yet read — candidates only

Found while verifying the above. **Not citable until read.** Listed so the final pass knows
where they came from.

| Source | Why it might matter |
|---|---|
| Passerat-Palmbach J et al. SoK: Encrypted Mempools Through the MEV Lens. IACR ePrint 2026/1643 | Directly on point for the sealed-bid mitigation in Ch 6, and it is the supervisor's own work |
| SoK: The Evolution of Maximal Extractable Value, From Miners to Cross-Chain. arXiv:2603.07716 | A recent MEV survey for Ch 2 framing |
| Gaming Dynamic Parimutuel Markets (Springer, LNCS) | Strategic behaviour in DPM, which is Delphi's execution surface |

## Still unverified, and the claims that depend on them

| Needed for | Status |
|---|---|
| LLM-as-judge reliability, position and verbosity bias | `UNVERIFIED` — Ch 3 semantic-validity argument. Reword to avoid if not found |
| Conditional recall (Xyn, Flashbots, 2022) | `UNVERIFIED` — Ch 6 mitigations. Currently sourced only to the breakout notes, which are a primary record of a meeting and can be cited as such |
| Trail of Bits audit of Delphi contracts | `UNVERIFIED` — one clause in Ch 3; drop the clause if not found |


## Positioning risk found while verifying the microstructure anchors

`nakamura2026privacysubsidy` (arXiv:2605.19742, 19 May 2026) derives closed-form bid-ask
spreads in the Glosten-Milgrom model when the market maker observes trade direction through
a noisy binary channel, and identifies a per-trade "privacy subsidy" transferred from the
protocol to traders. A companion preprint does the same for continuous-time Kyle
(arXiv:2605.25631, not yet read).

**This is close to the experiment's territory and the report must engage with it rather
than ignore it.** It does not pre-empt the project: it is analytic rather than simulated,
it treats a single market maker rather than `n` competing responders with correlated
signals, and it says nothing about resolution power, which is the report's primary
contribution. But it does mean two things. First, the framing of H1 as a validity check is
now better supported, since the sign is not merely expected on theoretical grounds but has
a closed form in the nearest model. Second, the noised-disclosure mitigation in Chapter 6
has a quantitative precedent that should be cited rather than reinvented.

Read arXiv:2605.25631 before Chapter 6. Both need reading properly before Chapter 4 claims
novelty for anything.


---

# Full verification pass — 7 September 2026

`reference-checker` ran across all 27 cited entries. **No fabricated reference.** All 27
exist, all 27 are cited, every key resolves, and all seven arXiv identifiers were opened
individually and match with no transposition. The nine `INHERITED` entries survived
re-checking with their bibliographic details intact.

The findings were in the second job, whether each source says what the report claims.
Seven citations were attached to claims their sources do not support. All are now fixed.

| Finding | Fix applied |
|---|---|
| Bittensor row said "scoring against realised outcomes"; the subnet scores against the market price seven days later, with the current price as baseline | Row rewritten to what the README states |
| Saguillo et al. cited twice for inconsistency "across venues"; the study is Polymarket-only and within-platform | Split: within-platform to Saguillo, across-platform to Gebele and Matthes |
| "Launched on Gensyn mainnet on 22 April 2026"; the word mainnet does not appear in the launch post | Reworded; the SDK is cited separately for the existence of a mainnet, and no launch date is asserted for it |
| "Auction resolves in seconds" cited to the relayer source, which fixes no timescale | Re-cited to the user guide, which states it verbatim |
| "The arrangement it replaced" asserted a sequence Truebit does not claim; their text is present tense and contrastive | Reworded to a contrast, restoring the section's own discipline |
| "Verifiable computing ... is explicit" attributed a disclaimer to both Gensyn and Truebit; only Gensyn states it | Attributed to Gensyn alone, with Truebit's silence noted |
| The adversarial-agents caution was stated as an empirical proposition with an added comparative clause; the source is one line of meeting notes | Reframed as a reported observation, explicitly not a measured result |
| Table row made three uncited factual claims about Polymarket and Kalshi by name | Replaced with a generic order-book row making no claim about any named venue |

Bibliographic corrections: Truebit's title restored to "The Orchestration Layer for Offchain
Agents"; the Numinous title, which was invented, replaced with the repository's own; the
MEV-SBC note no longer claims Imperial College participation, which the notes do not record;
DOIs added for Glosten-Milgrom and Kyle; the Hanson entry now records that the linked copy is
the author's January 2002 working paper rather than the published version; the Sapience user
guide entry now points at the pinned subpages rather than the docs root.

**One claim softened rather than fixed.** The Sapience repository's README describes the
project as MIT-licensed, but the LICENSE file it links to returns 404 at the pinned commit
and GitHub's licence API detects none. Chapter 1 and Chapter 3 now attribute the licence to
the repository's own description rather than asserting it.

**Known and accepted.** `vancouver.bst` silently drops the DOI field, so DOIs are recorded in
the `.bib` for completeness but do not render. Title case is inconsistent across entries
because it follows each source.

**One disagreement with the checker, recorded.** It reports that UMA's documentation does not
support the unstaking-delay rationale. The page states that if the oracle were corrupted the
token "would depreciate significantly in the following week, resulting in a loss for the
attackers", which is that rationale. The citation stands.

## Status of the declaration

The Declarations state that every reference has been checked against its primary source.
After this pass that sentence is true, with the two qualifications recorded above: the
Hanson text was verified in the author's working-paper copy rather than the published
version, and the Sapience licence is reported as the repository's own claim.

---

# Submission-day pass, 16 September 2026: arXiv entries against published versions

The department's checklist asks that arXiv preprints be checked for peer-reviewed
published versions and that the official version be cited. Each of the seven arXiv
entries was searched by an agent required to open a DOI landing page before claiming a
published version, and every positive claim was then attacked by two independent refuters
who re-resolved the DOI and compared against the publisher's own citation export.

| Key | Outcome |
|---|---|
| `daian2019flashboys` | **Published.** 2020 IEEE Symposium on Security and Privacy, pp. 910–927, doi:10.1109/SP40000.2020.00040. Both refuters confirmed every field. One "refuted" on the title alone: the camera-ready is *Flash Boys 2.0: Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus Instability*, not the arXiv title. Entry switched to the IEEE version **under the published title**; key kept for cross-reference stability; year now 2020. |
| `lui2025bittensor` | **Published.** In Leonardos S, Goharshady AK, Knottenbelt W, Pardalos P (eds), Mathematical Research for Blockchain Economy (MARBLE 2025), Lecture Notes in Operations Research, Springer, Cham, 2026, pp. 145–165, doi:10.1007/978-3-032-13377-9_7. Both refuters confirmed. Title identical to the arXiv version. Year now 2026. Editor names recorded as initials only, as the publisher gives them. |
| `chitra2023uncertainty` | Preprint only. No journal-ref on arXiv, no DOI landing page found. Stays as arXiv. |
| `gebele2026semantic` | Preprint only. Stays as arXiv. |
| `passeratpalmbach2025dphints` | Preprint only. Stays as arXiv. |
| `nakamura2026privacysubsidy` | Preprint only. Stays as arXiv. |
| `nakamura2026kyle` | Preprint only. Stays as arXiv. |

DOIs: `vancouver.bst` drops the `doi` field silently, so every entry with a DOI now also
carries it in `url`, which the style renders as "Available from: https://doi.org/…". All
nine DOIs render.
