# Business_Project-
This project is for completion of Master's in Management (Supply Chain Logistics)
This Python model compares logistics routes from Shanghai to six UK distribution destinations through airports and seaports in the North East, Midlands and South of England. It evaluates each route by total cost, total delivery time and an equal-weight balanced cost-time score.

To run the program, just run the main.py files. It will generate all the output files: Lowest Cost, Fastest Delivery, and Balanced, along with the graphs used in the research paper. 

<!-- Model Scope -->
International modes: Air Standard, Air Fast and Sea Freight.

Domestic modes: Haulage Standard and Haulage Fast.

Airports: Newcastle, Teesside, East Midlands and Heathrow.

Seaports: Port of Tyne, Teesport and Port of Felixstowe.

Destinations: Leeds, Liverpool, Birmingham, Norwich, Kidlington (Oxford) and Bristol.

Units: costs are in pounds sterling (£); times are in days.

<!-- Project Files -->
data/Book1.xlsx: Main input workbook containing international freight, domestic haulage and gateway operational data.

outputs/ : Stores the three results workbooks and all generated PNG figures.

main.py: Main entry point. It reads and preprocesses the input data, generates and exports all route results, runs every Fig*.py script in numerical order and saves its image as Graph<number>.png.

All_routes_generator.py: Defines the permitted combinations of international and domestic modes and generates all routes for every destination.

route_generator.py: Matches international services, gateway fees and domestic haulage by gateway and destination, then calculates each route's cost and time components.

route_selector.py: Orders routes for a selected destination by cost, time or Balanced Score.

export_all_files.py: Exports all destinations to Results_Lowest_Cost.xlsx, Results_Fastest_Delivery.xlsx and Results_Balanced.xlsx, with one worksheet per destination.

excel_exporter.py: Exports a single user-selected destination and priority to a timestamped Excel file.

User_interface.py: Provides command-line selections for destination and optimisation priority.

<!-- Input workbook Coponentes -->
Directory: data/Book1.xlsx :
