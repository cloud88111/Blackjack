# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 09:20:56 2018

@author: kings
"""

import random

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
    
    suits = ['Club','Heart','Diamond','Spade']
    
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
        
    def rand_name(self):
        return 'Guest' + ''.join([str(random.randint(0,9)) for x in range(8)])
    
class Dealer(Player):
    
    def __init__(self):
        self.name = 'Dealer'
        self.bank = float('inf')
    
class Blackjack:
    
    def __init__(self,dealer_stand=17,betting=False,decks=1,shuffle=True,cut=True):
        self.dealer_stand = dealer_stand
        self.player = Player()
        self.dealer = Dealer()
        self.betting = betting
        self.cut = cut
        self.decks = decks
        self.shuffle = shuffle
        
    def create_deck(self):
        return Deck(self.cut).deck*self.decks
    
    def new_game(self):
        if self.shuffle == True:
            self.deck = self.create_deck()
            self.shuffled()
            if self.cut == True:
                self.shuffle = False
        self.player.hand = []
        self.dealer.hand = []
        
    def shuffled(self):
        print('Shuffling')
        self.deck = random.sample(self.deck,len(self.deck))
        if self.cut == True:
            if [i for i,x in enumerate(self.deck) if x == 'Cut'][0] > len(self.deck) * (2/3):
                self.shuffled()
        
    def print_cards(self,cards):
        for card in cards:
            print(card.value,card.suit)
            
    def print_dealer(self):
        print(self.dealer.hand[0].value,self.dealer.hand[0].suit)
            
    def draw_card(self):
        card = self.deck[0]
        self.deck.remove(card)
        if card == 'Cut':
            print('Cut card drawn, shuffle next hand')
            card = self.draw_card()
            self.shuffle = True
        return card

    def deal(self):
        self.player.hand.append(self.draw_card())
        self.dealer.hand.append(self.draw_card())
        self.player.hand.append(self.draw_card())
        self.dealer.hand.append(self.draw_card())
        print(self.player.name + ' hand:')
        self.print_cards(self.player.hand)
        print('Dealer hand:')
        self.print_dealer()

    def player_turn(self,player):
        action = 'none'
        print(player + ' Total: ' + str(self.calc_hand(self.player.hand)))
        while self.check_bust(self.player.hand) != True and action.upper() not in ['S']:
            action = input('Hit or Stand? Enter H or S: ')
            if action.upper() == 'H':
                card = self.draw_card()
                self.player.hand.append(card)
                self.print_cards([card])
                print(player + ' Total: ' + str(self.calc_hand(self.player.hand)))
            elif action.upper() != 'S':
                print('ERROR! You must enter H or S!')
        if self.check_bust(self.player.hand) == True:
            print('Bust!')
            
    def calc_hand(self,hand):
        score = [card.value for card in hand]
        score = [10 if x in ['J','Q','K'] else 1 if x == 'A' else x for x in score]
        if (sum(score) <= 11) and (1 in score):
            return sum(score)+10
        else: return sum(score)
        
    def check_bust(self,hand):
        if self.calc_hand(hand) > 21:
            return True
    
    def dealer_turn(self):
        self.print_cards(self.dealer.hand)
        print('Dealer Total: ' + str(self.calc_hand(self.dealer.hand)))
        while self.calc_hand(self.dealer.hand) < self.dealer_stand:
            card = self.draw_card()
            self.dealer.hand.append(card)
            self.print_cards([card])
            print('Dealer Total: ' + str(self.calc_hand(self.dealer.hand)))
        if self.check_bust(self.dealer.hand) == True:
            print('Dealer Bust!')
        
    def check_winner(self,on_deal=False,on_player=False,on_dealer=False):
        if on_deal == True:
            if len(self.player.hand) == 2 and  self.calc_hand(self.player.hand) == 21 and len(self.dealer.hand) == 2 and  self.calc_hand(self.dealer.hand) != 21:
                return 'Blackjack'
            elif len(self.player.hand) == 2 and  self.calc_hand(self.player.hand) == 21 and len(self.dealer.hand) == 2 and  self.calc_hand(self.dealer.hand) == 21:
                return 'Push'
            elif self.calc_hand(self.dealer.hand) == 21:
                return False
        elif on_player == True:
            if self.calc_hand(self.player.hand) > 21:
                return False
        elif on_dealer == True:
            if self.calc_hand(self.dealer.hand) > 21:
                return True
            elif self.calc_hand(self.player.hand) > self.calc_hand(self.dealer.hand):
                return True
            elif self.calc_hand(self.player.hand) == self.calc_hand(self.dealer.hand):
                return 'Push'
            else: return False
        
    def play(self):
        self.new_game()
        if self.betting == True:
            stake = input('How much would you like to bet? ')
            stake = int(stake)
            self.player.bank += -stake
        self.deal()
        if self.check_winner(on_deal=True) == False:
            print('Dealer Hand')
            self.print_cards(self.dealer.hand)
            print('Player Loses')
        elif self.check_winner() == 'Blackjack':
            print('BLACKJACK! Player wins')
            if self.betting == True:
                self.player.bank += stake*2.5
        elif self.check_winner() == 'Push':
            print('Push')
        else:
            self.player_turn(self.player.name)
            if self.check_winner(on_player=True) == False:
                print('Dealer Hand')
                self.print_cards(self.dealer.hand)
                print('Player Loses')
            else: 
                self.dealer_turn()
                winner = self.check_winner(on_dealer=True)
                if winner == False:
                    print('Player Loses')
                elif winner == True:
                    print('Player wins')
                    if self.betting == True:
                        self.player.bank += stake*2 
                else: 
                    print('Push')
                    if self.betting == True:
                        self.player.bank += stake
        if self.betting == True:
            print(self.player.bank)
            