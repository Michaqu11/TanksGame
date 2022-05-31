#import aima.utils
#import aima.logic

class Bot:

    def __init__(self, screen, game, bot):
        self.screen = screen
        self.game = game
        self.bot = bot
        self.clauses = []
        #self.clausesFun()

    '''def clausesFun(self):
        KB = aima.logic.FolKB(self.clauses)

        for player in self.game.players:
            if player != self:
                KB.tell(aima.utils.expr("Enemy("+self.bot+", " + player + ")"))

        hostile = KB.ask(aima.utils.expr('Enemy('+self.bot+', ' + self.screen.players[0] + ')'))

        print(hostile)'''


