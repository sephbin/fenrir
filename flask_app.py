from flask import Flask
import ghhops_server as hs
import rhino3dm
app = Flask(__name__)
hops = hs.Hops(app)



@hops.component(
	"/projecttransform",
	name="projecttransform",
	description="projecttransform",
	#icon="/home/sephbin/fenrir/#icons/projecttransform.png",
	inputs = [
		hs.HopsString("From", "F", "Projection From String" ),
		hs.HopsString("To", "T", "Projection To String" ),
		# hs.HopsString("Coordinates", "C", "Coordinates as String", hs.HopsParamAccess.LIST),
		hs.HopsPoint("Coordinates", "C", "Coordinates as Points"),
	],
	outputs = [
		hs.HopsPoint("T", "T", "Projected Point"),
	],
)


def projecttransform(fromProj, toProj, coordinates):
	print(fromProj, toProj, coordinates)
	points = None
	try:
		from pyproj import Proj, Transformer, CRS
		fromCRS = CRS.from_epsg(int(fromProj.replace("EPSG:","")))
		toCRS = CRS.from_epsg(int(toProj.replace("EPSG:","")))
		# print(toCRS)
		#print("-"*100)
		print(fromCRS, fromCRS.area_of_use)
		print(toCRS, toCRS.area_of_use)
		# for d in dir(toCRS):
		# 	print(d)
		transformer = Transformer.from_crs(fromCRS,toCRS, always_xy=True)

		x_Dump = []
		y_Dump = []
		points = []
		if type(coordinates) != type([]):
			coordinates = [coordinates]
		for coord in coordinates:
			print(coord)
			coords = transformer.transform(float(coord.X),float(coord.Y))
			print(coords)
			points.append(rhino3dm.Point3d(coords[0],coords[1],0))
			x_Dump.append(coords[0])
			y_Dump.append(coords[1])

	except Exception as e:
		print(e)
	return points

@hops.component(
	"/giraffeGetProjectList",
	name="giraffeGetProjectList",
	description="giraffeGetProjectList",
	#icon="/home/sephbin/fenrir/#icons/giraffeGetProjectList.png",
	inputs = [
		hs.HopsString("Token", "T", "Token" ),
	],
	outputs = [
		hs.HopsString("I", "I", "I"),
		hs.HopsString("P", "P", "P"),
	],
)
def giraffeGetProjectList(token):
	import requests
	domain = "https://app.giraffe.build"
	projectsUrl = "/api/projects/"
	cookies_dict = {"giraffe_session": token}
	r = requests.get(domain+projectsUrl, cookies=cookies_dict)
	data = r.json()
	indexList = []
	nameList = []
	for i in data["results"]:
		print(i)
		indexList.append(i["id"])
		nameList.append(i["boundary"]["properties"]["name"])
	return indexList, nameList

@hops.component(
	"/giraffeGetProject",
	name="giraffeGetProject",
	description="giraffeGetProject",
	#icon="/home/sephbin/fenrir/#icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("Token", "T", "Token" ),
		hs.HopsInteger("ID", "I", "ID" ),
	],
	outputs = [
		hs.HopsString("J", "J", "J"),
	],
)
def giraffeGetProject(token, projectId):
	try:
		import requests
		import json
		domain = "https://app.giraffe.build"
		url = "/api/projects/%s/"%(projectId)
		cookies_dict = {"giraffe_session": token}
		r = requests.get(domain+url, cookies=cookies_dict)
		projectData = r.json()

		url = "/api/sections/?projectId=%s"%(projectId)
		r = requests.get(domain+url, cookies=cookies_dict)
		projectData["sections"] = r.json()["results"]
		print(projectData)
		for section in projectData["sections"]:
			print(section)
			cleanProperties = {"layerId":"","id":"","projectId":"","stackOrder":1,"levels":"","cornerRadius":"","public":"","appId":"","usage":"","setback":""}
			try:
				cleanProperties.update(section["boundary"]["properties"])
				section["boundary"]["properties"] = cleanProperties
			except Exception as e:
				cleanProperties["error"] = str(e)
				section["boundary"]["properties"] = cleanProperties
		return json.dumps(projectData)
	except Exception as e:
		return str(e)

@hops.component(
	"/giraffeGetProjectUsages",
	name="giraffeGetProjectUsages",
	description="giraffeGetProjectUsages",
	#icon="/home/sephbin/fenrir/#icons/giraffeGetProjectUsages.png",
	inputs = [
		hs.HopsString("Token", "T", "Token" ),
		hs.HopsInteger("ID", "I", "ID" ),
	],
	outputs = [
		hs.HopsString("J", "J", "J"),
	],
)
def giraffeGetProjectUsages(token, projectId):
	try:
		import requests
		import json
		domain = "https://app.giraffe.build"
		url = "/api/projectapps.json/?projectId=%s"%(projectId)
		cookies_dict = {"giraffe_session": token}
		r = requests.get(domain+url, cookies=cookies_dict)
		projectData = r.json()["results"]
		outOb ={}
		for r in projectData:
			outOb.update(r["featureCategories"]["usage"])

		return json.dumps(outOb)
	except Exception as e:
		return str(e)
