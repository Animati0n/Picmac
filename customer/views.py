from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings
from artist.views import uploadFile

c =settings.CUR
conn = settings.CONN

# Create your views here.

def payment(request):
    artid = request.session['artid']
    c.execute("SELECT * FROM `arts` WHERE `id`={}".format(artid))
    art = c.fetchone()
    unameId = request.session['userId']
    postData = request.session['postData']
    if "pay" in request.POST:
        c.execute("INSERT INTO `customerPayment`(`artId`,`custId`, `status`,`fname`,`lname`,`phone`,`pincode`,`landmark`,`address`,`district`) VALUES ({},{},{},'{}','{}','{}','{}','{}','{}','{}')".format(artid,unameId,1,postData['firstName'],postData['lastName'],postData['phone'],postData['pincode'],postData['landmark'],postData['address'],postData['district']))
        if(conn.commit() == None):
            c.execute("UPDATE `arts` SET `status`= 2 WHERE `id`={}".format(artid))
            if conn.commit() == None:
                return redirect("/customer/myorders")
    return render(request,"payment/payment.html",{'art':art})

def home(request):
    artList =[]
    
    username = request.session['username']
    c.execute("SELECT userType FROM users WHERE username= %s ",([username]))
    data = c.fetchone()
    c.execute("SELECT ar.*,us.firstName,us.lastName FROM `arts` AS ar INNER JOIN users as us WHERE us.id = ar.artistId AND ar.status = 1")
    data2 = c.fetchall()
    print("data2:", data2)
    if len(data2) != 0:
        artList = data2
        msg = {'username':username,'userType':data['userType'],'artList':artList}
        return render(request,'customer/userdash.html',msg)
    msg = {'username':username,'userType':data['userType']}
    return render(request,'customer/userdash.html',msg) 

def bookNow(request):
    try:
        request.session['username']
    except KeyError:
        return redirect("/signup")
    uname = request.session['username']
    unameId = request.session['userId']
    dislist = ['Alappuzha','Ernakulam','Idukki','Kannur','Kasaragod','Kollam','Kottayam','Kozhikode','Malappuram','Palakkad','Pathanamthitta','Thiruvananthapuram','Thrissur','Wayanad',]
    c.execute("SELECT * FROM `users` WHERE `id`={}".format(unameId))
    udetail = c.fetchone()
    if "booknowbtn" in request.POST:
        artid = request.POST["artid"]

        return render(request,"customer/booking.html",{'udetail':udetail,'dislist':dislist,"artid":artid})  
    
    print(udetail)
    
    if "booknowbtn2" in request.POST:
        if "dis" in request.POST and request.POST['dis'] == '0':
            return render(request,"customer/booking.html",{'udetail':udetail,'dislist':dislist,'error':'Please select district'}) 
        postData = {
            "firstName": request.POST["firstName"],
            "lastName": request.POST["lastName"],
            "phone": request.POST["phone"],
            "pincode": request.POST["pincode"],
            "landmark": request.POST["landmark"],
            "district": request.POST["dis"],
            "address": request.POST["address"],
        }
        artid = request.POST["artid"]
        request.session['artid'] = artid
        

        c.execute("UPDATE `users` SET `firstName`='{}',`lastName`='{}',`pincode`='{}',`landmark`='{}',`district`='{}',`phone`='{}',address='{}' WHERE `id`={}".format(postData['firstName'],postData['lastName'],postData['pincode'],postData['landmark'],postData['district'],postData['phone'],postData['address'],unameId))
        resp = conn.commit()
        if(resp == None):
            request.session['postData'] = postData
            
            return redirect(payment) 

        
    return render(request,"customer/booking.html",{'udetail':udetail,'dislist':dislist})    



def quickView(request):
    try:
        request.session['username']
    except KeyError:
        return redirect("/signup")
    if "quickView" in request.POST:
        artId = request.POST['artId']
        c.execute('SELECT ar.*,us.firstName,us.lastName FROM `arts` as ar INNER JOIN users as us WHERE ar.id = {}'.format(artId))
        artDetails = c.fetchone()

        if artDetails:
            c.execute('SELECT ar.*,us.firstName,us.lastName FROM `arts` as ar INNER JOIN users as us ON ar.artistId = us.id WHERE ar.artistId = {} AND ar.status = 1'.format(artDetails['artistId']))
            artistArts = c.fetchall()
            return render(request,'customer/quickview.html',{'artDetails':artDetails,'artistArts':artistArts})
    if "quickViewreq" in request.POST:
        reqId = request.POST['reqId']
        c.execute("SELECT rq.*,us.firstName,us.lastName,ar.artName,ar.imageUrl,ar.discription as artDes FROM `requests` AS rq INNER JOIN arts ar ON ar.id = rq.artId INNER JOIN users us ON us.id = ar.artistId WHERE rq.id = {}".format(reqId))
        reqDetail = c.fetchone()
        return render(request,'customer/quickview.html',{'reqDetail':reqDetail})
    return redirect("/")

