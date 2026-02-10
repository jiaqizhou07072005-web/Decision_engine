# Decision Engine Notes

## Problem
Compare two options under uncertainty using expected value and variance.

## Inputs
- outcomes
- probabilities
- risk_aversion

## Outputs
- expected value
- variance
- risk-adjusted score

## Model
EV = sum(p_i * x_i)
Var = sum(p_i * (x_i - EV)^2)
Score = EV - lambda * Var
