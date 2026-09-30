# Governance & Voting Model

## 1. Voting Weights
- **Founder (Joshua Kleinsasser):** 2 votes (subject to the sunset clause).
- **Verified Contributor:** 1 vote.
- **Observer / Unverified Participant:** 0 votes.

## 2. Earning Contributor Status
A participant earns voting eligibility through a verified contribution, such as:
- Code contributions or bug fixes
- Test harnesses or reproducibility reports
- Security audits or code reviews
- Benchmarks or experimental data runs

## 3. Separation of Governance and Technical Acceptance
- **Governance Decides:** Should the organism pursue this change or research direction?
- **Automated Evaluation Decides:** Does the implementation satisfy hard technical gates (tests, security, schema validation, reproducibility)?
- *Rule:* Popularity or governance approval can never override a failed technical gate.

## 4. Founder Vote Sunset Clause
The founder’s 2-vote weight shall automatically sunset upon reaching **Generation 25** or upon accepting **25 unique verified external contributors**, whichever occurs first. Upon sunset, the founder vote defaults to 1.
