import datetime
from bson.json_util import dumps


class User:

    def __init__(self, username, password=None, role="user"):
        self.username = username
        self.password = password
        self.role = role

    def save_to_db(self, mongo_connection, user_collection):
        return mongo_connection[user_collection].insert_one({"userID": self.username, "password": self.password,
                                                             "role": self.role, "last_login": "never",
                                                             "creationTime": datetime.datetime.now().isoformat()})

    def remove_from_db(self, mongo_connection, user_collection):
        token_to_remove = dict(mongo_connection[user_collection].find_one({"userID": self.username})).get('token', None)
        mongo_connection[user_collection].delete_one({"userID": self.username})
        return token_to_remove

    def get_role(self, mongo_connection, user_collection):
        user = mongo_connection[user_collection].find_one({"userID": self.username}, {'id': 0})
        return user['role']

    # thi function checks if the current user are allowed to perform the requested operation.
    # return true if the user has sufficient permission
    def check_user_permission(self, mongo_connection, user_collection, user_id):
        user = mongo_connection[user_collection].find_one({"userID": self.username}, {'id': 0})
        if user['role'] != 'admin':
            if user['userID'] != user_id:
                return False
            else:
                return True
        else:
            return True

    def check_admin_permission(self, mongo_connection, user_collection):
        user = mongo_connection[user_collection].find_one({"userID": self.username}, {'id': 0})
        return user['role'] == 'admin'

    @classmethod
    def find_by_username(cls, mongo_connection, user_collection, tenant_id):
        user = mongo_connection[user_collection].find_one({"userID": tenant_id}, {'id': 0})
        if user is not None:
            return user['userID'], user['password']
        return None, None
