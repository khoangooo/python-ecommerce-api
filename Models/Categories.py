class Categories:
	def __init__(self, database):
		"""
			input: nhập đối tượng database để khởi tạo database dùng cho class Categories
			output: void
		"""
		self.database = database

	def get_category_detail(self, category_id):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
				category_id: tương ứng với một category cụ thể trong collection Categories
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm: 
						status - trạng thái, 
						message - một tin nhắn thông báo
						data - thông tin trả về cho một category với kiểu dữ liệu dictionary tương ứng với category_id (nếu có)
					giá trị thứ hai là status_code hay HTTP code
		"""
		params = []
		query = {}
		database = self.database
		if category_id and category_id != 0:
			params.append({ "kind": int(category_id) })

		if len(params) > 0: 
			query = { "$and": params }

		pipelines = [
			{ "$match": query },
			{
				"$addFields": {
					"_id": {
						"$toString": "$_id"
					},
				}
			},
			{
			"$project": {
					"_id": 0,
					"name": 1,
					"kind": 1
			}
			},
		]

		try:
			categories = database["Categories"].aggregate(pipelines)
			data = list(categories)[0]
			res = {
				"status": True, 
				"message": "Success", 
				"data": data,
			}
			return res, 200
		except:
			return {
				"status": False,
				"message": "Something went wrong."
			}
