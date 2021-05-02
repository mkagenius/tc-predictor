# PRE_REQUISITES:
# perf.txt needs to created and kept in the same directory as this
# perf.txt is basically the performance of today's match
# It is created using a socket MITMproxy
# The mimtdump script is to be run like:
# mitmdump -p 8089 -s create_perf_file.py --ssl-insecure
# create_perf_file.py is also checking it in this repo
# Set Firefox browser proxy as 127.0.0.1 with port 8089
# Go to arena.topcoder.com and login and click on any Room, eg. Room5
# The File perf.txt should be created now
# THE perf.txt FILE NEEDS TO BE CREATED AFTER EACH NEW SRM

from flask import Flask, jsonify, make_response, render_template
import requests
from datetime import datetime, timedelta, timezone
from math import sqrt, exp, inf,pi, log
from random import randint
from time import sleep
import json
# "https://api.topcoder.com/v3/members/mkagenius/stats"

app = Flask(__name__)

INITIAL_SCORE = 1200.0
ONE_STD_DEV_EQUALS = 1200.0
INITIAL_WEIGHT = 0.60
FINAL_WEIGHT = 0.18
FIRST_VOLATILITY = 385

P_LOW  = 0.02425
P_HIGH = 1.0 - P_LOW

# Coefficients in rational approximations.
NORMINV_A = [ -3.969683028665376e+01,  2.209460984245205e+02,
-2.759285104469687e+02,  1.383577518672690e+02,
-3.066479806614716e+01,  2.506628277459239e+00 ]

NORMINV_B = [ -5.447609879822406e+01,  1.615858368580409e+02,
-1.556989798598866e+02,  6.680131188771972e+01,
-1.328068155288572e+01 ]

NORMINV_C = [ -7.784894002430293e-03, -3.223964580411365e-01,
-2.400758277161838e+00, -2.549732539343734e+00,
4.374664141464968e+00,  2.938163982698783e+00 ]

NORMINV_D = [ 7.784695709041462e-03,  3.224671290700398e-01,
2.445134137142996e+00,  3.754408661907416e+00 ]

def winprobability(r1, r2, v1, v2):
    return (erf((r1-r2)/sqrt(2.0*(v1*v1+v2*v2)))+1.0)*.5


def erf(z):
    t = 1.0 / (1.0 + 0.5 * abs(z))

    # use Horner's method
    ans = 1 - t * exp( -z*z   -   1.26551223 +
                                        t * ( 1.00002368 +
                                        t * ( 0.37409196 + 
                                        t * ( 0.09678418 + 
                                        t * (-0.18628806 + 
                                        t * ( 0.27886807 + 
                                        t * (-1.13520398 + 
                                        t * ( 1.48851587 + 
                                        t * (-0.82215223 + 
                                        t * ( 0.17087277))))))))))
    if (z >= 0):
        return  ans
    else:
        return -ans


def normsinv(p):

    
    if(p <= 0):
        return -inf
    elif(p >= 1):
        return inf
    
    z = 0

    # Rational approximation for lower region:
    if( p < P_LOW ):
    
        q  = sqrt(-2*log(p))
        z = (((((NORMINV_C[0]*q+NORMINV_C[1])*q+NORMINV_C[2])*q+NORMINV_C[3])*q+NORMINV_C[4])*q+NORMINV_C[5]) / ((((NORMINV_D[0]*q+NORMINV_D[1])*q+NORMINV_D[2])*q+NORMINV_D[3])*q+1)
    
    # Rational approximation for upper region:
    elif ( P_HIGH < p ):
    
        q  = sqrt(-2*log(1-p))
        z = -(((((NORMINV_C[0]*q+NORMINV_C[1])*q+NORMINV_C[2])*q+NORMINV_C[3])*q+NORMINV_C[4])*q+NORMINV_C[5]) / ((((NORMINV_D[0]*q+NORMINV_D[1])*q+NORMINV_D[2])*q+NORMINV_D[3])*q+1)
    
    # Rational approximation for central region:
    else:
    
        q = p - 0.5
        r = q * q
        z = (((((NORMINV_A[0]*r+NORMINV_A[1])*r+NORMINV_A[2])*r+NORMINV_A[3])*r+NORMINV_A[4])*r+NORMINV_A[5])*q / (((((NORMINV_B[0]*r+NORMINV_B[1])*r+NORMINV_B[2])*r+NORMINV_B[3])*r+NORMINV_B[4])*r+1)
    
    
    z = refine(z, p)
    return z


