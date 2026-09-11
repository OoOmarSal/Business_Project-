import pandas as pd

def generate_routes(
        datasets,
        destination,
        international_mode,
        domestic_mode):

    routes = []
    fees = datasets["Operational_Fees"]
    international = datasets[international_mode]

    domestic = datasets[domestic_mode]


    for _, int_row in international.iterrows():

        for _, dom_row in domestic.iterrows():

            # Check gateway connection
            if int_row["Gateway"] == dom_row["Gateway"]:

                # Check destination
                if dom_row["Destination"] == destination:
                    fee_row = fees[
                        fees["Gateway"] == int_row["Gateway"]
                        ].iloc[0]

                    international_cost = int_row["Average_Cost"]

                    domestic_cost = dom_row["Average_Cost"]


                    international_time = int_row["Average_Time"]

                    domestic_time = dom_row["Average_Time"]

                    operational_cost = (
                            fee_row["Average_Handling"]
                            + fee_row["Average_Security"]
                            + fee_row["Documentation"]
                    )

                    processing_time = fee_row["Average_Time"]

                    total_cost = (
                            international_cost
                            + operational_cost
                            + domestic_cost
                    )

                    total_time = (
                            international_time
                            + processing_time
                            + domestic_time
                    )


                    routes.append({

                        "International_Mode": international_mode,

                        "Domestic_Mode": domestic_mode,

                        "Gateway": int_row["Gateway"],

                        "Destination": destination,

                        "International_Cost": international_cost,

                        "Domestic_Cost": domestic_cost,

                        "Total_Cost": total_cost,

                        "International_Time": international_time,

                        "Domestic_Time": domestic_time,

                        "Total_Time": total_time,

                        "Operational_Cost": operational_cost,

                        "Processing_Time": processing_time,

                    })


    return routes

def generate_all_routes(datasets, destination):

    all_routes = []


    combinations = [

        ("Air_Standard", "Haulage_Transport_Standard"),

        ("Air_Standard", "Haulage_Transport_Fast"),

        ("Air_Fast", "Haulage_Transport_Standard"),

        ("Air_Fast", "Haulage_Transport_Fast"),

        ("Sea_Freight", "Haulage_Transport_Standard"),

        ("Sea_Freight", "Haulage_Transport_Fast")

    ]


    for international, domestic in combinations:

        routes = generate_routes(
            datasets,
            destination,
            international,
            domestic
        )

        all_routes.extend(routes)



    return all_routes
