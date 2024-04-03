# PartSelect ChatBot

Customer-facing chatbot that provides users with product information pertaining to Refrigerator and Dishwasher products from the e-commerce website [PartSelect](https://www.partselect.com/). Utilizes the gpt-3.5-turbo language model and a ChromaDB vector store within a Flask backend framework to deliver domain-specific knowledge to users.  


## FRONTEND SETUP
Load the “build” directory as a [chrome extension](https://bashvlas.com/blog/install-chrome-extension-in-developer-mode) to view the chat interface right from your Chrome browser’s side panel. 


## BACKEND SETUP
- Get an OpenAI [API Key](https://platform.openai.com/account/api-keys)
- Copy `.env.template` to `.env`, then set `OPENAI_API_KEY` and `FLASK_SECRET_KEY`
- Install `requirements.txt`


## BUILDING A VECTOR DATABASE
- In `build_database.py` scroll to `main()` and set `category_baseURL`. Acceptable URLs for this field include any of the links found on the Products page from PartSelect. Select a link that looks like these:

  - https://www.partselect.com/Dishwasher-Parts.htm
  - https://www.partselect.com/Refrigerator-Parts.htm
  - https://www.partselect.com/Dryer-Parts.htm
  - https://www.partselect.com/Freezer-Parts.htm
    
- By default, `build_database.py` will create a vector store named “PartSelect”. If you run this script again with a different `category_baseURL`, you’ll be adding to that same vector store. 
- Wait until confirmation prints to the terminal that the ChromaDB has been successfully populated. 


**Note on database size:** The default webscraping depth for `create_product_databse()` is 0, meaning you’ll retrieve the first 10 products listed in the “Popular Parts” section found at that `category_baseURL`, which will take a few minutes. If you increase the depth to 1, you’ll retrieve around 455 products, but this will take quite a while! While this approach does result in a limited database, it allows you to run and test out this implementation without investing too much time into setup. 


**Note on runtime:** The runtime of this process is primarily due to its reliance on the OpenAI API for converting the raw text data from each product page into natural language. This conversion is essential for the embedding function to encode the data accurately, which enhances the accuracy of queries on the vector store. This solution was implemented to prioritize response quality over response range, but if I had more time, this process is one of the first I’d optimize.


## TESTING SCOPE
Because we set our scrape depth limit to 0 for the sake of runtime, we only retrieved the first 10 prodcuts featured on your `category_baseUR`. If you'd like to test this bot out with some questions, visit your `category_baseURL`, click on any of the "Featured Products" and quiz the bot! Increasing scrape depth will increase the scope of the knowledge base, but buidling a larger dataset may take long on your system. 


## RUNNING THE APP
- Choose to run either `app.py` or `app-no-memory.py` depending on your use case.
  - **app.py**
    - _pros_: can elegantly handle ambiguous follow-up questions since it “remembers” what you just said.
    - _cons_: cannot switch between topics automatically, the user must press the “new question” button to switch topics.
  - **app-no-memory.py**
    - _pros:_ can handle successive topic switches as long as you provide enough context with each question.
    - _cons:_ cannot process ambiguous follow-up questions accurately since new context is retrieved for each message.
- Launch the extension in your browser, and enjoy!


