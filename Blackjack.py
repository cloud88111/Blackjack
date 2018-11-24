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
        self.stake = 0
        
    def rand_name(self):
        return 'Guest' + ''.join([str(random.randint(0,9)) for x in range(8)])
    
class Dealer(Player):
    
    def __init__(self):
        self.name = 'Dealer'
        self.bank = float('inf')
    
class Blackjack:
    
    def __init__(self,dealer_stand=17,betting=False,decks=1,shuffle=True,cut=True,seats=6):
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
                self.players.append(Player(name=name))
            else:
                self.players.append(Player(name,bank))
        
    def create_deck(self):
        return Deck(self.cut).deck*self.decks
    
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
        for x in (1,2):
            for player in self.players:
                player.hand.append(self.draw_card())
                if len(player.hand) == 2:
                    print(player.name + ' hand:')
                    self.print_cards(player.hand)
            self.dealer.hand.append(self.draw_card())
        print('Dealer hand:')
        self.print_dealer()
        
    def get_card(self,player):
        card = self.draw_card()
        player.hand.append(card)
        self.print_cards([card])
        
    def player_turn(self,player):
        action = 'none'
        draws = 0
        print(player.name + ' Total: ' + str(self.calc_hand(player.hand)))
        while self.check_bust(player.hand) != True and action.upper() not in ['S','D']:
            action = self.get_inst(player,draws)
            if action.upper() == 'H':
                self.get_card(player)
                draws += 1
            elif action.upper() == 'D':
                player.bank -= player.stake
                player.stake = player.stake * 2
                self.get_card(player)
                draws += 1
            print(player.name + ' Total: ' + str(self.calc_hand(player.hand)))
        if self.check_bust(player.hand) == True:
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
    
    def get_inst(self,player,draws):
        if draws == 0:
            if player.hand[0].value == player.hand[1].value:
                value = input('Hit(H), Stand(S), Double(D) or Split(P)?: ')
                if value.upper() not in ['H','S','D','P']:
                    print('ERROR! You must enter H, S, D or P!')
                    value = self.get_inst(player,draws)
            else:
                value = input('Hit(H), Stand(S) or Double(D)?: ')
                if value.upper() not in ['H','S','D']:
                    print('ERROR! You must enter H, S or D!')
                    value = self.get_inst(player,draws)
        else:
            value = input('Hit(H) or Stand(S)?: ')
            if value.upper() not in  ['H','S']:
                print('ERROR! You must enter H or S!')
                value = self.get_inst(player,draws)
        return value
            
        
    def dealer_turn(self):
        self.print_cards(self.dealer.hand)
        print('Dealer Total: ' + str(self.calc_hand(self.dealer.hand)))
        while self.calc_hand(self.dealer.hand) < self.dealer_stand:
            self.get_card(self.dealer)
            print('Dealer Total: ' + str(self.calc_hand(self.dealer.hand)))
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
            
    def get_stake(self):
        stake = input('How much would you like to bet? ')
        return int(stake)
        
    def play(self):
        self.new_game()
        if self.betting == True:
            for player in self.players:
                player.stake = self.get_stake()
                player.bank += -player.stake
        self.deal()
        for player in self.players:
            if self.check_winner(player,on_deal=True) == False:
                print('Dealer Hand')
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
                    print('Dealer Hand')
                    self.print_cards(self.dealer.hand)
                    print(player.name + ' Loses')
        self.dealer_turn()
        for player in self.players:
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
                print(player.name, player.bank)

b = Blackjack(betting=True)
"""b.add_player('Rob',5000)
play_on = True
while play_on == True:
    b.play()
    play_on = input('Would you like to play another hand? (Y/N): ')
    play_on = (True if play_on.upper() == 'Y' else False)"""