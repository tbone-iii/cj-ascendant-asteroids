from discord import ButtonStyle, Embed, Interaction, SelectOption
from discord.ui import Button, View, button, Select
from discord.ext import tasks

from article_overload.bot import ArticleOverloadBot
from article_overload.db.objects import Article
from article_overload.tools.embeds import create_article_embed, create_error_embed, create_time_up_embed, create_too_many_incorrect_embed
from utils.game_classes import Game, Player
from article_overload.constants import COLOR_GOOD, COLOR_BAD, CORRECT_ANSWER_POINTS

class SentenceSelect(Select):
    CHAR_LIMIT = 97
    def __init__(self, sentences: list[str]):
        super().__init__(placeholder="Select a sentence", options=[SelectOption(label=f"{n + 1}: {question[:self.CHAR_LIMIT]}", value=question[:self.CHAR_LIMIT]) for n, question in enumerate(sentences)])

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

class ContinueButton(View):
    def __init__(self):
        super().__init__()

    @button(label="Next Question")
    async def continue_question(self, interaction: Interaction, _: Button):
        await interaction.response.defer()

        self.stop()

class GameView(View):
    def __init__(self, og_interaction: Interaction, article: Article, player: Player, game: Game, client: ArticleOverloadBot):
        super().__init__()
        self.og_interaction = og_interaction
        self.client = client
        self.article = article
        self.game = game

        self.player = player
        
        self.sentence_selection = SentenceSelect(self.article.questions)
        self.add_item(self.sentence_selection)

        self.check_time.start()

    @button(label="Submit", style=ButtonStyle.green, row=1)
    async def submit_answer(self, interaction: Interaction, _: Button) -> None:
        await interaction.response.defer()

        if len(self.sentence_selection.values) == 0:
            return await interaction.followup.send(embed=create_error_embed(title="Select an Answer!", description="Please select an answer choice using the select menu!", ephemeral=True))

        self.game.stop_article_timer()

        if self.sentence_selection.values[0] == self.article.false_statement:
            self.player.add_correct()
            embed = Embed(title="Correct!", description=f"You have correctly deduced the false statement from the article! You gained {CORRECT_ANSWER_POINTS} points and your score is now {self.player.get_score()}. Press continue to move on", color=COLOR_GOOD)

        else:
            self.player.add_incorrect()
            embed = Embed(title="Incorrect!", description=f"You did not select the false statement correctly! No points for you! Press continue to move on\n\nCorrect Answer: {self.article.highlight_answer_in_summary}", color=COLOR_BAD)

        if self.player.incorrect == 3:
            self.check_time.stop()
            return await interaction.edit_original_response(embed=create_too_many_incorrect_embed(self.player, self.game), view=None)
        
        continue_button = ContinueButton()
        
        await interaction.edit_original_response(embed=embed, view=continue_button)
        await continue_button.wait()

        self.article = await self.client.database_handler.get_random_article()
        self.remove_item(self.sentence_selection)
        self.sentence_selection = SentenceSelect(self.article.questions)
        self.add_item(self.sentence_selection)

        self.game.start_article_timer()

        embed = create_article_embed(self.article, self.player.get_player_id(), self.game)

        await interaction.edit_original_response(embed=embed, view=self)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.og_interaction.user.id:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False
        
        return True
    
    @tasks.loop(seconds=0.5)
    async def check_time(self):
        if self.game.article_timer_active and self.game.get_article_timer() == 0:
            self.game.end_game()

            self.client.games.pop(self.og_interaction.user.id)

            embed = create_time_up_embed(self.player, self.game)

            await self.og_interaction.edit_original_response(embed=embed, view=None)

            self.check_time.stop()