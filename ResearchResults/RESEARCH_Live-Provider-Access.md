# Live Provider Access Record

*Observed against authenticated YouVersion Platform and Gloo AI Studio accounts on 2026-07-19. No credential values are recorded here.*

## Outcome

Both required challenge providers are usable from server-side code:

- YouVersion application `Corvus` exists in **In Development** status and a live passage request succeeded.
- Gloo OAuth2 credentials exist and both token exchange and a live Responses API request succeeded.
- Local credential material is stored in the macOS Keychain, not in the repository.

The local Keychain service identifiers are:

- `Corvus-YouVersion-App-Key`
- `Corvus-Gloo-Client-ID`
- `Corvus-Gloo-Client-Secret`

Deployment must copy these values into the hosting provider secret manager. The local Keychain is not a production credential store.

## YouVersion Platform

### Account and application

- Application name: `Corvus`
- Description: `Intelligent theological responses for language models.`
- Status: `In Development`
- App registration required the account owner to confirm that the application is non-commercial and free, contains no paywalled material, and runs no advertising around the YouVersion-integrated experience.
- No publisher fast-track Bible licence has been accepted.

### Authentication and live checks

- Base API: `https://api.youversion.com/v1`
- Authentication header: `X-YVP-App-Key`
- `GET /bibles/3034/passages/JHN.3.16` returned HTTP `200` with `id`, `content`, and `reference`; the reference was `John 3:16`.
- An invalid passage returned HTTP `404` with a top-level `message` string.
- A missing required query parameter returned HTTP `422` with a top-level `detail` array.
- An invalid page size returned HTTP `400` with a top-level `message` string.
- Responses exposed an `x-request-id` but no numeric rate-limit headers.

### Currently available English collection

`GET /bibles` requires at least one `language_ranges[]` query value. The observed endpoint enforces `page_size` from 1 through 99, despite the overview documentation saying requests may generally contain up to 100 items.

With `language_ranges[]=en&page_size=99`, the development application returned 11 English Bibles and no next-page token:

| ID | Abbreviation | Title |
| ---: | --- | --- |
| 12 | ASV | American Standard Version |
| 42 | CPDV | Catholic Public Domain Version |
| 2163 | enggnv | Geneva Bible |
| 130 | TOJB2011 | The Orthodox Jewish Bible |
| 2660 | LSV | Literal Standard Version |
| 3034 | BSB | Berean Standard Bible |
| 1207 | WMBBE | World Messianic Bible British Edition |
| 1209 | WMB | World Messianic Bible |
| 3427 | TCENT | The Text-Critical English New Testament |
| 1932 | FBV | Free Bible Version |
| 206 | engWEBUS | World English Bible, American English Edition, without Strong's Numbers |

The portal separately offers fast-track publisher agreements, including Biblica editions such as NIV and Lockman editions such as NASB. Those are not part of current access and must not be used until the account owner separately reviews and accepts their agreements.

### Rate and content handling boundary

YouVersion states that challenge access is rate-limited and that applications can request larger limits through **Make Live**. No numeric development quota was displayed or returned in response headers.

Until a specific version licence has been reviewed, implementation must treat Scripture display text as non-persistable: retrieve it server-side, retain it only for the active request, and keep durable caches limited to identifiers and non-content metadata. Version-specific cache and display rules belong in source-registry policy rather than application-wide assumptions.

Primary references: [YouVersion API Usage](https://developers.youversion.com/api-usage), [YouVersion Platform](https://platform.youversion.com/).

## Gloo AI Studio

### Authentication and live checks

- OAuth token endpoint: `POST https://platform.ai.gloo.com/oauth2/token`
- Flow: OAuth2 client credentials with scope `api/access`
- Successful token response: HTTP `200`, bearer token, `expires_in` 3600 seconds
- Recommended inference endpoint: `POST https://platform.ai.gloo.com/ai/v1/responses`
- Live request with `gloo-openai-gpt-5-mini`: HTTP `200`
- Observed response contained one message output and usage of 19 input, 64 output, and 83 total tokens.
- The Studio Usage page recorded the request and displayed a flat 6.5% Studio markup over model list prices.
- A request without authorization returned HTTP `401` with `{ "error": "Missing Authorization", "code": "unauthorized_missing_authorization" }`.
- No numeric rate-limit headers were observed.

### Available surface

The public model catalog is served by `GET /platform/v2/models`. The catalog includes current OpenAI families such as GPT-5.4, GPT-5.5, and GPT-5.6, as well as Anthropic, Google, and open-source models. The catalog marks model capabilities including tools, streaming, reasoning, vision, context size, and list pricing.

The Responses API is OpenAI-compatible. Gloo also documents Completions V2 for routing, values-aligned `tradition` responses, and grounded/RAG completions. The product architecture still treats Gloo output as structured analysis rather than provenance: every visible theological claim must resolve to Scripture or an admitted Tradition source.

### Billing and challenge credit

- The account is active on Pay As You Go and accepted a live request.
- Studio documents payment activation and a weekly spend limit for Pay As You Go.
- The challenge page advertises $20 credit for the first 500 participants, but the account UI did not establish whether that credit has been applied.
- The test request displayed total spend as `$0.00` at the observed precision.

Primary references: [Gloo developer quickstart](https://docs.gloo.com/getting-started/quickstart-developers), [Gloo supported models](https://docs.gloo.com/api-guides/supported-models), [Gloo challenge](https://studio.ai.gloo.com/challenge).

## Implementation consequences

1. Use a server-side YouVersion REST adapter and a server-side Gloo OAuth client; never expose either credential set to the Apps SDK component or ChatGPT tool result.
2. Refresh Gloo access tokens before their one-hour expiry and coalesce concurrent refreshes.
3. Model provider status and error shape explicitly; neither provider exposed numeric rate-limit headers during the live checks.
4. Begin development with the 11 currently available English versions. Treat additional publisher editions as a separately reviewed expansion.
5. Default to no persistent Scripture-text caching until the selected version policy proves it is allowed.
6. Preserve provider request identifiers in content-free operational telemetry where available.
7. Verify challenge credit and production limits before load testing or public launch.