@hops.component(
	"/giraffeUpdateProject",
	name="giraffeUpdateProject",
	description="giraffeUpdateProject",
	#icon="/home/sephbin/fenrir/#icons/giraffeUpdateProject.png",
	inputs = [
		hs.HopsString("Token", "T", "Token" ),
		hs.HopsString("JSON", "J", "JSON" ),
	],
	outputs = [
		hs.HopsString("R", "R", "R"),
	],
)
def giraffeUpdateProject(token, data):
	try:
		import requests
		import json
		cookies_dict = {"giraffe_session": token}
		domain = "https://app.giraffe.build"
		data = json.loads(data)
		projectId = data["id"]
		url = "/api/sections/?projectId=%s"%(projectId)
		r = requests.get(domain+url, cookies=cookies_dict)
		sectionData = r.json()["results"]
		print(sectionData)
		for section in sectionData:
			url = "/api/sections/%s"%(section["id"])
			r = requests.delete(domain+url, cookies=cookies_dict)
		for section in data["sections"]:
			url = "/api/sections/"
			r = requests.post(domain+url, json = section, cookies=cookies_dict)



		return "Done Updating"
	except Exception as e:
		return str(e)

@hops.component(
	"/QRencoder",
	name = "QRencoder",
	description = "Encodes input/s to a QR code binary",
	#icon = "",
	inputs = [
		hs.HopsString("Data", "d", "Data to encode", access=hs.HopsParamAccess.LIST),
	],
	outputs = [
		hs.HopsString("Binary", "b", "Binary representation of QR Code")
	],
)

def QREncoder(d):
	import pyqrcode

	b2 = []

	for substring in d:
		code = pyqrcode.create(substring)
		b2.append(code.text(quiet_zone=0).replace("\n",""))

	return b2

def cleanDictValues(dictionary):
	# print("cleanDictVal")
	# print(type(dictionary))
	if type(dictionary) == type({}):
		for k,v in dictionary.items():
			# print("\t",type(v))
			if type(v) == type(""):
				dictionary[k] = v.replace("\"","'").replace("\n"," ").replace("ç","c")
			if type(v) == type({}) or type(v) == type([]):
				dictionary[k] = cleanDictValues(v)
	if type(dictionary) == type([]):
		# print("running list")
		for k,v in enumerate(dictionary):
			# print("\t",k,type(v))
			if type(v) == type(""):
				dictionary[k] = v.replace("\"","'").replace("\n"," ").replace("ç","c")
			if type(v) == type({}) or type(v) == type([]):
				dictionary[k] = cleanDictValues(v)
	return dictionary



@hops.component(
	"/requestGet",
	name="requestGet",
	description="requestGet",
	# #icon="#icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("url", "U", "url", optional=True ),
		hs.HopsString("headers", "H", "headers", optional=True ),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def requestGet(url="https://api.namefake.com", headers = {}):
	try:
		import requests
		import json
		urls = url.split("|")
		outList = []
		for url_i in urls:
			run = False
			allowedDomains = ['https://api.namefake.com','https://random-data-api.com', 'https://api-footprint.techequipt.com.au','https://tgbcalc.com']
			for aD in allowedDomains:
				if url.startswith(aD):
					run = True
			# print("run",run)
			if run:
				cookies_dict = json.loads(headers)
				r = requests.get(url_i, headers=cookies_dict)#cookies=cookies_dict,
				response = r.json()
				# print("response", response, type(response))
				response = cleanDictValues(response)
				# print(response)
				if type(response) == type([]):
					for r in response:
						if type(r) == type({}):
							r["url"] = url_i
					outList = outList+response
				else:
					outList.append(response)
			else:
				return json.dumps({"error":"restricted domain"})
			# return "Hello"
		return outList
	except Exception as e:
		# print("error",e)
		return json.dumps({"error":str(e)})

@hops.component(
	"/renderSVG",
	name="renderSVG",
	description="renderSVG",
	# #icon="#icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("SVG", "SVG", "SVG" ),
	],
	outputs = [
		hs.HopsString("IMG", "IMG", "IMG"),
	],
)
def renderSVG(svg):
	try:
		# import io
		print("renderSVG", svg)
		if type(svg) != type([]):
			svg = [svg]
		import subprocess
		import locale
		# from PIL import Image
		inkscape = r"C:\Program Files\Inkscape\bin\inkscape.exe"
	except:pass
