import collections
import math


def h(x):
    return x * -math.log2(x)


def syndrome(guess, ans):
    syndrome = []
    for i, (l1, l2) in enumerate(zip(ans, guess)):
        if l1 == l2:
            syndrome.append(i)
    hist = collections.Counter(guess)
    for l, count in sorted(collections.Counter(ans).items()):
        syndrome.append(l * min(count, hist[l]))
    return tuple(syndrome)


def main():
    # Read the word lists.
    with open("wordle-allowed-guesses.txt") as f:
        allowed_guesses = f.read().split()
        allowed_guesses.sort()
    with open("wordle-answers-alphabetical.txt") as f:
        answers_alphabetical = f.read().split()
        answers_alphabetical.sort()

    def info_of_guess(guess):
        buckets = collections.defaultdict(list)
        for ans in answers_alphabetical:
            buckets[syndrome(guess, ans)].append(ans)
        return (
            sum(
                h(len(bucket) / len(answers_alphabetical))
                for bucket in buckets.values()
            ),
            guess,
        )

    for info, guess in sorted(map(info_of_guess, allowed_guesses)):
        print(info, guess)


if __name__ == "__main__":
    main()
