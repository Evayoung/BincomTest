from datetime import datetime

from fasthtml.common import *
from fasthtml.fastapp import *
from utility import backend

app, rt = fast_app()


@rt('/')
async def redirect_home():
    return Redirect('/home')

@rt('/home')
async def home():
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="/css/style.css"),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            Title("Bincom Online Test 2")
        ),

        # application body
        Body(
            Div(
                Div(
                    Ul(
                        Li(A("Home", hx_get="/", hx_target="#main-container")),
                        Li(A("View Poll", hx_get="/view_poll", hx_target="#main-container")),
                        Li(A("New Poll", hx_post="/new_poll", hx_target="#main-container")),
                    ),
                    _class="nav-container"
                ),

                Div(
                    Div(
                        H1("Polling Unit Result"),
                        Div(
                            Form(
                                Div(
                                    Input(type="text", name="name", placeholder="Enter Polling Unit ID", required=True)
                                ),
                                Button("Search", type="submit"),
                                hx_post="/get_pu_result",
                                hx_target="#table-content",
                                hx_trigger="submit",
                            ),
                        ),
                        Div(

                            _class="table-content", id="table-content"
                        ),
                    ),

                    _class="main-container", id="main-container"
                ),
                Div(
                    P("Olorundare Micheal"),
                    _class="footer-container"
                ),
                _class="page-home"
            )
        ),
    )


@rt("/view_poll")
async def view_poll():
    lgas = []
    try:
        result = await backend.get_lga()
        lgas = [i[0] for i in result]  # Populate the lgas list

    except Exception as e:
        print(e)
    return Div(
        H1("View Total Results Of LGA "),
        Div(
            P("LGA:"),

        ),
        Div(
            Form(
                Select(
                Option("Local Government Area", value=""),
                *[Option(lga, value=lga) for lga in lgas],  # Use the populated lgas list
                name="lga",
                id="lga-dropdown",
                required=True
                ),
                hx_post="/get_lga_data",
                hx_target="#lga-total",
                hx_trigger="change",
            ),
        ),

        Div(
            _class="lga-total", id="lga-total"
        ),
        _class="content"
    )


# Question 3 Answer routes
@rt("/new_poll")
async def new_poll():
    states = []
    parties = []
    try:
        # get all state
        result = await backend.get_state_for_lga()
        states = [i[0] for i in result]

        # get all party data
        result2 = await backend.get_party()
        parties = [j[0] for j in result2]

    except Exception as e:
        print(e)

    return Div(
        Div(
            Div(
                H1("Store New Polling Unit Results"),
            ),
            Div(
                Form(
                    Div(
                        Select(
                            Option("Select State", value=""),
                            *[Option(state, value=state) for state in states],
                            name="states",
                            id="state-dropdown",
                            hx_trigger="change",
                            hx_post="/get_lga_lists",
                            hx_target="#lga-dropdown-container",
                            hx_swap="innerHTML",
                            required=True
                        ),
                    ),

                    Div(
                        Select(
                            Option("Select LGA", value=""),
                            name="lga",
                            id="lga-dropdown",
                            required=True
                        ),
                        id="lga-dropdown-container"
                    ),

                    Div(
                        Select(
                            Option("Select Ward", value=""),
                            name="ward",
                            id="ward-dropdown",
                            required=True
                        ),
                        id="ward-dropdown-container"
                    ),

                    Hr(),

                    Div(
                        Select(
                            Option("Select Polling Unit", value=""),
                            name="unit",
                            id="unit-dropdown",
                            required=True
                        ),
                        id="unit-dropdown-container"
                    ),

                    Div(
                        Select(
                            Option("Select Party", value=""),
                            *[Option(party, value=party) for party in parties],
                            name="party",
                            id="party-dropdown",
                            required=True
                        ),
                    ),

                    Div(Input(type="number", name="score", placeholder="Enter Party Score", required=True)),
                    Div(Input(type="text", name="user", placeholder="Poll entered by", required=True)),
                    Div(Input(type="date", name="date_entered", required=True)),
                    Div(Input(type="text", name="address", placeholder="User IP Address", required=True)),

                    Button("Submit", type="submit"),

                    hx_post="/submit_poll",
                    hx_target="#poll-container",
                    hx_swap="innerHTML",
                ),
                id="poll-form",
                _class="new-poll"
            ),
            id="poll-container",
            _class="poll-container"
        ),
        _class="content"
    )

# ========================================= Backend Communication routes =============================================
# ------------------------------- fetch and return the list of polling units in a table
@rt("/get_pu_result", methods=['POST'])
async def table_data(req: Request):
    form_data = await req.form()
    data = form_data.get('name')
    try:
        result = await backend.get_polling_unit_result(data)
        # print(result)
    except Exception as e:
        print(e)

    fields = "Result ID", "Polling Unit ID", "Party Abbreviation", "Party Score"
    rows = [Tr(*map(Td, row)) for row in result]
    head = Thead(*map(Th, fields))
    return Table(head, *rows,)


