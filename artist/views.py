from ctypes import addressof
from re import sub
from urllib import request
from django.conf import settings
from django.http.response import HttpResponse, JsonResponse,HttpResponseRedirect
from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
import random
import string
from django.urls import reverse
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
c =settings.CUR
conn = settings.CONN

def getSubscriptionDetail(artistId):
    c.execute("SELECT * FROM `subscription` WHERE `artistid`= {}".format(artistId))
    subdata = c.fetchone()
    return subdata
def insertArtistPayment(subid,price,status):
    c.execute("INSERT INTO `artistPayment`(`subid`, `price`, `status`) VALUES ({},{},{})".format(subid,price,status))
    return conn.commit()

# Create your views here.
artistid = ''

#Subscriptio
def subscription(request):
    artistid = request.session['userId']
    c.execute("SELECT * FROM `subscription` WHERE `artistid`= {}".format(artistid))
    subdata = c.fetchone()
    
    if subdata == None:
        pagestatus = 1
    else:
        pagestatus = 0

    if "sub-btn" in request.POST:
        subtype = request.POST.get("sub_id")
        print(subtype)
        if subtype == "1":
            print("inside first")
            today = date.today()
            expire = date.today() + relativedelta(months=+6)
            c.execute("INSERT INTO `subscription`(`subtype`, `subdate`, `expiredate`, `status`,`subname`,`artistid`)VALUES('{}','{}','{}',{},'{}',{})".format(subtype,today,expire,1,"free",artistid))
            conn.commit()
            return redirect(artuploads)
            
        elif subtype == "2" :
            plan = {"price":1199 ,"type":"Pro" ,"ntype":"2"}
            #return redirect(request,"/artist/payment",{'temp':pagestatus,'plan':plan,})
            #return render(request,"payment/payment.html",{'plan':plan,'temp':pagestatus})

        elif subtype == "3":
            plan = {"price":2000 ,'type':"Ultimate","ntype":"3"}
            print(plan)
        request.session['plan'] = plan
        request.session['state'] = pagestatus 
        #
        return HttpResponseRedirect("/artist/payment",)    #

        
            
    
    return render(request,"subscription.html",{'pagestatus': pagestatus})

def payment(request):
    print("inside")
    artistid = request.session['userId']
    today = date.today()
    plan =  request.session['plan']
    state =  request.session['state']
    print(state)
    type = plan['ntype']
    print(type)
    if "pay" in request.POST:
        if state == 1:
            if type == "2":
                expire = date.today() + relativedelta(months=+6)
                print("Today's date:", today)
                print(expire)
                print("pro")
                c.execute("INSERT INTO `subscription`(`subtype`, `subdate`, `expiredate`, `status`,`subname`,`artistid`)VALUES('{}','{}','{}',{},'{}',{})".format(type,today,expire,1,"pro",artistid))
                conn.commit()
                subData = getSubscriptionDetail(artistid)
                price = request.session['plan']['price']
                if insertArtistPayment(subData['id'],price,1) == None:

                    return redirect(artuploads)
            elif type == "3":
                expire = date.today() + relativedelta(years=+1)
                print("Today's date:", today)
                print(expire)
                print("ultimate")
                c.execute("INSERT INTO `subscription`(`subtype`, `subdate`, `expiredate`, `status`,`subname`,`artistid`)VALUES('{}','{}','{}',{},'{}')".format(type,today,expire,1,"ultimate",artistid))
                conn.commit()
                subData = getSubscriptionDetail(artistid)
                price = request.session['plan']['price']
                if insertArtistPayment(subData['id'],price,1) == None:

                    return redirect(artuploads)
        else:
            status = 2
            if type == "2":
                expire = date.today() + relativedelta(months=+6)
                c.execute("UPDATE `subscription` SET `subtype`='{}',`subdate`='{}',`expiredate`='{}',`status`={},`subname`='{}' WHERE `artistid`= {}".format(type,today,expire,1,"pro",artistid))
                conn.commit()
                subData = getSubscriptionDetail(artistid)
                price = request.session['plan']['price']
                if insertArtistPayment(subData['id'],price,1) == None:
                    return redirect(artuploads)
                #return render(request,"artistdash.html")
            elif type == "3":
                expire = date.today() + relativedelta(years=+1)
                c.execute("UPDATE `subscription` SET `subtype`='{}',`subdate`='{}',`expiredate`='{}',`status`={},`subname`='{}' WHERE `artistid`= {}".format(type,today,expire,1,"ultimate",artistid))
                conn.commit()
                subData = getSubscriptionDetail(artistid)
                price = request.session['plan']['price']
                if insertArtistPayment(subData['id'],price,1) == None:

                    return redirect(artuploads)

        
        return redirect("/artist/payment")
    return render(request,"payment/payment.html",{'plan':plan})

