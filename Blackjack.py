# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 09:20:56 2018

@author: kings
"""

import random
import time

class Card(object):
    
    def __init__(self,value,suit):
        self.value = self.card_value(value)
        self.suit = suit
        
    def card_value(self,value):
        if value == 1:
            return 'A'
        elif value == 11:
            return 'J'
        elif value == 12:
            return 'Q'
        elif value == 13:
            return 'K'
        else: return value
               
class Deck(object):
    
    suits = ['Club','Spade','Heart','Diamond']
    
    def __init__(self,cut=True):
        self.deck = [Card(value, suit) for value in range(1, 14) for suit in self.suits]
        if cut == True:
            self.insert_cut()
        
    def insert_cut(self):
        self.deck.append('Cut')
    
class Player:
    
    def __init__(self,name=None,bank=500):
        if name == None:
            self.name = self.rand_name()
        else: self.name = name
        self.bank=bank
        self.hand = []
        self.stake = 0
        
    def rand_name(self):
        return 'Guest' + ''.join([str(random.randint(0,9)) for x in range(8)])
    
class Dealer(Player):
    
    def __init__(self):
        self.name = 'Dealer'
        self.bank = float('inf')
        
class Ghost(Player):
    
    def __init__(self,player):
        self.name = player.name + '_split'            
        self.bank = -player.stake
        self.hand = []
        self.stake = player.stake
        self.orig = player
        while type(self.orig) == Ghost:
            player = player.orig
            self.orig = player
    
class Blackjack:
    
    CARD = """\
    ┌─────────┐
    │{}       │
    │         │
    │         │
    │    {}   │
    │         │
    │         │
    │       {}│
    └─────────┘
    """.format('{rank: <2}', '{suit: <2}', '{rank: >2}')
    
    HIDDEN_CARD = """\
    ┌─────────┐
    │░░░░░░░░░│
    │░░░░░░░░░│
    │░░░░░░░░░│
    │░░░░░░░░░│
    │░░░░░░░░░│
    │░░░░░░░░░│
    │░░░░░░░░░│
    └─────────┘
    """
    
    def __init__(self,dealer_stand=17,betting=False,decks=6,shuffle=True,cut=True,seats=6):
        self.dealer_stand = dealer_stand
        self.dealer = Dealer()
        self.players = []
        self.betting = betting
        self.cut = cut
        self.decks = decks
        self.shuffle = shuffle
        self.seats = seats
        
    def add_player(self,name=None,bank=None):
        if len(self.players) >= self.seats:
            print('Sorry! Table is Full')
        else:
            if bank == None:
                self.players.append(Player(name=(None if name == '' else name)))
            else:
                self.players.append(Player(name,bank))
        
    def create_deck(self):
        return Deck(self.cut).deck*self.decks
    
    def join_lines(self,strings):

        liness = [string.splitlines() for string in strings]
        return '\n'.join(''.join(lines) for lines in zip(*liness))
    
    def ascii_version_of_card(self,*cards):

        name_to_symbol = {
            'Spade':   '♠',
            'Diamond': '♦',
            'Heart':   '♥',
            'Club':    '♣',
        }
    
        def card_to_string(card):
            rank = card.value
    
            return self.CARD.format(rank=rank, suit=name_to_symbol[card.suit])
    
    
        return self.join_lines(map(card_to_string, cards))
    
    def ascii_version_of_hidden_card(self,*cards):

        return self.join_lines((self.HIDDEN_CARD, self.ascii_version_of_card(*cards[1:])))
    
    def new_game(self):
        if self.shuffle == True:
            self.deck = self.create_deck()
            self.shuffled()
            if self.cut == True:
                self.shuffle = False
        for player in self.players:
            player.hand = []
        self.dealer.hand = []
        
    def shuffled(self):
        print('Shuffling')
        self.deck = random.sample(self.deck,len(self.deck))
        if self.cut == True:
            if [i for i,x in enumerate(self.deck) if x == 'Cut'][0] > len(self.deck) * (2/3):
                self.shuffled()
        
    def print_cards(self,cards):
        print(self.ascii_version_of_card(*cards))
            
    def print_dealer(self):
        print(self.ascii_version_of_hidden_card(*self.dealer.hand))
            
    def draw_card(self):
        card = self.deck[0]
        self.deck.remove(card)
        if card == 'Cut':
            print('Cut card drawn, shuffle next hand')
            card = self.draw_card()
            self.shuffle = True
        return card

    def deal(self):
        for x in (1,2):
            for player in self.players:
                player.hand.append(self.draw_card())
                if len(player.hand) == 2:
                    print(player.name + ' Hand:')
                    self.print_cards(player.hand)
            self.dealer.hand.append(self.draw_card())
        print('Dealer hand:')
        self.print_dealer()
        
    def get_card(self,player):
        card = self.draw_card()
        player.hand.append(card)
        
    def player_turn(self,player):
        action = 'none'
        print(player.name + ' Total: ' + str(self.calc_hand(player.hand)))
        while self.check_bust(player.hand) != True and action.upper() not in ['S','D'] and not (type(player) == Ghost and player.hand[0] == 'A') and not (action.upper() == 'P' and player.hand[0] == 'A'):
            action = self.get_inst(player)
            if action.upper() == 'H':
                self.get_card(player)
                print(player.name + ' Hand: ')
                self.print_cards(player.hand)
            elif action.upper() == 'D':
                player.bank -= player.stake
                player.stake = player.stake * 2
                self.get_card(player)
                print(player.name + ' Hand: ')
                self.print_cards(player.hand)
            elif action.upper() == 'P':
                self.split(player)
            print(player.name + ' Total: ' + str(self.calc_hand(player.hand)))
        if self.check_bust(player.hand) == True:
            print('Bust!')
            
    def split(self,player):
        ghost = Ghost(player)
        place = self.players.index(player)
        self.players.insert(place+1,ghost)
        ghost.hand.append(player.hand[1])
        player.hand.remove(player.hand[1])
        player.hand.append(self.draw_card())
        ghost.hand.append(self.draw_card())
        print(player.name + ' Hand: ')
        self.print_cards(player.hand)
        print(ghost.name + ' Hand: ')
        self.print_cards(ghost.hand)
        
            
    def calc_hand(self,hand):
        score = [card.value for card in hand]
        score = [10 if x in ['J','Q','K'] else 1 if x == 'A' else x for x in score]
        if (sum(score) <= 11) and (1 in score):
            return sum(score)+10
        else: return sum(score)
        
    def check_bust(self,hand):
        if self.calc_hand(hand) > 21:
            return True
    
    def get_inst(self,player):
        if len(player.hand) == 2:
            if (player.hand[0].value == player.hand[1].value) or (player.hand[0].value in [10,'J','Q','K'] and player.hand[1].value in [10,'J','Q','K']):
                value = input('Hit(H), Stand(S), Double(D) or Split(P)?: ')
                if value.upper() not in ['H','S','D','P']:
                    print('ERROR! You must enter H, S, D or P!')
                    value = self.get_inst(player)
            else:
                value = input('Hit(H), Stand(S) or Double(D)?: ')
                if value.upper() not in ['H','S','D']:
                    print('ERROR! You must enter H, S or D!')
                    value = self.get_inst(player)
        else:
            value = input('Hit(H) or Stand(S)?: ')
            if value.upper() not in  ['H','S']:
                print('ERROR! You must enter H or S!')
                value = self.get_inst(player)
        return value
            
        
    def dealer_turn(self):
        print('Dealer Hand:')
        self.print_cards(self.dealer.hand)
        print('Dealer Total: ' + str(self.calc_hand(self.dealer.hand)))
        time.sleep(2)
        while self.calc_hand(self.dealer.hand) < self.dealer_stand:
            self.get_card(self.dealer)
            print('Dealer Hand: ')
            self.print_cards(self.dealer.hand)
            print('Dealer Total: ' + str(self.calc_hand(self.dealer.hand)))
            time.sleep(2)
        if self.check_bust(self.dealer.hand) == True:
            print('Dealer Bust!')
        
    def check_winner(self,player,on_deal=False,on_player=False,on_dealer=False):
        if on_deal == True:
            if len(player.hand) == 2 and  self.calc_hand(player.hand) == 21 and len(self.dealer.hand) == 2 and  self.calc_hand(self.dealer.hand) != 21:
                return 'Blackjack'
            elif len(player.hand) == 2 and  self.calc_hand(player.hand) == 21 and len(self.dealer.hand) == 2 and  self.calc_hand(self.dealer.hand) == 21:
                return 'Push'
            elif self.calc_hand(self.dealer.hand) == 21:
                return False
        elif on_player == True:
            if self.calc_hand(player.hand) > 21:
                return False
        elif on_dealer == True:
            if self.calc_hand(self.dealer.hand) > 21:
                return True
            elif self.calc_hand(player.hand) > self.calc_hand(self.dealer.hand):
                return True
            elif self.calc_hand(player.hand) == self.calc_hand(self.dealer.hand):
                return 'Push'
            else: return False
            
    def get_stake(self,player):
        stake = input(player.name + ' How much would you like to bet? ')
        return int(stake)
        
    def game(self):
        self.new_game()
        if self.betting == True:
            for player in self.players:
                player.stake = self.get_stake(player)
                player.bank += -player.stake
        self.deal()
        active = []
        for player in self.players:
            if self.check_winner(player,on_deal=True) == False:
                print('Dealer Hand: ')
                self.print_cards(self.dealer.hand)
                print(player.name + ' Loses')
            elif self.check_winner(player,on_deal=True) == 'Blackjack':
                print('BLACKJACK! ' + player.name + ' wins')
                if self.betting == True:
                    player.bank += player.stake*2.5
            elif self.check_winner(player,on_deal=True) == 'Push':
                print('Push')
            else:
                self.player_turn(player)
                if self.check_winner(player,on_player=True) == False:
                    print(player.name + ' Loses')
                else: active.append(player)
        if len(active) > 0:
            self.dealer_turn()
            for player in active:
                winner = self.check_winner(player,on_dealer=True)
                if winner == False:
                    print(player.name + ' Loses')
                elif winner == True:
                    print(player.name + ' wins')
                    if self.betting == True:
                        player.bank += player.stake*2
                else: 
                    print('Push')
                    if self.betting == True:
                        player.bank += player.stake
        if self.betting == True:
            for player in self.players:
                if type(player) == Ghost:
                    player.orig.bank += player.bank
                    self.players.remove(player)
            for player in self.players:
                print(player.name, player.bank)        

    def play(self):
        if len(self.players) == 0:
            self.add_player()
        play_on = True
        while play_on == True:
            self.game()
            play_on = input('Would you like to play another hand? (Y/N): ')
            play_on = (True if play_on.upper() == 'Y' else False)