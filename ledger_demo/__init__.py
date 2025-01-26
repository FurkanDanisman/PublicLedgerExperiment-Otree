from otree.api import *
import json
import random

doc = """
Market experiment with 6 players per group: 1 producer, 2 sellers, and 3 buyers.
Public ledger updates at each transaction to highlight market behavior.
"""


class Constants(BaseConstants):
    name_in_url = 'ledger_demo'
    players_per_group = 6
    num_rounds = 4
    base_price_suggestion = 2
    product_price_suggestion = 3
    initial_base = 2
    seller_initial_tokens = 3
    buyer_initial_tokens = 5


class Subsession(BaseSubsession):
    treatment = models.StringField()
    random_number = models.IntegerField()


class Group(BaseGroup):
    public_ledger = models.LongStringField(initial="[]")  # Store ledger as JSON
    buyer_order = models.LongStringField(initial="[]")

    def add_to_ledger(self, transaction):
        ledger = json.loads(self.public_ledger)
        ledger.append(transaction)
        self.public_ledger = json.dumps(ledger)


class Player(BasePlayer):
    offer_to_producer = models.IntegerField(
        choices=[1, 2, 3],  # Sellers can choose from 1, 2, or 3 Tokens
        blank=True
    )

    position = models.StringField()
    tokens = models.IntegerField()
    bases = models.IntegerField()
    products = models.IntegerField()
    product_price = models.IntegerField(blank=True)

    accept_offer_2 = models.BooleanField(blank=True,label="Accept the offer from Seller (2)?")
    accept_offer_3 = models.BooleanField(blank=True,label="Accept the offer from Seller (3)?")

    b1_buy_decision_a1 = models.BooleanField(blank=True)
    b1_buy_decision_a2 = models.BooleanField(blank=True)

    b2_buy_decision_a1 = models.BooleanField(blank=True)
    b2_buy_decision_a2 = models.BooleanField(blank=True)

    b3_buy_decision_a1 = models.BooleanField(blank=True)
    b3_buy_decision_a2 = models.BooleanField(blank=True)

    b1_buy_amount_a1 = models.IntegerField(blank=True)
    b1_buy_amount_a2 = models.IntegerField(blank=True)

    b2_buy_amount_a1 = models.IntegerField(blank=True)
    b2_buy_amount_a2 = models.IntegerField(blank=True)

    b3_buy_amount_a1 = models.IntegerField(blank=True)
    b3_buy_amount_a2 = models.IntegerField(blank=True)

    # Number Guessing Game
    guess = models.IntegerField(min=1, max=100, blank=True)
    rank = models.IntegerField(blank=True)


def calculate_payoff(group):

    for player in group.get_players():

        if player.position == "producer":
            player.payoff = player.tokens

        elif player.position == "seller":
            player.payoff = player.tokens * 2

        elif player.position == "buyer":

            if player.id_in_group == 4:

                buy_amount_a1 = player.field_maybe_none('b1_buy_amount_a1') or 0
                buy_amount_a2 = player.field_maybe_none('b1_buy_amount_a2') or 0

                player.payoff = (buy_amount_a1 + buy_amount_a1) * 5 + player.tokens

            elif player.id_in_group == 5:

                buy_amount_a1 = player.field_maybe_none('b2_buy_amount_a1') or 0
                buy_amount_a2 = player.field_maybe_none('b2_buy_amount_a2') or 0
                player.payoff = (buy_amount_a1 + buy_amount_a1) * 5 + player.tokens

            elif player.id_in_group == 6:

                buy_amount_a1 = player.field_maybe_none('b3_buy_amount_a1') or 0
                buy_amount_a2 = player.field_maybe_none('b3_buy_amount_a2') or 0

                player.payoff = (buy_amount_a1 + buy_amount_a1) * 5 + player.tokens

# Functions

def creating_session(subsession: Subsession):
    subsession.treatment = subsession.session.config.get('treatment', 'default')
    subsession.random_number = random.randint(1, 100)

    for player in subsession.get_players():
        if player.id_in_group == 1:
            player.position = "producer"
            player.tokens = 0
            player.bases = Constants.initial_base
        elif player.id_in_group in [2, 3]:  # Sellers
            player.position = "seller"
            player.tokens = Constants.seller_initial_tokens
            player.bases = 0
            player.products = 0  # ✅ Ensure sellers start with 0 products
        else:  # Buyers
            player.position = "buyer"
            player.tokens = Constants.buyer_initial_tokens
            player.products = 0  # ✅ Initialize for consistency

        # Dynamically create accept_offer_<seller_id> fields for producers
        if player.position == "producer":
            for seller in subsession.get_players():
                if seller.position == "seller":
                    setattr(
                        Player,
                        f'accept_offer_{seller.id_in_group}',
                        models.BooleanField(blank=True)
                    )