def erfc(z):
    return 1.0 - erf(z)


def refine(x, d):
    if( d > 0 and d < 1):
        e = 0.5 * erfc(-x/sqrt(2.0)) - d
        u = e * sqrt(2.0*pi) * exp((x*x)/2.0)
        x = x - u/(1.0 + x*u/2.0)
    return x

score = {}
def get_registered_handles():
    lst = []
    with open("perf.txt", "r") as f:
        lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            j = json.loads(line)
            for k in j:
                if j[k]["score"] == 0 and j[k]["rating"] == 0:
                    continue
                score[k] = {"score" : j[k]["score"] ,
                            "rating":  j[k]["rating"] }
                lst.append(k)
    return lst
    
@app.route('/next-contest')
def next_contest():
    url = "https://clients6.google.com/calendar/v3/calendars/appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com/events"
    current_time = datetime.now(timezone.utc)
    current_plus_30 = current_time + timedelta(days=30)
    timeMin = current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
    timeMax = current_plus_30.strftime("%Y-%m-%dT%H:%M:%S%z")
    params = {
                "calendarId":"appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com",
                "singleEvents": "true",
                "maxAttendees":1,
                "maxResults":250,
                "sanitizeHtml":"true",
                "timeMin":timeMin,
                "timeMax":timeMax,
                "key":"AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"
            
            }
    
    resp = requests.get(url = url, params = params)
    data = resp.json()
    
    try:
        data["items"]
    except Exception as e:
        response = make_response(
                jsonify(
                    {"message": "Google Calendar didn't return data", "severity": "danger"}
                ),
                400,
            )
        response.headers["Content-Type"] = "application/json"
        return response
    
    items = data["items"]
    date2contest = {}
    for item in items:
        summary = item["summary"]
        if "SRM" in summary or "Algorithm" in summary:
            dateTime = datetime.strptime(item["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z")
            date2contest[dateTime] = summary
        
    if len(date2contest) == 0:
        response = make_response(
                jsonify(
                    {"message": "No Contest Scheduled"}
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response

    for k in sorted(date2contest):
        response = make_response(
                jsonify(
                    {"message": date2contest[k], "dateTime": k}
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response


rating_store = {}

def get_user_stats(handle):
    with open("volatility.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            j = json.loads(line)
            if handle in j:
                print(f"Returing from file for {handle} ")
                return {"volatility": j[handle]["volatility"], "tot": j[handle]["tot"]}

    print(f"Fetching: {handle}")
    resp = requests.get(f"https://api.topcoder.com/v3/members/{handle}/stats")

    j = resp.json()
    if "id" not in j:
        return {}
    else:
        with open("volatility.txt", "a") as f:
            f.write(json.dumps({handle: {"volatility":j["result"]["content"][0]["DATA_SCIENCE"]["SRM"]["rank"]["volatility"], "tot":j["result"]["content"][0]["DATA_SCIENCE"]["SRM"]["challenges"]+1}}))
            f.write("\n")
        return {"volatility":j["result"]["content"][0]["DATA_SCIENCE"]["SRM"]["rank"]["volatility"], "tot":j["result"]["content"][0]["DATA_SCIENCE"]["SRM"]["challenges"]+1}

@app.route("/contestant-ratings")
def contestant_ratings():
    handles = get_registered_handles()
    for handle in handles:
        if handle not in rating_store:
            sleep(0.01)
            try:
                j = get_user_stats(handle)
                rating_store[handle] = {
                    "rating": score[handle]["rating"],
                    "volatility": j["volatility"],
                    "score": score[handle]["score"],
                    "tot": j["tot"],
                    }
            except:
                rating_store[handle] = {"rating":1200, "volatility": 900, "score": score[handle]["score"], "tot": 1}

    response = make_response(
                jsonify(
                    rating_store
                ),
                200,
            )
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/predictor/<handle>/<extra>")
def predictor(handle, extra):
    _ = contestant_ratings()

    if handle in rating_store:
        rating_store[handle]["score"] += int(extra)
    # ave rating
    rave = 0
    for k in rating_store:
        rave += int(rating_store[k]["rating"])
        
    rave /= len(rating_store)
    
    # cf
    rtemp = 0
    vtemp = 0
    for k in rating_store:
        vtemp += float(rating_store[k]["volatility"])**2
        rtemp += (int(rating_store[k]["rating"]) - rave)**2
    num = len(rating_store)
    matchStdDevEquals = sqrt(vtemp / num + rtemp / (num-1) ) 

    # exp perf
    for k in rating_store:
        est = 0.5
        myskill = (float(rating_store[k]["rating"]) - INITIAL_SCORE ) / ONE_STD_DEV_EQUALS
        mystddev = float(rating_store[k]["volatility"]) / ONE_STD_DEV_EQUALS
        for j in rating_store:
            est += winprobability(float(rating_store[j]["rating"]), 
                float(rating_store[k]["rating"]), 
                float(rating_store[j]["volatility"]), 
                float(rating_store[k]["volatility"])
            )
        rating_store[k]["exp_rank"] = est
        rating_store[k]["exp_perf"] = -normsinv((est - .5) / num)


    # actual perf
    

    handles = list(rating_store.keys())
    n = len(handles)
    i = 0
    done_cnt = 0

    assert n > 1
    if "new_rating" in rating_store[handles[0]]:
        for h in handles:
            rating_store[h]["act_rank"] = 0
            rating_store[h]["act_perf"] = 0.1084
        
    while i < n:
        k = handles[i]
        mx = -inf
        count = 0
        for ii in range(n):
            j = handles[ii]
            if rating_store[j]["score"] >= mx and ("act_rank" not in rating_store[j] or rating_store[j]["act_rank"] == 0):
                if rating_store[j]["score"] == mx:
                    count+=1
                else:
                    count=1
                mx = rating_store[j]["score"]

        for ii in range(n):
            j = handles[ii]
            if rating_store[j]["score"] == mx:
                rating_store[j]["act_rank"] = i + 0.5+ count  / 2.0
                rating_store[j]["act_perf"] = -normsinv((i + count / 2.0) / num)

        i+=count

    for j in range(n):
        i = handles[j]
        diff = rating_store[i]["act_perf"] - rating_store[i]["exp_perf"]

        oldrating = int(rating_store[i]["rating"])
        performedAs = oldrating + diff * matchStdDevEquals
        weight = (INITIAL_WEIGHT - FINAL_WEIGHT) / (rating_store[i]["tot"] + 1) + FINAL_WEIGHT


        # get weight - reduce weight for highly rated people
        weight = 1 / (1 - weight) - 1
        if (oldrating >= 2000 and oldrating < 2500):
            weight = weight * 4.5 / 5.0
        if (oldrating >= 2500):
            weight = weight * 4.0 / 5.0

        newrating = (oldrating + weight * performedAs) / (1 + weight)

        # get and inforce a cap
        cap = 150 + 1500 / (2 + (rating_store[i]["tot"]))
        if (oldrating - newrating > cap):
            newrating = oldrating - cap
        if (newrating - oldrating > cap):
            newrating = oldrating + cap
        if (newrating < 1):
            newrating = 1

        rating_store[i]["new_rating"] = (int(newrating))

        if (rating_store[i]["tot"] != 0):
            oldVolatility = rating_store[i]["volatility"]
            rating_store[i]["volatility"] = (int((sqrt((oldVolatility*oldVolatility) / (1+weight) + ((newrating-oldrating)*(newrating-oldrating))/ weight))))
        else:
            rating_store[i]["volatility"] = (int((FIRST_VOLATILITY)))
    
    colnames = list(rating_store[handles[0]].keys())
    response = render_template("pred.html", rating_store=rating_store, colnames=["handle"] + colnames)
    return response

if __name__ == '__main__':
    app.run()
