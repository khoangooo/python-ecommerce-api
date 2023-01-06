import math

class Products:
	def __init__(self, database):
		"""
			input: nhập đối tượng database để khởi tạo database dùng cho class Products
			output: void
		"""
		self.database = database
	
	def get_products(self, req):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
				req: hay là request, một dictionary chứa các key để thực hiện truy vấn collection Products
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm: 
						status - trạng thái, 
						message - một tin nhắn thông báo
						data - thông tin về là một list gồm một hoặc một số product nếu nội dung truy vấn là hợp lệ
					giá trị thứ hai là status_code hay HTTP code
		"""
		
		database = self.database
		sort = "name"
		order = 1
		current_page = 1
		pages = 1
		per_page = 0
		offset = 0
		total = 0
		data = []
		params = []
		query = {}

		if req.get("search"): 
			params.append({
				"name": {
					"$regex" : req.get("search") , 
					"$options" : "i"
				} 
			})

		if req.get("kind"): 
			params.append({ "kind" : int(req.get("kind")) })

		if req.get("star"): 
			params.append({ "star" : float(req.get("star")) })

		if req.get("discount"):
			params.append({ "discount": { "$gt": 0 } })

		if req.get("price_from"):
			params.append({  
				"$expr": { 
					"$gte": [
						{
							"$multiply": [
								"$price", 
								{ 
									"$subtract": [1, "$discount"] 
								}
							]
						}, 
						int(req.get("price_from"))
					] 
				} 
			})

		if req.get("price_to"):
			params.append({  
				"$expr": { 
					"$lte": [
						{
							"$multiply": [
								"$price", 
								{ 
									"$subtract": [1, "$discount"] 
								}
							]
						}, 
						int(req.get("price_to"))
					] 
				} 
			})

		if req.get("sort"):  
			sort = "discounted_price" if req.get("sort") == "price" else req.get("sort")

		if req.get("order") == "desc": 
			order = -1

		if req.get("per_page"): 
			per_page = int(req.get("per_page"))
		
		if req.get("current_page"): 
			current_page = int(req.get("current_page"))

		if len(params) > 0: 
			query = { "$and": params }

		offset = current_page * per_page

		pipelines = [
			{ "$match": query },
			{
				"$lookup": {
					"from": "Categories",
					"localField": "kind",
					"foreignField": "kind",
					"as": "NewProducts"
				}
			},
			{
				"$unwind": {
					"path": "$NewProducts",
					"preserveNullAndEmptyArrays": True
				}
			},
			{
				"$addFields": {
					"_id": {
						"$toString": "$_id"
					},
					"category": "$NewProducts.name"
				}
			},
			{
				"$project": {
					"_id": 0,
					"name": 1,
					"price": 1,
					"discount": 1,
					"kind": 1,
					"category": 1,
					"star": 1,
					"description": 1,
					"uid": 1,
					"image": 1,
					"discounted_price": {
						"$cond": [
							{ "$gt": ["$discount", 0] },
							{ "$multiply": ["$price", { "$subtract": [1, "$discount"] }] },
							"$price",
						],
					},
				}
			},
			{ "$sort": { sort: order } }
		]

		if per_page > 0:
			pipelines.extend([{ "$skip": offset }, { "$limit": per_page }])

		try:
			products = database["Products"].aggregate(pipelines)
			data = list(products)
			total = len(data) \
				if per_page == 0 or len(data) < per_page \
				else database["Products"].count_documents({})

			pages = 1 if per_page == 0 else math.ceil(total / per_page)

			res = {
				"status": True, 
				"message": "Success", 
				"data": data, 
				"total": total
			}

			if per_page > 0:
				res.setdefault("current_page", current_page)
				res.setdefault("per_page", per_page)
				res.setdefault("pages", pages)

			return res, 200

		except Exception as e:
			return {
				"status": False,
				"message": "Something went wrong."
			}, 400

	def get_product_detail(self, product_id):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
				product_id: tương ứng với một product cụ thể trong collection Products
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm: 
						status - trạng thái, 
						message - một tin nhắn thông báo
						data - thông tin trả về cho một product với kiểu dữ liệu dictionary tương ứng với product_id (nếu có)
					giá trị thứ hai là status_code hay HTTP code
		"""
		database = self.database
		params = []
		queryCmd = {}
		if product_id and product_id != 0:
			params.append({ "uid": int(product_id) })

		if len(params) > 0: 
			queryCmd = { "$and": params }

		pipelines = [
			{ "$match": queryCmd },
			{
				"$lookup": {
					"from": "Categories",
					"localField": "kind",
					"foreignField": "kind",
					"as": "NewProducts"
				}
			},
			{
				"$unwind": {
					"path": "$NewProducts",
					"preserveNullAndEmptyArrays": True
				}
			},
			{
				"$addFields": {
					"_id": {
						"$toString": "$_id"
					},
					"category": "$NewProducts.name"
				}
			},
			{
				"$project": {
					"_id": 0,
					"name": 1,
					"price": 1,
					"discount": 1,
					"kind": 1,
					"category": 1,
					"star": 1,
					"description": 1,
					"uid": 1,
					"image": 1,
					"discounted_price": {
						"$cond": [
							{ "$gt": ["$discount", 0] },
							{ "$multiply": ["$price", { "$subtract": [1, "$discount"] }] },
							"$price",
						],
					},
				}
			},
			{ "$sort": { "kind": 1 } }
		]

		try:
			product = database["Products"].aggregate(pipelines)
			data = list(product)[0]
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
			}, 400

	def count_products_by_categories(self):
		"""
			input: 
				self: dùng để truy cập các biến trong construction của class hiện tại
			output: biểu diễn câu trả lời của máy chủ (server) cho yêu cầu đến từ máy khách (client)
				gồm 2 giá trị:
					giá trị đầu tiên là dictionary mang thông tin gồm: 
						status - trạng thái, 
						message - một tin nhắn thông báo
						data - thông tin về là một list gồm các catogory và số lượng các product thuộc về cùng category đó nếu nội dung truy vấn là hợp lệ
					giá trị thứ hai là status_code hay HTTP code
		"""
		database = self.database
		pipelines = [
			{
				"$lookup": {
					"from": "Categories",
					"localField": "kind",
					"foreignField": "kind",
					"as": "NewProducts"
				}
			},
			{
				"$unwind": {
					"path": "$NewProducts",
					"preserveNullAndEmptyArrays": True
				}
			},
			{
				"$group": {
					"_id": "$kind",
					"total": {
						"$sum": 1
					},
					"kind": {
						"$first": "$kind"
					},
					"name": {
						"$first": "$NewProducts.name"
					}
				}
			},
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
					"total": 1,
					"kind": 1,
				}
			},
			{ "$sort": { "kind": 1 } }
		]

		try: 
			products = database["Products"].aggregate(pipelines)
			data = list(products)
			newData = data.copy()
			newData.insert(0, {
				"kind": 0,
				"name" : "All",
				"total": sum(d['total'] for d in data)
			})

			res = {
				"status": True, 
				"message": "Success", 
				"data": newData,
			}
			return res, 200

		except Exception as e:
			res = {
				"status": False, 
				"message": "Something went wrong.", 
			}
			return res, 400

