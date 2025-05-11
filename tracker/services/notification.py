class Notify:
    def __init__(self, notification_engine):
        self.engine = notification_engine

    @staticmethod
    def notify_user(user, message):
        print(f"{message}")
        print(f'Notified to {user}')