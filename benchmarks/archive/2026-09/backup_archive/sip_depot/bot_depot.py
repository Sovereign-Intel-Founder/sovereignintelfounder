import time

class CircuitBreaker:
    def __init__(self, max_drawdown=1000.0):
        self.tripped = False
        self.drawdown = 0.0
        self.max_drawdown = max_drawdown

    def check(self):
        if self.drawdown >= self.max_drawdown:
            self.tripped = True
        return not self.tripped

class BotDepot:
    def __init__(self, pool_size=5):
        self.skeleton_pool = [{"bot_id": i, "state": "PRE_WARMED", "allocated_capital": 5000.0} for i in range(pool_size)]

    def acquire_bot(self):
        if not self.skeleton_pool:
            return None
        bot = self.skeleton_pool.pop(0)
        bot["state"] = "FIRED"
        bot["fire_timestamp_ns"] = time.time_ns()
        return bot

    def return_bot(self, bot):
        bot["state"] = "PRE_WARMED"
        bot["fire_timestamp_ns"] = None
        self.skeleton_pool.append(bot)
