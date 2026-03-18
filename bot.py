import discord
from discord.ext import commands
from blackjack import BlackjackGame
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Track active games: user_id -> BlackjackGame
games = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(name="blackjack", description="Start a game of blackjack")
async def blackjack(ctx: discord.ApplicationContext):
    if ctx.user.id in games:
        await ctx.respond("You already have a game running!")
        return

    game = BlackjackGame(player_id=ctx.user.id)
    games[ctx.user.id] = game
    embed = game.render_embed()
    view = game.render_buttons(bot, games)
    await ctx.respond(embed=embed, view=view)

bot.run(os.getenv("DISCORD_TOKEN"))
