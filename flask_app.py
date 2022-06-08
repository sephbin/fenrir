from flask import Flask
import ghhops_server as hs
import rhino3dm
app = Flask(__name__)
hops = hs.Hops(app)

@hops.component(
	"/projecttransform",
	name="projecttransform",
	description="projecttransform",
	icon="/home/sephbin/fenrir/icons/projecttransform.png",
	inputs = [
		hs.HopsString("From", "F", "Projection From String" ),
		hs.HopsString("To", "T", "Projection To String" ),
		# hs.HopsString("Coordinates", "C", "Coordinates as String", access=hs.HopsParamAccess.LIST),
		hs.HopsPoint("Coordinates", "C", "Coordinates as Points", access=hs.HopsParamAccess.LIST),
	],
	outputs = [
		hs.HopsPoint("T", "T", "Projected Point"),
	],
)


def projecttransform(fromProj, toProj, coordinates):
	from pyproj import Proj, Transformer

	transformer = Transformer.from_crs(fromProj,toProj, always_xy=True)

	x_Dump = []
	y_Dump = []
	points = []
	for coord in coordinates:
		coords = transformer.transform(float(coord.X),float(coord.Y))
		points.append(rhino3dm.Point3d(coords[0],coords[1],0))
		x_Dump.append(coords[0])
		y_Dump.append(coords[1])

	return points

@hops.component(
	"/giraffeGetProjectList",
	name="giraffeGetProjectList",
	description="giraffeGetProjectList",
	icon="/home/sephbin/fenrir/icons/giraffeGetProjectList.png",
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
	icon="/home/sephbin/fenrir/icons/giraffeGetProject.png",
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
	icon="/home/sephbin/fenrir/icons/giraffeGetProjectUsages.png",
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
	icon="/home/sephbin/fenrir/icons/giraffeUpdateProject.png",
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
	icon = "",
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
	# icon="icons/giraffeGetProject.png",
	inputs = [
		hs.HopsString("url", "U", "url" ),
		hs.HopsString("headers", "H", "headers" ),
	],
	outputs = [
		hs.HopsString("jsonOut", "J", "jsonOut"),
	],
)
def requestGet(url, headers):
	try:
		import requests
		import json
		print(headers)
		run = False
		allowedDomains = ['https://api.namefake.com','https://random-data-api.com', 'https://api-footprint.techequipt.com.au','https://tgbcalc.com']
		for aD in allowedDomains:
			if url.startswith(aD):
				run = True
		print("run",run)
		if run:
			cookies_dict = json.loads(headers)
			r = requests.get(url, headers=cookies_dict)#cookies=cookies_dict,
			response = r.json()
			# print("response", response, type(response))
			response = cleanDictValues(response)
			return response
		else:
			return json.dumps({"error":"restricted domain"})
		# return "Hello"
	except Exception as e:
		print("error",e)
		return json.dumps({"error":str(e)})




if __name__ == "__main__":
	app.run()