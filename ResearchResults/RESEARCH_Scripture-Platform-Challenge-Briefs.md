# Scripture Platform Challenge Briefs

*Primary-source research, accessed 2026-07-19. This note separates publisher-stated facts from implementation inferences and records material access limits.*

## Executive synthesis

The **Scripture in New Frontiers** challenge asks builders to place Scripture in digital contexts where it is native to the experience (the examples are games, wearables, social platforms, and creator tools). The public Gloo brief makes the core technical constraint unusually clear: **both the YouVersion Platform API and Gloo AI Studio API must be meaningfully integrated**. It also requires an open-source submission, final demo, and write-up. [Gloo challenge brief](https://studio.ai.gloo.com/challenge)

The technical division of responsibility is likewise clear from the two first-party pages: YouVersion supplies authenticated access to Bible-platform content through SDKs or a REST API; Gloo supplies its faith-context AI offering. **Inference:** a competitive proposal needs a visibly real, non-token use of each integration, rather than an application that merely displays a verse beside generic AI output. This follows from the published technical-depth criterion and the requirement that both APIs be meaningful. [YouVersion API usage](https://developers.youversion.com/api-usage) · [Gloo challenge brief](https://studio.ai.gloo.com/challenge)

## 1. YouVersion Platform — documented integration facts

| Topic | Verified fact | Decision input |
| --- | --- | --- |
| Access model | A developer must create an account and register an application to obtain an App Key. Every API request requires that key in the `X-YVP-App-Key` header. | Registration/key provisioning is an early dependency; do not put the key in a client application or repository. |
| API choices | YouVersion provides SDKs for several languages and a REST API that exposes the same services. The docs position REST for custom integrations, content-workflow automation, and platforms lacking an SDK. | Choose an SDK only if its supported platform fits; otherwise plan a server-side REST integration. |
| Scripture retrieval | The documented REST example fetches John 3:16 from BSB through `GET /v1/bibles/3034/passages/JHN.3.16`. The passages API is the route for verse, passage, and chapter text. | Make scripture selection, retrieval, and rendering a demonstrable product flow. |
| Licensing/availability | Bible versions are listed through a Bible collection only after the relevant licence agreements have been accepted. | Version availability is not universal; select translation(s) after licensing/collection access is confirmed. |
| Discovery and scale | Other routes expose Bible book, chapter, and verse metadata. Some endpoints paginate with `page_size`/`page_token`, normally up to 100 items per page, returning `next_page_token`. | Design content browsing/import flows for paging; do not assume an unbounded list response. |

Source for every row: [YouVersion, “API Usage”](https://developers.youversion.com/api-usage).

### Reproducible access check

On 2026-07-19, an unauthenticated request to the documentation's sample passage URL returned HTTP `401` with an API-key-resolution error. This independently confirms that usable production retrieval is key-gated; it does **not** test behavior for a registered application. The corresponding first-party route reference is the [Bible API reference](https://developers.youversion.com/api/bibles).

## 2. Gloo AI Studio challenge brief — verified constraints

### Product direction

- The stated purpose is a global virtual developer challenge to integrate Scripture thoughtfully into emerging digital environments. The named frontiers are gaming, creator tools, wearables, developer IDEs, fitness apps, and social platforms; the page says these are invitations rather than requirements. [Gloo challenge brief](https://studio.ai.gloo.com/challenge)
- The public page describes the YouVersion side as Scripture texts, reading plans, highlights, verse of the day, and community data, and the Gloo side as faith-tuned inference, content generation/personalization, safety infrastructure, and spiritual-formation context. These are sponsor descriptions, not independently tested API guarantees. [Gloo challenge brief](https://studio.ai.gloo.com/challenge)

### Non-negotiable participation/submission constraints

- Both APIs must be **meaningfully integrated**.
- Individual developers and teams of up to four may participate.
- All submissions must be open sourced.
- By the stated submission close, a final demo, write-up, and open-source repository are required.
- The YouVersion API/SDK is offered free to participants **with rate limits**; Gloo offers **$20 credit to the first 500 participants**.

Source: [Gloo challenge brief](https://studio.ai.gloo.com/challenge).

### Rubric (100 points)

| Weight | Criterion | What the organizers say they assess |
| ---: | --- | --- |
| 40 | Impact & Vision | A real problem, meaningful and potentially transformative Scripture integration, an inspiring vision, and potential scale. |
| 30 | Video Pitch & Storytelling | A compelling story/product demonstration with a real-feeling user experience and potential to travel widely. |
| 30 | Technical Depth & Execution | Code and write-up must show innovative, functional, well-engineered use of both APIs—not a demo-only fake. |

Source: [Gloo challenge brief](https://studio.ai.gloo.com/challenge).

### Timeline published by Gloo

| Date | Milestone |
| --- | --- |
| 2026-06-29 | Information session |
| 2026-07-06 | Challenge opens; registration, API access, and starter resources go live |
| 2026-07-06–31 | Build period; office hours, community forums, and mentors |
| 2026-07-31 | Submissions close |
| 2026-08-03–07 | Judging |

Source: [Gloo challenge brief](https://studio.ai.gloo.com/challenge). **Time-sensitive:** this is the sponsor-published schedule observed on 2026-07-19, not a guarantee that deadlines will remain unchanged.

## 3. Kaggle competition — verified Overview and Rules

Kaggle identifies this as the **“Scripture in New Frontiers” Community Hackathon** and repeats the product brief: build Scripture natively into games, wearables, social platforms, creator tools, or another emerging context using the YouVersion Platform and Gloo AI Studio APIs. The competition provides no sponsor dataset. [Kaggle Overview](https://www.kaggle.com/competitions/scripture-in-new-frontiers) · [Kaggle Rules](https://www.kaggle.com/competitions/scripture-in-new-frontiers/rules)

### Submission package

A valid final submission is a submitted (not draft) Kaggle Writeup with:

- a media gallery and required cover image;
- a public notebook/code artifact that does not require a login or paywall;
- a public YouTube video of no more than three minutes;
- a public working-product or interactive-demo link, or, when that is infeasible, a public code repository with detailed setup instructions.

The Writeup is capped at 500 words and should explain the architecture, both API integrations, challenges, and technical choices. The Overview calls the public code repository “non-negotiable” and says code will be reviewed to verify that the demo reflects working technology. [Kaggle Overview](https://www.kaggle.com/competitions/scripture-in-new-frontiers)

### Prize and judging

There is one track and one **$10,000 cash prize** for the best submission. The scoring weights match Gloo’s page: Impact & Vision 40, Video Pitch & Storytelling 30, and Technical Depth & Execution 30. Kaggle emphasizes that the video is the primary judging lens while the write-up and code establish authenticity and engineering depth. [Kaggle Overview](https://www.kaggle.com/competitions/scripture-in-new-frontiers)

### Competition-specific legal and participation terms

- Kaggle’s competition-specific rules state a maximum team size of **five** and allow only **one submission per team**.
- The competition supplies no competition data. External data, models, and tools are allowed when they are publicly/equally accessible at no cost or satisfy Kaggle’s reasonable-access/minimal-cost criteria.
- The competition is generally open worldwide, excluding the territories and persons barred by the listed U.S. sanctions/export-control rules. Sponsor/Kaggle employees and related personnel may participate but cannot win.
- A winner must license the winning submission and its source code under an OSI-approved license that does not restrict commercial use, subject to exceptions for procurable third-party software and incompatible input-data/pretrained-model licences. Reproducible documentation and complete setup instructions may be required.
- Taxes are the winner’s responsibility; a team’s monetary prize is normally divided evenly unless all eligible team members agree otherwise before payout.

Source: [Kaggle Rules](https://www.kaggle.com/competitions/scripture-in-new-frontiers/rules).

### Material discrepancy and drafting defect

The Gloo challenge page says teams may contain **up to four**, while Kaggle’s competition-specific rules say **up to five**. Plan conservatively for four unless the organizers clarify which limit controls. The Rules page also currently displays the sponsor address as `[INSERT]`, suggesting the legal template was not fully completed when inspected on 2026-07-19. These are source defects worth recording, not resolving by inference. [Gloo challenge brief](https://studio.ai.gloo.com/challenge) · [Kaggle Rules](https://www.kaggle.com/competitions/scripture-in-new-frontiers/rules)

## Recommended decision inputs

1. **Resolve the team-size conflict before forming a five-person team.** Four satisfies both published limits; five relies on Kaggle’s rules prevailing over Gloo’s public brief.
2. **Treat dual integration as an architecture requirement.** Allocate a concrete user-facing responsibility to each API and preserve evidence of it for the code, write-up, and video.
3. **Make the demo/video a first-class deliverable.** It is 30% of the stated score, equal to technical execution.
4. **De-risk access immediately:** developer registration/App Key, relevant Bible-version licences/collection access, and Gloo credit/rate-limit headroom. The last two constraints can directly determine which experience is feasible.

## Sources

- [YouVersion Platform Developer Docs — API Usage](https://developers.youversion.com/api-usage)
- [YouVersion Platform Developer Docs — Bible API reference](https://developers.youversion.com/api/bibles)
- [Gloo AI Studio — Challenge](https://studio.ai.gloo.com/challenge)
- [Kaggle — Scripture in New Frontiers](https://www.kaggle.com/competitions/scripture-in-new-frontiers)
- [Kaggle — Scripture in New Frontiers Rules](https://www.kaggle.com/competitions/scripture-in-new-frontiers/rules)
