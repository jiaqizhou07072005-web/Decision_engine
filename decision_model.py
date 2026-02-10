def compute_stats(outcomes, probabilities):
    """
    Compute expected value and variance. 

    outcomes: list of numbers
    probabilities: list of probabilities (same length)
    """

    # Expected value
    ev = sum(p * x for x, p in zip(outcomes, probabilities))

    # Variance
    var = sum(p * (x - ev) ** 2 for x, p in zip(outcomes, probabilities))

    return ev, var


def risk_adjusted_score(outcomes, probabilities, risk_aversion):
    """
    Compute EV, variance, and risk-adjusted score.
    Score = EV − lambda * Var
    """

    ev, var = compute_stats(outcomes, probabilities)
    score = ev - risk_aversion * var

    return ev, var, score


if __name__ == "__main__":
    print("Decision Engine")

    outcomes = input("Enter outcomes separated by commas: ")
    probabilities = input("Enter probabilities separated by commas: ")
    risk_aversion = float(input("Enter risk aversion (lambda): "))

    outcomes = [float(x) for x in outcomes.split(",")]
    probabilities = [float(p) for p in probabilities.split(",")]

    ev, var, score = risk_adjusted_score(outcomes, probabilities, risk_aversion)

    print("\nResults:")
    print("Expected Value:", ev)
    print("Variance:", var)
    print("Score:", score)

