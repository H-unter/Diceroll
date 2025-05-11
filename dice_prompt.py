"""
Class to represent a dice prompt
eg. 1d6, 2d10+3, 1d6+4d4+3
"""

import numpy as np
from convolution import convolve, fft_convolve
import random

class DicePrompt:
    def __init__(self, prompt_string="1d6"):
        self.prompt_string = prompt_string
        self.prompt_dice_terms, self.prompt_total_offset = self.parse_dice_prompt(prompt_string)
        self.pdf = self.calculate_pdf()
        self.cdf = self.calculate_cdf()
        
    def parse_dice_prompt(self, prompt_string):
        """
        Parse dice prompt to return a list of dice roll prompts and total offset
        eg. 2d4+3+4d7+8 returns ([(2, 4), (4, 7)], 11)
        eg. 1d6 returns ([(1, 6)], 0)
        """
        prompt_string = prompt_string.replace('-', '+-')  # Handle negative offsets
        dice_roll_terms = prompt_string.split('+')
        
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

    def calculate_pdf(self):
        """
        Get the probability density function of the dice roll in the form of a dictionary, outcome_to_probability"
        """
        outcome_to_probability = {outcome: 0 for outcome in range(1, self.max() + 1)}
        is_pdf_initialised = False
        # iterate through prompt dice terms and convolve outcome_to_probability with the dice roll pdf
        for num_dice, num_faces in self.prompt_dice_terms:
            dice_outcome_to_probability = {outcome: 1/num_faces for outcome in range(1, num_faces + 1)}
            for dice_index in range(num_dice):
                if not is_pdf_initialised:
                    outcome_to_probability = dice_outcome_to_probability
                    is_pdf_initialised = True
                else:
                    outcome_to_probability = convolve(outcome_to_probability, dice_outcome_to_probability)
        # add the total offset to the outcome
        outcome_to_probability = {outcome + self.prompt_total_offset: probability for outcome, probability in outcome_to_probability.items()}
        return outcome_to_probability

    def calculate_cdf(self):
        """
        Get the cumulative density function of the dice roll in the form of a dictionary, outcome_to_cumulative_probability"
        """
        cdf = {}
        cumulative_probability = 0
        for outcome in sorted(self.pdf.keys()):
            cumulative_probability += self.pdf[outcome]
            cdf[outcome] = cumulative_probability
        return cdf
    
    def __repr__(self):
        return f"{self.prompt_string}"
    def __str__(self):
        return f"{self.prompt_string}"
    def max(self):
        return sum([num_dice * num_faces for num_dice, num_faces in self.prompt_dice_terms]) + self.prompt_total_offset
    def mean(self):
        return round(sum(num_dice * (num_faces + 1) / 2 for num_dice, num_faces in self.prompt_dice_terms) + self.prompt_total_offset, 1)
    def min(self):
        return sum([num_dice for num_dice, num_faces in self.prompt_dice_terms]) + self.prompt_total_offset
    def outcomes(self):
        """return a list of the possible outcomes"""
        return list(range(self.min(), self.max() + 1))
    
    def roll(self, show_outcome=True):
        """roll the dice prompt and return the outcome"""
        outcome = 0
        for num_dice, num_faces in self.prompt_dice_terms:
            for roll_index in range(num_dice):
                outcome += random.randint(1, num_faces)
        outcome += self.prompt_total_offset
        if show_outcome:
            print(f"Rolled {self.prompt_string} = {outcome}")
        return outcome



if __name__ == '__main__':
    
    roll = DicePrompt("1d6")
    # roll the dice 1000 times and plot the histogram
    outcomes = [roll.roll() for _ in range(1000)]
    import matplotlib.pyplot as plt
    plt.hist(outcomes, bins=range(roll.min(), roll.max() + 2), density=True, alpha=0.5, color='blue', edgecolor='black')
    plt.show()
    print(roll.mean())
    