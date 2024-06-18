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
	# icon="icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("Keynote", "K", "Keynote", hs.HopsParamAccess.LIST ),
		hs.HopsString("TSheet", "T", "TSheet", optional=True ),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def keyNoteClassify(keynote, tSheet):
	import json

	return json.dumps({"code":"Ss_00_00_00_00"})



if __name__ == "__main__":
	app.run()