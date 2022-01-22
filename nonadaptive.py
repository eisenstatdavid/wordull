# This program finds a Wordle strategy that will never lose.


import collections
import itertools
import random

# pip install ortools
from ortools.linear_solver import pywraplp


# The following two functions work in tandem. Both yield immutable objects such
# that, if tests_of_guess(guess) intersects distinguishing_tests(ans1, ans2),
# then guess distinguishes ans1 from ans2; note, not if and only if, due to edge
# cases with repeated letters.
def tests_of_guess(guess):
    # Letters at specific positions.
    yield from enumerate(guess)
    # Letters in arbitrary positions.
    yield from set(guess)


def distinguishing_tests(ans1, ans2):
    for i, (l1, l2) in enumerate(zip(ans1, ans2)):
        if l1 != l2:
            yield i, l1
            yield i, l2
    yield from set(ans1) ^ set(ans2)


def main():
    # Read the word lists.
    with open("wordle-allowed-guesses.txt") as f:
        allowed_guesses = f.read().split()
        allowed_guesses.sort()
    with open("wordle-answers-alphabetical.txt") as f:
        answers_alphabetical = f.read().split()
        if False:
            answers_alphabetical = random.sample(answers_alphabetical, 300)
        answers_alphabetical.sort()

    # Formulate the mixed integer program.
    solver = pywraplp.Solver.CreateSolver("GLOP")

    # These variables indicate the first five guesses.
    guess_variables = {guess: solver.BoolVar(guess) for guess in allowed_guesses}
    solver.Minimize(sum(guess_variables.values()))

    guesses_of_test = collections.defaultdict(int)
    for guess, x in guess_variables.items():
        for test in tests_of_guess(guess):
            guesses_of_test[test] += x

    test_variables = {}
    previous = None
    for ans1, ans2 in itertools.combinations(answers_alphabetical, 2):
        if ans1 != previous:
            previous = ans1
            print(ans1)
        coverage = 0
        for test in distinguishing_tests(ans1, ans2):
            x = test_variables.get(test)
            if x is None:
                x = solver.BoolVar(str(test))
                solver.Add(x <= guesses_of_test[test])
                test_variables[test] = x
            coverage += x
        solver.Add(coverage >= 1)

    solver.EnableOutput()
    status = solver.Solve()
    if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        print(solver.Objective().Value())
        for guess, x in sorted(
            guess_variables.items(), key=lambda item: item[1].SolutionValue()
        ):
            if x.SolutionValue():
                print(guess, x.SolutionValue())


if __name__ == "__main__":
    main()
