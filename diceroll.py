"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import random
import matplotlib.pyplot as plt

TRIAL_NUMBER = 50000


def main():
    """Calculate the probability distribution of a dice roll prompt"""
    # prompt = input("Enter Dice: ")  # 2d6+1
    prompt = "4d6+5"
    number_of_dice = int(prompt.split('d')[0])
    number_of_faces = int(prompt.split('d')[1].split('+')[0])
    modifier = int(prompt.split('+')[1])

    minimum_outcome = number_of_dice + modifier
    maximum_outcome = number_of_dice * number_of_faces + modifier

    outcome_to_occurrences = {}
    for i in range(minimum_outcome, maximum_outcome + 1):
        outcome_to_occurrences[i] = 0

    simulate_dicerolls(number_of_faces, number_of_dice, modifier, outcome_to_occurrences, TRIAL_NUMBER)
    plot_values(prompt, outcome_to_occurrences)


def simulate_dicerolls(number_of_faces, number_of_dice, modifier, outcome_to_occurrences, trial_number):
    """Run trial_number amount of trials on the given dice prompt"""
    for i in range(trial_number):
        result = 0
        for j in range(number_of_dice):
            result += (random.randint(1, number_of_faces))
        result += modifier
        outcome_to_occurrences[result] += 1


def plot_values(prompt, outcome_to_occurrences):
    """Plot values given an input dictionary"""
    x_values = list(outcome_to_occurrences.keys())
    y_values = [(value / TRIAL_NUMBER) * 100 for value in outcome_to_occurrences.values()]
    plt.bar(x_values, y_values, color='blue')
    plt.xlabel('Sum')
    plt.ylabel('% occurrence')
    plt.title(f'Histogram of Results from {prompt}')
    plt.xticks(x_values)  # setting x-ticks to match the sums
    plt.show()


main()
