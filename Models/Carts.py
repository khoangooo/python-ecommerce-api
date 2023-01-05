from datetime import datetime

class Carts:
	def __init__(self, database):
		"""
			input: nhập đối tượng database để khởi tạo database dùng cho class Carts
			output: void
		"""
		self.database = database

	def add_to_cart(self, req):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
				req: hay là request, đối tượng giỏ hàng được gửi lên từng web hoặc app
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm 
						status - trạng thái
						message - một tin nhắn thông báo
					giá trị thứ hai là status_code hay HTTP code
		"""
		database = self.database
		cart = {}

		for key, value in req.items():
			cart[key] = value

		cart["date"] = datetime.now().isoformat()

		try:
			new_cart = database["Carts"].insert_one(cart)
			if new_cart:
				return {
						"status": True,
						"message": "Success",
					}, 200
			else:
				return {
					"status": False,
					"message": "Add your items to cart unsucessfully. Please try again",
					}, 302

		except Exception as e:
			return {
					"status": False,
					"message": "Something went wrong.",
			}, 500
