"""
Hunter Kruger-Ilingworth | Dice roll application
"""
import matplotlib.pyplot as plt
import math
import time
import convolution # custom module for convolution of probability distributions
import numpy 

is_results_displayed = True

def parse_dice_prompt(dice_prompt):
    """Parse dice prompt and return an object with dice rolls and total offset. eg 2d4+3+4d7+8"""
    dice_prompt = dice_prompt.replace('-', '+-')  # Handle negative offsets
    dice_roll_terms = dice_prompt.split('+')
    
    dice_rolls = []
    total_offset = 0

    for dice_roll_term in dice_roll_terms:
        is_diceroll_term = 'd' in dice_roll_term
        if is_diceroll_term: # dice roll, eg 4d5
            num_dice, num_faces = map(int, dice_roll_term.split('d'))
            dice_rolls.append((num_dice, num_faces))
        else:
            total_offset += int(dice_roll_term)
    return dice_rolls, total_offset

def calculate_pdf(dice_rolls, modifier):
        """Convolve the discrete probability densities https://www.youtube.com/watch?v=IaSGqQa5O-M&ab_channel=3Blue1Brown"""
        pdf = {}
        # Calculate the probability distribution for each dice roll
        max_total_outcome = sum([num_faces*num_dice for (num_dice, num_faces) in dice_rolls]) + modifier
        total_outcome_range = range(1, max_total_outcome + 1)
        pdf = {outcome: 0 for outcome in total_outcome_range}
        is_pdf_initialised = False

        for (number_of_dice, number_of_faces) in dice_rolls:
            die_face_probability = 1 / number_of_faces
            single_die_range = range(1, number_of_faces + 1)
            single_die_pdf = {outcome: die_face_probability for outcome in single_die_range}

            if not is_pdf_initialised:
                pdf = single_die_pdf
                is_pdf_initialised = True
                convolution_count = number_of_dice - 1
            else:
                convolution_count = number_of_dice

            for outcome_index in range(convolution_count):
                pdf = convolution.convolve(pdf, single_die_pdf)

        return {key + modifier: value for key, value in pdf.items() if value != 0} # shift the pdf by the modifier

def calculate_mean(outcome_to_probability):
    """Calculate the mean dice outcome"""
    outcomes = list(outcome_to_probability.keys())
    probabilities = list(outcome_to_probability.values())
    mean_value = 0
    for i in range(len(outcomes)):
        mean_value += probabilities[i] * outcomes[i]
    mean_value = round(mean_value, 1)
    return mean_value

def calculate_cdf(outcome_to_probability):
        """Calculate the cumulative distribution function of a dice roll"""
        cumulative_probability = 0
        outcome_to_cumulative_probability = {}
        for outcome, probability in outcome_to_probability.items():
            cumulative_probability += probability
            outcome_to_cumulative_probability[outcome] = cumulative_probability
        return outcome_to_cumulative_probability

