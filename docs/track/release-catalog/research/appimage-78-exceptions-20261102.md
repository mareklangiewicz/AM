# The 78 frozen AppImage exceptions — offline classification

Research on November 2, 2026. No network requests, recipe changes or new collection were performed for this classification. Counts refer only to the frozen thousand-recipe queue; the separate eight redirect leftovers from the earlier 124-recipe queue are excluded.

## Findings

| Cause | Source identities | Recipe paths | Evidence needed next |
| --- | ---: | ---: | --- |
| HTTP 301 identity | 59 | 65 | Verify numeric destination and exact public identity, then bounded release body; one destination already has saved accepted evidence |
| HTTP 404 identity | 2 | 4 | No accepted destination; preserve recipes until an explicit replacement source is established |
| Oversized release response | 1 | 1 | New bounded descriptor, not a cap increase or retry of the refused response |
| Original selector absent from returned asset set | 5 | 8 | Policy/availability decisions described below; no mechanical safe replacement established |

Primary input: [frozen exceptions](appimage-next-large-batch-20261102/prepared/migration.json), [original selectors/fingerprints](appimage-next-large-batch-20261102/payload.json), and [portable original acquisition archive](appimage-next-large-batch-20261102/evidence.tar.gz). The archive contains the named `identity-NNNN` / `release-NNNN` directories below, each with exact body, headers and report. Ignored local copies under `appimage-next-large-batch-20261102/live/` were used read-only. The source decision rule is [large_migration.py](../../../../tools/catalog-collector/large_migration.py).

## Redirect destinations and exact recipe paths

Each destination is an observed 301 Location, not an accepted new public identity by itself. Preserve the literal old alias when enrollment is reviewed; do not normalize aliases silently. Numeric destination identity GET and its release GET are separate requests with redirects and retries disabled. The exact original endpoint suffix (`/releases` or `/releases/latest`) must be preserved.

