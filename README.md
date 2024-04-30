# Style-Savvy
Style Savvy is an application built on React and Flask that allows users to upload a picture of an outfit, and optionally a celebrity full name, and recieve fashion recommendations along with Amazon links.

Challenges:
1. Finding the best Amazon Listing: The solution to this was some experimentation with different algorithms. The three algorithms we chose were cheapest, random, and price / reviews and we discovered the last one was the best based on user testing.
2. Amazon API: Amazon's own API is bad when it comes to performance and listing details. Here, we rely on Rainforest which has scraped Amazon and created a database that can be queried using an API endpoint.
3. Performance: The model and the Rainforest API are naturally slow due to the amount of resources they take. We opted to remove some layers of the model to make it faster while retaining a great accuracy. As for the API, we developed an RDS database cache that is referenced before the API is called, which upon a hit, can reduce latency from 10+ seconds to less than 0.5 a second.


Application Demo: https://youtu.be/wFeF4KocW64

Install: 
1. Make sure you have Python installed  
2. Then on your terminal do `pip install -r requirements.txt`
3. Navigate to the backend folder
4. Then run `python server.py` to start the backend 

To start the frontend: 
1. Open your terminal and make sure you have node.js installed 
2. In your directory, do `create-react-app style-savvy`
3. navigate to style-savvy do `npm install` to install the node packages
4. `npm start` 

