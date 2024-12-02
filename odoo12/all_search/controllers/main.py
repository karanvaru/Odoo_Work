# -*- coding: utf-8 -*-

import odoo
from odoo import http
from odoo.http import request
import numbers
import traceback


class OdooSearch(http.Controller):
	
	
	@http.route('/add_new_name', type='http', auth="public")
	def add_new_name(self, **kwargs):
		base_path = request.httprequest.environ['HTTP_REFERER']
		action = request.env['ir.actions.actions'].search([('name', '=', 'Contacts')], limit=1)
		url = ''
		if action:
			url = '%s#id=&action=%s&model=res.partner&view_type=form' % (base_path, action.id)
			
		temp = request.env['temp.temp'].search([('user', '=', request._uid)])
		if temp: temp.unlink()
		
		request.env['temp.temp'].sudo().create({'name': 'name', 'user': request._uid, 'value': kwargs['query']})
		
		return url
	
	@http.route('/add_new_phone', type='http', auth="public")
	def add_new_phone(self, **kwargs):
		base_path = request.httprequest.environ['HTTP_REFERER']
		action = request.env['ir.actions.actions'].search([('name', '=', 'Contacts')], limit=1)
		url = ''
		if action:
			url = '%s#id=&action=%s&model=res.partner&view_type=form' % (base_path, action.id)
			
		temp = request.env['temp.temp'].search([('user', '=', request._uid)])
		if temp: temp.unlink()
		request.env['temp.temp'].sudo().create({'name': 'phone', 'user': request._uid, 'value': kwargs['query']})
		
		return url
	
	@http.route('/add_new_mob', type='http', auth="public")
	def add_new_mob(self, **kwargs):
		base_path = request.httprequest.environ['HTTP_REFERER']
		action = request.env['ir.actions.actions'].search([('name', '=', 'Contacts')], limit=1)
		url = ''
		if action:
			url = '%s#id=&action=%s&model=res.partner&view_type=form' % (base_path, action.id)
			
		temp = request.env['temp.temp'].search([('user', '=', request._uid)])
		if temp: temp.unlink()
		request.env['temp.temp'].sudo().create({'name': 'mobile', 'user': request._uid, 'value': kwargs['query']})
		
		return url
		
		
		
		

	def one_step_inner_m2one(self, DB_MODEL, added_data, final_data_dict, avoid_tables_names, base_path, id, from_object_name):
		##FOR MANY2ONE FIELDS
		request._cr.execute("select name, relation, field_description, id from ir_model_fields where model='%s' and ttype='many2one'"%(DB_MODEL, ))
		many2one_fields = request._cr.fetchall()
		for many2one_field in many2one_fields:
			print (many2one_field, 'ffffiiii')
			try:
				ID = many2one_field[3]
				field_name = many2one_field[0]
				related_model = many2one_field[1].replace('.', '_')
				
				if related_model in ['sale_order', 'stock_picking']:
					print (field_name, 'MMMFFF')
					
				q = "select %s from %s where id=%s" % (field_name, DB_MODEL.replace('.', '_'), id[0])
				request._cr.execute(q)
				many2one_data = request._cr.fetchall()
				
				object_name = related_model
				request._cr.execute("select name from ir_model where model='%s'"%related_model.replace('_', '.'))

				object_data = request._cr.fetchall()
				if object_data and object_data[0]:
					object_name = object_data[0][0]
					
				if object_name not in avoid_tables_names:
					for item3 in many2one_data:
						
						NAME_GET = request.env[related_model.replace('_', '.')].browse(item3[0]).name_get()
						if NAME_GET and NAME_GET[0]:
							NAME_GET = NAME_GET[0][1]
						else:
							NAME_GET = ''

						line_string = NAME_GET+"-"+ object_name+"-"+ many2one_field[2]
						if line_string not in added_data and NAME_GET and NAME_GET not in ['']:
							row = [base_path, item3[0], related_model.replace('_', '.'), NAME_GET, object_name, from_object_name+">>"+many2one_field[2]]
						
							if object_name not in final_data_dict:
								final_data_dict[object_name] = [row]
							else:
								final_data_dict[object_name].append(row)
				
							added_data.append(line_string)
						
			except:
				request._cr.rollback()
				
		return added_data, final_data_dict



	def avoid(self, model):
		flag = False
		"""if 'report' in model.replace('_', '.'):
			flag = True
		if 'model' in model.replace('_', '.'):
			flag = True
		if 'website' in model.replace('_', '.'):
			flag = True
		if 'action' in model.replace('_', '.'):
			flag = True
		if 'base.' in model.replace('_', '.'):
			flag = True
		if 'ir.' in model.replace('_', '.'):
			flag = True
		if 'theme' in model.replace('_', '.'):
			flag = True
		if 'ir.module.module' in model.replace('_', '.'):
			flag = True"""
		
		return flag
	
	def exclude_tables(self, model, tables):
		exclude = False
		model_obj = request.env['ir.model'].sudo().search([('model', '=', model)])
		if model_obj.name in tables:
			exclude = True
			
		return exclude
	
	
	def get_object_name(self, model):
		object_name = ''
		request._cr.execute("select name from ir_model where model='%s'" % model.replace('_', '.'))
		object_data = request._cr.fetchall()
		if object_data and object_data[0]:
			object_name = object_data[0][0]
			
		return object_name
			
	
	def get_name_name(self, model, id):
		NAME_GET = ''
		try:
			NAME_GET = request.env[model.replace('_', '.')].browse(id).name
		except:
			request._cr.rollback()
			NAME_GET = request.env[model.replace('_', '.')].browse(id).name_get()
			if NAME_GET and NAME_GET[0]:
				NAME_GET = NAME_GET[0][1]
			else:
				NAME_GET = ''
			
		return NAME_GET	
	
	
	def get_name_name2(self, model, item):
		NAME_GET = ''
		try:
			request._cr.execute("select name from %s where id=%s" % (table.replace('.','_'), item.id))
			NAME_GET = request._cr.fetchall([0])
		except:
			request._cr.rollback()
		if not NAME_GET:
			try:
				request._cr.execute("select code from %s where id=%s" % (table.replace('.','_'), item.id))
				NAME_GET = request._cr.fetchall([0])
			except:
				request._cr.rollback()
				
		if not NAME_GET:
			NAME_GET = item.name_get()
			if NAME_GET and NAME_GET[0]:
				NAME_GET = NAME_GET[0][1]
			else:
				NAME_GET = ''	
				
		return NAME_GET	
	

	@http.route('/fetch_query_data', type='http', auth="public")
	def fetch_query_data(self, **kwargs):
		##======================================================
		# The method searches given query in all tables from the Database.
		# Initially two fields 'name' and 'origin' are considered as a basic fields to search. 
		# If the record found against 'name' and 'origin' go ahead and try to find its related records like 'many2one', 'one2many' etc.
		##======================================================
		import time
		start_time = time.time()

		stage = kwargs['stage']
		if not request.env['res.users'].browse(request._uid).has_group('all_search.group_allow_search'):
			return "<div style='color: black; text-align: center;'><h4>You don't have access rights to use Easy Search<br></br>Please contact to Administrator</h4></div>"
		
		urls = """<div><table style='border: 1px solid #7b7bad; color: black; text-align: left; width: 100%; font-size: 16px;'>
			    <tr style='border-bottom: 1pt solid #7b7bad;'>
			    <th style='padding-left:5px; '></th>
			    <th >Result</th>
			    <th >Reference</th></tr>"""
		
		avoid_tables = []
		avoid_tables_names = []
		
		for item in request.env['exclude.objects'].search([]):
			avoid_tables.append(item.model_id.model)
			avoid_tables_names.append(item.model_id.name)
		

		
		base_path = request.httprequest.environ['HTTP_REFERER']
		added_data = []
		final_data_dict = {}
		
		
		object_ids = {}
		object_id_ref = {}
		
		fields1 = ['default_code', 'name', 'origin', 'email', 'phone', 'mobile', 'e-mail', 'emailid', 'zip', 'street', 'website', 'description', 'desc', 'short_desc', 'barcode', 'subject', 'body']
		for item in request.env['new.fields'].search([]):
			str1 = item.name.strip()
			if str1:
				fields1.append(str1)
				
				
		for field in fields1 :
			
			request._cr.execute("select model from ir_model_fields where name='%s' and store=true" %(field, ))
			many2one_fields = request._cr.fetchall()
	
			for many2one_field in many2one_fields:
				
				DB_MODEL = request.env['ir.model'].sudo().search([('model', '=', many2one_field[0])])
				
				if self.avoid(DB_MODEL.model):
					continue
				
				try:
					##FIRST TRY TO FIND RECORD/RECORDS FROM 'NAME' AND/OR 'ORIGIN' FIELD FROM DATABASE
					DB_MODEL_DATA = []
					#for field in ['name', 'origin', 'email', 'phone', 'mobile', 'e-mail', 'emailid', 'zip', 'street', 'website', 'description'] :
					print ("Field loop----")
					try:				
						q = "select id from %s where %s ilike '$$%s$$'"%(DB_MODEL.model.replace('.', '_'), field, kwargs['query'])
						q = q.replace('$$', "%")
						request._cr.execute(q)
						DB_MODEL_DATA = request._cr.fetchall()
					except:
						request._cr.rollback()
						#continue
						#print (traceback.format_exc())
						
						
					model = DB_MODEL.model.replace('.', '_')
					try:
						print (2)
						##FOR CONTACT SPECIFIC
						##CONTACT MAY CONTAIN SPACES OR DASHES(-) IN NUMBERS. BELOW CODE WORK ON IT 
						if model == 'res_partner' and field == 'phone':
							s = kwargs['query'].replace('-', '').replace(' ', '')
							for contact in request.env['res.partner'].sudo().search([]):
								phone = contact.phone.replace('-', '').replace(' ', '')
								if s in phone:
									key = 'res.partner' +"$$$"+ DB_MODEL.name
									if key in object_ids:
										object_ids[key].append(contact.id)
									else:
										object_ids[key] = [contact.id]
									
									DB_MODEL_DATA.append((contact.id,))
										
										
						if model == 'res_partner' and field == 'mobile':
							s = kwargs['query'].replace('-', '').replace(' ', '')
							for contact in request.env['res.partner'].sudo().search([]):
								phone = contact.mobile.replace('-', '').replace(' ', '')
								
								if s in phone:
									key = 'res.partner' +"$$$"+ DB_MODEL.name
									if key in object_ids:
										object_ids[key].append(contact.id)
									else:
										object_ids[key] = [contact.id]
									
									DB_MODEL_DATA.append((contact.id,))
									
					except:
						request._cr.rollback()
					
					
					for DB_MODEL_DATA_RECORD in DB_MODEL_DATA:
						print ("Found record-----", DB_MODEL_DATA_RECORD)
						ID = DB_MODEL_DATA_RECORD[0]
						
						if not self.exclude_tables(DB_MODEL.model, avoid_tables_names):
							key = DB_MODEL.model.replace('_', '.') +"$$$"+ DB_MODEL.name
							if key in object_ids:
								object_ids[key].append(ID)
							else:
								object_ids[key] = [ID]
							
						
						if stage == '1':
							continue
						
						##FOR MANY2ONE FIELDS
						##FOR SECOND LAYER SEARCH
						request._cr.execute("select name, model, field_description, id from ir_model_fields where relation='%s' and ttype='many2one' and store=true "%(DB_MODEL.model, ))
						many2one_fields = request._cr.fetchall()
						
						print (DB_MODEL.model, 'zzzzzzzz')
						many2one_fields_PRPR = []
						if DB_MODEL.model == 'product.template':
							print ('jkkkkkkkkkkkkk')
							request._cr.execute("select name, model, field_description, id from ir_model_fields where relation='%s' and ttype='many2one' and store=true "%('product.product', ))
							many2one_fields_PRPR = request._cr.fetchall()
							ID2 = request.env['product.product'].sudo().search([('product_tmpl_id', '=', ID)], limit=1).id
							print (ID, 'IIII00')
							
						if DB_MODEL.model == 'product.product':
							request._cr.execute("select name, model, field_description, id from ir_model_fields where relation='%s' and ttype='many2one' and store=true "%('product.template', ))
							many2one_fields_PRPR = request._cr.fetchall()
							ID2 = request.env['product.product'].sudo().browse(ID).product_tmpl_id.id
							print ('lllpp')
							
						for many2one_field in many2one_fields:
							print ('Working..')
							

							try:
								field_name = many2one_field[0]
								related_model = many2one_field[1].replace('.', '_')
								if related_model == 'stock_move':
									print (3)
								q = "select id from %s where %s = %s"%(related_model, field_name, ID)
								
								request._cr.execute(q)
								many2one_data = request._cr.fetchall()
								
								l3 = len(many2one_data)
								l3_c = 1
								
								if not self.exclude_tables(related_model, avoid_tables_names):
									if self.avoid(related_model):
										continue
				
									object_name = self.get_object_name(related_model)
									if object_name == 'Sales Order Line':
										print (1)
									for item3 in many2one_data:
										
										if stage == '3':
											##FOR THIRD LAYER SEARCH
											added_data, final_data_dict = self.one_step_inner_m2one(many2one_field[1], added_data, final_data_dict, avoid_tables_names, base_path, item3, object_name)
										
										print (related_model)
										print ('Working... %s of %s' % (l3_c, l3))
										l3_c = l3_c + 1
										
										NAME_GET = self.get_name_name(related_model, item3[0])
										

										if 'Commercial Entity' == many2one_field[2]:
											continue
											
										key = related_model.replace('_', '.') +"$$$"+ object_name
										if key in object_ids:
											object_ids[key].append(item3[0])
										else:
											object_ids[key] = [item3[0]]
											
											
										key = related_model.replace('_', '.') +"$$$"+ str(item3[0])
										if key in object_id_ref:
											object_id_ref[key].append(many2one_field[2])
										else:
											object_id_ref[key] = [many2one_field[2]]
											
								
							except:
								request._cr.rollback()
								
							
							
						
						
						##IF WE FOUND SOME MATCH IN "PRODUCT", WE NEED TO CHECK THIS FROM "PRODUCT TEMPLATE" SIDE ALSO AND VICE-VERSA
						##FOR EXAMPLE "DEFAULT_CODE" FIELD AVAILABLE IN "PRODUCT.TEMPLATE" BUT IN MANY PLACES 
						##IN ONE TO MANY LINES "PRODUCT.PRODUCT" IS USED
						if many2one_fields_PRPR:
							for many2one_field in many2one_fields_PRPR:
								print ('Working..')
								if stage == '3':
									added_data, final_data_dict = self.one_step_inner_m2one(many2one_field[1], added_data, final_data_dict, avoid_tables_names, base_path)
	
								try:
									field_name = many2one_field[0]
									related_model = many2one_field[1].replace('.', '_')
									if related_model == 'stock_move':
										print (3)
									q = "select id from %s where %s = %s"%(related_model, field_name, ID2)
									
									request._cr.execute(q)
									many2one_data = request._cr.fetchall()
									
									
									l3 = len(many2one_data)
									l3_c = 1
									
									if not self.exclude_tables(related_model, avoid_tables_names):
										if self.avoid(related_model):
											continue
										
										object_name = self.get_object_name(related_model)
										for item3 in many2one_data:
											if stage == '3':
												added_data, final_data_dict = self.one_step_inner_m2one(many2one_field[1], added_data, final_data_dict, avoid_tables_names, base_path, item3, object_name)
											print (related_model)
											print ('Working... %s of %s' % (l3_c, l3))
											l3_c = l3_c + 1
											
											NAME_GET = self.get_name_name(related_model, item3[0])
	
											if 'Commercial Entity' == many2one_field[2]:
												continue
												
											key = related_model.replace('_', '.') +"$$$"+ object_name
											if key in object_ids:
												object_ids[key].append(item3[0])
											else:
												object_ids[key] = [item3[0]]
												
												
											key = related_model.replace('_', '.') +"$$$"+ str(item3[0])
											if key in object_id_ref:
												object_id_ref[key].append(many2one_field[2])
											else:
												object_id_ref[key] = [many2one_field[2]]
												
									
								except:
									request._cr.rollback()
									
							
										
				except:
					request._cr.rollback()
					
					
		l4 = len(object_ids.items())
		l4_c = 1
		try:			
			for k, v in object_ids.items():
				print ('Working.... %s of %s' % (l4_c, l4))
				l4_c = l4_c + 1
				v = list(set(v))
				table = k.split('$$$')[0].replace('_', '.')
				table_name = k.split('$$$')[1]
				print (table_name, v, 'tabname')
				recs = []
				try:
					recs = request.env[table].sudo().search([('id', 'in', v)], order='write_date desc')
				except:
					try:
						recs = request.env[table].sudo().search([('id', 'in', v)], order='create_date desc')
					except:
						try:
							recs = request.env[table].sudo().search([('id', 'in', v)], order='id desc')
						except:
							recs = request.env[table].sudo().search([('id', 'in', v)])
						
				l5 = len(recs)
				l5_c = 1
				for item in recs:
					print ('Working..... %s of %s' % (l5_c, l5))
					l5_c = l5_c + 1
					NAME_GET = self.get_name_name2(table, item)

					ref_key = table+"$$$"+ str(item.id)
					if ref_key in object_id_ref:
						row = [base_path, item.id, table, NAME_GET, table_name, object_id_ref[ref_key][0]]
					else:
						row = [base_path, item.id, table, NAME_GET, table_name, '']
					
					if table+"_"+str(item.id) not in added_data:
						if table_name not in final_data_dict:
							final_data_dict[table_name] = [row]
						else:
							final_data_dict[table_name].append(row)
					
						added_data.append(table+"_"+str(item.id))
				
					
			
		except:
			request._cr.rollback()		
				
			
		
		xml = ""
		
		
		for key, items in final_data_dict.items():
			urls = '<span style="border-bottom: 1pt solid #7b7bad; color: black; font-size: 16px; font-weight: bolder; margin-top: 30px">'+key+'('+str(len(items))+')'+"</span><i class='fa fa-caret-down toggle-btn'></i>"
			
			urls += '''
						<div class="header-table-div" style="overflow: hidden; margin-bottom: 35px;">
						<table style="width: 100%; color: black; margin-bottom: 20px;background-color: #eeeeee;"><colgroup>
					       <col span="1" style="width: 7%;">
					       <col span="1" style="width: 70%;">
					       <col span="1" style="width: 15%;">
					    </colgroup>''' 

			add_c = 1
			counter = 1
			hide = False
			for item in items:
				add_c += 1
				
				t = (str(counter)+"&#160;&#160;", item[0], item[1], item[2], item[3], item[5])
				if not hide:
					urls += '<tr style="border-bottom: 1pt solid #7b7bad;" class="rec-link" >\
							<td style="padding-left:5px; max-width: 50px; overflow-wrap: break-word; font-size: small;">%s</td>\
							<td style="max-width: 300px; min-width: 300px; overflow-wrap: break-word; "><a href="%s#id=%s&model=%s&view_type=form" >%s</a></td>\
							<td style="max-width: 200px; min-width: 200px; overflow-wrap: break-word; font-size: small;">%s</td>\
							</tr>'%t
					if add_c > 10 and len(items) > 10:
						urls += '<tr style="border-top: 1pt solid #7b7bad; background-color: white;" class="rec-link" >\
							<td style="padding-left:5px; max-width: 50px; overflow-wrap: break-word; font-size: small;"></td>\
							<td style="max-width: 300px; min-width: 300px; overflow-wrap: break-word; color: red; text-decoration: underline; cursor: pointer;"><span class="show-more">Show more</span><span style="margin-left: 15px" class="show-all">Show all</span></td>\
							<td style="max-width: 200px; min-width: 200px; overflow-wrap: break-word; font-size: small;"></td>\
							</tr>'
						add_c = 1
						hide = True 
					
				else:
					urls += '<tr style="border-bottom: 1pt solid #7b7bad; display: none" class="rec-link" >\
						<td style="padding-left:5px; max-width: 50px; overflow-wrap: break-word; font-size: small;">%s</td>\
						<td style="max-width: 300px; min-width: 300px; overflow-wrap: break-word; "><a href="%s#id=%s&model=%s&view_type=form" >%s</a></td>\
						<td style="max-width: 200px; min-width: 200px; overflow-wrap: break-word; font-size: small;">%s</td>\
						</tr>'%t
						
					if add_c > 10 and len(items) > 10:
						urls += '<tr style="border-top: 1pt solid #7b7bad; background-color: white;; display: none" class="rec-link" >\
							<td style="padding-left:5px; max-width: 50px; overflow-wrap: break-word; font-size: small;"></td>\
							<td style="max-width: 300px; min-width: 300px; overflow-wrap: break-word; color: red; text-decoration: underline; cursor: pointer;"><span class="show-more">Show more</span><span style="margin-left: 15px" class="show-all">Show all</span></td>\
							<td style="max-width: 200px; min-width: 200px; overflow-wrap: break-word; font-size: small;"></td>\
							</tr>'
						add_c = 1
						hide = True 
						
				counter += 1
				
			urls += "</table>"
			urls += "</div>"
			
			
			xml += urls
		
		print ('Search Completed!')
		print("--- %s seconds ---" % (time.time() - start_time))
		return xml
	
	
	





