| Original alias (`https://api.github.com/repos/…`) | Numeric destination | Recipe paths (`programs/…`) | Original evidence member |
| --- | --- | --- | --- |
| `afadil/wealthfolio/releases` | `806618581` | `x86_64/wealthfolio`, `aarch64/wealthfolio` | `identity-0004` |
| `akhial/shpd-seed-seeker/releases` | `1295884869` | `x86_64/shpd-seed-seeker`, `aarch64/shpd-seed-seeker` | `identity-0005` |
| `fathom-media/fathom/releases` | `1310170482` | `x86_64/fathom`, `aarch64/fathom` | `identity-0057` |
| `streetpea/chiaki4deck/releases` | `526448037` | `x86_64/chiaki4deck`, `aarch64/chiaki4deck` | `identity-0211` |
| `trevorbayless/cli-chess/releases` | `332327422` | `x86_64/cli-chess`, `aarch64/cli-chess` | `identity-0225` |
| `ydmy007/fntv-plus/releases` | `1362367741` | `x86_64/fntv-plus`, `aarch64/fntv-plus` | `identity-0249` |
| `9mtm/dpro-agent/releases` | `993148803` | `x86_64/dpro-agent` | `identity-0322` |
| `AkashaProject/Community/releases` | `115051437` | `x86_64/akasha` | `identity-0331` |
| `All-Hands-AI/OpenHands/releases` | `771302083` | `x86_64/openhands` | `identity-0335` |
| `AppImage/NCSA-Mosaic-AppImage/releases` | `88671738` | `x86_64/ncsa-mosaic` | `identity-0338` |
| `ArtBelll/school-sections/releases` | `147951266` | `x86_64/school-sections` | `identity-0346` |
| `Bwc9876/ow-mod-man/releases` | `592635586` | `x86_64/outer-wilds-mod-manager` | `identity-0372` |
| `Bytespeicher/BytespeicherTrayIcon/releases` | `98292273` | `x86_64/bytespeichertrayicon` | `identity-0373` |
| `CAU-Kiel-Tech-Inf/socha-gui/releases` | `154306755` | `x86_64/software-challenge-gui` | `identity-0375` |
| `ChatGPTNextWeb/ChatGPT-Next-Web/releases` | `612344730` | `x86_64/chatgpt-next-web` | `identity-0380` |
| `ChungZH/notepanda/releases` | `258935245` | `x86_64/notepanda` | `identity-0383` |
| `Cloud-V/Malice/releases` | `93928747` | `x86_64/malice` | `identity-0386` |
| `Cuperino/QPrompt/releases` | `306907376` | `x86_64/qprompt` | `identity-0396` |
| `DATL4G/BurningSeries-Android/releases` | `426737899` | `x86_64/burning-series` | `identity-0398` |
| `DamirPorobic/ksnip/releases` | `64607359` | `x86_64/ksnip` | `identity-0400` |
| `Dummerle/Rare/releases` | `310661703` | `x86_64/rare` | `identity-0408` |
| `ElyPrismLauncher/ElyPrismLauncher/releases` | `561202233` | `x86_64/elyprismlauncher` | `identity-0417` |
| `EricTurf/osrs-tools/releases` | `171335100` | `x86_64/osrs-tools` | `identity-0419` |
| `Fantasy-programming/Onlyrefs/releases` | `754078855` | `x86_64/onlyrefs` | `identity-0426` |
| `ForgQi/biliup-app/releases` | `192654884` | `x86_64/biliup-app` | `identity-0432` |
| `ItzSwirlz/iheartradio-webapp/releases/latest` | `319694314` | `x86_64/iheartradio-webapp` | `identity-0470` |
| `K3vinb5/Unyo/releases` | `776821095` | `x86_64/unyo` | `identity-0487` |
| `KRTirtho/spotube/releases` | `338719962` | `x86_64/spotube` | `identity-0488` |
| `KRTirtho/wives/releases` | `504444581` | `x86_64/wives` | `identity-0489` |
| `KeitIG/museeks/releases` | `31598574` | `x86_64/museeks` | `identity-0492` |
| `KhushrajRathod/TeleDrive/releases` | `283761791` | `x86_64/teledrive` | `identity-0493` |
| `Kthulu120/mangle/releases` | `118871400` | `x86_64/cryplicity` | `identity-0498` |
| `KurozeroPB/CustomRPC/releases` | `124373138` | `x86_64/customrpc` | `identity-0500` |
| `KurtPfeifle/htmldoc/releases` | `118270386` | `x86_64/htmldoc` | `identity-0501` |
| `KurtPfeifle/rasterview/releases` | `118181355` | `x86_64/rasterview` | `identity-0502` |
| `Lateralus138/unishellectv2/releases` | `533930478` | `x86_64/unishellect` | `identity-0517` |
| `LightningPeach/lightning-peach-wallet/releases` | `134248241` | `x86_64/lightning-peach-wallet` | `identity-0528` |
| `MainframeHQ/onyx/releases` | `110005052` | `x86_64/onyx` | `identity-0537` |
| `Master0fFate/pi-fategui/releases` | `1309373203` | `x86_64/pi-fategui` | `identity-0541` |
| `Mindmapp/mindmapp/releases` | `103155188` | `x86_64/mindmapp` | `identity-0550` |
| `NiewidzialnyCzlowiek/pubsub-webapp/releases` | `155561509` | `x86_64/twetter` | `identity-0559` |
| `ORB-HD/rbdl-toolkit/releases` | `183447712` | `x86_64/rbdl-toolkit` | `identity-0565` |
| `PabloF7/noter/releases` | `146669084` | `x86_64/noter` | `identity-0586` |
| `PowerBall253/EternalModManager-Avalonia/releases` | `489052641` | `x86_64/eternalmodmanager` | `identity-0603` |
| `Rapiz1/DungeonRush/releases` | `242162049` | `x86_64/dungeonrush` | `identity-0610` |
| `Samueru-sama/pavucontrol-qt-AppImage/releases/latest` | `805270353` | `x86_64/pavucontrol-qt` | `identity-0625` |
| `Samueru-sama/rofi-AppImage/releases` | `789428801` | `x86_64/rofi` | `identity-0626` |
| `Samueru-sama/strawberry-AppImage/releases/latest` | `887563299` | `x86_64/strawberry` | `identity-0628` |
| `Subsurface-divelog/subsurface/releases` | `2319498` | `x86_64/subsurface` | `identity-0646` |
| `Superjo149/auryo/releases` | `73500678` | `x86_64/auryo` | `identity-0648` |
| `Supermegadex/libassist-client/releases` | `152028144` | `x86_64/libassist` | `identity-0649` |
| `TheFutureShell/updatedeployqt/releases` | `173540223` | `x86_64/updatedeployqt` | `identity-0657` |
| `VinnyVynce/wxMEdit.AppImage/releases` | `247178970` | `x86_64/wxmedit` | `identity-0669` |
| `WayzDev/Kage/releases` | `157828507` | `x86_64/kage` | `identity-0679` |
| `WesterosCraftCode/ElectronLauncher/releases` | `183921740` | `x86_64/westeroscraftlauncher` | `identity-0682` |
| `Wooyme/Wsocks/releases` | `161272220` | `x86_64/wsocks` | `identity-0686` |
| `Xstoudi/alduin/releases` | `71763543` | `x86_64/alduin` | `identity-0689` |
| `aceeee2077/booloo/releases` | `1348439612` | `x86_64/booloo` | `identity-0704` |
| `adil192/saber/releases` | `516598834` | `x86_64/saber` | `identity-0708` |