#initializing

dislist = ['Alappuzha','Ernakulam','Idukki','Kannur','Kasaragod','Kollam','Kottayam','Kozhikode','Malappuram','Palakkad','Pathanamthitta','Thiruvananthapuram','Thrissur','Wayanad',]
#Arts Upload
def artuploads(request,args=''):
    print("ecdata: ",args)
    artistid = request.session['userId']
    print("artistId: ",artistid)
    c.execute("SELECT * FROM `category`")
    catalist = c.fetchall()
   
    c.execute("SELECT * FROM `arts` WHERE `artistId`={}  ORDER BY id DESC".format(artistid))
    artslist =  c.fetchall()
    

    c.execute("SELECT * FROM `subscription` WHERE `artistid`= {}".format(artistid))
    subdata = c.fetchone()
    print("subdata")
    print(subdata)

    if subdata == None:
       
        
        return HttpResponseRedirect("subscription/page")

    if subdata != None:
        print("innnnn")
        ExpirationDate = datetime.strptime(subdata['expiredate'],"%Y-%m-%d").date()
        now = date.today()
        if ExpirationDate <= now:
            print("inn2")
            c.execute("UPDATE `subscription` SET `status`= 0 WHERE `artistid`={}".format(artistid))
            conn.commit()
            exp = 1
            return render(request,"artistdash.html",{'exp':exp})
    
        
        #return render(request,"artistdash.html")
    
    #Subscription renwval
    print("Subscription renwval")
    if "setrenew" in request.POST:
        print("renwval......")
        return redirect("subscription.html".subscription)
        #return render(request,"subscription.html")

    if "delbtn" in request.POST:
        print("delete inside")
        id = request.POST.get('artId')
        print(id)
        c.execute("DELETE FROM `arts` WHERE `id`= {} ".format(id))
        conn.commit()
        c.execute("SELECT * FROM `arts` WHERE `artistId`={}  ORDER BY id DESC".format(artistid))
        artslist =  c.fetchall()
        return render(request,"artistdash.html",{'catalist':catalist,'artslist':artslist,'page':1,'alert':2})

    if "setAv" in request.POST:
        id = request.POST.get('artId')
        print(id)
        c.execute("UPDATE `arts` SET `status`=0 WHERE `id`= {} ".format(id))
        conn.commit()
        c.execute("SELECT * FROM `arts` WHERE `artistId`={}  ORDER BY id DESC".format(artistid))
        artslist =  c.fetchall()
        return render(request,"artistdash.html",{'catalist':catalist,'artslist':artslist,'page':1,'alert':5})    
    if "edit" in request.POST:
        id = request.POST.get("id")
        c.execute("SELECT * FROM `arts` WHERE `id`={} ".format(id))
        artsedit =  c.fetchone()
        print(id,artsedit)

        return render(request,"artistdash.html",{'catalist':catalist,'page':6,'editart':artsedit})
    #Upload arts
    if "UploadArt"in request.POST:
        print('hai')
        artname = request.POST.get('artname')
        artprice = request.POST.get('artprice')
        artwidth = request.POST.get('artwidth')
        artheight  = request.POST.get('artheight')
        artdiatype  = request.POST.get('artdiatype')
        category  = request.POST.get('category')
        artimage  = request.FILES.get('artimage')
        imageurl = uploadFile(artimage)
        discription = request.POST.get('discription')
        #print(artname,artprice,artwidth,artheight,artdiatype,category,imageurl,discription,0,55)
        c.execute("INSERT INTO `arts` (`artName`, `price`, `width`, `height`, `dimension`, `catname`, `imageUrl`, `discription`, `status`,`artistId`) VALUES ('{}',{},'{}','{}','{}','{}','{}','{}',{},{})".format(artname,artprice,artwidth,artheight,artdiatype,category,imageurl,discription,0,artistid))
        conn.commit()
        c.execute("SELECT * FROM `arts` WHERE `artistId`={}  ORDER BY id DESC".format(artistid))
        artslist =  c.fetchall()
        # return HttpResponseRedirect("/artist/artistdash/store",{'alert':'Your art uploaded successfully'})
        return render(request,"artistdash.html",{'catalist':catalist,'artslist':artslist,'page':1,'alert':1})
    
    if "editSub" in request.POST:
        id = request.POST.get('id')
        artname = request.POST.get('artname')
        artprice = request.POST.get('artprice')
        artwidth = request.POST.get('artwidth')
        artheight  = request.POST.get('artheight')
        artdiatype  = request.POST.get('artdiatype')
        category  = request.POST.get('catogery')
        artimage  = request.FILES.get('artimage')
        print("value in file",artimage)
        discription = request.POST.get('discription')
        if artimage == None:
            c.execute("UPDATE `arts` SET  `artName`='{}',`price`={},`width`='{}',`height`='{}',`dimension`='{}',`catname`='{}',`discription`='{}' WHERE `id`={}".format(artname,artprice,artwidth,artheight,artdiatype,category,discription,id))
            conn.commit()
        else:
            imageurl = uploadFile(artimage)

            c.execute("UPDATE `arts` SET  `artName`='{}',`price`={},`width`='{}',`height`='{}',`dimension`='{}',`catname`='{}',`imageUrl`='{}',`discription`='{}' WHERE `id`={}".format(artname,artprice,artwidth,artheight,artdiatype,category,imageurl,discription,id))
            conn.commit()

        c.execute("SELECT * FROM `arts` WHERE `artistId`={}  ORDER BY id DESC".format(artistid))
        artslist =  c.fetchall()
        return render(request,"artistdash.html",{'catalist':catalist,'artslist':artslist,'page':1,'alert':3})    

    
    return render(request,"artistdash.html",{'catalist':catalist,'artslist':artslist,'page':1})

