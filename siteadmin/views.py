from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse,HttpResponseRedirect
from django.conf import settings
c =settings.CUR
conn = settings.CONN
# Create your views here.
def adminload(request):
    c.execute("SELECT sb.*,us.firstName,us.lastName FROM `subscription` AS sb INNER JOIN `users` AS us WHERE artistid = us.id")
    userslist = c.fetchall()
    

    return render(request,"admin/admindash.html",{'userslist': userslist,'page':1})



def transaction(request):
    c.execute('SELECT ap.*,us.firstName,us.lastName,sb.subname,sb.subdate,sb.expiredate FROM `artistPayment` as ap INNER JOIN `subscription` as sb INNER JOIN `users` as us WHERE sb.id = ap.subid AND us.id = sb.artistid')
    transactions = c.fetchall()
    c.execute('SELECT SUM(price) as sum FROM `artistPayment`')
    sum = c.fetchone()
    return render(request,"admin/admindash.html",{'page':2,"transactions":transactions,'sum':sum})

def newArtUpload(request):
    c.execute("SELECT * FROM `arts` WHERE `status`= 0 ORDER BY id DESC")
    newArts = c.fetchall()
    print("newarts",newArts)


    if "delete_art" in request.POST:
        print("delete inside")
        id = request.POST.get('id')
        print(id)
        c.execute("DELETE FROM `arts` WHERE `id`= {} ".format(id))
        conn.commit()

        return HttpResponseRedirect("/admin1/newartuploads")

    if "aprvart" in request.POST:
        artid = request.POST.get('id')
        print("apprv check",artid)
        c.execute("UPDATE `arts` SET `status`=1 WHERE `id`={}".format(artid))
        conn.commit()
        return HttpResponseRedirect("/admin1/newartuploads")


    return render(request,"admin/admindash.html",{'page':3,'newArts': newArts})



def allArts(request):
    c.execute("SELECT * FROM `arts` WHERE `status`= 1 ")
    allArtslist = c.fetchall()
    print("allarts",allArtslist)

    if "deleteart" in request.POST:
        print("delete inside")
        id = request.POST.get('id')
        print(id)
        c.execute("DELETE FROM `arts` WHERE `id`= {} ".format(id))
        conn.commit()

    return render(request,"admin/admindash.html",{'page':4,'allArtslist': allArtslist})