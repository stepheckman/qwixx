import qwixx_objects

# https://gamewright.com/pdfs/Rules/QwixxTM-RULES.pdf

def main():
    # 2 players
    hopper = qwixx_objects.Player("Hopper")
    lacey = qwixx_objects.Player("Lacey")

    game = qwixx_objects.Game(player1=hopper, player2=lacey)
    game.play(max=60)


if __name__ == "__main__":
    main()