def uploadFile(image):
    fs = FileSystemStorage()
    file_type = image.content_type.split('/')[1]
    name =''.join(random.choices(string.ascii_lowercase+ string.digits, k = 7))
    filename = fs.save(name+'.'+file_type, image)
    uploaded_file_url = fs.url(filename)
    return uploaded_file_url

#My Earnings
def earnings(request):
    # c.execute("SELECT * FROM `earnings` WHERE `artistid`={}".format(artistid))
    # earningslist = c.fetchall()   ,'earningslist':earningslist
    artistid = request.session['userId']

    c.execute("SELECT cs.*,ar.artName,ar.price FROM `customerPayment` AS cs INNER JOIN arts as ar INNER JOIN users as us WHERE cs.artId = ar.id AND us.id = {}".format(artistid))
    bookings = c.fetchall()
    print("bookings: ",bookings)
    c.execute("SELECT SUM(ar.price) as total FROM `customerPayment` AS cs INNER JOIN arts as ar INNER JOIN users as us WHERE cs.artId = ar.id AND us.id = {}".format(artistid))
    total = c.fetchone()
    return render(request,"artistdash.html",{'page':2,'bookings':bookings,'total':total})

#Subscription Details
def subscriptiondetails(request):
    artistid = request.session['userId']
    c.execute("SELECT * FROM `subscription` WHERE `artistid`={} ".format(artistid))
    subdetails = c.fetchone()   
    print("subdetails",subdetails)
    return render(request,"artistdash.html",{'page':3, 'subdetails':subdetails})

