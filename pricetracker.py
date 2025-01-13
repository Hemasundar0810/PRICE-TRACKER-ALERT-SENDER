import requests
from bs4 import BeautifulSoup #for webscraping
import smtplib #for sending email
from email.mime.text import MIMEText
import time 
import re #for converting expressions
import streamlit as st
import os

def get_price(url):
  try:

    headers = {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
              'Accept-Language': 'en-US,en;q=0.9',
              'Accept-Encoding': 'gzip, deflate, br',
              'Connection': 'keep-alive',
              'DNT': '1',
              'Cache-Control': 'max-age=0'
          }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check if the URL is from Amazon or Flipkart
    if 'amzn' in url.lower():
        # Amazon price selector
        price_element = soup.select_one('.a-price-whole')
    elif 'flipkart' in url.lower():
        # Flipkart price selector
        price_element = soup.select_one('.Nx9bqj.CxhGGd.yKS4la')
    else:
        print("Unsupported URL")
        st.text("Unsupported URL")
        return None
  # price_element = soup.select_one('.Nx9bqj CxhGGd') #flipkart

    if(price_element):
      price_txt=price_element.text.strip()
      price_num=re.findall(r'[\d,]+',price_txt)
      if(price_num):
        price=float(price_num[0].replace(',',''))
        return price
    return None
  except Exception as e:
    print(f"error fetching price:{e}")
    st.text(f"error fetching price:{e}")
    return None


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def send_mail(subject,body,to_email,from_email,from_password):
  try:
    if not validate_email(to_email):
            print("Invalid recipient email address.")
            st.text("Invalid recipient email address.")
            return None
    msg=MIMEText(body)
    msg['subject']=subject
    #msg['From']=from_email
    msg['To']=to_email
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()  # Explicitly start TLS
    server.login(from_email,from_password)
    server.send_message(msg)
    server.quit()
    print("email sent successfully!")
    st.text("email sent successfully!")
  except Exception as e:
    print(f"error sending mail:{e}")
    st.text(f"error sending mail:{e}")
    return None
def track_price(url,target_price,check_interval,to_email,from_email,from_password):
  while True:
    current_price=get_price(url)
    if current_price is not None:
      print(f"current price:{current_price}")
      st.text(f"current price:{current_price}")
      if current_price <=target_price:
        subject="Price Drop Alert!"
        body=f"""
        price dropped to{current_price}!
        This is below your target price of{target_price}
        check the product here:{url}"""
        send_mail(subject,body,to_email,from_email,from_password)
       
        break
      else:
        print("price not dropped yet")
        print("checking again in 60 seconds")
        time.sleep(check_interval)
    else:
      print("failed to retrieve price.Rechecking....")
      st.text("failed to retrieve price.Rechecking....")
      
    
from_email = os.getenv('FROM_EMAIL')
from_password = os.getenv('FROM_PASSWORD')

if not from_email or not from_password:
    st.error("Email credentials are not set in the environment variables.")
    print("Error: Missing environment variables for email credentials.")
else:
    st.title("Price Tracker")
    url = st.text_input("Product URL", "")
    target_price = st.number_input("Target Price", min_value=0.0, step=0.01)
    to_email = st.text_input("Recipient Email", "")
    if st.button("Track Price"):
        if url and target_price and to_email:
            track_price(url, target_price, 60, to_email, from_email, from_password)
        else:
            st.error("Please fill in all the fields.")



