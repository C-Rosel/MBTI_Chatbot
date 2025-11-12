def determine_final_score(probabilities):
    # this is what we're wrking with
    # "E/I": {"labels": ["E", "I", "E", "E", "I"], "probs": [0.75, 0.6, 0.8, 0.72, 0.68]} FOR EXAMPLEE

    #innitialize results to empty
    dichotomy_results = {}
    mbti_type = ""
    
    # ducks in a row.. 
    dichotomy_order = ["E/I", "S/N", "T/F", "J/P"]
    
    for dichotomy in dichotomy_order:
        if dichotomy not in probabilities:
            continue #error handling but we shouldn't have any question iterations that dont have one dichotomy in this version
            
        data = probabilities[dichotomy]
        if not data.get("labels") or not data.get("probs"):
            continue
        
        labels = data["labels"]
        probs = data["probs"]
        
        # breakup time! (for ex. ["E", "I"])
        trait_pair = dichotomy.split("/")
        first_trait = trait_pair[0]
        second_trait = trait_pair[1]
        
        # extract probs for each trait
        first_trait_probs = [p for i, p in enumerate(probs) if labels[i] == first_trait]
        second_trait_probs = [p for i, p in enumerate(probs) if labels[i] == second_trait]
        
        # weighted avg
        avg_first_prob = sum(first_trait_probs) / len(first_trait_probs) if first_trait_probs else 0
        avg_second_prob = sum(second_trait_probs) / len(second_trait_probs) if second_trait_probs else 0
        
        # winner winner??
        if avg_first_prob > avg_second_prob:
            dominant_trait = first_trait
            dominant_score = avg_first_prob
            other_score = avg_second_prob
        else:
            dominant_trait = second_trait
            dominant_score = avg_second_prob
            other_score = avg_first_prob
        
        # normalizing scores
        total_score = dominant_score + other_score
        if total_score > 0:
            normalized_dominant = dominant_score / total_score
            normalized_other = other_score / total_score
        else:
            normalized_dominant = 0.5
            normalized_other = 0.5
        
        # store results with detailed breakdown
        dichotomy_results[dichotomy] = {
            "label": dominant_trait,
            "dominant_score": normalized_dominant,
            "other_score": normalized_other,
            "avg_prob_first": avg_first_prob,
            "avg_prob_second": avg_second_prob,
            "count_first": len(first_trait_probs),
            "count_second": len(second_trait_probs),
        }
        
        # now we build the mbti type from the winner of each dichotomy in order
        mbti_type += dominant_trait
    
    return mbti_type, dichotomy_results

#take a sip of water for how many times we said the word "dichotomy"... in this project. 