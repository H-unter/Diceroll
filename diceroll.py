"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import matplotlib.pyplot
import math
import convolution


def main():
    """Calculate the probability distribution of a die roll prompt"""
    # prompt = input("Enter Dice: ")  # 2d6+1
    dice_prompt = "4d12+12"
    number_of_dice, number_of_faces, modifier = parse_dice_prompt(dice_prompt)

    outcome_to_probability = calculate_pdf(number_of_faces, number_of_dice, modifier)
    mean_value = calculate_mean(outcome_to_probability)  # change to "expected_outcome"?
    plot_values(dice_prompt, outcome_to_probability, mean_value)


def parse_dice_prompt(dice_prompt):
    """Parse dice prompt and return the 3 characteristic parameters XdY+Z"""
    number_of_dice, remainder = dice_prompt.split('d')
    number_of_faces, modifier = remainder.split('+')
    return int(number_of_dice), int(number_of_faces), int(modifier)


def calculate_pdf(number_of_faces, number_of_dice, modifier):
    """Convolve the discrete probability densities https://www.youtube.com/watch?v=IaSGqQa5O-M&ab_channel=3Blue1Brown"""
    die_face_probability = 1 / number_of_faces
    single_die_range = range(1 + modifier, number_of_faces + modifier + 1)
    die_probability_distribution = {outcome: die_face_probability for outcome in single_die_range}

    pdf = {}
    for i in range(1 + modifier, number_of_faces * number_of_dice + modifier + 1):
        if i in single_die_range:
            pdf[i] = die_face_probability
        else:
            pdf[i] = 0
    for i in range(number_of_dice - 1):
        pdf = convolution.convolve(pdf, die_probability_distribution)
    return {key: value for key, value in pdf.items() if value != 0}


def calculate_mean(outcome_to_probability):
    """Calculate the mean dice outcome"""
    outcomes = list(outcome_to_probability.keys())
    probabilities = list(outcome_to_probability.values())
    mean_value = 0
    for i in range(len(outcomes)):
        mean_value += probabilities[i] * outcomes[i]
    mean_value = round(mean_value, 1)
    return mean_value


def plot_values(prompt, outcome_to_occurrences, mean_value):
    """Plot values given an input dictionary"""
    x_values = list(outcome_to_occurrences.keys())
    y_values = list(outcome_to_occurrences.values())
    x_range = max(x_values) - min(x_values)
    x_increment = math.ceil(x_range / 25) if x_range >= 25 else 1
    # print(f"x_increment = {x_increment}")

    matplotlib.pyplot.bar(x_values, y_values, color='green')
    matplotlib.pyplot.xlabel('Sum')
    matplotlib.pyplot.ylabel('% Occurrence')
    matplotlib.pyplot.title(f'Histogram of Results from {prompt}')
    matplotlib.pyplot.axvline(x=mean_value, label=f"Mean = {mean_value}", color='r')
    matplotlib.pyplot.legend()
    matplotlib.pyplot.xticks(range(min(x_values), max(x_values) + 1, x_increment))
    matplotlib.pyplot.grid(axis='y', linestyle='--', alpha=0.7)
    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
