from route_generator import generate_routes


def generate_all_routes(datasets):

    all_routes = {}

    combinations = [
        ("Air_Standard", "Haulage_Transport_Standard"),
        ("Air_Standard", "Haulage_Transport_Fast"),

        ("Air_Fast", "Haulage_Transport_Standard"),
        ("Air_Fast", "Haulage_Transport_Fast"),

        ("Sea_Freight", "Haulage_Transport_Standard"),
        ("Sea_Freight", "Haulage_Transport_Fast")
    ]

    destinations = (
        datasets["Haulage_Transport_Standard"]
        ["Destination"]
        .unique()
    )


    for destination in destinations:

        destination_routes = []


        for international, domestic in combinations:

            routes = generate_routes(
                datasets,
                destination,
                international,
                domestic
            )

            destination_routes.extend(routes)


        all_routes[destination] = destination_routes


    return all_routes
