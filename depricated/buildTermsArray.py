def buildTermsArray(db, posts, client):
    db.Posts.update_many(
        {},
        [
            {"$set": {"newTitle": {"$split": ["$Title", " "]}, "newBody": {"$split": ["$Body", " "]}}},
            {"$set": {"termsNoFilter": {"$setUnion": [{"$ifNull": ["$newTitle", []]}, {"$ifNull": ["$newBody", []]}]}}},
            {"$unset": ["newBody", "newTitle"]},
            {"$set": {"ext": {"$map": {"input": "$termsNoFilter", "as": "term","in": {"$regexFindAll": {"input": "$$term", "regex": "[a-zA-Z0-9]{3,}"}}}}}},
            {"$unset": ["termsNoFilter"]},
            {"$set": {"collapsed": {"$reduce": {"input": "$ext", "initialValue": [], "in": {"$concatArrays": ["$$value", "$$this"]}}}}},
            {"$unset": ["ext"]},
            {"$set": {"TermsDuplicates": {"$map": {"input": "$collapsed", "as": "term", "in": "$$term.match"}}}},
            {"$unset": ["collapsed"]},
            {"$set": {"Terms": {"$reduce": {"input": "$TermsDuplicates", "initialValue": [], "in": {
            "$concatArrays": ["$$value", {"$cond": [{"$in": ["$$this", "$$value"]}, [], ["$$this"]]}]}}}}},
            {"$unset": ["TermsDuplicates"]}
        ]
    )