#Request..

def artrequest(request):
    #c.ececute("SELECT * FROM `requests` WHERE `artistid`={}".format(artistid))
    #requestslist = c.fetchchall()  ,'request':requestslist

    # if "apprBtn" in request.POST:
    #     c.execute("UPDATE `requests` SET 'status'=0 WHERE `id`={}".format(id))
    #     conn.commit()
    # if "rejBtn" in request.POST:
    #     c.execute("UPDATE `requests` SET 'status'=1 WHERE `id`={}".format(id))
    #     conn.commit()
    artistid = request.session['userId']

    if "apprBtn" in request.POST:
        reqid = request.POST['reqid']
        c.execute("UPDATE `requests` SET `status` = 2 WHERE `id`={}".format(reqid))
        if conn.commit() == None:
            c.execute("SELECT rq.*,us.firstName,us.lastName,us.username,ar.imageUrl,ar.catname FROM `requests` as rq INNER JOIN arts as ar ON ar.id = rq.artId INNER JOIN users as us ON rq.custId = us.id WHERE ar.artistId ={}".format(artistid))
            allrequests = c.fetchall()
            return render(request,"artistdash.html",{'page':4,'allrequests':allrequests,'alert':6})
    
    if "rejBtn" in request.POST:
        reqid = request.POST['reqid']
        c.execute("UPDATE `requests` SET `status` = 3 WHERE `id`={}".format(reqid))
        if conn.commit() == None:
            c.execute("SELECT rq.*,us.firstName,us.lastName,us.username,ar.imageUrl,ar.catname FROM `requests` as rq INNER JOIN arts as ar ON ar.id = rq.artId INNER JOIN users as us ON rq.custId = us.id WHERE ar.artistId ={}".format(artistid))
            allrequests = c.fetchall()
            return render(request,"artistdash.html",{'page':4,'allrequests':allrequests,'alert':6})



    c.execute("SELECT rq.*,us.firstName,us.lastName,us.username,ar.imageUrl,ar.catname FROM `requests` as rq INNER JOIN arts as ar ON ar.id = rq.artId INNER JOIN users as us ON rq.custId = us.id WHERE ar.artistId ={}".format(artistid))
    allrequests = c.fetchall()
    return render(request,"artistdash.html",{'page':4,'allrequests':allrequests})

#My Profile---
def profile(request):
    artistid = request.session['userId']
    def fecthuser(idd):
        print("idtest",idd)
        c.execute("SELECT * FROM `users` WHERE `id` = '{}' ".format(idd))
        userdata = c.fetchone()
        print("userdata",userdata)
        print("userid",artistid)
        return userdata
    userdata = fecthuser(artistid)
    if "profileUpdate" in request.POST:
        fname = request.POST.get('fname')
        lname  = request.POST.get('lname')
        phone  = request.POST.get('phno')
        address  = request.POST.get('address')
        district  = request.POST.get('dis')
        c.execute("UPDATE `users` SET `firstName`='{}',`lastName`='{}',`phone`='{}',`address`='{}',`district`='{}' WHERE `id`= {}".format(fname,lname,phone,address,district,artistid))
        conn.commit()
        userdata = fecthuser(artistid)
        return render(request,"artistdash.html",{'userdata': userdata ,'page':5,'dislist':dislist,'alert':4})
        #return render(request,"artistdash.html",{'userdata': userdata ,'page':5,'dislist':dislist})
    return render(request,"artistdash.html",{'userdata': userdata ,'page':5,'dislist':dislist})


# def createPost(request):
#     if request.method == "POST":
#         artName = request.POST.get('artName')
#         height = request.POST.get('height')
#         width = request.POST.get('width')
#         dimension = request.POST.get('dimension')
#         image = request.FILES['image']
#         furl = uploadFile(image)
#         respData = {
#             "artName":artName,
#             "height":height,
#             "width":width,
#             "dimension":dimension
#         }

#         return JsonResponse(respData)
#     if request.method == "GET":
#         return render(request,'artist/tempLoad.html')
