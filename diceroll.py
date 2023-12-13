"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import random
import matplotlib.pyplot as plt
import math

TRIAL_NUMBER = 50000


def main():
    """Calculate the probability distribution of a dice roll prompt"""
    # prompt = input("Enter Dice: ")  # 2d6+1
    dice_prompt = "10d5+0"
    number_of_dice, number_of_faces, modifier = parse_dice_prompt(dice_prompt)

    minimum_outcome = number_of_dice + modifier
    maximum_outcome = number_of_dice * number_of_faces + modifier
    outcome_to_occurrences = {outcome: 0 for outcome in
                              range(number_of_dice + modifier, number_of_dice * number_of_faces + modifier + 1)}

    simulate_dicerolls(number_of_faces, number_of_dice, modifier, outcome_to_occurrences, TRIAL_NUMBER)
    mean_value = calculate_mean(outcome_to_occurrences)  # change to "expected_outcome"?
    plot_values(dice_prompt, outcome_to_occurrences, mean_value)


def parse_dice_prompt(dice_prompt):
    """Parse dice prompt and return the 3 characteristic parameters XdY+Z"""
    number_of_dice, remainder = dice_prompt.split('d')
    number_of_faces, modifier = remainder.split('+')
    return int(number_of_dice), int(number_of_faces), int(modifier)


def simulate_dicerolls(number_of_faces, number_of_dice, modifier, outcome_to_occurrences, trial_number):
    """Run TRIAL_NUMBER amount of trials on the given dice prompt"""
    for i in range(trial_number):
        result = 0
        for j in range(number_of_dice):
            result += (random.randint(1, number_of_faces))
        result += modifier
        outcome_to_occurrences[result] += 1
    # TODO: continue running until either double the trial number has been run or the centre values are roughly symmetrical


def calculate_mean(outcome_to_occurrences):
    """Calculate the mean dice outcome"""
    outcomes = list(outcome_to_occurrences.keys())
    probabilities = [value / TRIAL_NUMBER for value in outcome_to_occurrences.values()]
    mean_value = 0
    for i in range(len(outcomes)):
        mean_value += probabilities[i] * outcomes[i]
    mean_value = round(mean_value, 1)
    return mean_value


def plot_values(prompt, outcome_to_occurrences, mean_value):
    """Plot values given an input dictionary"""
    x_values = list(outcome_to_occurrences.keys())
    y_values = [(value / TRIAL_NUMBER) * 100 for value in outcome_to_occurrences.values()]
    x_range = max(x_values) - min(x_values)
    x_increment = math.ceil(x_range / 25) if x_range >= 25 else 1
    print(f"x_increment = {x_increment}")

    plt.bar(x_values, y_values, color='green')
    plt.xlabel('Sum')
    plt.ylabel('% Occurrence')
    plt.title(f'Histogram of Results from {prompt}')
    plt.axvline(x=mean_value, label=f"Mean = {mean_value}", color='r')
    plt.legend()
    plt.xticks(range(min(x_values), max(x_values) + 1, x_increment))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


if __name__ == "__main__":
    main()
