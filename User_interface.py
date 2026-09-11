def choose_destination(datasets):

    destinations = sorted(
        datasets["Haulage_Transport_Standard"]["Destination"].unique()
    )

    print("\nAvailable destinations:\n")

    for i, destination in enumerate(destinations, start=1):
        print(f"{i}. {destination}")

    choice = int(input("\nChoose destination: "))

    return destinations[choice - 1]


def choose_priority():

    print("\nChoose optimisation objective:\n")

    print("1. Lowest Cost")
    print("2. Fastest Delivery")
    print("3. Balanced")

    choice = input("\nEnter choice: ")

    if choice == "1":
        return "cost"

    elif choice == "2":
        return "time"

    else:
        return "balanced"