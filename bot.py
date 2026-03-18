import discord
from discord.ext import commands
from blackjack import BlackjackGame
from currency import get_balance
import os
import keep_alive  # keeps bot alive for uptime robot

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

games = {}  # user_id -> BlackjackGame

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Check CP balance
@bot.slash_command(name="cp", description="Check your CP balance")
async def check_cp(ctx: discord.ApplicationContext):
    balance = get_balance(ctx.user.id)
    await ctx.respond(f"You have **{balance} CP**.")

# Start a blackjack game with a bet
@bot.slash_command(name="blackjack", description="Play blackjack with a CP bet")
async def blackjack_bet(ctx: discord.ApplicationContext, bet: int = 10):
    if bet < 1:
        await ctx.respond("Bet must be at least 1 CP!")
        return
    from currency import get_balance
    if bet > get_balance(ctx.user.id):
        await ctx.respond("You don't have enough CP!")
        return
    if ctx.user.id in games:
        await ctx.respond("You already have a game running!")
        return

    game = BlackjackGame(player_id=ctx.user.id, bet=bet)
    games[ctx.user.id] = game
    await ctx.respond(embed=game.render_embed(), view=game.render_buttons(bot, games))

bot.run(os.getenv("DISCORD_TOKEN"))
