# Next-ten pinned-source/runtime preparation

Ticket [135](../issues/135-prepare-next-ten-existing-recipes.md), November 6, 2026.
All 22 screened existing recipes remain byte-identical to upstream Git objects at
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22`. The maintained Catalogue classifier
recognizes whole templates and reconstructs each byte-for-byte from original Git
template objects; repeated app/repository/FUNCTION captures agree. No source
recipe is executed during recognition.

The following source gates are independent of payload readiness. `agent-desktop`,
`agent-launcher`, `agent-pulse` and `agent-smith` use generic download selectors
without an AppImage suffix. Their exact full-response winner must be a unique
direct AppImage before raw-layout conversion. `affinity` uses the R35 selector
without armhf exclusion; current shared name-based architecture rules remain
explicit policy rather than unconditional legacy parity. All original templates
strip the literal no-sandbox substring, so passing recipes need explicit
`DESKTOP_STRIP_NO_SANDBOX=true` and actual inert desktop transformation comparison.

Shared runtime and policy contracts remain those reviewed in
[the preceding batch](large-batch-runtime-review.md). Require one visible logical
root desktop, no actions, supported internal desktop/icon links, complete static
listing, nonempty icon and matching published/computed full-payload SHA-256.
Reject absolute build-host links, distinct additional desktops, missing Exec,
ambiguous archive/sidecar winners and payloads beyond the fixed budgets. Existing
installed ownership/remover responsibilities remain outside source conversion.
Publication/name ordering, retained structured facts, ordinary freshness and
direct acquisition intentionally follow the shared policy; saved URL equality
does not establish all-history semantic equivalence.

| Recipe | Pinned repository | Source SHA-256 |
| --- | --- | --- |
| aevum | `alonera/aevum` | `3f818b587727f1983ab78f0fa878c188b60a67eca5a15970b792de9ea4b535da` |
| affinity | `ryzendew/Linux-Affinity-Installer` | `5e19aecb783a33b05e69d4d48ad4023af41c08767fd01dadaf33a0d7fa051302` |
| afsplug | `zhangxianhe666/afsplug` | `9f4d6ed202cfe0770c660dd5ed054d778cdcb27f9914c07ab444ef11d7caa435` |
| ag-repatch | `etosheartem/ag-repatch` | `a0c0141928187ca079c71b457f02930c8861581910f4c68fbea7b314c3cd7f51` |
| agaric | `jfolcini/agaric` | `cd8e203fc209d384cea05a6601af1e1f973a25c0bde093336e4bc4f24d3ae49f` |
| ageha-editor | `itsuki-maru/ageha-editor` | `35d45b481816dadbf3ffe15657181b5fd081b05ad5d4ee1948811612d0142652` |
| agency | `tennnisai/agency` | `d022d043ef5f4af1fa1f51d3a0dee251256f8142cc693e634ae94cff38d61faa` |
| agency-agents-app | `msitarzewski/agency-agents-app` | `fad3b084adfd7ffc4bed054f670f726ae22056e81d77b87d7c15823720d1cfcc` |
| agent-arcade | `danwahlin/agent-arcade` | `607475960c18748296cf980264bafe49e032ed7590f49446a8bb27f4294f21ba` |
| agent-buddy | `danwahlin/agent-buddy` | `686a92ebdf09a81e910b64a4ba6d11db3b33a2794d9cf5f1202a52f2b56acb64` |
| agent-comm-hub | `jochenyang/agent-comm-hub` | `1df98174139550754183eb5b41ac2160709b766b8e7e119486b3ae6767e05420` |
| agent-desktop | `balaurent/agent-desktop` | `ebe88da0e35672612d7d878043e2868f545f0a533eca98dc92e11f1b635cad94` |
| agent-launcher | `agent-launch/agent-launcher` | `904332917cecd5863d58d3ebfc5a3a1b4915e117856561dfe120aefa0359168b` |
| agent-loom | `alpha-coders/agent-loom` | `6a7c3fec49d73dd2f47d7e1a75608f15680a34c4af99fba856b6ae2a5536e252` |
| agent-orchestrator | `untrivial-ai/agent-orchestrator` | `e68c772d1c2c1a235f5128f8bda99a43f3647980c34a74047944b05ad78baa8c` |
| agent-os | `desirecore/agent-os` | `be5de065e36cb21345fb036b5c6f55e539df2a92dbfec7884ea66b23ae2c5d16` |
| agent-pulse | `dipen-dedania/agent-pulse` | `b271382a46eb8bc3f4b0606710108f967ca1c99287846feac466ba30b0ee9fe7` |
| agent-skills | `chrlsio/agent-skills` | `a4f25b4d40ff1660dbad92028ee870f3a09ffc9d837587efb82148b168461cb7` |
| agent-smith | `ghostwrk/agent-smith` | `518fd8d9245b68b7f222b004e5a7bac477c59c3cd52c358239035842951c1def` |
| agent-switchboard | `y4nkk/agent-switchboard` | `03a8dcb3d3f092980126b8ac1459660a33ecd4b4cabc99e67018d6bc27e2cb03` |
| agent-teams-ai | `777genius/agent-teams-ai` | `44ceeede96ccb9e4570887c5b0ca81789a732654c67ab9b1f9fdc49ca6218056` |
| agent-toolkit | `ulises-jeremias/agent-toolkit` | `422cd9c94d5e725718610867f5784d7d2811a305f209123b62ee47a13fccf195` |

The actual candidates, first-party API hashes, exact selectors, full payload
receipts and compatibility results are recorded by the next-ten evidence/report.
These source findings alone authorize no payload execution, install or live change.
