# Decision log

### D-1 Does a space always belong to a lot?
- status: answered
- answer: yes, always
- source: human
- request: register-lots-and-spaces

### D-2 How many owners does a lot have?
- status: answered
- answer: exactly one
- source: human
- request: register-lots-and-spaces

### D-3 Who registers and edits lots and spaces?
- status: answered
- answer: only the manager
- source: human
- request: register-lots-and-spaces

### D-4 What happens when another role tries to register or edit?
- status: answered
- answer: refused, with a manager-only refusal
- source: human
- request: register-lots-and-spaces

### D-5 Are French legal rules and rentals part of this feature?
- status: answered
- answer: no, out of scope
- source: human
- request: register-lots-and-spaces

### D-6 Can a lot be removed?
- status: human-needed
- answer: pending
- source: none (PRD requirement 7 covers spaces only; scope says "removing an entry")
- recommended: no, lot removal is outside F1.2; only spaces can be removed
- request: register-lots-and-spaces

### D-7 Are identifiers and numbers compared exactly, or ignoring case and surrounding spaces?
- status: human-needed
- answer: pending
- source: none (PRD requirements 1 and 2 say "unique" only)
- recommended: ignoring case and surrounding spaces ("A12" and " a12 " are the same lot)
- request: register-lots-and-spaces

### D-8 Is a blank identifier, space number or owner name accepted?
- status: human-needed
- answer: pending
- source: none (PRD requirement 3 refuses a missing owner only)
- recommended: no, a blank value counts as missing and is refused
- request: register-lots-and-spaces

### D-9 What does the listing show beyond spaces, and in what order?
- status: human-needed
- answer: pending
- source: none (PRD requirement 5 names spaces only)
- recommended: lots sorted by identifier, each with its owner, then its spaces sorted by number; a lot with no space still appears
- request: register-lots-and-spaces

### D-10 Can a lot be removed? (supersedes D-6)
- status: answered
- answer: no, only spaces can be removed in F1.2
- source: human
- request: register-lots-and-spaces

### D-11 Uniqueness of identifiers and numbers? (supersedes D-7)
- status: answered
- answer: compared ignoring case and surrounding spaces
- source: human
- request: register-lots-and-spaces

### D-12 Blank identifier, space number or owner name? (supersedes D-8)
- status: answered
- answer: refused, a blank value counts as missing
- source: human
- request: register-lots-and-spaces

### D-13 Listing content and order? (supersedes D-9)
- status: answered
- answer: lots sorted by identifier with their owner, spaces sorted by number, lots with no space still shown
- source: human
- request: register-lots-and-spaces

### D-14 How does a use case report a refusal?
- status: answered
- answer: a documented application error per reason (duplicate lot, duplicate space, unknown lot, blank value, manager-only), all under one Refusal base
- source: human
- request: register-lots-and-spaces

### D-15 What does the listing show for an identifier or number entered with surrounding spaces or other case?
- status: answered
- answer: the trimmed text as typed, case kept; only the comparison ignores case
- source: human
- request: register-lots-and-spaces

### D-16 When a non-manager also sends a blank or duplicate value, which refusal wins?
- status: answered
- answer: the manager-only refusal, before any validation
- source: human
- request: register-lots-and-spaces

### D-17 Who may read the register listing?
- status: answered
- answer: anyone; only writes require the manager role
- source: human
- request: register-lots-and-spaces

### D-18 Which roles exist, and what happens to any other?
- status: answered
- answer: manager, owner, resident; only the manager has an effect, any other value is refused as manager-only
- source: human
- request: register-lots-and-spaces

### D-19 What does the manager see when the store file is corrupt or malformed?
- status: answered
- answer: a named "store unreadable" error on read and on write; the file is never overwritten
- source: human
- request: register-lots-and-spaces

### D-20 How are identifiers and numbers sorted in the listing? (completes D-13)
- status: answered
- answer: natural order, case-folded ("p2" before "p10"), for lots and spaces
- source: human
- request: register-lots-and-spaces

### D-21 A correction to the same value (same owner, or a number differing only by case)?
- status: answered
- answer: accepted; the stored text becomes the new trimmed text
- source: human
- request: register-lots-and-spaces

### D-22 Order of two identifiers that tie in natural order ("a01" and "a1")
- status: answered
- answer: registration order
- source: human
- request: register-lots-and-spaces

### D-23 Which store contents count as unreadable (D-19)?
- status: answered
- answer: invalid JSON or encoding, wrong shape or missing fields, a blank owner, a duplicate lot or space, a space on an unknown lot
- source: human
- request: register-lots-and-spaces