@hops.component(
	"/TEST",
	name="TEST",
	description="TEST",
	# icon="icons/giraffeGetProject.png",
	inputs = [
		hs.HopsCurve("TEST", "TEST", "TEST", access=hs.HopsParamAccess.LIST),
		# hs.HopsDefault("DTEST", "DTEST", "DTEST" ),
	],
	outputs = [
		hs.HopsCurve("objOUT", "O", "objOUT"),
	],
)
def func_test(TEST=None):
	try:
		result = subprocess.run([inkscape, '--export-type=png', '--export-filename=-', f'--export-width={420*72}', f'--export-height={297*72}', '--pipe'], input=svg[0].encode(), capture_output=True)
		
		stdout =str(result.stdout)
		print("-"*50)
		print(stdout)
		return stdout
		# print(result)
		# with open("testImg.png", "wb") as file:
		# 	file.write(result.stdout)
		# print(in_memory_file)
	except Exception as e:
		print(e)
		return ""

@hops.component(
	"/textMatchList",
	name="textMatchList",
	description="textMatchList",
	# ##icon="#icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("list", "L", "list", hs.HopsParamAccess.LIST),
		hs.HopsString("search", "S", "search", hs.HopsParamAccess.LIST),
		hs.HopsNumber("threshold", "T", "threshold"),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def textMatchList(L, S, T):
	import json
	from fuzzywuzzy import fuzz
	from fuzzywuzzy import process
	try:
		out = []
		for searchString in S:
			# scored = process.extract(searchString, L, scorer=fuzz.token_sort_ratio)
			scored = process.extract(searchString, L, limit=int(T))
			print(scored)
			out.append(str(scored))
	except Exception as e:
		print(e)
	return out

@hops.component(
	"/devTest",
	name="devTest",
	description="devTest",
	# #icon="#icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("url", "U", "url" ),
		hs.HopsString("headers", "H", "headers" ),
	],
	outputs = [
		hs.HopsInteger("jsonOut", "J", "jsonOut"),
	],
)
def devTest(url, headers):
	return 7

@hops.component(
	"/sendToDB",
	name="sendToDB",
	description="sendToDB",
	# #icon="#icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("J", "J", "J" ),
	],
	outputs = [
		hs.HopsString("PRINT", "PRINT", "PRINT"),
	],
)
def sendToDB(J):
	import json
	try:
		J = json.loads(J)

		file = rhino3dm.File3dm()
		for ob in J:
			mesh = rhino3dm.GeometryBase.Decode(ob)
			file.Objects.Add(mesh)
		file.Write(r"C:\mydev\fenrir\files\test.3dm")

		# print(J["InneerTree"])
		# print(mesh)
		# verts = map(lambda x: (x.X,x.Y,x.Z), mesh.Vertices)
		# print(list(verts))
		return "COMPLETED"
	except Exception as e:
		return str(e)

@hops.component(
    "/pointat",
    name="PointAt",
    description="Get point along curve",
    inputs=[
        hs.HopsCurve("Curve", "C", "Curve to evaluate"),
        hs.HopsNumber("t", "t", "Parameter on Curve to evaluate"),
    ],
    outputs=[
        hs.HopsPoint("P", "P", "Point on curve at t")
    ]
)
def pointat(curve, t):
    return curve.PointAt(t)

