from DicePrompt import DicePrompt
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick  
import seaborn as sns


MAX_SPELL_LEVEL = 9

class Spell:
    def __init__(self, name, starting_level=None, starting_damage_diceroll=None, damage_increment_diceroll=None, num_levels_per_damage_increase=None, hardcoded_level_to_diceroll=None, is_saving_throw=False, is_healing=False):
        self.name = name
        self.is_healing = is_healing
        self.starting_damage_diceroll = self.coerce_to_dice_prompt_type(starting_damage_diceroll)
        self.damage_increase_per_level = self.coerce_to_dice_prompt_type(damage_increment_diceroll)
        self.is_hardcoded = hardcoded_level_to_diceroll is not None
        if not self.is_hardcoded and starting_damage_diceroll is None:
            raise ValueError(f"No value Specified for starting damage diceroll")
        if self.is_hardcoded and (starting_damage_diceroll is not None or damage_increment_diceroll is not None or num_levels_per_damage_increase is not None):
            raise ValueError("Cannot specify both hardcoded_level_to_diceroll and (starting_damage_diceroll, damage_increment_diceroll, or num_levels_per_damage_increase)")
        if self.is_hardcoded:
            self.level_to_diceroll = self.calculate_level_to_diceroll(hardcoded_level_to_diceroll)
            self.level_increases = self.get_level_increases()
        if not self.is_hardcoded:
            self.starting_level = starting_level
            self.num_levels_per_damage_increase = num_levels_per_damage_increase
            self.level_to_diceroll = self.calculate_level_to_diceroll()
            self.level_increases = self.get_level_increases()
        self.is_halved_on_miss = is_saving_throw

    def coerce_to_dice_prompt_type(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return DicePrompt(value)
        elif isinstance(value, DicePrompt):
            return value
        else:
            raise ValueError("Value must be a string or a DicePrompt instance.")
        
    def calculate_level_to_diceroll(self, hardcoded_level_to_diceroll=None):
        """Calculate the level to diceroll mapping based on starting damage and increments."""

        if self.is_hardcoded:
            level_to_diceroll = {level: self.coerce_to_dice_prompt_type(dice_roll) for level, dice_roll in hardcoded_level_to_diceroll.items()}
            is_valid = all(isinstance(level, int) for level in level_to_diceroll.keys()) and all(isinstance(dice_roll, DicePrompt) for dice_roll in level_to_diceroll.values())
            if not is_valid:
                raise ValueError("Invalid values passed into hardcoded_level_to_diceroll")
            return level_to_diceroll
        elif not self.is_hardcoded and (self.starting_damage_diceroll is None or self.damage_increase_per_level is None or self.num_levels_per_damage_increase is None):
            raise ValueError("Cannot calculate level to diceroll mapping without starting damage, damage increment, and number of levels per increase. Use hardcoded_level_to_diceroll instead.")
        elif not self.is_hardcoded:
            level_to_diceroll = {}
            for level in range(self.starting_level, MAX_SPELL_LEVEL + 1):
                if level == self.starting_level:
                    level_to_diceroll[level] = self.starting_damage_diceroll
                else:
                    num_damage_increases = (level - self.starting_level) // self.num_levels_per_damage_increase
                    if num_damage_increases < 1:
                        level_to_diceroll[level] = self.starting_damage_diceroll
                    else:
                        new_damage_roll = self.starting_damage_diceroll + num_damage_increases * self.damage_increase_per_level
                        level_to_diceroll[level] = new_damage_roll
            return level_to_diceroll
        
    def get_damage_roll(self, level, is_critical_hit=False, is_miss=False):
        """For a given level, return the damage roll"""
        if (is_critical_hit and is_miss):
            raise ValueError("A spell cannot be both a critical hit and a miss at the same time.")

        if self.is_hardcoded:
            if level not in self.level_to_diceroll:
                # use highest available level less than or equal to `level`
                available_levels = [l for l in self.level_to_diceroll.keys() if l <= level]
                if not available_levels:
                    raise ValueError(f"No available hardcoded damage for level {level}")
                level = max(available_levels)
            base = self.level_to_diceroll[level]
            if is_critical_hit:
                return base * 2
            return base

        # default case: not hardcoded
        if level < self.starting_level:
            raise ValueError(f"Level cannot be less than the starting level of the spell ({self.starting_level}).")

        num_damage_increases = (level - self.starting_level) // self.num_levels_per_damage_increase
        if num_damage_increases < 1:
            return self.starting_damage_diceroll

        new_damage_roll = self.starting_damage_diceroll + num_damage_increases * self.damage_increase_per_level
        return new_damage_roll * 2 if is_critical_hit else new_damage_roll

        
    def get_level_increases(self):
        """
        return a list of levels where the spell sees an increased damage roll. 
        eg for a spell that starts at level 1 with a damage roll of 2d6, and increases to 3d6 at level 5, this would return [1, 5]
        """
        if self.is_hardcoded:
            starting_level = min(self.level_to_diceroll.keys())
            level_increases = [starting_level]
            previous_diceroll = self.level_to_diceroll[starting_level]
            for level, diceroll in self.level_to_diceroll.items():
                if diceroll != previous_diceroll:
                    level_increases.append(level)
                    previous_diceroll = diceroll
            return level_increases
        else:
            level_increases = [self.starting_level]
            previous_diceroll = self.starting_damage_diceroll
            for level in range(self.starting_level + 1, MAX_SPELL_LEVEL + 1):
                current_diceroll = self.get_damage_roll(level)
                if current_diceroll != previous_diceroll:
                    level_increases.append(level)
                    previous_diceroll = current_diceroll
            return level_increases

    def get_damage_distribution(self, level, enemy_ac, player_modifier):
        """ determines the probability of each possible damage outcome, inclusive of misses and critical hits"""

        if level < self.starting_level:
            raise ValueError(f"Level cannot be less than the starting level of the spell ({self.starting_level}).")
        if enemy_ac is None or player_modifier is None:
            raise ValueError("Both enemy AC and player modifier must be specified.")

        # misses happen when roll + mod < AC
        # hits happen when AC <= roll + mod (except on a roll of 20)
        # crits happen when roll = 20

        minimum_roll_to_hit = enemy_ac - player_modifier # roll has to make the difference and meets it beats it
        maximum_roll_to_miss = minimum_roll_to_hit - 1

        chance_to_crit = 1/20
        if minimum_roll_to_hit < 1: # if the player modifier is high enough to hit on a roll of 1
            minimum_roll_to_hit = 1
            chance_to_miss = 0
            chance_to_hit = 19/20
        elif minimum_roll_to_hit > 19: # if the player modifier is so low that they can never hit (therefore can only hit on a crit)
            chance_to_miss = 19/20
            chance_to_hit = 0
        else:
            chance_to_miss = maximum_roll_to_miss / 20
            chance_to_hit = 1 - chance_to_miss - chance_to_crit

        hit_damage_pdf = self.get_damage_roll(level).pdf
        crit_damage_pdf = self.get_damage_roll(level, is_critical_hit=True).pdf
        miss_damage_pdf = self.get_damage_roll(level).halved_pdf() if self.is_halved_on_miss else {0: 1.0}  

        all_outcomes = set(hit_damage_pdf.keys()).union(set(crit_damage_pdf.keys())).union(set(miss_damage_pdf.keys()))
        pdf = {outcome: 0 for outcome in all_outcomes}

        # add all the probabilities with matching keys, being mindfil that keys may be missing from some distributions
        for outcome in all_outcomes:
            pdf[outcome] = (hit_damage_pdf.get(outcome, 0)*chance_to_hit + 
                            crit_damage_pdf.get(outcome, 0)*chance_to_crit + 
                            miss_damage_pdf.get(outcome, 0)*chance_to_miss)

        return pdf

    def plot_damage(self, max_level=MAX_SPELL_LEVEL, x_tick_interval=None, colormap = plt.cm.plasma, show=False):
        level_to_damage_roll = {level: self.get_damage_roll(level) for level in self.level_increases if level <= max_level}

        fig = plt.figure(figsize=(7, 5))  # Adjusted figure size
        gs = gridspec.GridSpec(2, 1, height_ratios=[0.2, 1])  # 2 rows, top section smaller
        ax_title = fig.add_subplot(gs[0])  # Top row for title & legend
        ax_plot = fig.add_subplot(gs[1])   # Bottom row for histogram

        if self.name:
            title = r"$\bf{" + self.name.replace(" ", r"\ ")  + r"}$" + "\nDamage Distribution\n"
            ax_title.text(0, 0.5, title, fontsize=16, ha='left', va='center', wrap=True)

        
        levels = list(level_to_damage_roll.keys())

        for level, dice_roll in level_to_damage_roll.items():
            pdf = dice_roll.pdf
            x_values = list(pdf.keys())
            y_values = [value * 100 for value in list(pdf.values())]  # Convert to percentage
            color = colormap(levels.index(level) / (len(levels)) if len(levels) > 1 else 0.5)
            bin_edges = np.arange(min(x_values) - 0.5, max(x_values) + 1.5, 1)

            mean_value = dice_roll.mean()
            label = rf"{level} $\in$ [{min(x_values)}, {max(x_values)}]; $\mu$={mean_value}"
            plot_label = r"$\mu_{" + str(level) + "}$" 
            ax_plot.hist(x_values, bins=bin_edges, weights=y_values, label=label, color=color, edgecolor='black', alpha=0.4, zorder=100)
            ax_plot.axvline(x=mean_value, color='black', linestyle='--', ymax=0.97)


            ax_plot.text(
                        mean_value,
                        ax_plot.get_ylim()[1] * 0.99,
                        f"{mean_value:.1f}".rstrip('0').rstrip('.'),
                        ha='center',
                        va='bottom',
                        fontsize=9,
                        color='black',
                        bbox=dict(
                            boxstyle='round,pad=0.15',
                            facecolor=color,
                            edgecolor='none',
                            alpha=0.3  # Adjust transparency to your liking
                        )
                    )
            
            ax_plot.text(
                        mean_value,
                        ax_plot.get_ylim()[1] * 1.045,
                        plot_label,
                        ha='center',
                        va='bottom',
                        fontsize=9,
                        color='black',
                        bbox=dict(
                            boxstyle='round,pad=0.15',
                            facecolor=color,
                            edgecolor='none',
                            alpha=0.3  # Adjust transparency to your liking
                        )
                    )



        ax_plot.yaxis.set_major_formatter(mtick.PercentFormatter())  # Converts axis labels to percentages
        ax_plot.spines["top"].set_visible(False)    
        ax_plot.spines["right"].set_visible(False)  

        ax_plot.legend(loc='lower right', frameon=False, bbox_to_anchor=(1.1, 0.5), fontsize=11)

        ax_title.set_xticks([])
        ax_title.set_yticks([])
        ax_title.spines['top'].set_visible(False)
        ax_title.spines['right'].set_visible(False)
        ax_title.spines['bottom'].set_visible(False)
        ax_title.spines['left'].set_visible(False)

        # **Axis Labels & Grid**
        ax_plot.set_xlabel('Damage Outcome')
        ax_plot.set_ylabel('% Occurrence')
        # ax_plot.grid(axis='y', linestyle='--', alpha=0.7)

        if x_tick_interval is not None:
            # Compute min and max x-values from all plotted distributions
            all_x_values = [x for dice_roll in level_to_damage_roll.values() for x in dice_roll.pdf.keys()]
            min_x = min(all_x_values)
            max_x = max(all_x_values)
            ax_plot.set_xticks(np.arange(x_tick_interval * round(float(min_x) / x_tick_interval), max_x + 1, x_tick_interval))
        if show:
            plt.show()

    def boxplot_damage(self, max_level=MAX_SPELL_LEVEL, colormap=plt.cm.plasma, show=False):

        sns.set_style("white")

        level_to_damage_roll = {
            level: self.get_damage_roll(level)
            for level in self.level_increases
            if level <= max_level
        }
        levels = sorted(level_to_damage_roll.keys())

        fig = plt.figure(figsize=(7, 5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[0.2, 1])
        ax_title = fig.add_subplot(gs[0])
        ax_plot = fig.add_subplot(gs[1])

        # Title
        title = r"$\bf{" + self.name.replace(" ", r"\ ") + r"}$"
        title += "\nHealing Distribution" if getattr(self, 'is_healing', False) else "\nDamage Distribution"
        ax_title.text(0, 0.5, title, fontsize=16, ha='left', va='center', wrap=True)

        data = []
        box_colors = []
        for level in levels:
            dice_roll = level_to_damage_roll[level]
            pdf = dice_roll.pdf

            samples = []
            for value, prob in pdf.items():
                count = max(1, int(prob * 10000))  # ensures every value appears at least once
                samples.extend([value] * count)

            data.append(samples)

            idx = levels.index(level)
            color = colormap(idx / (len(levels) - 1) if len(levels) > 1 else 0.5)
            box_colors.append(color)

        positions = np.arange(len(levels), 0, -1)

        # KDE overlays first (zorder=1)
        for samples, y_pos, color in zip(data, positions, box_colors):
            sns.kdeplot(
                samples,
                ax=ax_plot,
                bw_adjust=1,
                fill=True,
                linewidth=1,
                alpha=0.5,
                color=color,
                clip=(min(samples), max(samples)),
                zorder=1,
            )
            # Shift KDE vertically to align with y_pos
            for coll in ax_plot.collections[-1:]:  # only last KDE
                path = coll.get_paths()[0]
                vertices = path.vertices
                vertices[:, 1] = y_pos + vertices[:, 1] / np.max(vertices[:, 1]) * 0.3  # scale + align vertically

        # Boxplot layer (zorder=3)
        boxplots = ax_plot.boxplot(
            data,
            vert=False,
            positions=positions,
            patch_artist=True,
            widths=0.3,
            boxprops=dict(color='black'),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black'),
            medianprops=dict(color='black'),
            showfliers=False,  
            whis=[5, 95],       # whiskers from 5th to 95th percentile
        )

        for patch in boxplots['boxes']:
            patch.set_facecolor((0, 0, 0, 0))  # Fully transparent
            patch.set_edgecolor('black')      # Solid black outline

        # Y-axis labels
        ax_plot.set_yticks(positions)
        ax_plot.set_yticklabels([f"Level {level}" for level in levels])

        # Annotate 7-number summary: min, 5%, Q1, median, Q3, 95%, max
        for i, level in enumerate(levels):
            samples = sorted(data[i])
            y_pos = positions[i]
            color = box_colors[i]

            summary_points = [
                np.percentile(samples, 0),
                np.percentile(samples, 5),
                np.percentile(samples, 25),
                np.percentile(samples, 50),
                np.percentile(samples, 75),
                np.percentile(samples, 95),
                np.percentile(samples, 100),
            ]

            for x in summary_points:
                ax_plot.text(
                    x,
                    y_pos + 0.35,
                    f"{x:.1f}".rstrip("0").rstrip("."),
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color='black',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor=color, edgecolor='none', alpha=0.3),
                    zorder=5
                )


        # Axis + styling
        ax_plot.set_xlabel("Healing Outcome" if getattr(self, 'is_healing', False) else "Damage Outcome")
        ax_plot.grid(axis='x', linestyle='--', alpha=0.3)
        ax_plot.spines["top"].set_visible(False)
        ax_plot.spines["right"].set_visible(False)
        ax_plot.set_ylabel("Spell Level")

        ax_title.set_xticks([])
        ax_title.set_yticks([])
        for spine in ax_title.spines.values():
            spine.set_visible(False)

        plt.tight_layout()
        if show:
            plt.show()

        return fig, ax_plot


            
if __name__ == '__main__':

    # Spell save DC = 8 + your proficiency bonus + your Wisdom modifier 
    # Spell attack modifier = your proficiency bonus + your Wisdom modifier

    spell = Spell(
        name="Inflict Wounds",
        starting_level=1,
        starting_damage_diceroll="3d10",
        damage_increment_diceroll="1d10",
        num_levels_per_damage_increase=1,
        is_saving_throw=False
    )

    

    spell2 = Spell(
        name="My Hardcoded Spell",
        hardcoded_level_to_diceroll={
            1: "2d6",
            5: "3d6",
            9: "4d6"
        }
    )

    # spell2.plot_damage(max_level=10, x_tick_interval=1, show=True)
    spell.boxplot_damage(show=True)

