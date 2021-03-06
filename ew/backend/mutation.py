from . import core as bknd_core
from ..static import cfg as ewcfg
from ..utils import core as ewutils


class EwMutation:
    id_server = -1
    id_user = -1
    id_mutation = ""

    data = ""
    # whether or not a mutation is gained through surgery
    artificial = 0

    # the level of a mutation
    tier = 0

    # unique id for every instance of a mutation. auto increments
    # a counter of -1 means the player doesn't have this mutation
    mutation_counter = -1

    """ Create a new EwMutation and optionally retrieve it from the database. """

    def __init__(self, id_user = None, id_server = None, id_mutation = None):
        # Retrieve the object from the database if the user is provided.
        if (id_user != None) and (id_server != None) and (id_mutation != None):
            self.id_server = id_server
            self.id_user = id_user
            self.id_mutation = id_mutation

            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                # Retrieve object
                cursor.execute("SELECT {data}, {mutation_counter}, {tier}, {artificial} FROM mutations WHERE id_user = %s AND id_server = %s AND {id_mutation} = %s".format(
                    data=ewcfg.col_mutation_data,
                    mutation_counter=ewcfg.col_mutation_counter,
                    id_mutation=ewcfg.col_id_mutation,
                    tier=ewcfg.col_tier,
                    artificial=ewcfg.col_artificial
                ), (
                    id_user,
                    id_server,
                    id_mutation,
                ))
                result = cursor.fetchone()

                if result != None:
                    # Record found: apply the data to this object.
                    self.data = result[0]
                    self.mutation_counter = result[1]
                    self.tier = result[2]
                    self.artificial = result[3]

            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

    """ Save this mutation object to the database. """

    def persist(self):

        try:
            # Get database handles if they weren't passed.
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Save the object.
            cursor.execute("REPLACE INTO mutations(id_user, id_server, {id_mutation}, {data}, {mutation_counter}, {tier}, {artificial}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
                id_mutation=ewcfg.col_id_mutation,
                data=ewcfg.col_mutation_data,
                mutation_counter=ewcfg.col_mutation_counter,
                tier=ewcfg.col_tier,
                artificial=ewcfg.col_artificial
            ), (
                self.id_user,
                self.id_server,
                self.id_mutation,
                self.data,
                self.mutation_counter,
                self.tier,
                self.artificial
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)

    def clear(self):
        try:
            bknd_core.execute_sql_query("DELETE FROM mutations WHERE {mutation_counter} = %s".format(
                mutation_counter=ewcfg.col_mutation_counter
            ), (
                self.mutation_counter
            ))
        except:
            ewutils.logMsg("Failed to clear mutation {} for user {}.".format(self.id_mutation, self.id_user))
