from discord import ButtonStyle, Interaction, SelectOption
from discord.ext import tasks
from discord.ui import Button, Select, View, button
from utils.game_classes import Game

from article_overload.bot import ArticleOverloadBot
from article_overload.constants import MAX_INCORRECT
from article_overload.db.objects import Article
from article_overload.tools.embeds import (
    create_article_embed,
    create_correct_answer_embed,
    create_error_embed,
    create_incorrect_answer_embed,
    create_time_up_embed,
    create_too_many_incorrect_embed,
)


class SentenceSelect(Select):
    """Sentence select menu class."""

    CHAR_LIMIT = 97

    def __init__(self, sentences: list[str]) -> None:
        """Subclass of Select.

        Description: Initializes a subclass of a select menu to allow a user to select sentences.
        :Return: None
        """
        super().__init__(
            placeholder="Select a sentence",
            options=[
                SelectOption(label=f"{n + 1}: {question[:self.CHAR_LIMIT]}", value=question[: self.CHAR_LIMIT])
                for n, question in enumerate(sentences)
            ],
        )

    async def callback(self, interaction: Interaction) -> None:
        """Select callback.

        Description: Callback to check if a sentence was selected.
        :Return: None
        """
        await interaction.response.defer()


class ContinueButton(View):
    """Continue button view class."""

    def __init__(self) -> None:
        """Subclass of View.

        Description: Initializes View subclass for a button that moves to next question in game.
        :Return: None
        """
        super().__init__()

    @button(label="Next Question")
    async def continue_question(self, interaction: Interaction, _: Button) -> None:
        """Button callback.

        Description: Callback to see if button was pressed.
        :Return: None
        """
        await interaction.response.defer()

        self.stop()


class GameView(View):
    """Game view class."""

    def __init__(
        self,
        og_interaction: Interaction,
        article: Article,
        game: Game,
        client: ArticleOverloadBot,
    ) -> None:
        """Subclass of View.

        Description: Initializes View subclass to create a game view.
        :Return: None
        """
        super().__init__()
        self.og_interaction = og_interaction
        self.client = client
        self.article = article
        self.game = game

        self.player = self.game.get_player(self.og_interaction.user.id)

        self.sentence_selection = SentenceSelect(self.article.questions)
        self.add_item(self.sentence_selection)

        self.check_time.start()

    @button(label="Submit", style=ButtonStyle.green, row=1)
    async def submit_answer(self, interaction: Interaction, _: Button) -> None:
        """Button callback.

        Description: Callback to see if user wants to submit their answer.
        :Return: None
        """
        await interaction.response.defer()

        if len(self.sentence_selection.values) == 0:
            return await interaction.followup.send(
                embed=create_error_embed(
                    title="Select an Answer!",
                    description="Please select an answer choice using the select menu!",
                    ephemeral=True,
                ),
            )

        self.game.stop_article_timer()

        if self.sentence_selection.values[0] == self.article.false_statement:  # noqa: PD011
            self.player.add_correct()
            embed = create_correct_answer_embed(self.player)

        else:
            self.player.add_incorrect()
            embed = create_incorrect_answer_embed(self.player, self.article)

        if self.player.incorrect == MAX_INCORRECT:
            self.check_time.stop()
            return await interaction.edit_original_response(
                embed=create_too_many_incorrect_embed(self.player, self.game),
                view=None,
            )

        continue_button = ContinueButton()

        await interaction.edit_original_response(embed=embed, view=continue_button)
        await continue_button.wait()

        self.article = await self.client.database_handler.get_random_article()
        self.remove_item(self.sentence_selection)
        self.sentence_selection = SentenceSelect(self.article.questions)
        self.add_item(self.sentence_selection)

        self.game.start_article_timer()

        embed = create_article_embed(self.article, self.player, self.game)

        return await interaction.edit_original_response(embed=embed, view=self)

    async def interaction_check(self, interaction: Interaction) -> None:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.og_interaction.user.id:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False

        return True

    @tasks.loop(seconds=0.5)
    async def check_time(self) -> None:
        """Time check loop.

        Description: Checks to see if user has time to answer the questions of an article.
        :Return: None
        """
        if self.game.article_timer_active and self.game.get_article_timer() == 0:
            self.game.end_game()

            self.client.games.pop(self.og_interaction.user.id)

            embed = create_time_up_embed(self.player, self.game)

            await self.og_interaction.edit_original_response(embed=embed, view=None)

            self.check_time.stop()