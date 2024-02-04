import qwixx_objects

# https://gamewright.com/pdfs/Rules/QwixxTM-RULES.pdf


def main():
    # 2 players
    hopper = qwixx_objects.Player("Hopper")
    lacey = qwixx_objects.Player("Lacey")

    game = qwixx_objects.Game(player1=hopper, player2=lacey)
    game.play(max=10)

    for p in (lacey, hopper):
        p.print_scoresheet()
        print(str(p.scoresheet.score))


if __name__ == "__main__":
    main()