### D-24 Which kinds of rule exist?
- status: answered
- answer: a closed list of two kinds, duration bounds and owner consent required
- source: human (PRD, decision Q1)
- request: legal-rules-skeleton

### D-25 With several rules, how is a proposal judged?
- status: answered
- answer: every rule is evaluated; one refusal suffices to refuse; every refusing rule is listed
- source: human (PRD, decision Q2)
- request: legal-rules-skeleton

### D-26 What if no rule is configured?
- status: answered
- answer: a valid proposal is allowed, and the answer says that no rule was evaluated
- source: human (PRD, decision Q3)
- request: legal-rules-skeleton

### D-27 Who configures rules, who lists and checks them?
- status: answered
- answer: only the manager configures (D-3, D-4); anyone may list rules and run a check (D-17)
- source: human (PRD, "Decisions of the human"; reuses D-3, D-4, D-17)
- request: legal-rules-skeleton

### D-28 Changing or removing a rule that does not exist?
- status: human-needed
- answer: pending
- source: none (PRD requirement 5 lists refusals for adding only)
- recommended: refused with a named "unknown rule" reason, rules unchanged
- request: legal-rules-skeleton

### D-29 In what order are rules listed (and refusing rules in an answer)?
- status: human-needed
- answer: pending
- source: none (PRD requirement 11 says "order of rule names" without saying which order; requirement 3 gives no order for the listing)
- recommended: the same order everywhere: rule names in natural order, case-folded, as D-20; ties in registration order as D-22
- request: legal-rules-skeleton

### D-30 A proposal with a missing or unreadable date, or a missing consent value?
- status: human-needed
- answer: pending
- source: none (PRD requirement 9 names blank name, unknown space, end before start only)
- recommended: refused as invalid, with a named reason, like requirement 9: no rule evaluated, rules and register unchanged
- request: legal-rules-skeleton

### D-31 When rules are unreadable and the proposal is also invalid, or when the rules are only listed?
- status: human-needed
- answer: pending
- source: none (PRD requirement 9 says no rule is evaluated; requirement 15 says a check ends with "rules unreadable")
- recommended: the proposal is validated first (it needs no rule), so an invalid proposal gets its invalid reason; "rules unreadable" applies to a valid proposal, and to listing the rules
- request: legal-rules-skeleton

### D-32 Changing or removing a rule that does not exist? (supersedes D-28)
- status: answered
- answer: refused with a named "unknown rule" reason on change and on removal; rules unchanged
- source: human
- request: legal-rules-skeleton

### D-33 Order of the rule list and of refusing rules in an answer? (supersedes D-29)
- status: answered
- answer: natural order of the names, case-folded; ties in registration order (as D-20, D-22)
- source: human
- request: legal-rules-skeleton

### D-34 A proposal with a missing or unreadable date, or no consent value? (supersedes D-30)
- status: answered
- answer: refused as invalid, with a named reason; no rule evaluated
- source: human
- request: legal-rules-skeleton

### D-35 Unreadable rules with an invalid proposal, and listing when unreadable? (supersedes D-31)
- status: answered
- answer: the proposal is validated first, so an invalid proposal gets its invalid reason; listing the rules, and a check of a valid proposal, fail with "rules unreadable"
- source: human
- request: legal-rules-skeleton

### D-36 Are duration bounds inclusive?
- status: answered
- answer: yes; with a minimum of 30 days, 30 passes and 29 is refused; the maximum likewise
- source: human
- request: legal-rules-skeleton

### D-37 Where are the rules stored?
- status: answered
- answer: a second JSON file next to the register file; the register file is untouched
- source: human
- request: legal-rules-skeleton

### D-38 Which new sensitive zones does the rules feature add?
- status: answered
- answer: the rule write use cases, the rule store write path, and the fail-closed path of the proposal check
- source: human
- request: legal-rules-skeleton

### D-39 Changing a duration rule's parameter: replace or merge?
- status: answered
- answer: replace; a given parameter is the whole new one, validated like an addition; none given keeps the old one
- source: human
- request: legal-rules-skeleton

### D-40 Source note on change: keep, replace, clear?
- status: answered
- answer: not given keeps it, text replaces it, blank text clears it; a blank note on add means no note
- source: human
- request: legal-rules-skeleton

### D-41 Shape of the duration parameter?
- status: answered
- answer: {"minimum": n, "maximum": n}, both keys always present, None for no bound; whole numbers above 0, text, decimals and booleans refused as invalid days; any other key refused as an invalid parameter
- source: human
- request: legal-rules-skeleton

