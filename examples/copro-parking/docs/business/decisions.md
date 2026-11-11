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
