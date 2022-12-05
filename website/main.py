import pandas as pd
from flask import Flask, request, jsonify, Response
import csv
import json
import re
import time
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO


user_dict = {}

app = Flask(__name__)
df = pd.read_csv("main.csv")


visits = 0

a_clicks = 0 
b_clicks = 0

@app.route('/')
def home():
    global visits
    
    global a_clicks
    global b_clicks
    
    visits += 1
    with open("index.html") as f:
        html = f.read()
    if (visits <= 10) and ((visits % 2) == 0):
        html = html.replace("donate.html", "donate.html?from=A")
        html = html.replace("Donate here", "Donate!")
        return html
    elif visits <= 10:
        html = html.replace("donate.html", "donate.html?from=B")
        return html    
    else:
        if a_clicks > b_clicks:
            html = html.replace("donate.html", "donate.html?from=A")
            return html.replace("Donate here", "Donate!")
        else:
            html = html.replace("donate.html", "donate.html?from=B")
            return html

@app.route('/browse.json')
def j_data():
    global df
     
        
    data_dict = df.to_dict()
    json_str = json.dumps(data_dict)
    
    ip = request.remote_addr 
    
    global user_dict
    
    if ip in user_dict:
        if time.time() - user_dict[ip] > 60:
            user_dict[ip] = time.time()
            return json_str
        else:
            html = "Too many requests - try again later."
            return Response(html, status=429, headers={"Retry-After": 60})
    else:
        user_dict[ip] = time.time()
        return json_str
    

@app.route('/browse.html')
def data():
    global df
    table = f"""
    <html>
    <head>
    <title>Top 50 Spotify Songs - 2019</title>
    </head>
    <h1>Top 50 Spotify Songs - 2019</h1>
    <body>
    {df.to_html()}
    </body>
    </html>
    
    """
    
    
    return table


@app.route('/donate.html')
def donate():
    
    global a_clicks
    global b_clicks
    
       
    args = dict(request.args)
    print(args)
    
    if args == {}:
        pass
    elif args['from'] == 'A':
        a_clicks += 1
    else:
        b_clicks += 1
    
    page = f"""
    <html>
        
        <head>
        <title>Donations</title>
        <b>Donate to the Spotify For All Foundation!</b>
        </head>
        <body>
        <h1>About:</h1>
        <br> According to doctors at Johns Hopkins, listening to music can promote better learning by stimulating the brain. <br> Donate to the Spotify For All Foundation to help make music accessible for all students. The foundation targets underprivileged kids so that everyone has equal access to music.
        </body>
    </html>
    """

    return page


@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    # \w* (0 or more of alphanumeric characters)
    # @{1} takes one @ symbol
    # \w gets domain
    # \. grabs dot
    if re.match(r"\w*@{1}\w*\.{1}\w*", email): # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        with open("emails.txt", "r") as f:
            num_subscribed = len(f.read().split("\n")[:-1])
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("Invalid email address!") # 3

    
@app.route('/plot1.svg')
def gen_svg1():
    fig, ax = plt.subplots(figsize=(6,4))
    
    pd.Series(df['Beats.Per.Minute']).plot.line(ax=ax)
    ax.set_ylabel('Beats Per Minute')
    
    f = StringIO()
    plt.tight_layout()
    plt.savefig(f, format="svg")
    plt.close()
    
    png = f.getvalue()
    
    hdr = {"Content-Type": "image/svg+xml"}
    return Response(png, headers=hdr)


#requests.args.get(query)

@app.route('/plot2.svg')
def gen_svg2():
    fig, ax = plt.subplots(figsize=(6,4))
    pop = pd.Series(df['Popularity'])
    dance = pd.Series(df['Danceability'])
    plt.scatter(pop, dance, c='springgreen', s=100, alpha=0.5)
    ax.set_ylabel('Danceability')
    ax.set_xlabel('Popularity')
    ax.set_title('Songs Dancability in Relation to Popularity')
    
    f = StringIO()
    plt.tight_layout()
    plt.savefig(f, format="svg")
    plt.close()
    
    png = f.getvalue()
    
    hdr = {"Content-Type": "image/svg+xml"}
    
    
    
    if request.args.get('query') == 'plot3':
        fig, ax = plt.subplots(figsize=(6,4))
        pop = pd.Series(df['Popularity'])
        dance = pd.Series(df['Danceability'])
        plt.scatter(pop, dance, c='b', s=100, alpha=0.5)
        ax.set_ylabel('Danceability')
        ax.set_xlabel('Popularity')
        
        
        f = StringIO()
        plt.tight_layout()
        plt.savefig(f, format="svg")
        plt.close()

        png = f.getvalue()

        hdr = {"Content-Type": "image/svg+xml"}
        
        return Response(png, headers=hdr)

    return Response(png, headers=hdr)



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.