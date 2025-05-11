import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick  # Formatter for percentage axis
from dice_prompt import DicePrompt


class Spell:
    def __init__(self, dice_prompts):
        """
        Initialize the Spell class.
        Args:
            dice_prompts: Either a single DicePrompt instance or a dictionary of {level: DicePrompt}
        """
        if isinstance(dice_prompts, str):
            dice_prompts = DicePrompt(dice_prompts)
            self.level_to_dice_prompt = {1: dice_prompts}
        if isinstance(dice_prompts, DicePrompt):  
            self.level_to_dice_prompt = {1: dice_prompts}
        elif isinstance(dice_prompts, dict):  
            self.level_to_dice_prompt = {
                level: (prompt if isinstance(prompt, DicePrompt) else DicePrompt(prompt))
                for level, prompt in dice_prompts.items()
            }
        else:
            raise ValueError("Input must be a DicePrompt instance or a dictionary of DicePrompt instances.")

        # Extract PDFs and means for each level
        self.level_to_pdf_dict = {
            level: prompt.pdf for level, prompt in self.level_to_dice_prompt.items()
        }
        self.level_to_mean = {
            level: prompt.mean() for level, prompt in self.level_to_dice_prompt.items()
        }

        # Determine min and max outcomes across all levels
        self.level_to_min = min(prompt.min() for prompt in self.level_to_dice_prompt.values())
        self.level_to_max = max(prompt.max() for prompt in self.level_to_dice_prompt.values())

    def plot_values(self, name=None, upgrade="Level", x_tick_interval=None, title_wrap_width=40):
        """
        Plot probability distributions of the spell's outcomes.
        Args:
            name (str): The name of the spell.
            upgrade (str): Label for the legend (e.g., "Spell Slot Level").
            x_tick_interval (int): Interval for X-axis ticks.
            title_wrap_width (int): Max characters per line before wrapping title.
        """
        fig = plt.figure(figsize=(7, 5))  # Adjusted figure size
        gs = gridspec.GridSpec(2, 1, height_ratios=[0.2, 1])  # 2 rows, top section smaller
        ax_title = fig.add_subplot(gs[0])  # Top row for title & legend
        ax_plot = fig.add_subplot(gs[1])   # Bottom row for histogram

        if name:
            title = r"$\bf{" + name.replace(" ", r"\ ")  + r"}$" + "\nDamage Distribution\n"
            ax_title.text(0, 0.5, title, fontsize=16, ha='left', va='center', wrap=True)

        colormap = plt.cm.magma  
        levels = list(self.level_to_dice_prompt.keys())

        for level in levels:
            pdf = self.level_to_pdf_dict[level]
            x_values = list(pdf.keys())
            y_values = [value * 100 for value in list(pdf.values())]  # Convert to percentage
            color = colormap(levels.index(level) / (len(levels) - 1) if len(levels) > 1 else 0.5)
            bin_edges = np.arange(min(x_values) - 0.5, max(x_values) + 1.5, 1)

            label = rf"{level} $\in$ [{min(x_values)}, {max(x_values)}]; $\mu$={self.level_to_mean[level]}"
            ax_plot.hist(x_values, bins=bin_edges, weights=y_values, label=label, color=color, edgecolor='black', alpha=0.4, zorder=100)
            ax_plot.axvline(x=self.level_to_mean[level], color=color, linestyle='--')

        # ax_plot.set_yscale('log')  # this is funny
        ax_plot.yaxis.set_major_formatter(mtick.PercentFormatter())  # Converts axis labels to percentages
  
        # **Remove Unnecessary Spines**
        ax_plot.spines["top"].set_visible(False)    
        ax_plot.spines["right"].set_visible(False)  

        # **Legend Formatting**
        ax_plot.legend(loc='lower right', frameon=False, bbox_to_anchor=(1, 1), fontsize=11)

        # **Remove axis from the title section**
        ax_title.set_xticks([])
        ax_title.set_yticks([])
        ax_title.spines['top'].set_visible(False)
        ax_title.spines['right'].set_visible(False)
        ax_title.spines['bottom'].set_visible(False)
        ax_title.spines['left'].set_visible(False)

        # **Axis Labels & Grid**
        ax_plot.set_xlabel('Sum')
        ax_plot.set_ylabel('% Occurrence')
        ax_plot.grid(axis='y', linestyle='--', alpha=0.7)

        if x_tick_interval is not None:
            ax_plot.set_xticks(np.arange(x_tick_interval * round(float(self.level_to_min) / x_tick_interval), self.level_to_max + 1, x_tick_interval))

        plt.show()


if __name__ == "__main__":
    # Example: Fireball spell with different slot levels
    fireball_spell_slot_to_dice_prompt = {
        3: DicePrompt("8d6"),
        4: DicePrompt("9d6"),
        5: DicePrompt("10d6"),
        6: DicePrompt("11d6")
    }
    fireball = Spell(fireball_spell_slot_to_dice_prompt)
    fireball.plot_values(name="Fireball", upgrade="Spell Slot Level", x_tick_interval=5)

    plt.show()
