# Backlog

Status: validated by delegate (sequencing as drafted, MoSCoW per slice, segment fields in the walking skeleton). Statuses: *idea*, *shaped*, *picked*, *done*. Picked: feature "connection requests" (3.1 + 3.2), PRD in `prd/connection-requests.md`.

Reasoning: the walking skeleton comes first because it is the thinnest path that delivers the promise end to end. Consent and deletion sit in slice 1 because the product is live in the EU from its first user. Segment-specific profile fields sit in slice 1 because they are the positioning; without them the product is the generalist red ocean.

| # | Item | Type | Epic / outcome | Value | Slice | Horizon | MoSCoW | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | E1 Account access | Epic | Prerequisite | Members can join and return | 1 | Now | Must | idea |
| 1.1 | Sign up | Feature | E1 | A person becomes a member | 1 | Now | Must | idea |
| 1.2 | Sign in and out | Feature | E1 | A member returns safely | 1 | Now | Must | idea |
| 2 | E2 Linguist profile | Epic | Outcome 1 | A profile worth connecting with | 1-2 | Now | Must | idea |
| 2.1 | Create profile with language pairs and specialties | Feature | E2 | States what matters in the trade | 1 | Now | Must | idea |
| 2.2 | View a colleague's profile | Feature | E2 | Colleagues recognise each other | 1 | Now | Must | idea |
| 2.3 | Edit profile | Feature | E2 | Profile stays accurate | 2 | Now | Should | idea |
| 3 | E3 Connections | Epic | Outcome 1 | A network of colleagues | 1-2 | Now | Must | idea |
| 3.1-3.2 | Connection requests: send a request; accept or decline it (one feature) | Feature | E3 | Reach a colleague, and control who connects | 1 | Now | Must | picked |
| 3.3 | List and remove connections | Feature | E3 | Manage the circle | 2 | Now | Should | idea |
| 4 | E4 Short posts and connections feed | Epic | Outcome 2 | Share and read within the circle | 1-2 | Now | Must | idea |
| 4.1 | Publish a short post | Feature | E4 | Share something to connections only | 1 | Now | Must | idea |
| 4.2 | Read the connections feed | Feature | E4 | See what colleagues share | 1 | Now | Must | idea |
| 4.3 | Edit or delete my post | Feature | E4 | Correct or retract | 2 | Now | Should | idea |
| 5 | E5 Data rights (GDPR baseline) | Epic | Outcome 3 | Trust; EU legal baseline | 1-2 | Now | Must | idea |
| 5.1 | Give and record consent at sign-up | Feature | E5 | Lawful collection | 1 | Now | Must | idea |
| 5.2 | Delete my account and data | Feature | E5 | Right to erasure | 1 | Now | Must | idea |
| 5.3 | Export my data | Feature | E5 | Right of access and portability | 2 | Now | Should | idea |
| 5.4 | Choose what my profile shows to whom | Feature | E5 | Control over exposure | 2 | Now | Should | idea |
| 6 | E6 Find colleagues | Epic | Outcome 1 | Grow the network beyond known people | 3 | Next | Should | idea |
| 6.1 | Search by name | Feature | E6 | Find a known colleague | 3 | Next | Should | idea |
| 6.2 | Search by language pair and specialty | Feature | E6 | Find colleagues in the trade | 3 | Next | Should | idea |
| 7 | E7 Safety | Epic | Outcome 3 | Abuse can be stopped | 3 | Next | Should | idea |
| 7.1 | Block a member | Feature | E7 | Stop unwanted contact | 3 | Next | Should | idea |
| 7.2 | Report a post or profile | Feature | E7 | Flag abuse | 3 | Next | Should | idea |
| 8 | Reactions and replies on posts | Epic | Outcome 2 | Conversation among colleagues | - | Later | Could | idea |
| 9 | Referrals and availability | Epic | Outcome 1 | Colleagues pass work to each other (watch the job-board anti-goal) | - | Later | Could | idea |
| 10 | Notifications | Epic | Outcome 2 | Members learn of new activity | - | Later | Could | idea |
| - | Monetization, payments | - | - | Out of scope for this example | - | - | Won't | - |

Open questions for the next level (not decided here): how long a "short" post is; whether a profile is visible to non-connections; what a member sees before connecting. These are product bets for the PRDs, or the human's.
