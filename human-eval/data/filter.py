import json

def filter_code(completion: str, model:str) -> str:
    # remove ''' at the beginning and end of the completion
    if model == "gemini":
        completion = completion.strip()
        if completion.startswith("```"):
            completion = completion[3:]
        if completion.endswith("```"):
            completion = completion[:-3]
        return completion
    elif model == "gpt":
        completion = completion.strip()
        #search for the first occurence of ```python in the completion
        start = completion.find("```python\n")
        end = completion.find("```\n\n")
        return completion[start+10:end]
    else:   
        return completion
    

if __name__ == "__main__":
    input_file = "data/samples_gpt.jsonl"
    output_file = "data/filtered_samples_gpt.jsonl"
    model = "gpt" #"gpt" or "gemini"
    with open(output_file, "w") as out:
        for line in open(input_file):
            sample = json.loads(line)
            sample["completion"] = filter_code(sample["completion"], model)
            out.write(json.dumps(sample) + "\n")