### Saved-evidence reuse: fntv-plus

The `ydmy007/fntv-plus` 301 Location is repository `1362367741`. That exact numeric ID already has accepted public identity evidence under `fnosp/anibox` in archive member `identity-0063`, and accepted release evidence in `release-0063` (`https://api.github.com/repositories/1362367741/releases`). Both frozen selectors were executed read-only against that exact saved body and both install/update results match returned `browser_download_url` assets:

- `programs/x86_64/fntv-plus`: `https://github.com/FNOSP/AniBox/releases/download/v4.1.0/AniBox_4.1.0_amd64.AppImage`.
- `programs/aarch64/fntv-plus`: `https://github.com/FNOSP/AniBox/releases/download/v3.9.0/Fntv-Plus_3.9.0_arm64.AppImage`.

This can prepare two recipe candidates without new metadata GETs. It still needs explicit alias enrollment and acceptance before delivery; the accepted anibox descriptor currently does not establish the old fntv-plus consumer alias. This is the only redirect destination found among the already accepted identity IDs in the thousand-queue acquisition summary. The other 58 destinations have no accepted identity/release evidence in this archive.

## Nonredirect cases

| Exact recipe paths | Cause and saved primary evidence | Next safe step |
| --- | --- | --- |
| `programs/x86_64/chatboxai`, `programs/aarch64/chatboxai` | Both selectors choose external release-note URLs on download.chatboxai.app (1.23.1), absent from returned asset set; older 1.20.3 GitHub AppImage assets exist (`release-0028`) | Keep original version/hosting policy; using older GitHub assets is a behavior change. Explicit external-link acceptance would need a reviewed metadata contract. |
| `programs/x86_64/opengeni`, `programs/aarch64/opengeni` | Both selectors empty; no AppImage-named assets in saved first 30 releases (agent/runtime/candidate releases) (`release-0035`) | Find an explicit first-party AppImage release policy or retain unsupported paths; no blind pagination/latest substitution. |
| `programs/x86_64/deepseek-harness-code`, `programs/aarch64/deepseek-harness-code` | HTTP 404 identity; no numeric destination accepted (`identity-0037`) | Preserve paths; source replacement requires separate first-party evidence. |
| `programs/x86_64/zkas-wallet`, `programs/aarch64/zkas-wallet` | HTTP 404 identity; no numeric destination accepted (`identity-0061`) | Preserve paths; source replacement requires separate first-party evidence. |
| `programs/x86_64/fizzy`, `programs/aarch64/fizzy` | Both selectors empty; no AppImage-named assets in saved first 30 releases (SDK/dependency cache releases) (`release-0062`) | Find an explicit first-party AppImage release policy or retain unsupported paths. |
| `programs/aarch64/pioneer` | ARM selector empty; saved releases contain x86_64 AppImages only (`release-0146`) | Retain ARM path; x86 asset selection cannot establish ARM compatibility. |
| `programs/aarch64/libation` | ARM selector empty; saved releases contain x86_64 AppImages only (`release-0154`) | Retain ARM path; x86 asset selection cannot establish ARM compatibility. |
| `programs/x86_64/vscodium` | HTTP 200 advertised Content-Length 8,880,492; curl exit 63, zero body bytes, refused against unchanged 8,000,000-byte bound (`release-0669`) | Review a smaller page/latest descriptor and alias policy; do not raise the cap or treat empty body as metadata. |

## Bounded acquisition implication

Largest straightforward follow-up is the 58 destinations without saved accepted identities: at most 58 exact numeric public-identity GETs plus one release GET per accepted identity, preserving endpoint suffixes. This is a proposed upper bound, not an instruction to retry, follow redirects or accept failed identities. The already saved fntv-plus destination can be excluded. Identity/public/private/fork-owner checks and repository-ID binding must be explicit. Capture original reports and headers without credentials. Stop on quota/missing-quota evidence as in the previous acquisition. A redirect to another destination, release body overflow or absent selector remains an exception rather than a reason to relax policy.

The two 404 identities are not proven deleted: unauthenticated/public availability and the recorded HTTP result are all that the evidence establishes. The saved release lists are finite snapshots; absence in a returned page does not prove no historical AppImage ever existed. No binary URL was fetched or executed.
