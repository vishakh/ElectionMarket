# ElectionMarket - Election market game for the Cryptonomic Summer 2019 hackathon

import smartpy as sp

class ElectionMarket(sp.Contract):
    def __init__(self, admin):
        self.init(administrator = admin, balances = sp.BigMap())

    # candidate - Name of new candidate to add to game
    # amount    - Initial amount of free tokens for the candiate
    @sp.entryPoint
    def addCandidate(self, params):
        sp.if ~(params.candidate in self.data.balances):
            self.data.balances[params.candidate] = sp.Map()
            self.data.balances[params.candidate][self.data.administrator] = params.amount
            
    @sp.entryPoint
    def addUser(self, params):
        sp.if ~("credits" in self.data.balances):
            self.data.balances["credits"] = sp.Map()
        sp.if ~(sp.sender in self.data.balances["credits"]):
            self.data.balances["credits"][sp.sender] = 100

    # candidate - Which candidate's tokens to buy
    # amount    - Amount of tokens to buy
    @sp.entryPoint
    def buy(self, params):
        # The given candidate should be valid
        sp.verify(params.candidate in self.data.balances)
        # The buyer should have enough credits
        sp.verify(self.data.balances["credits"][sp.sender] >= params.amount)
        # There should be enough free tokens for the given candidate
        sp.verify(self.data.balances[params.candidate][self.data.administrator] >= params.amount)
        # Ensure the sender starts out with a zero token balance if they have never owned this candidate's tokens.
        sp.if ~(sp.sender in self.data.balances[params.candidate]):
            self.data.balances[params.candidate][sp.sender] = 0
        self.data.balances[params.candidate][sp.sender] += params.amount
        self.data.balances[params.candidate][self.data.administrator] -= params.amount
        self.data.balances["credits"][sp.sender] -= params.amount 
    
    # candidate - Which candidate's tokens to buy
    # amount    - Amount of tokens to buy
    @sp.entryPoint
    def sell(self, params):
        # The given candidate should be valid
        sp.verify(params.candidate in self.data.balances)
        sp.verify(self.data.balances[params.candidate][sp.sender] >= params.amount)
        self.data.balances[params.candidate][sp.sender] -= params.amount
        self.data.balances[params.candidate][self.data.administrator] += params.amount
        self.data.balances["credits"][sp.sender] += params.amount

    @addTest(name = "ElectionMarket test")
    def test():
        admin = sp.address("admin")
        user1 = sp.address("donkey")
        user2 = sp.address("monkey")
        c1 = ElectionMarket(admin)
        html  = c1.fullHtml()
        html += c1.addUser().run(sender = user1).html()
        html += c1.addUser().run(sender = user2).html()
        html += c1.addCandidate(candidate="Bernie Sanders", amount = 1000).run(sender = admin).html()
        html += c1.addCandidate(candidate="Elizabeth Warren", amount = 1000).run(sender = admin).html()
        html += c1.buy(candidate="Bernie Sanders", amount = 100).run(sender = user1).html()
        html += c1.sell(candidate="Bernie Sanders", amount = 50).run(sender = user1).html()
        setOutput(html)
