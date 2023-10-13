# Introduce 
Hi! Thanks for comming my page. 
When you want to know the latest date of all date with list.Please use latestTouki. 
 
There are various ways to write the date of registration in Japan. 
This method extracts only the exact date from them and returns the latest date. 
Please input the list of dates as a list. 
 
# How to install 
pip install latestTouki 
 
# How to coding 
import latestTouki 

answer = latestTouki.detect(["令和４年７月４日登記", "2023年6月24日", "Some text without a date"]) 
 
print(answer)  
 
# License 
MIT  
