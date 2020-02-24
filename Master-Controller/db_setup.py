from werkzeug.security import generate_password_hash
userID = "admin"
password_start = "passw0rd"
role_start = "admin"
password_cifrata = generate_password_hash(password_start)
mongo_db_setup = {'userID': userID, 'password': password_cifrata, 'role': role_start}

# Inserire user nel mongoDB
# db.createUser(
#   {
#     user: "admin",
#     pwd: "passw0rd",
#     roles: [
#        {role: "userAdminAnyDatabase", db:"admin"}
#     ]
#   }
# )



# db-svc-mc.default.svc.cluster.local