from discord import ButtonStyle, Embed, Interaction, SelectOption
from discord.ui import Button, View, button, Select
from discord.ext import tasks
import time

from article_overload.bot import ArticleOverloadBot
from article_overload.db.objects import Article
from utils.game_classes import Game
from article_overload.constants import COLOR_GOOD, COLOR_BAD, CORRECT_ANSWER_POINTS

class SentenceSelect(Select):
    CHAR_LIMIT = 100
    def __init__(self, sentences: list[str]):
        super().__init__(placeholder="Select a sentence", options=[SelectOption(label=question[:self.CHAR_LIMIT], value=question[:self.CHAR_LIMIT]) for question in sentences])

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
    def __init__(self, og_interaction: Interaction, client: ArticleOverloadBot, article: Article, game: Game):
        super().__init__()
        self.og_interaction = og_interaction
        self.client = client
        self.article = article
        self.game = game

        self.player = self.game.get_player(self.og_interaction.user.id)
        
        self.sentence_selection = SentenceSelect(self.article.questions)
        self.add_item(self.sentence_selection)

        self.check_time.start()

    @button(label="Submit", style=ButtonStyle.green)
    async def submit_answer(self, interaction: Interaction, _: Button):
        await interaction.response.defer()

        self.game.stop_article_timer()

        if self.sentence_selection.values[0] == self.article.false_statement:
            self.player.update_score(CORRECT_ANSWER_POINTS)
            embed = Embed(title="Correct!", description=f"You have correctly deduced the false statement from the article! You gained {CORRECT_ANSWER_POINTS} points and your score is now {self.player.get_score()}. Press continue to move on", color=COLOR_GOOD)

        else:
            embed = Embed(title="Incorrect!", description="You did not select the false statement correctly! No points for you! Press continue to move on", color=COLOR_BAD)

        continue_button = ContinueButton()
        
        await interaction.edit_original_response(embed=embed, view=continue_button)
        await continue_button.wait()

        self.article = await self.client.database_handler.get_random_article()
        self.remove_item(self.sentence_selection)
        self.sentence_selection = SentenceSelect(self.article.questions)
        self.add_item(self.sentence_selection)
        
        embed = Embed(title="Article Overload!", description=f"Please read the following article summary and use the select menu below to choose which sentence is false:\n\n{self.article.marked_up_summary}")
        
        self.game.start_article_timer()

        await interaction.edit_original_response(embed=embed, view=self)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.og_interaction.user.id:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False
        
        return True
    
    @tasks.loop(seconds=0.5)
    async def check_time(self):
        if self.game.get_article_timer() == 0:
            self.game.end_game()

            self.client.games.pop(self.og_interaction.user.id)

            embed = Embed(title="Game Over!", description=f"You ran out of time! Here are your statistics from this game:\nScore: {self.player.get_score()}\nGame Time: {self.game.get_game_duration()}")

            await self.og_interaction.edit_original_response(embed=embed, view=None)

            self.check_time.stop()