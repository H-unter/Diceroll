"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import random
import matplotlib.pyplot as plt


def main():
    # prompt = input("Enter Dice: ")  # 2d6+1
    prompt = "2d6+1"
    number_of_dice = int(prompt.split('d')[0])
    number_of_faces = int(prompt.split('+')[0][-1])
    modifier = int(prompt.split('+')[1][0])

    minimum_outcome = number_of_dice + modifier
    maximum_outcome = number_of_dice * number_of_faces + modifier

    print(f"for: {number_of_dice}d{number_of_faces}+{modifier}")
    outcome_to_occurrences = {}
    for i in range(minimum_outcome, maximum_outcome + 1):
        outcome_to_occurrences[i] = 0

    for i in range(0, 10000):
        result = random.randint(1, number_of_faces) + random.randint(1, number_of_faces) + modifier
        outcome_to_occurrences[result] += 1
    plot_values(prompt, outcome_to_occurrences)


def plot_values(prompt, outcome_to_occurrences):
    """Plot values given an input dictionary"""
    x_values = list(outcome_to_occurrences.keys())
    y_values = list(outcome_to_occurrences.values())
    plt.bar(x_values, y_values, color='blue')
    plt.xlabel('Sum')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of Results from {prompt}')
    plt.xticks(x_values)  # setting x-ticks to match the sums
    plt.show()


main()