### D-42 A duration parameter with a single key, such as {"minimum": 30}
- status: answered
- answer: accepted; the missing key means no bound, and both keys are stored (refines D-41)
- source: human
- request: legal-rules-skeleton

### D-43 A source note that is not text
- status: answered
- answer: refused as a blank value; unreadable rules when it is read from the file
- source: human
- request: legal-rules-skeleton

### D-44 Changing a rule with an empty parameter
- status: answered
- answer: parameter={} is refused as "no bound"; None keeps the old parameter
- source: human
- request: legal-rules-skeleton

### D-45 Who may offer a space?
- status: answered
- answer: only the owner of the space's lot; any other owner is refused, and a role other than owner (manager included) is refused as not allowed to offer
- source: human, PRD offer-a-space, answered question Q1
- request: offer-a-space

### D-46 How is the offering owner identified?
- status: answered
- answer: the offerer gives a name, compared with the lot owner ignoring case and surrounding spaces (D-11); limit: without accounts this proves nothing about who is typing
- source: human, PRD offer-a-space, answered question Q2
- request: offer-a-space

### D-47 May an offer start in the past?
- status: answered
- answer: no; a start date in the past is refused
- source: human, PRD offer-a-space, answered question Q3
- request: offer-a-space

### D-48 May two offers of the same space share a day?
- status: answered
- answer: no; a second offer sharing a day with an existing offer of the same space is refused
- source: human, PRD offer-a-space, answered question Q4
- request: offer-a-space

### D-49 Does an offer carry a price?
- status: answered
- answer: no; no price in this feature (the amount due comes with E4)
- source: human, PRD offer-a-space, answered question Q5
- request: offer-a-space

### D-50 Does an offer change the "no rental" answer of the rental check, and are the E5 rules applied at offer time?
- status: answered
- answer: no to both; the answer "no rental" is untouched and the rules are not applied at offer time
- source: human, PRD offer-a-space, answered question Q6
- request: offer-a-space

### D-51 May an owner withdraw an offer, and may a space with an open offer be removed?
- status: answered
- answer: the owner can withdraw an offer; a space with an open offer cannot be removed from the register
- source: human, PRD offer-a-space, answered question Q7
- request: offer-a-space

### D-52 Does an offer whose end date has passed stay open?
- status: answered
- answer: no; it stops being open the day after its end date: it leaves the list and blocks neither another offer nor the removal of the space
- source: human, stories.md open point 1
- request: offer-a-space

### D-53 Is a start date equal to today accepted?
- status: answered
- answer: yes; only dates strictly before today are refused (refines D-47)
- source: human, stories.md open point 2
- request: offer-a-space

### D-54 Who may withdraw an offer, and how is it designated?
- status: answered
- answer: only the owner, by the same name check as offering (D-46); the offer is designated by an offer number added to the listing (completes D-45..D-51 and the listing of the PRD)
- source: human, stories.md open point 3
- request: offer-a-space

### D-55 Withdrawing an offer already withdrawn?
- status: answered
- answer: refused as an unknown offer
- source: human, stories.md open point 4
- request: offer-a-space

### D-56 When the lot's owner is corrected, which owner does an open offer show?
- status: answered
- answer: the current owner, read from the register
- source: human, stories.md open point 5
- request: offer-a-space

### D-57 Changing the number of a space that has an open offer?
- status: answered
- answer: refused as "space offered", as for removal
- source: human, architect.md question Q2
- request: offer-a-space

### D-58 Withdrawing an offer whose end date has passed?
- status: answered
- answer: refused as an unknown offer, since it is no longer open (D-52), like an offer already withdrawn (D-55)
- source: human, architect.md question Q3
- request: offer-a-space

### D-59 Blank, missing or non-text offerer name or space number in an offer?
- status: answered-by-delegate
- answer: refused as invalid input (`BlankValueRefused`, D-12), at the rank of a bad period: after the role check, before unknown space and owner
- source: delegate, planner.md question Q1
- request: offer-a-space

### D-60 Which date forms does an offer accept?
- status: answered-by-delegate
- answer: a date object (a datetime is refused) or text `YYYY-MM-DD` with surrounding spaces ignored; anything else is an invalid date
- source: delegate, planner.md question Q2
- request: offer-a-space

### D-61 Number of the first offer?
- status: answered-by-delegate
- answer: 1, then 2, 3; numbers are never reused
- source: delegate, planner.md question Q3
- request: offer-a-space

### D-62 Listing open offers when an offered space is no longer in the register (until S4 blocks the removal)
- status: answered
- answer: the listing skips that offer; it does not fail with "offers unreadable"
- source: human, developer-1.md "Behaviors added" 1
- request: offer-a-space
