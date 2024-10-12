import mysql.connector
from config import settings

class Backend:
    def __init__(self):
        super().__init__()
        self.mydb = mysql.connector.connect(
            host=settings.HOST,
            user=settings.USER,
            passwd=settings.PASSWORD,
            database=settings.DATABASE,
            port=settings.PORT
        )

        self.polling_dict = {}

    # create cursor
    def _get_cursor(self):
        return self.mydb.cursor()

    # close cursor
    def _close_cursor(self, cursor):
        cursor.close()


    # ----------------------------------------- Fetch Polling by id
    def get_polling_unit(self, data):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT * FROM polling_unit WHERE polling_unit_id=%s", (data, ))
            result = cursor.fetchall()
            # print(result)
            return result
        finally:
            self._close_cursor(cursor)


    # ------------------------------------------ Fetch poll sum totals
    async def get_lga_pol_total(self, data):
        with self._get_cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT 
                        apr.party_abbreviation, 
                        SUM(apr.party_score) AS total_score
                    FROM 
                        announced_pu_results apr
                    JOIN 
                        polling_unit pu ON apr.polling_unit_uniqueid = pu.uniqueid
                    JOIN 
                        lga l ON pu.lga_id = l.lga_id
                    WHERE 
                        l.lga_name = %s
                    GROUP BY 
                        apr.party_abbreviation;
                """, (data,))
                result = cursor.fetchall()
                if not result:
                    return []
                return result
            except Exception as e:
                print(f"Exception Error: {e}")
                return []


    # ------------------------------------------ Get Selected LGA
    async def get_lga(self):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT lga_name FROM lga")
            result = cursor.fetchall()
            # print(result)
            return result
        finally:
            self._close_cursor(cursor)

    # --------------------------------------------- Get Available States
    async def get_state_for_lga(self):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT state_name, state_id FROM states")
            result = cursor.fetchall()

            return result
        finally:
            self._close_cursor(cursor)

    # --------------------------------------- Get LGA belonging to State ---------------------------------------------
    async def get_lga_for_ward(self, data):
        cursor = self._get_cursor()
        try:
            cursor.execute("""
                SELECT l.lga_name, l.lga_id
                FROM lga l
                JOIN states s ON l.state_id = s.state_id
                WHERE s.state_name = %s;
            """, (data,))
            result = cursor.fetchall()

            return result
        finally:
            self._close_cursor(cursor)

    # ----------------------------------------------- Get wards  belonging to LGA ---------------------------------
    async def get_ward_for_poll(self, data):
        cursor = self._get_cursor()
        try:
            cursor.execute("""
                        SELECT w.ward_name, w.ward_id
                        FROM ward w
                        JOIN lga l ON w.lga_id = l.lga_id
                        WHERE l.lga_name = %s;
                    """, (data,))
            result = cursor.fetchall()

            return result
        finally:
            self._close_cursor(cursor)

    # ------------------------------------- Get polling units belonging to a ward -------------------------------------
    async def get_polling_units(self, data):
        cursor = self._get_cursor()
        try:
            cursor.execute("""
                        SELECT p.polling_unit_name, p.polling_unit_id
                        FROM polling_unit p
                        JOIN ward w ON p.ward_id = w.ward_id
                        WHERE w.ward_name = %s;
                    """, (data,))
            result = cursor.fetchall()
            for i in result:
                self.polling_dict[i[0]] = i[1]
            print("Polling data", self.polling_dict)
            return result
        finally:
            self._close_cursor(cursor)

    async def get_party(self):
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT partyname FROM party")
            result = cursor.fetchall()
            # print(result)
            return result
        finally:
            self._close_cursor(cursor)

    # ------------------------------------- Get selected polling units data -------------------------------------
    async def get_polling_unit_result(self, data):
        cursor = self._get_cursor()
        try:
            cursor.execute("""
                SELECT 
                    result_id, polling_unit_uniqueid, party_abbreviation, party_score  
                FROM 
                    announced_pu_results where polling_unit_uniqueid=%s
                    """, (data,))
            result = cursor.fetchall()
            # print(result)
            return result
        finally:
            self._close_cursor(cursor)

    def get_poll_id(self, data):
        for poll, id_ in self.polling_dict.items():
            if data == poll:
                print(id_)
                break
            return id_

    # ----------------insert new poll
    async def save_poll_data(self, data):
        cursor = self._get_cursor()
        print(f"The raw data {data[0]}")
        unit_id = self.get_poll_id(data[0])
        print(unit_id)
        print(data)
        try:
            cursor.execute("""
                INSERT INTO announced_pu_results 
                (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                           (unit_id, data[1], data[2], data[3], data[4], data[5]))
            print("success")
            return "Poll record created successfully"
        except Exception as e:
            print(e)
            return str(e)

        finally:
            self._close_cursor(cursor)


backend = Backend()