@hops.component(
	"/getGeom",
	name="getGeom",
	description="getGeom",
	# icon="icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("pk", "P", "pk", optional=True ),
		# hs.HopsString("headers", "H", "headers", optional=True ),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def getGeom(pk):
	import requests
	import json
	url = "http://localhost:8000/muninn/test/?updated__gt=2023-07-17+15%3A06%2B0000".format(pk=pk)
	# url = "http://localhost:8000/muninn/test.json/"
	r = requests.get(url)
	response = r.json()
	if type(response) != type([]):
		response = [response]
	response = list(map(lambda x: json.dumps(x["geometry"]), response))
	return response


@hops.component(
	"/postGeom",
	name="postGeom",
	description="postGeom",
	# icon="icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("post", "P", "post", optional=True ),
		# hs.HopsString("headers", "H", "headers", optional=True ),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def postGeom(pk):
	import requests
	import json
	pk = json.loads(pk)
	# url = "http://localhost:8000/muninn/test.json/".format(pk=pk)
	url = "http://localhost:8000/muninn/test/3/"
	data = {"pk":3, "geometry":pk}
	# r = requests.post(url, json=data)
	r = requests.put(url, json=data)
	print(r)
	response = r.json()
	try:
		if type(response) != type([]):
			response = [response]
		response = list(map(lambda x: json.dumps(x["geometry"]), response))
	except:
		response = json.dumps(response)
	return response


@hops.component(
	"/keyNoteClassify",
	name="keyNoteClassify",
	description="keyNoteClassify",
	inputs = [
		hs.HopsString("Keynote", "K", "Keynote", hs.HopsParamAccess.LIST ),
		hs.HopsString("TSheet", "T", "TSheet", optional=True ),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def keyNoteClassify(keynotes, tSheet):
	import json
	jsonFilePath = r'E:\mydev\Arch_Manu-Hackathon\data\testJSON.json'
	#print(keynote, tSheet)
	#print("Keynote: ", keynotes["InnerTree"]["{0;0}"])
	with open(jsonFilePath) as f:
		matchData = json.load(f)
	matches = {}
	for keynoteValue in keynotes:
		if keynoteValue in matchData:
			print("Keynote: ", keynoteValue)
			print("Uniclass: ", matchData[keynoteValue]["CODE"])
			matches[keynoteValue] = {}
			matches[keynoteValue]["MaterialUniClass"] = matchData[keynoteValue]["CODE"]
			matches[keynoteValue]["Confidence"] = matchData[keynoteValue]["Confidence"]

	return [json.dumps(matches)]

@app.route("/roomNames")
def roomNames():
	names = ["test"
		# {"name":"ACCESS SHAFT","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"ALLERGEN PREP","department":"CATERING FACILITIES","class":"boh habitable"},
		# {"name":"ATRIUM - GENERAL","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"ATRIUM - PREMIUM","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"BAR OUTLET","department":"CATERING FACILITIES","class":"bar aco-medium habitable foh"},
		# {"name":"BASEMENT STORE","department":"PREMIUM AREAS","class":"store boh"},
		# {"name":"BEER RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"BIKE PARKING","department":"ADMINISTRATION FACILITIES","class":"foh"},
		# {"name":"BIN BAY","department":"CLEANING AND WASTE FACILITIES","class":"bin boh"},
		# {"name":"BIN STORE","department":"CLEANING AND WASTE FACILITIES","class":"store bin boh"},
		# {"name":"BOWL - CORPORATE BOXES","department":"SEATING BOWL","class":"foh"},
		# {"name":"BOWL - MEMBERS SEATS","department":"SEATING BOWL","class":"foh"},
		# {"name":"BOWL - PREMIUM LOUNGE","department":"SEATING BOWL","class":"foh"},
		# {"name":"BOWL - PREMIUM TERRACE","department":"SEATING BOWL","class":""},
		# {"name":"BOWL - SEATING POSITION - SEATED","department":"SEATING BOWL","class":"foh"},
		# {"name":"BOWL - SEATING POSITION - SEATED UB","department":"SEATING BOWL","class":"foh"},
		# {"name":"BOWL - SUITE","class":"SEATING BOWL","department":"foh"},
		# {"name":"BOWL - SUPER SUITE","department":"SEATING BOWL","class":"foh"},
		# {"name":"CAMERA DECK","department":"MEDIA FACILITIES","class":"boh aco-medium"},
		# {"name":"CATERING STORE - LOOSE FF&E","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"CHANGING PLACE","department":"GENERAL ADMISSION AREAS","class":"wet toilet universalaccess foh"},
		# {"name":"CHEFS/ HACCP OFFICE","department":"CATERING FACILITIES","class":"boh office aco-medium habitable"},
		# {"name":"CLEANERS OFFICE","department":"FACILITY MANAGEMENT AREAS","class":"boh office aco-medium habitable"},
		# {"name":"CLEANERS ROOM","department":"CLEANING AND WASTE FACILITIES","class":"cleanersroom boh habitable"},
		# {"name":"CLUB LOUNGE CLOAK ROOM","department":"PREMIUM AREAS","class":"foh"},
		# {"name":"COACHES BOXES","department":"TEAM FACILITIES","class":"boh studio habitable"},
		# {"name":"COACHES BRIEFING","department":"TEAM FACILITIES","class":"boh habitable"},
		# {"name":"COACHES OFFICE","department":"TEAM FACILITIES","class":"boh office aco-medium habitable"},
		# {"name":"COACHES TOILET","department":"TEAM FACILITIES","class":"wet toilet unisex boh"},
		# {"name":"COACHES TOILET (UA)","department":"PREMIUM AREAS","class":"wet toilet unisex"},
		# {"name":"COLD KITCHEN","department":"CATERING FACILITIES","class":"boh habitable"},
		# {"name":"COLD SHELL","department":"OTHER","class":"boh"},
		# {"name":"COMMS RISER","department":"ENGINEERING SERVICES","class":"riser comms boh"},
		# {"name":"COMMS ROOM","department":"ENGINEERING SERVICES","class":"plant comms boh habitable"},
		# {"name":"CONCESSION COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"CONCESSION FREEZER","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"CONCOURSE - GENERAL","department":"CIRCULATION AREAS","class":"aco-medium foh"},
		# {"name":"CONCOURSE - PREMIUM","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"CORPORATE CORRIDOR","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"DAIRY COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"DAS ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"DAY STORE","department":"EVENT DAY FACILITIES","class":"store boh"},
		# {"name":"DB RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"DECANT COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"DETERGENT STORE","department":"CLEANING AND WASTE FACILITIES","class":"store boh"},
		# {"name":"DIAMOND CLUB","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"DIAMOND CLUB RECEPTION & CLOAK","department":"PREMIUM AREAS","class":"foh"},
		# {"name":"DIESEL TANK","department":"ENGINEERING SERVICES","class":"plant mech boh"},
		# {"name":"DISH & POT STORE","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"DISH & POT WASHING","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"DOCK MANAGERS OFFICE","department":"FACILITY MANAGEMENT AREAS","class":"boh office aco-medium habitable"},
		# {"name":"DOPING CONTROL STATION","department":"TEAM FACILITIES","class":"boh medical aco-medium habitable"},
		# {"name":"DOPING CONTROL TOILETS","department":"TEAM FACILITIES","class":"wet toilet unisex boh"},
		# {"name":"DOPING CONTROL TOILETS - (UA-L)","department":"TEAM FACILITIES","class":"wet toilet universalaccess lefth boh"},
		# {"name":"DRINKS STATION","department":"TEAM FACILITIES","class":"boh habitable"},
		# {"name":"ELECTRICAL RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"ENTRANCE - GENERAL","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"ENTRANCE - VIP","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"ESCALATOR","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"EVENT BREAK ROOM","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"EVENT BRIEFING ROOM","department":"EVENT DAY FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"EVENT DAY OFFICE","department":"EVENT DAY FACILITIES","class":"boh office aco-medium habitable"},
		# {"name":"EVENT LAUNDRY COLLECTION","department":"EVENT DAY FACILITIES","class":"boh"},
		# {"name":"EVENT STAFF FACILITIES","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"EVENT WASH ROOM - (F)","department":"EVENT DAY FACILITIES","class":"boh toilet female"},
		# {"name":"EVENT WASH ROOM - (M)","department":"EVENT DAY FACILITIES","class":"boh toilet male"},
		# {"name":"EVENT WASH ROOM - (UA)","department":"EVENT DAY FACILITIES","class":"wet toilet unisex boh"},
		# {"name":"FHR","class":"ENGINEERING SERVICES","department":"fhr boh fireequiptment"},
		# {"name":"FINISHED GOODS COOLROOM 1","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"FINISHED GOODS COOLROOM 2","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"FIRE BOOSTER ASSEMBLY","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"FIRE CONTROL ROOM","department":"ENGINEERING SERVICES","class":"plant boh fireequiptment"},
		# {"name":"FIRE RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"FIRST AID POST","department":"EVENT DAY FACILITIES","class":"boh medical aco-medium habitable"},
		# {"name":"FIRST AID ROOM","department":"EVENT DAY FACILITIES","class":"boh medical aco-medium habitable"},
		# {"name":"FIRST AID WC UA-R","department":"PREMIUM AREAS","class":"wet toilet universalaccess righth foh"},
		# {"name":"GA TOILET (F)","department":"GENERAL ADMISSION AREAS","class":"wet toilet female foh"},
		# {"name":"GA TOILET (M)","department":"GENERAL ADMISSION AREAS","class":"wet toilet male foh"},
		# {"name":"GA TOILET (UA-L)","department":"GENERAL ADMISSION AREAS","class":"wet toilet universalaccess lefth foh"},
		# {"name":"GA TOILET (UA-R)","department":"GENERAL ADMISSION AREAS","class":"wet toilet universalaccess righth foh"},
		# {"name":"GAS METER ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"GENERAL/ VEG COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"GENERATOR ROOM","department":"ENGINEERING SERVICES","class":"plant generator boh"},
		# {"name":"GOODS LIFT","department":"CIRCULATION AREAS","class":"lift boh"},
		# {"name":"GREASE TRAP","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"HIRERS DINING ROOM","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"HIRERS OFFICE","department":"EVENT DAY FACILITIES","class":"boh office aco-medium habitable"},
		# {"name":"HOT KITCHEN","department":"CATERING FACILITIES","class":"boh habitable"},
		# {"name":"HOT WATER ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"HV CONTROL ROOM","department":"ENGINEERING SERVICES","class":"plant generator boh"},
		# {"name":"HV INTAKE ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"HYDRAULIC RISER","department":"ENGINEERING SERVICES","class":"riser hydro boh"},
		# {"name":"IN-HOUSE VIDEO PRODUCTION","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"INDEPENDENT MEDICAL ROOM","department":"TEAM FACILITIES","class":"boh medical aco-medium habitable"},
		# {"name":"INDEPENDENT MEDICAL ROOM TOILETS - (UA-R)","department":"TEAM FACILITIES","class":"wet toilet universalaccess righth boh"},
		# {"name":"INDOOR WICKETS","department":"OTHER","class":"boh"},
		# {"name":"INGREDIENT COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"INWARD GOODS/ DECANT","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"KEG & PACKAGED LIQUOR COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"KITCHEN FREEZER","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"KITCHEN STORE","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"LIFT LOBBY","department":"CIRCULATION AREAS","class":"lift foh"},
		# {"name":"LINEN STORE","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"LIQUOR STORE","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"LOADING DOCK - CATERING","department":"FACILITY MANAGEMENT AREAS","class":"boh"},
		# {"name":"LOADING DOCK - GENERAL SUPPLIES","department":"FACILITY MANAGEMENT AREAS","class":"boh"},
		# {"name":"LOCKER ROOM","department":"TEAM FACILITIES","class":"boh habitable"},
		# {"name":"MAIN COMPUTER ROOM","department":"ENGINEERING SERVICES","class":"plant boh habitable"},
		# {"name":"MAIN SWITCH ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"MAKE-UP STUDIO","department":"MEDIA FACILITIES","class":"boh habitable"},
		# {"name":"MDF ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"MEAT COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"MECH - PITCH DRAIN","department":"ENGINEERING SERVICES","class":"plant mech boh"},
		# {"name":"MECH OTHER","department":"ENGINEERING SERVICES","class":"plant mech boh"},
		# {"name":"MECH RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"MEDIA - TOILET (UA -R)","department":"MEDIA FACILITIES","class":"wet toilet unisex boh"},
		# {"name":"MEDIA - TOILET (UA)","department":"MEDIA FACILITIES","class":"wet toilet unisex boh"},
		# {"name":"MEDIA LOUNGE","department":"MEDIA FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"MEDIA STORE","department":"MEDIA FACILITIES","class":"store boh"},
		# {"name":"MEDIA TOILET (F)","department":"MEDIA FACILITIES","class":"wet toilet female boh"},
		# {"name":"MEDIA TOILET (M)","department":"MEDIA FACILITIES","class":"wet toilet male boh"},
		# {"name":"MEDICAL ROOM","department":"TEAM FACILITIES","class":"boh medical aco-medium habitable"},
		# {"name":"MEMBERS RECEPTION","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"MEMBERS RESERVE","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"MEMBERS TERRACE","department":"PREMIUM AREAS","class":"foh"},
		# {"name":"MERCHANDISE KIOSK","department":"COMMERCIAL FACILITIES","class":"habitable foh"},
		# {"name":"MERCHANDISE SUPER STORE","department":"COMMERCIAL FACILITIES","class":"habitable foh"},
		# {"name":"OB COMPOUND","department":"MEDIA FACILITIES","class":"boh"},
		# {"name":"OB GENERATOR","department":"MEDIA FACILITIES","class":"boh"},
		# {"name":"OB MULTI-PURPOSE ROOMS","department":"MEDIA FACILITIES","class":"boh"},
		# {"name":"OB PATCH ROOM","department":"MEDIA FACILITIES","class":"boh"},
		# {"name":"OB RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"OB TOILET (M)","department":"MEDIA FACILITIES","class":"wet toilet male boh"},
		# {"name":"OFFICE - 2P (G&M)","department":"FACILITY MANAGEMENT AREAS","class":"boh office aco-medium habitable"},
		# {"name":"OFFICE - 3P (BSO)","department":"FACILITY MANAGEMENT AREAS","class":"boh office aco-medium habitable"},
		# {"name":"OFFICIALS BOX","department":"TEAM FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"OFFICIALS LOBBY","department":"TEAM FACILITIES","class":"boh"},
		# {"name":"OFFICIALS LOCKER ROOM (F)","department":"TEAM FACILITIES","class":"boh habitable privatelocker female"},
		# {"name":"OFFICIALS LOCKER ROOM (M)","department":"TEAM FACILITIES","class":"boh habitable privatelocker male"},
		# {"name":"OSD PIPE ROOM","department":"OTHER","class":"boh"},
		# {"name":"OSD TANK","department":"OTHER","class":"boh"},
		# {"name":"OUTDOOR TERRACE","department":"OTHER","class":"boh"},
		# {"name":"OUTLET - BAR","department":"CATERING FACILITIES","class":"bar aco-medium habitable foh"},
		# {"name":"OUTLET - FOOD","department":"CATERING FACILITIES","class":"habitable foh"},
		# {"name":"PA SYSTEM CONTROL ROOM","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"PARENTING RM","department":"GENERAL ADMISSION AREAS","class":"habitable foh"},
		# {"name":"PARK (TEAM)","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"PARK (VIP)","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"PASSENGER LIFT","department":"CIRCULATION AREAS","class":"lift foh"},
		# {"name":"PATRON SERVICES OFFICE","department":"EVENT DAY FACILITIES","class":"boh office aco-medium habitable"},
		# {"name":"PHOTOGRAPHERS WORKROOM","department":"MEDIA FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"PHYSIO / MASSAGE","department":"TEAM FACILITIES","class":"boh habitable"},
		# {"name":"PITCH ACCESS VOMITORIES","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"PLAYERS LOBBY","department":"TEAM FACILITIES","class":"boh"},
		# {"name":"PLAYERS WET AREA","department":"TEAM FACILITIES","class":"boh"},
		# {"name":"PLAYING SURFACE","department":"PITCH","class":""},
		# {"name":"POLICE BRIEFING ROOM","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"POLICE INTERVIEW ROOM","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"POLICE RECEPTION","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"PRAYER RM","department":"GENERAL ADMISSION AREAS","class":"habitable foh"},
		# {"name":"PREM PARENTING RM","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"PREM TOILETS - (F)","department":"PREMIUM AREAS","class":"wet toilet female foh"},
		# {"name":"PREM TOILETS - (M)","department":"PREMIUM AREAS","class":"wet toilet male foh"},
		# {"name":"PREM TOILETS - (UA-L)","department":"PREMIUM AREAS","class":"wet toilet universalaccess lefth foh"},
		# {"name":"PREM TOILETS - (UA-R)","department":"PREMIUM AREAS","class":"wet toilet universalaccess righth foh"},
		# {"name":"PREM TOILETS - (UNISEX)","department":"PREMIUM AREAS","class":"wet toilet unisex foh"},
		# {"name":"PREM TOILETS - AIRLOCK","department":"PREMIUM AREAS","class":"wet toilet airlock foh"},
		# {"name":"PREMIUM LOUNGE","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"PREMIUM LOUNGE CLOAK ROOM","department":"PREMIUM AREAS","class":"foh"},
		# {"name":"PREMIUM TERRACE","department":"PREMIUM AREAS","class":"foh"},
		# {"name":"PREPARATION","department":"CATERING FACILITIES","class":"boh habitable"},
		# {"name":"PRESS CONFERENCE ROOM","department":"MEDIA FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"PRESS VIDEO BOOTH","department":"MEDIA FACILITIES","class":"boh habitable aco-medium"},
		# {"name":"PRODUCTION BREAKOUT ROOM","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"PRODUCTION OFFICE","department":"CATERING FACILITIES","class":"boh office aco-medium habitable"},
		# {"name":"PROPERTY ROOM","department":"TEAM FACILITIES","class":"boh"},
		# {"name":"PUMP ROOM - BORE WATER","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"PUMP ROOM - FIRE","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"PUMP ROOM - POTABLE WATER","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"PUMP ROOM - RAINWATER","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"RADIO BOX (S)","department":"MEDIA FACILITIES","class":"boh studio habitable"},
		# {"name":"RAMP","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"RECOVERY ROOM","department":"TEAM FACILITIES","class":"boh habitable"},
		# {"name":"SATELLITE KITCHEN","department":"CATERING FACILITIES","class":"boh habitable"},
		# {"name":"SATELLITE KITCHEN - RISER","department":"ENGINEERING SERVICES","class":"riser boh"},
		# {"name":"SEAFOOD COOLROOM","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"SECURITY OFFICE","department":"FACILITY MANAGEMENT AREAS","class":"boh office aco-medium habitable"},
		# {"name":"SECURITY OFFICE BREAK ROOM","department":"FACILITY MANAGEMENT AREAS","class":"boh aco-medium habitable"},
		# {"name":"SECURITY TOILET (UA)","department":"FACILITY MANAGEMENT AREAS","class":"wet toilet unisex boh"},
		# {"name":"SERVICE / BOH CORRIDORS","department":"CIRCULATION AREAS","class":"boh circulation"},
		# {"name":"SERVICE LIFT","department":"CIRCULATION AREAS","class":"lift boh"},
		# {"name":"SERVICE ROAD","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"SERVICE STAIRS","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"SEWER PUMP ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"SFIP","department":"ENGINEERING SERVICES","class":"boh fireequiptment"},
		# {"name":"SIGN IN DESK","department":"EVENT DAY FACILITIES","class":"boh habitable"},
		# {"name":"SIN BIN","department":"SEATING BOWL","class":""},
		# {"name":"SMOKE EXHAUST","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"STAIR","department":"CIRCULATION AREAS","class":"firestair foh"},
		# {"name":"STAIR LOBBY","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"STORE - CELLAR STORE","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"STORE - CHEMICALS","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - CLEANERS","department":"CLEANING AND WASTE FACILITIES","class":"store boh"},
		# {"name":"STORE - EVENT","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - FURNITURE","department":"FACILITY MANAGEMENT AREAS","class":"store furniture boh"},
		# {"name":"STORE - GAS","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - GENERAL","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - GROUNDS AND MAINTENANCE","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - GROW LIGHTS AND FANS","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - HOME TEAM","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - KEGS","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"STORE - LINE MARKING","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - MERCHANDISE","department":"EVENT DAY FACILITIES","class":"store boh"},
		# {"name":"STORE - MOBILE EQUIPMENT DISPERSED","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"STORE - RADIO","department":"EVENT DAY FACILITIES","class":"store boh"},
		# {"name":"STORE - SAND","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - SEED & FERTILISER","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - SOIL","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - SPIRIT STORE","department":"CATERING FACILITIES","class":"store boh"},
		# {"name":"STORE - SPORTING EQUIPMENT STORE","department":"FACILITY MANAGEMENT AREAS","class":"store boh"},
		# {"name":"STORE - UNIFORM","department":"EVENT DAY FACILITIES","class":"store boh"},
		# {"name":"STUDIO BOX","department":"MEDIA FACILITIES","class":"boh studio habitable"},
		# {"name":"SUB-STATION","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"SUITE","department":"PREMIUM AREAS","class":"aco-medium habitable foh"},
		# {"name":"SUITE CORRIDOR","department":"CIRCULATION AREAS","class":"foh"},
		# {"name":"SUITE TERRACE","department":"PREMIUM AREAS","class":"foh"},
		# {"name":"SUPER SUITE","department":"PREMIUM AREAS","class":"aco-medium habitable foh"},
		# {"name":"SUPER SUITE RECEPTION & CLOAK","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"SUPER SUITE TOILETS - (F)","department":"PREMIUM AREAS","class":"wet toilet female foh"},
		# {"name":"SUPER SUITE TOILETS - (M)","department":"PREMIUM AREAS","class":"wet toilet male foh"},
		# {"name":"SUPER SUITE TOILETS - (UA-L)","department":"PREMIUM AREAS","class":"wet toilet universalaccess lefth foh"},
		# {"name":"SUPER SUITE TOILETS - (UA-R)","department":"PREMIUM AREAS","class":"wet toilet universalaccess lefth foh"},
		# {"name":"SUPER SUITE TOILETS - AIRLOCK","department":"PREMIUM AREAS","class":"wet toilet airlock foh"},
		# {"name":"SWITCH ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"TANK - BORE WATER","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"TANK - POTABLE WATER","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"TANK - RAINWATER","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"TANK - SEWER HOLDING","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"TEAM CIRCULATION","department":"TEAM FACILITIES","class":"boh"},
		# {"name":"TICKET BOX EAST","department":"EVENT DAY FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"TICKET BOX WEST","department":"EVENT DAY FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"TRAINING CHEFS TABLE","department":"CATERING FACILITIES","class":"boh habitable"},
		# {"name":"TROLLEY PARK","department":"CATERING FACILITIES","class":"boh"},
		# {"name":"TROLLEY WASH","department":"CIRCULATION AREAS","class":"boh"},
		# {"name":"TUNNEL - PRIMARY","department":"TEAM FACILITIES","class":"boh"},
		# {"name":"TUNNEL CLUB","department":"PREMIUM AREAS","class":"habitable foh"},
		# {"name":"TV COMMENTARY BOX","department":"MEDIA FACILITIES","class":"boh habitable"},
		# {"name":"UNALLOCATED","department":"OTHER","class":"boh"},
		# {"name":"UNUSED ROOM","department":"OTHER","class":""},
		# {"name":"UPS ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"UTILITY","department":"ADMINISTRATION FACILITIES","class":"aco-medium foh"},
		# {"name":"VEHICLE WASHDOWN BAY","department":"FACILITY MANAGEMENT AREAS","class":"boh"},
		# {"name":"VOID","department":"OTHER","class":""},
		# {"name":"WARM-UP ROOM","department":"TEAM FACILITIES","class":"boh aco-medium habitable"},
		# {"name":"WASTE STORE","department":"CLEANING AND WASTE FACILITIES","class":"store boh"},
		# {"name":"WATER METER ROOM","department":"ENGINEERING SERVICES","class":"plant boh"},
		# {"name":"WRITTEN PRESS","department":"MEDIA FACILITIES","class":"boh aco-medium habitable"},
	]
	return names

if __name__ == "__main__":
	# app.run()
	
	app.run(debug=True)