def rank_buyers(group: Group):
    buyers = [p for p in group.get_players() if p.position == "buyer"]

    # Calculate distance from the random number
    for buyer in buyers:
        buyer.rank = abs(buyer.subsession.random_number - buyer.guess)

    # Sort buyers by closest guess
    buyers_sorted = sorted(buyers, key=lambda b: b.rank)
    buyer_order = [b.id_in_group for b in buyers_sorted]

    # Store the order in JSON format
    group.buyer_order = json.dumps(buyer_order)


# Pages

class Introduction(Page):
    form_model = 'player'

    def vars_for_template(player: Player):
        return {
            'treatment': player.subsession.treatment,
            'base_price_suggestion': Constants.base_price_suggestion,
            'product_price_suggestion': Constants.product_price_suggestion,
        }


class OfferToProducer(Page):
    form_model = 'player'
    form_fields = ['offer_to_producer']

    @staticmethod
    def is_displayed(player: Player):
        return player.position == "seller"

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'ledger': json.loads(player.group.public_ledger),
            'instructions': "As a seller, make an offer to buy a base from the producer (1-3 Tokens).",
        }


class DecideOnOffer(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return player.position == "producer"

    @staticmethod
    def vars_for_template(player: Player):
        sellers = [
            {
                'id': seller.id_in_group,
                'offer': seller.offer_to_producer,
                'form_field': f'accept_offer_{seller.id_in_group}',
            }
            for seller in player.group.get_players()
            if seller.position == "seller" and seller.offer_to_producer is not None
        ]
        return {
            'sellers': sellers,
            'ledger': json.loads(player.group.public_ledger),
            'instructions': "Decide which seller(s) you want to sell to based on their offers.",
        }

    @staticmethod
    def get_form_fields(player: Player):
        # Return the predefined form fields for sellers 2 and 3
        return ['accept_offer_2', 'accept_offer_3']

    def before_next_page(player: Player, timeout_happened):
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.offer_to_producer is not None:
                field_name = f'accept_offer_{seller.id_in_group}'
                if getattr(player, field_name):  # If the producer accepted the offer
                    seller.tokens -= seller.offer_to_producer
                    player.tokens += seller.offer_to_producer
                    seller.bases += 1
                    seller.products += 2  # ✅ Sellers now get 2 products per base
                    player.bases -= 1  # Producer loses the base

                    transaction = {
                        'round': player.round_number,
                        'type': "Base Purchase",
                        'seller_id': seller.id_in_group,
                        'seller_role': "Seller",
                        'buyer_id': player.id_in_group,
                        'buyer_role': "Producer",
                        'amount': seller.offer_to_producer,
                        'quantity': 1,  # One base purchased
                    }
                    player.group.add_to_ledger(transaction)



class GuessNumber(Page):
    form_model = 'player'
    form_fields = ['guess']

    @staticmethod
    def is_displayed(player: Player):
        return player.position == "buyer"

class RankBuyers(WaitPage):
    after_all_players_arrive = 'rank_buyers'


class SetProductPrice(Page):
    form_model = 'player'
    form_fields = ['product_price']

    @staticmethod
    def is_displayed(player: Player):
        return player.position == "seller" and player.bases > 0  # Only sellers with a base see this page

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'ledger': json.loads(player.group.public_ledger),
            'instructions': "Set a price for your products.",
        }