# ------------------------------ Fetch and return List of LGA in a table
@rt("/get_lga_data", methods=['POST'])
async def get_lga_pol(req: Request):
    form_data = await req.form()
    data = form_data.get('lga')
    try:
        result = await backend.get_lga_pol_total(data)
    except Exception as e:
        print(e)

    fields = "Party", "Party Score"
    rows = [Tr(*map(Td, row)) for row in result]
    head = Thead(*map(Th, fields))
    return Table(head, *rows, )


# ------------------------------- get lists of LGA
@rt("/get_lga_lists", methods=['POST'])
async def get_lga(req: Request):
    form_data = await req.form()
    data = form_data.get('states')
    try:
        result = await backend.get_lga_for_ward(data)
        return Select(
            Option("Select LGA", value=""),
            *[Option(lga[0], value=lga[0]) for lga in result],
            name="lga",
            id="lga-dropdown",
            hx_trigger="change",
            hx_post="/get_ward_lists",
            hx_target="#ward-dropdown-container",
            hx_swap="innerHTML",
            required=True
        )

    except Exception as e:
        print(e)
        raise

# ---------------------------- This fetch the lists of wards
@rt("/get_ward_lists", methods=['POST'])
async def get_ward(req: Request):
    form_data = await req.form()
    data = form_data.get('lga')
    # print(data)
    try:
        result = await backend.get_ward_for_poll(data)
        return Select(
            Option("Select Ward", value=""),
            *[Option(ward[0], value=ward[0]) for ward in result],
            name="ward",
            id="ward-dropdown",
            hx_trigger="change",
            hx_post="/get_poll_lists",
            hx_target="#unit-dropdown-container",
            hx_swap="innerHTML",
            required=True
        )

    except Exception as e:
        print(e)
        raise


# -------------------------------------------------- This fetch the polling units
# -------------------------------------------------------------------------------------------------------------------
@rt("/get_poll_lists", methods=['POST'])
async def get_ward(req: Request):
    form_data = await req.form()
    data = form_data.get('ward')

    try:
        result = await backend.get_polling_units(data)
        return Select(
            Option("Select Polling Unit", value=""),
            *[Option(poll[0], value=poll[0]) for poll in result],
            name="unit",
            id="unit-dropdown",
            required=True
        )

    except Exception as e:
        print(e)
        raise

# -------------------------------------------- Submit New polling data
@rt("/submit_poll", methods=['POST'])
async def submit_new_pol(req: Request):
    form_data = await req.form()
    date_entered = form_data.get('date_entered')
    polling_unit_uniqueid = form_data.get('unit')
    party_abbreviation = form_data.get('party')
    party_score = form_data.get('score')
    entered_by_user = form_data.get('user')
    user_ip_address = form_data.get('address')
    state = form_data.get('states')
    lga = form_data.get('lga')
    ward = form_data.get('ward')

    errors = []

    # Validate date format
    try:
        date_ = datetime.strptime(date_entered, '%Y-%m-%d').date().isoformat()
    except ValueError:
        errors.append("Invalid date format. Please use YYYY-MM-DD.")

    # Validate party score
    if not party_score.isdigit() or int(party_score) < 0:
        errors.append("Invalid party score. Please enter a non-negative integer.")

    # Validate user input
    if not entered_by_user.strip():
        errors.append("Please enter your name.")

    # Validate user IP address
    if not user_ip_address.strip():
        errors.append("Please enter your IP address.")

    # Validate state, LGA, ward, and polling unit
    if not state.strip():
        errors.append("Please select a state.")
    if not lga.strip():
        errors.append("Please select an LGA.")
    if not ward.strip():
        errors.append("Please select a ward.")
    if not polling_unit_uniqueid.strip():
        errors.append("Please select a polling unit.")

    # Validate party
    if party_abbreviation.strip() == "Select Party":
        errors.append("Please select a party.")

    if not party_abbreviation.strip():
        errors.append("Please select a party.")

    if errors:
        return Div(
            H2("Data could not be saved", _class ="error-title"),
        Ul( *[Li(error) for error in errors]),
        Button("Back to Create Poll", _class="back-button", hx_get="/new_poll",
        hx_target="#poll-container", hx_swap="innerHTML"),
        _class ="error-container"
    )

    try:
        # Save the data to the database
        response = await backend.save_poll_data([polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user,
                                     date_, user_ip_address])

        return Div(
            H2("Saved Request Response", _class ="success-title"),
        P(f"{response}"),
        Button("Back to Create Poll", _class="back-button", hx_get="/new_poll",
        hx_target="#poll-container", hx_swap="innerHTML"),
        _class="success-container", id="success-container"
    )
    except Exception as e:
        return Div(
            H2("Error saving data", _class ="error-title"),
        P("An error occurred while saving your data. Please try again later."),
        Button("Back to Create Poll", _class ="back-button", hx_get="/new_poll",
        hx_target = "#poll-container", hx_swap = "innerHTML"),
        _class ="error-container", id="error-container"

    )


serve()
