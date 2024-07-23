from discord import Button, ButtonStyle, Interaction, SelectOption
from discord.ui import button, Select, View


class SelectOptions(Select):
    def __init__(
        self,
        option_titles: list,
        option_values: list,
        min_val: int = 1,
        max_val: int = 1,
    ):
        super().__init__(
            options=[
                SelectOption(
                    label=option_titles[i],
                    description=option_values[i],
                    value=option_values[i],
                )
                for i in range(len(option_titles))
            ],
            min_values=min_val,
            max_values=max_val,
        )

    async def callback(self, interaction: Interaction):
        self.view.clicked.extend(self.values)


class SelectOptionsView(View):
    def __init__(
        self,
        org_user: int,
        option_titles: list,
        option_values: list,
        min_val: int = 1,
        max_val: int = 1,
    ):
        super().__init__(timeout=600)

        self.org_user = org_user
        self.clicked = []
        self.min_val = min_val
        self.max_val = max_val

        for i in range(0, len(option_titles), 25):
            self.add_item(
                SelectOptions(
                    option_titles[i : i + 25],
                    option_values[i : i + 25],
                    min_val,
                    max_val,
                )
            )

    @button(label="Complete", style=ButtonStyle.green, row=4)
    async def submit(self, interaction: Interaction, button: Button):
        self.stop()

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return

        if len(self.clicked) == self.max_val:
            await interaction.send(f"Maximum selections is {self.max_val}!")
            return

        return True