class dice_roll_toolbox:
    def __init__(self, dice_prompt="1d10+3"):
        # Always use dice_prompts, check if it's a single string or a dictionary
        if isinstance(dice_prompt, dict):
            self.is_dict_input = True
            self.dice_prompts = dice_prompt
            # For each level, calculate its PDF and store the result
            self.outcome_to_probability_dict = {
                level: calculate_pdf(*parse_dice_prompt(dice_prompt_string))  # unpack the output of parse_dice_prompt
                for level, dice_prompt_string in dice_prompt.items()
            }
        else:
            self.is_dict_input = False
            self.dice_prompts = {1: dice_prompt}  # Single dice prompt treated as level 1
            self.outcome_to_probability_dict = {
                1: calculate_pdf(*parse_dice_prompt(dice_prompt))  # unpack the output of parse_dice_prompt
            }

        # After initializing, calculate min/max outcomes and mean
        self.min_outcome = min(min(pdf.keys()) for pdf in self.outcome_to_probability_dict.values())
        self.max_outcome = max(max(pdf.keys()) for pdf in self.outcome_to_probability_dict.values())
        self.mean_outcome = {level: calculate_mean(pdf) for level, pdf in self.outcome_to_probability_dict.items()}

    def output_all_numerical_results(self):
        """Display all the numerical insights of the dice roll"""     
        for outcome, probability in self.outcome_to_cumulative_probability.items():
            cumulative_probability_percentage = probability * 100
            print(f"P({self.min_outcome} <= x <= {outcome}) = {cumulative_probability_percentage:.3f}%;        P({outcome} <= x <= {self.max_outcome}) = {100 - cumulative_probability_percentage:.3f}%")

    def output_select_numerical_results(self, y):
        """Display select numerical insights of the dice roll"""
        try:
           print(f"P({self.min_outcome} <= x <= {y}) = {self.outcome_to_cumulative_probability[y] * 100:.3f}%;        P({y} <= x <= {self.max_outcome}) = {(1 - self.outcome_to_cumulative_probability[y]) * 100:.3f}%")
        except KeyError:
           print("The value of y is out of range, i should write code to handle this")

    def plot_values(self, title=None, upgrade="Level"):
        """Plot values given an input dictionary with an optional title, and upgrade parameter, which means is the spell upgrading with player level or spell slot level"""
        fig, ax = plt.subplots(figsize=(6, 4))
        plt.tight_layout()

        if title:
            ax.set_title(title)  # Set custom title if provided

        # Get the unique levels from the dictionary keys
        levels = list(self.outcome_to_probability_dict.keys())
        num_levels = len(levels)  # Get the number of unique levels

        # Create a colormap
        colormap = plt.cm.magma

        if self.is_dict_input:
            # Plot multiple distributions if input is a dictionary
            for level in levels:
                outcome_to_probability = self.outcome_to_probability_dict[level]
                max_outcome = max(outcome_to_probability.keys())
                min_outcome = min(outcome_to_probability.keys())
                x_values = list(outcome_to_probability.keys())
                y_values = list(outcome_to_probability.values())
                bin_edges = numpy.arange(min(x_values) - 0.5, max(x_values) + 1.5, 1)
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

                # Normalize the level index to the range of the colormap
                color = colormap(levels.index(level) / (num_levels - 1))  # Normalize for gaps in levels
                color = (*color[:3], 0.4) # Add alpha channel to color
                # Plot histogram with Plasma colormap
                bars = ax.hist(x_values, bins=bin_edges, weights=y_values, label=f"Level {level} \u2208[{min_outcome}, {max_outcome}]; \u03BC={self.mean_outcome[level]}", edgecolor='black', color=color)

                # Plot the mean line using the same color as the bars
                ax.axvline(x=self.mean_outcome[level], color=color, linestyle='--')

            ax.legend(title=f"{upgrade}", loc='best', frameon=False)
        else:
            # Plot a single distribution
            level = list(self.dice_prompts.keys())[0]
            outcome_to_probability = self.outcome_to_probability_dict[level]
            x_values = list(outcome_to_probability.keys())
            y_values = list(outcome_to_probability.values())
            bin_edges = numpy.arange(min(x_values) - 0.5, max(x_values) + 1.5, 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            # Use the Plasma colormap for a single distribution
            color = colormap(0.5)  # Middle of the colormap for a single plot

            # Plot histogram with Plasma colormap
            bars = ax.hist(x_values, bins=bin_edges, weights=y_values, color=color, edgecolor='black', alpha=0.5)

            # Plot the mean line using the same color as the bars
            ax.axvline(x=self.mean_outcome[level], label=f"Mean = {self.mean_outcome[level]}", color=color, linestyle='--')
            ax.legend()

        ax.set_xlabel('Sum')
        ax.set_ylabel('% Occurrence')
        ax.grid(axis='y', linestyle='--', alpha=0.7)




if __name__ == "__main__":

    inflict_wounds_spell_slot_level_to_dice_prompt = {
        1: "3d10",
        2: "4d10",
        3: "5d10",
        4: "6d10"}
    inflict_wounds = dice_roll_toolbox(inflict_wounds_spell_slot_level_to_dice_prompt)
    inflict_wounds.plot_values(title=f"Inflict Wounds Damage Distribution", upgrade="Spell Slot Level") # Slot
    


    plt.show()
    
    

