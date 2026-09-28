# Protocol sources and access dates

Every Delphi, Sapience, UMA and Truebit source cited in the report, with the date it was
read. Protocol documentation changes; the report must say when it was true.

All reads were passive. No request was sent to the Sapience relayer, no transaction was
signed, and no capital was committed anywhere.

| Source | URL | Accessed | Used for |
|---|---|---|---|
| Gensyn, Delphi SDK — Methods | `docs.gensyn.ai/tech/delphi-sdk/methods` | 7 Sep 2026 | Settlement-related SDK surface; the automated-settlement/legacy distinction |
| Gensyn, Delphi SDK — Overview | `docs.gensyn.ai/tech/delphi-sdk` | 6 Sep 2026 (Addendum 2) | DPM in production; automated-settlement gateways by default; legacy markets |
| Gensyn, *Building Delphi: Pricing, Settlement, and Agentic Trading* | `gensyn.ai/blog/building-delphi-pricing-settlement-and-agentic-trading` | 4 Sep 2026 | DPM rationale, tiered judge, creator-written settlement prompts |
| Truebit, *Orchestration layer for offchain agents* | `truebit.io/orchestration-layer-for-offchain-agents/` | 6 Sep 2026 | Attested settlement architecture; the stated threat |
| Sapience, Auction Relayer API | `github.com/sapiencexyz/sapience` → `packages/docs/.../builder-guide/api/auction-relayer.mdx` | 7 Sep 2026 | RFQ flow, roles, endpoint, message types |
| Sapience, relayer broadcast handler | `packages/relayer/src/handlers/escrow.ts` | 7 Sep 2026 | Broadcast is to all connected clients |
| Sapience, auction type definitions | `packages/sdk/types/escrow.ts` | 7 Sep 2026 | Exact contents of the broadcast payload |
| UMA, How does UMA's oracle work | `docs.uma.xyz/protocol-overview/how-does-umas-oracle-work` | 7 Sep 2026 | Bonds, challenge window, commit–reveal, 65% threshold |

Repository state at time of reading: `sapiencexyz/sapience`, default branch `main`, last
pushed 6 August 2026, MIT licence.

---

## Finding 1 — the Gensyn–Truebit link is NOT confirmed

`docs.gensyn.ai/tech/delphi-sdk/methods` **does not mention Truebit, a Truebit oracle
relayer, or any oracle relayer.** It exposes `redeemMarket()`, `quoteLiquidate()`,
`liquidate()` and `getMarketStatus()` (statuses `open` / `awaiting_settlement` / `settled`
/ `expired` / `failed`), and refers to "automated-settlement and legacy deployments"
without describing the settlement mechanism or the oracle infrastructure behind it.

**Consequence.** No sentence in the report may link Gensyn to Truebit by name. Use the
wording fixed in `BRIEF.md` §11.1 and nothing stronger.

**The evolution narrative survives intact**, because it never depended on Truebit. Gensyn's
own SDK documentation is sufficient first-party evidence that Delphi moved from an earlier
deployment to automated-settlement gateways, and Truebit's own case study describes the
architecture of an unnamed client. The report presents the third stage as *an* attested
architecture that Truebit documents, not as *Delphi's*, and says explicitly that the
identification is not established.

## Finding 2 — the Sapience broadcast is wider than the research notes recorded

`context/protocol-research-delphi-sapience.md` says the relayer "broadcasts the request to
market makers", and points at `packages/api/src/auction`. **That path no longer exists**;
the relayer is now its own package at `packages/relayer`. The behaviour is also stronger
than "to market makers".

From `packages/relayer/src/handlers/escrow.ts`, the handler context declares:

> `allClients: () => Iterable<ClientConnection>;` — *"All connected clients — used for
> global auction.started broadcast."*

and the broadcast loop is commented *"Broadcast auction.started with auction details to all
connected clients"*, iterating every open connection with no filter, no subscription
requirement and no responder allowlist. The endpoint, `wss://relayer.sapience.xyz/auction`,
is public and documented in the builder guide.

From `packages/sdk/types/escrow.ts`, the broadcast payload `AuctionDetails` carries:

| Field | What it reveals |
|---|---|
| `picks: PickJson[]`, each `{conditionResolver, conditionId, predictedOutcome}` | the **full pick set**, with the predicted direction on **every leg** |
| `predictorCollateral` | the **position size** |
| `predictor` | the forecaster's **address** |
| `predictorNonce`, `predictorDeadline`, `createdAt` | timing |

So the observable action is richer than the model assumed: it is the complete pick set with
per-leg direction, the size, and a **persistent identity**.

### This changes the §2.1 analysis, and Chapter 6 must reflect it

- **Asymmetric access — weakened.** Access is not privileged. Any client that opens a
  WebSocket receives every auction. The asymmetry lies in who connects and who holds
  capital to act, not in protocol permission. The report should say so; it cuts against
  the easiest version of the argument and is more interesting for doing so.
- **Accumulation — strengthened, and now cheap.** `predictor` is in every broadcast, so any
  observer can build a per-forecaster history at zero cost and with no privileged position.
  This is documented protocol behaviour, not an inference. It remains **argued rather than
  demonstrated**, because the simulator's `c` models exposure and not cross-event learning.
- **No priced option not to disclose — confirmed by primary evidence.** The documentation
  states that `intentSignature` is "optional at the protocol level, but vault counterparties
  only respond with actionable bids to signed RFQs. Treat unsigned RFQs as price-discovery
  only." A forecaster who wants a fill must broadcast picks, direction, size and identity in
  full. There is no partial-disclosure path. This is exactly the structural claim §2.1 was
  reformulated to make, and it is now supported rather than asserted.
- **Role-conditional — needs care.** Since the stream is public, the advantage attaches to
  the *capital and infrastructure* to quote on it rather than to a permissioned role. State
  this plainly rather than letting "responder role" do unearned work.

Minor open point, not load-bearing: `intentSignature` is annotated "relayer-only" on
`AuctionRFQPayload` but appears as an optional field on `AuctionDetails`. Whether the
signature is forwarded to observers does not affect the leakage argument, since picks, size
and identity are forwarded regardless.
