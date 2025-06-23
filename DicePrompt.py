"""
Class to represent a dice prompt
eg. 1d6, 2d10+3, 1d6+4d4+3
"""

import numpy as np
from convolution import convolve, fft_convolve
import random
from collections import defaultdict

class DicePrompt:
    def __init__(self, prompt_string="1d6", is_halved=False):
        self.is_halved = is_halved
        self.prompt_dice_terms, self.prompt_total_offset = self.parse_dice_prompt(prompt_string)
        self.prompt_string = self.get_prompt_string(self.prompt_dice_terms, self.prompt_total_offset)
        self.pdf = self.pdf()
        self.cdf = self.cdf()

    def parse_dice_prompt(self, prompt_string):
        """
        Parse dice prompt to return a list of dice roll prompts and total offset.
        Simplifies repeated dice, e.g. 1d6+1d6+1d8 -> 2d6+1d8.
        eg. 2d4+3+4d7+8 returns ([(2, 4), (4, 7)], 11)
        eg. 1d6 returns ([(1, 6)], 0)
        """
        prompt_string = prompt_string.replace('-', '+-')  # Handle negative offsets
        dice_roll_terms = prompt_string.split('+')
        
        dice_rolls = []
        total_offset = 0

        for dice_roll_term in dice_roll_terms:
            is_diceroll_term = 'd' in dice_roll_term
            if is_diceroll_term:  # dice roll, eg 4d5
                num_dice, num_faces = map(int, dice_roll_term.split('d'))
                dice_rolls.append((num_dice, num_faces))
            elif dice_roll_term.strip() != '':
                total_offset += int(dice_roll_term)
        
        # Simplify repeated dice by summing num_dice for each num_faces
        dice_dict = defaultdict(int)
        for num_dice, num_faces in dice_rolls:
            dice_dict[num_faces] += num_dice
        simplified_dice_rolls = [(num_dice, num_faces) for num_faces, num_dice in dice_dict.items() if num_dice > 0]
        # Sort for consistency (optional)
        simplified_dice_rolls.sort(key=lambda x: x[1])
        return simplified_dice_rolls, total_offset

    def get_prompt_string(self, prompt_dice_terms, prompt_total_offset):
        prompt_string = '+'.join([f"{num_dice}d{num_faces}" for num_dice, num_faces in prompt_dice_terms])
        if prompt_total_offset != 0:
            if prompt_total_offset > 0:
                prompt_string += f"+{prompt_total_offset}"
            else:
                prompt_string += f"{prompt_total_offset}"
        return prompt_string

    def pdf(self):
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

        if self.is_halved:
            halved_pdf = {}
            for outcome, prob in outcome_to_probability.items():
                halved_outcome = outcome // 2
                halved_pdf[halved_outcome] = halved_pdf.get(halved_outcome, 0) + prob
            return halved_pdf
    
        
        return outcome_to_probability

    def cdf(self):
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
    
    def __add__(self, other):
        if not isinstance(other, DicePrompt):
            return NotImplemented
        # Combine dice terms and offsets
        combined_prompt_dice_terms = self.prompt_dice_terms + other.prompt_dice_terms
        combined_prompt_total_offset = self.prompt_total_offset + other.prompt_total_offset
        # Build new prompt string
        combined_terms_string = '+'.join([f"{num_dice}d{num_faces}" for num_dice, num_faces in combined_prompt_dice_terms])
        if combined_prompt_total_offset != 0:
            if combined_prompt_total_offset > 0:
                combined_terms_string += f"+{combined_prompt_total_offset}"
            else:
                combined_terms_string += f"{combined_prompt_total_offset}"
        return DicePrompt(combined_terms_string)
    
    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply DicePrompt by an integer.")
        if other < 1:
            raise ValueError("Multiplier must be a positive integer.")
        multiplied_terms = [(num_dice * other, num_faces) for num_dice, num_faces in self.prompt_dice_terms]
        multiplied_offset = self.prompt_total_offset * other
        new_dice_prompt_string = self.get_prompt_string(multiplied_terms, multiplied_offset)
        return DicePrompt(new_dice_prompt_string)

    def __rmul__(self, other):
        return self.__mul__(other)

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
    
    def halved_pdf(self):
        """return the pdf of the outcome after having been halved"""
        min_halved_outcome = self.min() // 2
        max_halved_outcome = self.max() // 2
        halved_pdf = {outcome: 0 for outcome in range(min_halved_outcome, max_halved_outcome + 1)}
        for outcome, probability in self.pdf.items():
            halved_outcome = outcome // 2
            halved_pdf[halved_outcome] += probability
        return halved_pdf



if __name__ == '__main__':
    
    roll = DicePrompt("2d6")
    roll2 = DicePrompt("1d6+2d4+3")
    print(f"{roll} + {roll2} = {roll + roll2}")
    print(f"{roll} * 2 = {roll * 2}")
    print(f"{roll} * 3 = {roll * 3}")