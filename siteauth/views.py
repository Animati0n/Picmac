from os import uname
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
import hashlib
from customer import views as customerViews
from artist import views as artistViews
from siteadmin import views as adminViews
  

import string
import random
c =settings.CUR
conn = settings.CONN
from helper import sndmail
# Create your views here.



def home(request):
    msg={}
    if 'username' in request.session and 'sellanart' not in request.POST and 'artistExtraBtn' not in  request.POST:
        username = request.session['username']
        c.execute("SELECT userType FROM users WHERE username= %s ",([username]))
        data = c.fetchone()
        msg = {'username':username,'userType':data['userType']}
        if(data['userType'] == 1):
            return redirect(adminViews.adminload)
        if(data['userType'] == 2):
            return redirect(artistViews.artuploads)
        if(data['userType'] == 3):
            
            return redirect(customerViews.home)

    if 'sellanart' in request.POST:
        username = request.session['username']
        msg = {'username':username}
        return render(request,'siteauth/artistExtra.html',msg)

    if 'artistExtraBtn' in request.POST:
        uname = request.POST.get('username')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        dis = request.POST.get('dis')

        if(dis == '0'):
            msg = {'username':uname,'msg':'Please choose district'}
            return render(request,'siteauth/artistExtra.html',msg)

        c.execute("UPDATE users SET firstName= '{}',lastName='{}',phone='{}',address='{}',district='{}', userType=2 WHERE username='{}'".format(
            firstName,lastName,phone,address,dis,uname
            ))
        resp = conn.commit()  
        print("resp: ",resp)  
        if resp != None:
            msg = {'username':uname}
            return render(request,'siteauth/artistExtra.html',msg)
        return redirect(artistViews.artuploads)

    artList =[]
    c.execute("SELECT ar.*,us.firstName,us.lastName FROM `arts` AS ar INNER JOIN users as us WHERE us.id = ar.artistId AND ar.status = 1")
    data2 = c.fetchall()
    if len(data2) != 0:
        artList = data2
        msg = {'artList':artList}
        return render(request,'siteauth/index.html',msg)

    return render(request,'siteauth/index.html',msg)


def signup(request):
    if 'unamesubmit' in request.POST:
        uname = request.POST.get('username')
        print(uname)
        c.execute("SELECT username,password FROM users WHERE username= %s ",([uname]))
        data = c.fetchone()
        if data == None:
            # using random.choices()
            # generating random strings 
            N = 7
            res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
            print(res)
            try:
                message = "Your otp for account verification: " + res
                sndmail(uname,message,"OTP For Your Account Verification")
                # #s = smtplib.SMTP('smtp.gmail.com', 587)
                # s = smtplib.SMTP_SSL('smtp.gmail.com', 587)
                # s.starttls()
                # message = res
                # s.login("ajeeshkr257@gmail.com", "ajeesh@2577")
                # s.sendmail("ajeeshkr257@gmail.com", uname, message)
                # s.quit()
                c.execute("INSERT INTO `users` (`otp`,`username`) VALUES ('{}','{}')".format(res,uname))
                conn.commit()
                
                msg = {"msg":"email send","username":uname,'temp':1}
                return render(request,"siteauth/login.html",msg) 
            except Exception as e:
                msg = {"msg":"Unable to send email","username":uname,'temp':0}
                return render(request,"siteauth/login.html",msg)
        elif data['password'] == None:
            msg = {"msg":"","username":uname,'temp':1,'paswordType':1}
            return render(request,"siteauth/login.html",msg)

        else:
            msg = {"msg":"","username":uname,'temp':3,'paswordType':2}
            return render(request,"siteauth/login.html",msg)

    if 'otpsubmit' in request.POST:
        uname = request.POST.get('username')
        otp = request.POST.get('otp')
        print("test uname")
        print(uname)
        c.execute("SELECT otp FROM users WHERE username= %s",([uname]))
        data = c.fetchone()
        print(data['otp'])
        if otp == data['otp']:
            print("verified")
            msg = {"msg":"Verified Successfully","username":uname,'temp':3,'paswordType':1}
            return render(request,"siteauth/login.html",msg) 
        else:
            msg = {"msg":"Incorrect otp","username":uname,'temp':1}
            return render(request,"siteauth/login.html",msg) 
        

    if 'register' in request.POST:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        cpwd = request.POST.get('cpassword')
        # initializing string
        
        # encoding GeeksforGeeks using encode()
        # then sending to md5()
        if pwd != cpwd:
            msg = {"msg":"Password doesnt match","username":uname,'temp':3,'paswordType':1}
            return render(request,"siteauth/login.html",msg)

        result = hashlib.md5(pwd.encode())
        hashed = result.hexdigest()
        print(hashed)
        c.execute("UPDATE users SET password= '{}', userType=3 WHERE username='{}'".format(hashed,uname))
        conn.commit()
        c.execute("SELECT `id` FROM `users` WHERE `username`='{}'".format(uname))
        dbData = c.fetchone()
        
        msg = {"msg":"registerd"}
        request.session['username'] = uname
        request.session['userId'] = dbData['id']
        return redirect(home)

        #c.execute("INSERT INTO `users` (`username`,`otp`,`password`,`usertype`) VALUES (%s,%s,%s,%d)"),(uname,otp,pas,us)
        
    if 'login' in request.POST:
        print('login')
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        c.execute("SELECT password,usertype FROM users WHERE username= '{}'".format(uname))
        data = c.fetchone()
        result = hashlib.md5(pwd.encode())
        
        if result.hexdigest() == data['password']:
            c.execute("SELECT `id` FROM `users` WHERE `username`='{}'".format(uname))
            dbData = c.fetchone()
            print("dbData: ",dbData)
            request.session['username'] = uname
            request.session['userId'] = dbData['id']
            if data['usertype'] == 1:
                msg = {"msg":"admindash"}
                return redirect(home)
            elif data['usertype'] == 2:
                msg = {"msg":"artistdash"}
                return redirect(home)
            else:
                msg = {"msg":"userdash"}
                return redirect(home)
        msg = {"msg":"Wrong password","username":uname,'temp':3,'paswordType':2}
        return render(request,"siteauth/login.html",msg)

    if 'back' in request.POST:
        uname = request.POST.get('username')
        c.execute("DELETE FROM users WHERE username= '{}'".format(uname))
        conn.commit()
        render(request,"siteauth/login.html",{'temp':1})

                
    return render(request,"siteauth/login.html",{'temp':0})

def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return redirect(home)