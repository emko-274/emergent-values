# Prompt-Installed Preferences Are Brittle Rules, Not Utilities

*Draft — abstract, introduction, and conclusion. Method, results, and appendices to follow.*

---

## Abstract

*(150 words — at the spec's ceiling)*

Mazeika et al. (2025) show that LLMs hold coherent value systems and rewrite them through fine-tuning. We ask whether a system prompt does the same, and introduce a behavioural assay separating an integrated edit from surface compliance: attach a cost to both options, sweep it, and locate the indifference price. We install preferences via system prompt as a known-provenance control, comparing them against native preferences and a placebo prompt across 13 outcome pairs stratified by native preference strength. Native preferences yield finite indifference prices in 8 of 13 pairs and placebo tracks them closely; installed preferences yield none in 26 fits spanning two price ranges, holding even at costs forty times the alternative. Compliance is total and does not vary with native preference strength. The only disruption we observe is an unrelated budget-rule violation, not the cost of the preference itself. Prompt-installed values behave as brittle rules rather than utilities.

---

## 1. Introduction

Mazeika et al. (2025) establish that large language models hold value systems coherent enough to be described with utility functions, and demonstrate that those utilities can be rewritten through supervised fine-tuning. Fine-tuning is expensive and permanent. The obvious cheaper alternative is to write the preference into a system prompt, and this is done routinely in deployment — constitutions, operator instructions, and behavioural policies are all delivered as text at inference time.

Whether that text produces the same kind of change is not obvious, and the distinction matters for safety. A model that has genuinely internalised a preference and a model that is following an instruction about a preference behave identically under direct questioning. They come apart only under pressure. If the preference is part of the model's utility function, it should trade off against other things the model wants; if it is a rule the model is obeying, it should not trade off at all — it should hold until something breaks it entirely.

We operationalise that distinction with a price. Both options in a forced binary choice carry a cost in abstract budget units. Sweeping the cost of one option and fitting a probit to the resulting choice proportions yields an indifference price: the cost differential at which the model is equally happy with either outcome. An integrated preference bends gradually as its price rises and produces a finite indifference price. A superficial one collapses at the first cost. A rule produces a flat line and no indifference price at all — the model neither bends nor breaks, because it is not trading.

**We install preferences via system prompt as a known-provenance control.** This is the design's central move. Studies that infer values from conversation cannot say where a value came from, which limits what can be concluded about how values are held. By writing a preference we choose into the system prompt — specifically, the reverse of one the model already holds — we know its provenance exactly, and can compare its behaviour under price pressure against a native preference measured on the identical outcome pair. A placebo condition carrying unrelated system text ("Paris is the capital of France.") separates the effect of the injected preference from the effect of having a system prompt at all.

Our contribution is threefold. First, the assay: a reproducible price-sweep protocol that distinguishes an integrated preference edit from surface compliance, together with a censoring rule for the degenerate case where a flat curve leaves the price coefficient unidentified. Second, the finding: across 13 outcome pairs and two price ranges spanning costs from one fifth to forty times the alternative, an installed preference never produced a measurable indifference price, while native preferences on the same pairs did. Third, a control experiment separating a genuine constraint effect from a nuisance one, which shows that the single condition under which installed compliance does break down is an arithmetic budget violation unrelated to the preference being tested.

We deliberately keep claims comparative. The paper's exchange-rate results drew criticism for framing sensitivity, and we do not claim that any outcome is worth a specific number of units. What we claim is relational: native and installed preferences respond differently to the same swept cost, on the same pairs, under the same elicitation.

---

## 2. Conclusion

Across 26 probit fits — 13 outcome pairs at each of two price ranges — a preference installed by system prompt never yielded a finite indifference price. Native preferences on the identical pairs yielded one in 8 of 13 cases in the standard range and 5 of 13 in the extended range, and the placebo condition tracked native rather than installed. The installed curves are not shallow; they are flat. Compliance with the injected preference was total at every price level tested, up to a cost forty times that of the alternative and twice the model's entire stated budget.

This is the third of the three outcomes our design anticipated, and the most safety-relevant. A preference that collapsed at the first cost would indicate parroting. A preference that bent gradually would indicate integration. What we observe instead is a rule: the model follows the instruction without trading it against anything, which means price is not a lever on it in either direction. For deployment this cuts both ways. An instructed behaviour will not be quietly eroded by competing incentives, which is desirable. It also will not be moderated by them, and a model that cannot be bargained down also cannot be bargained with.

The one apparent exception proved instructive. At the highest cost tested, compliance broke down in 4 of 13 pairs, which invites the reading that sufficient pressure eventually overcomes an installed preference. A three-cell control experiment rules this out. Holding the cost number fixed at 200 while raising the budget ceiling so the option became affordable restored full compliance in every pair; holding the over-budget ratio fixed while multiplying the number fivefold reproduced the breakdown almost exactly. The disruption tracks the budget-rule violation, not the magnitude of the price and not the strength of the preference under pressure. What looked like a price effect was an arithmetic one.

This also disposes of a hypothesis we had entertained: that compliance would track native preference strength, with strongly held native preferences collapsing faster when overridden. It does not. Compliance was uniformly total across weak, moderate, and strong strata, and the only variance in the dataset — confined to the single price level that violated the budget — correlated with strength at rho = −0.267 (p = 0.378), a negative sign and not distinguishable from zero. Preference strength does not predict how an installed preference behaves under cost, because installed preferences do not behave under cost at all.

**Limitations.** The pair set is smaller and less balanced than intended. An exhaustive screen of all 351 pairs in the source category found only 23 usable for stratification — 117 were near-ties and 211 were already saturated — yielding 13 pairs at 4 weak, 3 moderate, and 6 strong against targets of 7/7/6. The design therefore skews strong, which weakens the analysis of installed behaviour as a function of native strength; though since compliance showed no variance at all across strata, more balanced sampling would likely not have changed that conclusion. Results are from a single model and a single outcome category. The affordability contrast is suggestive rather than established at p = 0.068, limited by a ceiling effect in which 9 of 13 pairs had no room to move. And the assay measures stated preference under forced choice, which is a proxy for a utility function, not a direct observation of one.

**Future work.** The clearest next step is to vary the cost denomination itself. Preliminary probes in which the cost is expressed as a death toll rather than abstract budget units produced bending curves where budget units produced flat ones, suggesting that the flatness we report may be a property of the currency rather than of installed preferences as such. Establishing that would sharpen the claim considerably: it would distinguish "instructed preferences do not trade" from "instructed preferences do not trade against things the model does not care about."

---

## Disclosure

We used the released `emergent-values` code for elicitation. New work in this paper is the pricing mechanism, the provenance conditions, the controls, and the analysis.

## Reproducibility notes

All results use `claude-sonnet-5` at temperature 1.0, K = 10 per price point (5 in each presentation order), with order counterbalancing resolved at write time. Two collection defects were found and corrected during the study and are documented in the appendix: responses lost when a thinking block consumed the entire token budget, and price points with no parseable response recorded as a unanimous vote rather than as missing data. Both are corrected in the released dataset, and every row records the token cap under which it was collected.
