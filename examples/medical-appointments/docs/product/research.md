# Market watch: online booking of medical appointments

Status: hypotheses for the human to validate. Web search was available; findings come from search snippets (vendor pages, review sites, one study set), not from full-page reading. Anything without a source is marked *unverified*.

Idea: an online booking service where patients see a practitioner's free slots, book one, and cancel it.

## 1. The problem and who has it

- **Patients.** They want to see when a practitioner is free and secure a slot without a phone call during office hours. Today: phone, front desk, or a practice's own site. *Unverified* (no patient interviews).
- **Practitioners and their practices.** An empty slot is lost capacity. No-shows and late cancellations cause it. Reported primary-care no-show rates range from 7.8% (14 family medicine clinics, 2022) to 26.6% (19 Bronx practices, 2018-2019), and 16.5% in a community health center where forgetting and miscommunication were the top reasons. Sources: [Annals of Family Medicine / PubMed results](https://pubmed.ncbi.nlm.nih.gov/24327664), [PMC4714455](https://pmc.ncbi.nlm.nih.gov/articles/PMC4714455/), [ClinicalTrials.gov NCT03850431](https://clinicaltrials.gov/study/NCT03850431). Figures come from different settings and are not comparable with each other; no market-wide figure is claimed.
- **Today's coping.** Phone and front desk, practice-specific tools, reminders (a centralized phone reminder only moved one academic center's rate from 16.3% to 15.8%, per the same search results). A cancellation that frees the slot for someone else is the lever the idea targets. *Unverified* that the practices in a target segment lack any online booking.

## 2. Competitors and substitutes

Only two competitors were checked; the list is not exhaustive.

| Name | Does well | Fails at / limits | Price | Source |
|---|---|---|---|---|
| Zocdoc (marketplace, US) | Free for patients; free practice scheduling tools; patients find and book online | Fee is charged at booking, even if the patient then misses the visit; critics object to this. Self-reported 8x ROI is not independent | No fixed fee; pay per new-patient booking, stated range $30-$140 by specialty and location; monthly spend cap; first-time bookings with a provider only | [Zocdoc pricing](https://www.zocdoc.com/about/newpricing), [billing help](https://zocdoc.com/provider-help/en/articles/10859404-understanding-zocdoc-pricing-and-billing) |
| Doctolib (Europe) | Online appointment management, reminders, patient messaging, video consultations, AI phone assistant (feature list from review sites) | Capterra reviews 4.1/5 from 13 reviews, value for money 3.6/5 (very small sample) | From 139 EUR per month, flat rate, per Capterra; G2 says no pricing provided | [Capterra](https://www.capterra.com/p/184480/Doctolib/pricing/), [G2](https://www.g2.com/products/doctolib/pricing) |
| Substitute: phone and front desk | Zero adoption cost, human triage | Office hours only, no visible free slots, reminders and cancellation by hand | Staff time | *unverified* |
| Substitute: practice-built or generic calendar tools | Cheap, familiar | Not designed for patient identity and health data | varies | *unverified* |

Not found in this search: Healthgrades features and pricing; any regional or small independent competitor. Ask the human for known competitors and sources.

## 3. Blue or red ocean

Factors buyers weigh (hypotheses): free slots visible to the patient; speed to book; cancellation and slot release; price model for the practitioner; reminders; breadth (video, messaging, intake); data protection.

| Factor | Zocdoc | Doctolib | Phone / front desk |
|---|---|---|---|
| Free slots visible online | yes (sourced) | yes (sourced, "online appointment management") | no (*unverified*) |
| Practitioner price model | per new-patient booking | flat monthly | none |
| Reminders | intake reminders (sourced) | yes (sourced) | manual |
| Breadth (video, messaging, intake) | video, intake | video, messaging, intake, AI phone | none |
| Cancel frees the slot | *unverified* | *unverified* | by hand |
| Cost when patient does not show up | fee still charged (sourced) | flat, unaffected | n/a |

Reading: the two sourced competitors compete on the same factors (breadth, marketplace reach), which looks like a **red ocean** at the high end. A possible gap: a deliberately narrow service doing only see-slots / book / cancel well, with a price model that does not penalize practitioners for no-shows. This is a hypothesis built on two competitors.

What would contradict it: many small tools already do exactly this cheaply (not searched); practitioners value breadth over simplicity; cancel-and-release already works well in the incumbents.

## 4. Trends and constraints

- **Health data.** Appointment data usually counts as health-related. Under GDPR, health data is a special category (Article 9) read broadly by the EU court; a booking revealing a specialty may be caught. Under HIPAA in the US, names plus context showing a person is a patient can be protected health information. Processing needs a legal basis and a processor contract (GDPR Article 28). Sources are secondary (vendor and consultancy blogs), primary texts not checked: [Noze on Article 9](https://www.noze.it/en/insights/gdpr-health-data-article-9/), [Accountable HQ on scheduling privacy](https://www.accountablehq.com/post/appointment-scheduling-privacy-considerations-how-to-stay-compliant-and-keep-data-safe), [IAPP on GDPR vs HIPAA](https://iapp.org/news/a/gdpr-match-up-the-health-insurance-portability-and-accountability-act). Advice found: collect the minimum, avoid diagnoses in booking. Which regime applies to us is *unverified* and needs the human's target country.
- Technology and behavior shifts (mobile booking, AI phone assistants): one sourced signal, Doctolib's AI phone assistant. Nothing else verified.

## 5. What is unknown

1. Target country and regulation: decides which privacy regime applies. *Unverified.*
2. Who pays: the practitioner (subscription, per booking) or nobody (a learning product)? No data.
3. Whether patients and practitioners want a narrow tool rather than a full suite.
4. Whether releasing a cancelled slot to other patients has measurable value (no source on fill rate).
5. Real size of the segment: no market size sourced, none stated.

## 6. Question for the human (positioning to carry into the vision)

Which positioning do we carry into the vision? Recommendation: A.

1. A) Narrow and simple: see free slots, book, cancel, nothing more; priced so a no-show does not cost the practitioner extra.
2. B) Full suite catching up with the incumbents (reminders, video, messaging).
3. C) Marketplace to find new patients (compete on reach).
4. D) Other / let me explain.

Also needed before the vision: target country (see 4), and whether this is a real product or a learning example.

## Human's answers (recorded)

Positioning: narrow and simple (A). Country: EU, GDPR. Nature: learning example, price model out of scope.
