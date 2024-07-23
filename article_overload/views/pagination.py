from discord import Button, ButtonStyle, Interaction, SelectOption
from discord.ui import button, Select, View


class PaginationSelect(Select):
    def __init__(self, data: list, full_data: list, page: int = 0):
        super().__init__(
            options=[
                SelectOption(
                    label=i["title"], description=i["description"], value=i["num"]
                )
                for i in data
            ]
        )

        self.full_data = full_data
        self.page = page

    async def callback(self, interaction: Interaction):
        await interaction.edit(
            embed=self.full_data[int(self.values[0]) - 1]["embed"],
            view=PaginationView(
                interaction.user.id, self.full_data, page=int(self.values[0]) - 1
            ),
        )


class PaginationView(View):
    def __init__(self, org_user: int, data: list, page: int):
        super().__init__(timeout=600)

        self.org_user = org_user

        self.data = data

        self.page = page

        for i in range(0, len(data), 25):
            self.add_item(PaginationSelect(data[i : i + 25], self.data, page))

    @button(emoji="<:left_arrow:1049429857488093275>", style=ButtonStyle.blurple)
    async def left_arrow(self, button: Button, interaction: Interaction):
        self.page -= 1 if self.page > 0 else 0
        await self.update_page(interaction)
        return

    @button(emoji="<:right_arrow:1049430086257999882>", style=ButtonStyle.blurple)
    async def right_arrow(self, button: Button, interaction: Interaction):
        self.page += 1 if self.page < len(self.data) - 1 else 0
        await self.update_page(interaction)
        return

    async def update_page(self, interaction: Interaction):
        await interaction.edit(embed=self.data[self.page]["embed"])

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return

        return True
