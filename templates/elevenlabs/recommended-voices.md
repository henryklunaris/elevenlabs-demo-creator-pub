# ElevenLabs Recommended Voices for Conversational AI

Best voices for low-latency conversational agents. Find more with `python3 scripts/el.py shared-voices --search "..."`.

## Top Female Voices

| Name | Voice ID | Profile | Best For |
|------|----------|---------|----------|
| Karen | `AGYozmgYT0SJVnLKg7iN` | Warm, professional, North American | Customer service, appointment booking |
| Liz | `uMM5TEnpKKgD758knVJO` | Friendly, clear, American | Lead qualification, general purpose |
| Ashley | `HKLuhpJqOsByvuQFiWBe` | Approachable, upbeat, American | Sales, outbound, friendly CS |
| Eryn | `DXFkLCBUTmvXpp2QwZjA` | Calm, composed, neutral American | Healthcare, professional services |
| Steffy | `bm3QvaZ3fUSCRBC3UV1f` | Energetic, youthful, American | E-commerce, tech, startups |
| Emma | `56bWURjYFHyYyVf490Dp` | Professional, Australian | APAC businesses, Australian clients, car/fleet |

## Top Male Voices

| Name | Voice ID | Profile | Best For |
|------|----------|---------|----------|
| Adrian Ashford | `bqnMEfPMfAsV6leYpGPD` | Polished, British | Luxury brands, consulting, finance |
| Joseph | `8fcyCHOzlKDlxh1InJSf` | Warm, trustworthy, American | Insurance, real estate, home services |
| Stephen | `6YQMyaUWlj0VX652cY1C` | Professional, authoritative, American | Legal, enterprise, B2B |
| Frederick Surrey | `KLON7Nwan8mJxpF2R8Yw` | Distinguished, British | Premium services, hospitality |

## Extended v2 Voice List

### English

| Name | Voice ID | Profile | Best For |
|------|----------|---------|----------|
| Sam | `scOwDtmlUjD3prqpp97I` | Male | General purpose |
| Jessica | `cgSgspJ2msm6clMCkdW9` | Female | General purpose |
| Arabella | `Z3R5wn05IrDiVCyEkUrK` | Female | General purpose |
| Eve | `BZgkqPqms7Kj9ulSkVzn` | Female | General purpose |
| Joanne | `37QJ59oEiWxc5ZUUeu16` | Female | General purpose |
| Carter the Mountain King | `qNkzaJoHLLdpvgh5tISm` | Male, deep | Character, unique branding |
| Tom | `DYkrAHD8iwork3YSUBbs` | Male, Australian | APAC businesses, casual |
| Monika | `2zRM7PkgwBPiau2jvVXc` | Female, Indian accent | Indian market businesses |
| Viraj | `P1bg08DkjqiVEzOn76yG` | Male, Hindi | Hindi-speaking clients |

### Multilingual / Non-English

| Name | Voice ID | Language | Best For |
|------|----------|----------|----------|
| Arabella (multilingual) | `aEO01A4wXwd1O8GPgGlF` | Best multilingual pick | Multi-language deployments |
| Leoni Vergara | `pBZVCk298iJlHAcHQwLr` | Multi-language | International businesses |
| Ceilian | `DGTOOUoGpoP6UZ9uSWfA` | French | French market |
| Sara Martin | `gD1IexrzCvsXPHUuT0s3` | Spanish | Spanish market |
| Iris | `9ebwxABSgElm9wISOP0J` | Spanish | Spanish market |
| Jhenny | `2Lb1en5ujrODDIqmp7F3` | Colombian Spanish | Latin American market |
| Ava | `AnvlJBAqSLDzEevYr9Ap` | German | German market |
| Peter | `fmj9wTxZg3ta4xR75kgB` | German | German market |
| Ela | `NE7AIW5DoJ7lUosXV2KR` | German | German market |
| Laura | `zKHQdbB8oaQ7roNTiDTK` | German | German market |
| Stefan Rank | `c9tXABmaj4sESRRQ4Uqo` | German | German market |
| Keon | `jfwdd64Nlhnj6vcFqRHZ` | Dutch | Dutch market |

## Model Compatibility

- **`eleven_v4_turbo`**: Default. Eleven v4 for real-time, ~100ms, ~87 languages.
- **`eleven_flash_v2_5`**: Fastest (~75ms), 32 languages. Good fallback if a voice sounds off on v4.
- **`eleven_v3_conversational`**: Expressive mode and audio tags, ~280ms.
- **`eleven_multilingual_v2`**: Still supported, slower.
- ~~`eleven_turbo_v2_5`~~ / ~~`eleven_turbo_v2`~~: Deprecated, use flash v2.5.
- `eleven_v4` (non-turbo) is for content/dialogue, not agents.

## Notes

- Voices above were tested on `eleven_flash_v2_5`. Do a quick listen on v4 turbo before a client demo.
- Default stability: 0.5, similarity_boost: 0.8 — adjust per voice if needed.
- Karen and Joseph are the safest "default" picks for most business use cases.