def myorders(request):
    unameId = request.session['userId']
    c.execute("SELECT cp.*,us.firstName,us.lastName,ar.artName,ar.price,ar.imageUrl,ar.id as artID FROM `customerPayment` AS cp INNER JOIN arts as ar ON cp.artId = ar.id INNER JOIN users as us ON us.id = ar.artistId WHERE cp.custId = {}".format(unameId))
    myordersList = c.fetchall()
    return render(request,'customer/MyRequest.html',{'myordersList':myordersList})

def requestNow(request):
    try:
        request.session['username']
    except KeyError:
        return redirect("/signup")
    unameId = request.session['userId']

    if "requestBtn" in request.POST:
        artId = request.POST['artId']
        c.execute('SELECT * FROM `arts` WHERE id = {}'.format(artId))
        artDetails = c.fetchone()
        return render(request,"customer/Request.html",{"artDetails":artDetails})

    if "finalReqBtn" in request.POST:
        artId = request.POST['artId']
        price = request.POST['price']
        width = request.POST['width']
        height = request.POST['height']
        dim = request.POST['dim']
        c.execute('SELECT * FROM `arts` WHERE id = {}'.format(artId))
        artDetails = c.fetchone()
        img = ''
        if "img" in request.FILES:
            img = uploadFile(request.FILES['img'])    
        if price == "0" or price == 0:
            price = artDetails['price']
        discr = request.POST['subject']   
        c.execute("INSERT INTO `requests` (`artId`,`reqPrice`,`width`, `height`, `dimension`, `image`, `discription`,`custId`, `status`) VALUES ({},{},'{}','{}','{}','{}','{}',{},1)".format(artId,price,width,height,dim,img,discr,unameId))
        if conn.commit() == None:
            return redirect("/customer/myrequests")

    return redirect("/")    



def myrequests(request):
    unameId = request.session['userId']
    c.execute("SELECT rq.*,us.firstName,us.lastName,ar.artName,ar.imageUrl FROM `requests` AS rq INNER JOIN arts ar ON ar.id = rq.artId INNER JOIN users us ON us.id = ar.artistId WHERE rq.custId = {}".format(unameId))
    myReqList = c.fetchall()
    return render(request,'customer/MyRequest.html',{'myReqList':myReqList})


def searchResult(request):
    if "searchbtn" in request.POST:
        searchTerm = request.POST['keyword']
        c.execute("SELECT ar.*,us.firstName,us.lastName FROM `arts` as ar INNER JOIN users as us ON us.id = ar.artistId WHERE ar.status = 1 AND (ar.artName LIKE '%{searchTerms}%' OR ar.catname LIKE '%{searchTerms}%' OR ar.discription LIKE '%{searchTerms}%' OR ar.width LIKE '%{searchTerms}%' or ar.height LIKE '%{searchTerms}%')".format(searchTerms=searchTerm))
        artList = c.fetchall()
        if(len(artList)>0):
            return render(request,"customer/searchresult.html",{"artList":artList})
        else:
            return render(request,"customer/searchresult.html")
    if "keyword" in request.GET:
        searchTerm = request.GET['keyword']
        c.execute("SELECT ar.*,us.firstName,us.lastName FROM `arts` as ar INNER JOIN users as us ON us.id = ar.artistId WHERE ar.status = 1 AND (ar.artName LIKE '%{searchTerms}%' OR ar.catname LIKE '%{searchTerms}%' OR ar.discription LIKE '%{searchTerms}%' OR ar.width LIKE '%{searchTerms}%' or ar.height LIKE '%{searchTerms}%')".format(searchTerms=searchTerm))
        artList = c.fetchall()
        if(len(artList)>0):
            return render(request,"customer/searchresult.html",{"artList":artList})
        else:
            return render(request,"customer/searchresult.html")
    return redirect("/")     