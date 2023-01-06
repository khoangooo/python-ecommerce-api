import bcrypt

class Users:
	def __init__(self, database):
		"""
			input: nhập đối tượng database để khởi tạo database dùng cho class Users
			output: void
		"""
		self.database = database
	
	def login(self, req):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
				req: hay là request, một dictionary chứa các key để thực hiện truy vấn collection Users
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm: 
						status - trạng thái, 
						message - một tin nhắn thông báo
						data - thông tin về là một user nội dung truy vấn là hợp lệ
					giá trị thứ hai là status_code hay HTTP code
		"""
		database = self.database
		query = {"username": None, "password": None }

		if req.get("username"):
			query["username"] = req.get("username")
		
		if req.get("password"):
			query["password"] = req.get("password")

		if not query["username"] or not query["password"]:
			return {
				"status": False,
				"message": "Missing username or password"
			}, 400

		pipelines = [
			{ "$match": { "username": query["username"] } },
			{
				"$addFields": {
					"_id": {
						"$toString": "$_id"
					},
				}
			}
		]

		try:
			users = database["Users"].aggregate(pipelines)
			if users: 
				users = list(users)
				user = users[0]
				encoded_input_pw = query["password"].encode('utf-8')
				encoded_pw_from_db =  user["password"].encode('utf-8')

				check = bcrypt.checkpw(encoded_input_pw, encoded_pw_from_db)
				if check:
					return {
						"status": True,
						"message": "Success.",
						"data": user
					}, 200
				else:
					return {
						"status": False,
						"message": "Password is not match.",
					}, 401 
			else: 
				return {
					"status": False,
					"message": "No such user exists.",
				}, 400
		except Exception as e:
			return {
				"status": False,
				"message": "Something went wrong.",
			}, 500

	def sign_up(self, req):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
				req: hay là request, một dictionary chứa các key để thực hiện thêm một document vào trong collection Users
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm: 
						status - trạng thái, 
						message - một tin nhắn thông báo
					giá trị thứ hai là status_code hay HTTP code
		"""

		database = self.database
		query = {}

		if not req["confirm_password"]:
			return {
				"status": False,
				"message": "Missing confirm password.",
			}, 401

		if req["password"] != req["confirm_password"]:
			return {
				"status": False,
				"message": "Password does not match with confirm password.",
			}, 401

		for key, value in req.items():
			query[key] = value

		salt = bcrypt.gensalt()
		query.setdefault("image", "")
		query["password"] = bcrypt.hashpw(query["password"].encode('utf-8'), salt).decode("utf-8") 
		query["role"] = "customer"
		del query["confirm_password"]
		pipelines = [
			{ "$match": { "username": query["username"] } },
			{
				"$addFields": {
					"_id": {
						"$toString": "$_id"
					},
				}
			}
		]

		try:
			users = database["Users"].aggregate(pipelines)
			users = list(users)
			if users:
				user = users[0]
				return {
					"status": False,
					"message": f'username ' + user["username"] + ' existed in the system.',
				}, 409  
			else:
				new_user = database["Users"].insert_one(query)
				if new_user:
					new_users = database["Users"].aggregate(pipelines)
					new_user = list(new_users)[0]
					new_user["password"] = ""
					del new_user["role"]
					return {
						"status": True,
						"message": "Success",
						"data": new_user
					}, 200
				else:
					return {
						"status": False,
						"message": "Create new user unsuccessfully. Please try again.",
					}, 401

		except Exception as e:
			return {
				"status": False,
				"message": "Something went wrong.",
			}, 500

