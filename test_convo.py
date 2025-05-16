from app.agents.intent_classification import worker as intent_classification_worker, IntentClassificationInputSchema



while True:
    query = input("Enter a query: ")

    res = intent_classification_worker.run(IntentClassificationInputSchema(query=query))
    print(res)