class BuyProducts(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        if player.position != "buyer":
            return False

        # Buyers act in the order of the guessing game result
        buyer_order = json.loads(player.group.buyer_order)
        current_rank = buyer_order.index(player.id_in_group)

        # Only the first buyer goes first, then we wait for the next buyer
        previous_buyers_finished = all(
            p.round_number > player.round_number for p in player.group.get_players()
            if p.position == "buyer" and buyer_order.index(p.id_in_group) < current_rank
        )

        return previous_buyers_finished  # Show page only if all previous buyers finished

    @staticmethod
    def get_form_fields(player: Player):
        fields = []

        # Dynamically create Yes/No fields for each seller
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.bases > 0:
                fields.append(f'b{player.id_in_group-3}_buy_decision_a{seller.id_in_group-1}')  # Yes/No decision

        # After Yes/No decision, allow specifying amount
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.bases > 0:
                fields.append(f'b{player.id_in_group-3}_buy_amount_a{seller.id_in_group-1}')  # Quantity field

        return fields

    @staticmethod
    def vars_for_template(player: Player):
        sellers = []
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.bases > 0:
                sellers.append({
                    'id': seller.id_in_group,
                    'price': seller.product_price,
                    'stock': seller.bases * 2,  # Each base produces 2 products
                })

        buyer_order = json.loads(player.group.buyer_order)
        rank_index = buyer_order.index(player.id_in_group) + 1  # Convert 0-based index to 1-based rank
        return {
            'sellers': sellers,
            'ledger': json.loads(player.group.public_ledger),
            'buyer_order': buyer_order,
            'rank_index': rank_index,
            'random_number': player.subsession.random_number,
            'instructions': f"You are ranked {rank_index}. You will buy when it's your turn.",
        }

    def before_next_page(player: Player, timeout_happened):
        total_cost = 0  # Track total cost for the buyer

        for seller in player.group.get_players():
            if seller.position == "seller" and seller.bases > 0:
                decision_field = f'b{player.id_in_group}_buy_decision_a{seller.id_in_group}'
                quantity_field = f'b{player.id_in_group}_buy_amount_a{seller.id_in_group}'

                # Check if the buyer said Yes to buying
                buy_decision = getattr(player, decision_field, False)

                if buy_decision:  # Buyer said "Yes"
                    quantity_requested = getattr(player, quantity_field, 0)

                    # Ensure buyer doesn't try to buy more than available stock
                    available_stock = seller.bases * 2
                    quantity_purchased = min(quantity_requested, available_stock)

                    # **🚨 Prevent overspending**
                    cost = quantity_purchased * seller.product_price
                    if cost > player.tokens:
                        raise ValueError(
                            f"Error: You only have {player.tokens} tokens but tried to spend {cost}!")  # ❌ Buyer tried to overspend

                    if quantity_purchased > 0:
                        player.tokens -= cost
                        seller.tokens += cost
                        seller.bases -= (quantity_purchased // 2)  # Reduce bases accordingly

                        # ✅ Log the transaction with updated stock
                        player.group.add_to_ledger({
                            'round': player.round_number,
                            'type': "Product Sale",
                            'buyer_id': player.id_in_group,
                            'buyer_role': "Buyer",
                            'seller_id': seller.id_in_group,
                            'seller_role': "Seller",
                            'amount': cost,
                            'quantity': quantity_purchased,
                        })


class BuyProducts1(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        if player.position != "buyer":
            return False

        # Load buyer order
        buyer_order = json.loads(player.group.buyer_order)

        # Only show to the first ranked buyer
        return player.id_in_group == buyer_order[0]

    @staticmethod
    def get_form_fields(player: Player):
        fields = []

        # Dynamically create Yes/No fields for each seller
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                fields.append(f'b1_buy_decision_a{seller.id_in_group - 1}')  # Yes/No decision

        # After Yes/No decision, allow specifying amount
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                fields.append(f'b1_buy_amount_a{seller.id_in_group - 1}')  # Quantity field

        return fields

    @staticmethod
    def vars_for_template(player: Player):
        sellers = []
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                sellers.append({
                    'id': seller.id_in_group,
                    'price': seller.product_price,
                    'stock': seller.products,  # Each base produces 2 products
                    'adjusted_id': seller.id_in_group - 1  # Seller ID - 1
                })

        buyer_order = json.loads(player.group.buyer_order)
        rank_index = buyer_order.index(player.id_in_group) + 1  # Convert 0-based index to 1-based rank
        return {
            'sellers': sellers,
            'ledger': json.loads(player.group.public_ledger),
            'buyer_order': buyer_order,
            'rank_index': 1,
            'random_number': player.subsession.random_number,
            'instructions': f"You are ranked {rank_index}. You will buy when it's your turn.",
        }

    def before_next_page(player: Player, timeout_happened):
        total_cost = 0  # Track total cost for the buyer

        for seller in player.group.get_players():

            if seller.position == "seller" and seller.products > 0:
                decision_field = f'b1_buy_decision_a{seller.id_in_group - 1}'
                quantity_field = f'b1_buy_amount_a{seller.id_in_group - 1}'

                # ✅ Use field_maybe_none() to avoid NoneType error
                buy_decision = player.field_maybe_none(decision_field) or False
                quantity_requested = player.field_maybe_none(quantity_field) or 0

                if buy_decision:  # Buyer said "Yes"
                    available_stock = seller.products
                    quantity_purchased = min(quantity_requested, available_stock)

                    # **🚨 Prevent overspending**
                    cost = quantity_purchased * seller.product_price
                    if cost > player.tokens:
                        raise ValueError(
                            f"Error: You only have {player.tokens} tokens but tried to spend {cost}!"
                        )  # ❌ Buyer tried to overspend

                    if quantity_purchased > 0:
                        # ✅ Update buyer's tokens
                        player.tokens -= cost
                        seller.tokens += cost

                        # ✅ Update stock
                        seller.products -= quantity_purchased  # Reduce products stock

                        # ✅ Log transaction in the ledger
                        player.group.add_to_ledger({
                            'round': player.round_number,
                            'type': "Product Sale",
                            'buyer_id': player.id_in_group,
                            'buyer_role': "Buyer",
                            'seller_id': seller.id_in_group,
                            'seller_role': "Seller",
                            'amount': cost,
                            'quantity': quantity_purchased,
                            'remaining_stock': seller.products
                        })

class BuyProducts2(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        if player.position != "buyer":
            return False

        # Load buyer order
        buyer_order = json.loads(player.group.buyer_order)

        # Only show to the first ranked buyer
        return player.id_in_group == buyer_order[1]

    @staticmethod
    def get_form_fields(player: Player):
        fields = []

        # Dynamically create Yes/No fields for each seller
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                fields.append(f'b2_buy_decision_a{seller.id_in_group - 1}')  # Yes/No decision

        # After Yes/No decision, allow specifying amount
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                fields.append(f'b2_buy_amount_a{seller.id_in_group - 1}')  # Quantity field

        return fields

    @staticmethod
    def vars_for_template(player: Player):
        sellers = []
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                sellers.append({
                    'id': seller.id_in_group,
                    'price': seller.product_price,
                    'stock': seller.products,  # Each base produces 2 products
                    'adjusted_id': seller.id_in_group - 1  # Seller ID - 1
                })

        buyer_order = json.loads(player.group.buyer_order)
        rank_index = buyer_order.index(player.id_in_group) + 1  # Convert 0-based index to 1-based rank
        return {
            'sellers': sellers,
            'ledger': json.loads(player.group.public_ledger),
            'buyer_order': buyer_order,
            'rank_index': 1,
            'random_number': player.subsession.random_number,
            'instructions': f"You are ranked {rank_index}. You will buy when it's your turn.",
        }

    def before_next_page(player: Player, timeout_happened):
        total_cost = 0  # Track total cost for the buyer

        for seller in player.group.get_players():

            if seller.position == "seller" and seller.products > 0:
                decision_field = f'b2_buy_decision_a{seller.id_in_group - 1}'
                quantity_field = f'b2_buy_amount_a{seller.id_in_group - 1}'

                # ✅ Use field_maybe_none() to avoid NoneType error
                buy_decision = player.field_maybe_none(decision_field) or False
                quantity_requested = player.field_maybe_none(quantity_field) or 0

                if buy_decision:  # Buyer said "Yes"
                    available_stock = seller.products
                    quantity_purchased = min(quantity_requested, available_stock)

                    # **🚨 Prevent overspending**
                    cost = quantity_purchased * seller.product_price
                    if cost > player.tokens:
                        raise ValueError(
                            f"Error: You only have {player.tokens} tokens but tried to spend {cost}!"
                        )  # ❌ Buyer tried to overspend

                    if quantity_purchased > 0:
                        # ✅ Update buyer's tokens
                        player.tokens -= cost
                        seller.tokens += cost

                        # ✅ Update stock
                        seller.products -= quantity_purchased  # Reduce products stock

                        # ✅ Log transaction in the ledger
                        player.group.add_to_ledger({
                            'round': player.round_number,
                            'type': "Product Sale",
                            'buyer_id': player.id_in_group,
                            'buyer_role': "Buyer",
                            'seller_id': seller.id_in_group,
                            'seller_role': "Seller",
                            'amount': cost,
                            'quantity': quantity_purchased,
                            'remaining_stock': seller.products
                        })

class BuyProducts3(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        if player.position != "buyer":
            return False

        # Load buyer order
        buyer_order = json.loads(player.group.buyer_order)

        # Only show to the first ranked buyer
        return player.id_in_group == buyer_order[2]

    @staticmethod
    def get_form_fields(player: Player):
        fields = []

        # Dynamically create Yes/No fields for each seller
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                fields.append(f'b3_buy_decision_a{seller.id_in_group - 1}')  # Yes/No decision

        # After Yes/No decision, allow specifying amount
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                fields.append(f'b3_buy_amount_a{seller.id_in_group - 1}')  # Quantity field

        return fields

    @staticmethod
    def vars_for_template(player: Player):
        sellers = []
        for seller in player.group.get_players():
            if seller.position == "seller" and seller.products > 0:
                sellers.append({
                    'id': seller.id_in_group,
                    'price': seller.product_price,
                    'stock': seller.products,  # Each base produces 2 products
                    'adjusted_id': seller.id_in_group - 1  # Seller ID - 1
                })

        buyer_order = json.loads(player.group.buyer_order)
        rank_index = buyer_order.index(player.id_in_group) + 1  # Convert 0-based index to 1-based rank
        return {
            'sellers': sellers,
            'ledger': json.loads(player.group.public_ledger),
            'buyer_order': buyer_order,
            'rank_index': 1,
            'random_number': player.subsession.random_number,
            'instructions': f"You are ranked {rank_index}. You will buy when it's your turn.",
        }

    def before_next_page(player: Player, timeout_happened):
        total_cost = 0  # Track total cost for the buyer

        for seller in player.group.get_players():

            if seller.position == "seller" and seller.products > 0:
                decision_field = f'b3_buy_decision_a{seller.id_in_group - 1}'
                quantity_field = f'b3_buy_amount_a{seller.id_in_group - 1}'

                # ✅ Use field_maybe_none() to avoid NoneType error
                buy_decision = player.field_maybe_none(decision_field) or False
                quantity_requested = player.field_maybe_none(quantity_field) or 0

                if buy_decision:  # Buyer said "Yes"
                    available_stock = seller.products
                    quantity_purchased = min(quantity_requested, available_stock)

                    # **🚨 Prevent overspending**
                    cost = quantity_purchased * seller.product_price
                    if cost > player.tokens:
                        raise ValueError(
                            f"Error: You only have {player.tokens} tokens but tried to spend {cost}!"
                        )  # ❌ Buyer tried to overspend

                    if quantity_purchased > 0:
                        # ✅ Update buyer's tokens
                        player.tokens -= cost
                        seller.tokens += cost

                        # ✅ Update stock
                        seller.products -= quantity_purchased  # Reduce products stock

                        # ✅ Log transaction in the ledger
                        player.group.add_to_ledger({
                            'round': player.round_number,
                            'type': "Product Sale",
                            'buyer_id': player.id_in_group,
                            'buyer_role': "Buyer",
                            'seller_id': seller.id_in_group,
                            'seller_role': "Seller",
                            'amount': cost,
                            'quantity': quantity_purchased,
                            'remaining_stock': seller.products
                        })
class WaitForNextBuyer(WaitPage):
    """Ensures each buyer waits for the previous one to finish before purchasing"""
    wait_for_all_groups = True


class ShowBuyerRank(Page):
    """Displays the ranking of buyers before purchasing begins"""

    @staticmethod
    def is_displayed(player: Player):
        return player.position == "buyer"

    @staticmethod
    def vars_for_template(player: Player):
        buyer_order = json.loads(player.group.buyer_order)
        rank_index = buyer_order.index(player.id_in_group) + 1  # Convert 0-based index to 1-based rank
        return {
            'buyer_order': buyer_order,
            'rank_index': rank_index,
            'random_number': player.subsession.random_number,
            'guessed_number': player.guess
        }


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # ✅ Convert JSON string into a proper Python dictionary list
        ledger = json.loads(player.group.public_ledger)

        return {
            'ledger': ledger,  # ✅ Now it's a list of dictionaries, accessible via dot notation in the template
            'payoff': player.payoff,
            'instructions': "Here are your final results.",
        }

class Wait(WaitPage):
    pass


class WaitForProducerDecision(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # You can add logic here to handle any group-level actions after the producer's decision
        pass


class GameResultsWaitPage(WaitPage):
    """
    This WaitPage ensures that all participants finish their actions
    before viewing the final results.
    """
    after_all_players_arrive = 'calculate_payoff'

page_sequence = [
    Introduction,
    Wait,
    OfferToProducer,
    Wait,
    DecideOnOffer,
    Wait,
    SetProductPrice,
    Wait,
    GuessNumber,  # 🎲 Buyers play the guessing game
    RankBuyers,
    ShowBuyerRank,  # 📢 Buyers see their ranking before buying
    Wait,
    BuyProducts1,  # 👑 Buyer 1 goes first
    Wait,  # Wait before Buyer 2 buys
    BuyProducts2,  # 🥈 Buyer 2 goes next
    Wait,  # Wait before Buyer 3 buys
    BuyProducts3,  # 🥉 Buyer 3 goes last
    GameResultsWaitPage,
    Results,
]

