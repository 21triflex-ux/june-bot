import random
import discord
from currency import add_balance, remove_balance, get_balance

class BlackjackGame:
    def __init__(self, player_id, bet=10):
        self.player_id = player_id
        self.bet = bet
        # Deduct bet from user balance
        if get_balance(player_id) < bet:
            raise ValueError("Not enough CP to bet")
        remove_balance(player_id, bet)

        self.deck = self.create_deck()
        self.player_hands = [[]]  # support splits
        self.player_bets = [bet]
        self.dealer_hand = []
        self.current_hand = 0
        self.finished = False
        self.result = ""
        self.initial_deal()

    def create_deck(self):
        suits = ["♠","♥","♦","♣"]
        values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
        deck = [f"{v}{s}" for v in values for s in suits]
        random.shuffle(deck)
        return deck

    def initial_deal(self):
        for hand in self.player_hands:
            hand.append(self.deck.pop())
            hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())

    def hand_value(self, hand):
        value, aces = 0, 0
        for card in hand:
            rank = card[:-1]
            if rank in ["J","Q","K"]:
                value += 10
            elif rank == "A":
                value += 11
                aces += 1
            else:
                value += int(rank)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def render_embed(self):
        embed = discord.Embed(title="Blackjack")
        for i, hand in enumerate(self.player_hands):
            status = " (Current)" if i == self.current_hand else ""
            embed.add_field(
                name=f"Your Hand {i+1}{status}", 
                value=f"{' '.join(hand)} = {self.hand_value(hand)}", 
                inline=False
            )
        dealer_display = f"{self.dealer_hand[0]} ❓"
        embed.add_field(name="Dealer Hand", value=dealer_display, inline=False)
        embed.add_field(name="Your CP Balance", value=f"{get_balance(self.player_id)} CP", inline=False)
        if self.result:
            embed.add_field(name="Result", value=self.result, inline=False)
        return embed

    def render_buttons(self, bot, games):
        view = discord.ui.View(timeout=None)

        async def hit_callback(interaction):
            hand = self.player_hands[self.current_hand]
            hand.append(self.deck.pop())
            if self.hand_value(hand) > 21:
                self.next_hand_or_end(games)
            await interaction.response.edit_message(embed=self.render_embed(), view=self.render_buttons(bot, games))

        async def stand_callback(interaction):
            self.next_hand_or_end(games)
            await interaction.response.edit_message(embed=self.render_embed(), view=self.render_buttons(bot, games))

        async def double_callback(interaction):
            hand = self.player_hands[self.current_hand]
            self.player_bets[self.current_hand] *= 2
            hand.append(self.deck.pop())
            self.next_hand_or_end(games)
            await interaction.response.edit_message(embed=self.render_embed(), view=self.render_buttons(bot, games))

        async def split_callback(interaction):
            hand = self.player_hands[self.current_hand]
            if len(hand) == 2 and hand[0][:-1] == hand[1][:-1]:
                new_hand = [hand.pop()]
                self.player_hands.insert(self.current_hand+1, new_hand)
                self.player_bets.insert(self.current_hand+1, self.player_bets[self.current_hand])
                hand.append(self.deck.pop())
                new_hand.append(self.deck.pop())
            await interaction.response.edit_message(embed=self.render_embed(), view=self.render_buttons(bot, games))

        view.add_item(discord.ui.Button(label="Hit", style=discord.ButtonStyle.green))
        view.add_item(discord.ui.Button(label="Stand", style=discord.ButtonStyle.red))
        view.add_item(discord.ui.Button(label="Double", style=discord.ButtonStyle.blurple))
        view.add_item(discord.ui.Button(label="Split", style=discord.ButtonStyle.gray))

        view.children[0].callback = hit_callback
        view.children[1].callback = stand_callback
        view.children[2].callback = double_callback
        view.children[3].callback = split_callback

        return view

    def next_hand_or_end(self, games):
        self.current_hand += 1
        if self.current_hand >= len(self.player_hands):
            # Dealer plays
            while self.hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
            self.evaluate_results()
            self.finished = True
            games.pop(self.player_id)

    def evaluate_results(self):
        dealer_val = self.hand_value(self.dealer_hand)
        results = []
        for hand, bet in zip(self.player_hands, self.player_bets):
            player_val = self.hand_value(hand)
            if player_val > 21:
                results.append(f"{' '.join(hand)}: Bust! You lose {bet} CP")
            elif dealer_val > 21 or player_val > dealer_val:
                results.append(f"{' '.join(hand)}: You win {bet} CP")
                add_balance(self.player_id, bet*2)
            elif player_val == dealer_val:
                results.append(f"{' '.join(hand)}: Push! Bet returned")
                add_balance(self.player_id, bet)
            else:
                results.append(f"{' '.join(hand)}: You lose {bet} CP")
        self.result = "\n".join(results)
