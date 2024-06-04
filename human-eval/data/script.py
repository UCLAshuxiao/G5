from human_eval.data import write_jsonl, read_problems
import pdb
import openai
import time
from datetime import datetime, timezone
import pytz
import re
import google.generativeai as genai



def normal_to_gemini_message(messages):
    for message in messages:
        if message['role'] == 'assistant':
            message['role'] = 'model'
        message['parts'] = message.pop('content')

def gemini_to_normal_message(messages):
    for message in messages:
        if message['role'] == 'model':
            message['role'] = 'assistant'
        message['content'] = message.pop('parts')

def get_response(model, messages, temperature):
    if re.match(r"^gpt", model) is not None:
        response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                api_key=openai.api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                n=n,
                )
        response['prompt'] = messages
        success = True
        messages.append({'role': 'assistant', 'content': response['choices'][0]['message']['content']})
        return messages
    elif re.match(r"gemini", model) is not None:
        normal_to_gemini_message(messages)
        response = gemini.generate_content(
            messages
        )
        gemini_to_normal_message(messages)
        if response.candidates and response.candidates[0].content.parts:
            messages.append({'role': 'assistant', 'content': response.candidates[0].content.parts[0].text})
            success = True
        else:
            messages.append({'role': 'assistant', 'content': 'Sorry, I cannot generate a response for this prompt.'})
            success = False
        return messages



# TODO: Implement a function that generates a completion for a given prompt
def generate_one_completion(prompt):
    # 这边可以用GPT-3之类的模型生成completion
    # return "This is a completion for the prompt: " + prompt
    messages = []
    messages.append({'role': 'user', 'content': prompt})
    return get_response(model_name, messages, 0)[1]['content']


safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

if __name__ == "__main__":
    model_name = "gpt-4-turbo-2024-04-09" # "gemini" or "gpt-4-1106-preview"
    num_samples_per_task = 1
    max_tokens = 1024
    n = 1
    only_first_k = 10
    genai.configure(api_key="Your key", transport = 'rest')
    gemini = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
    openai.api_key = "You api key" 
    # pdb.set_trace()

    problems = read_problems()
    # for debug
    # problems = {k: problems[k] for k in list(problems.keys())[:2]}
    samples = []
    total_problem_count = len(problems)
    problem_count = 0
    for task_id in problems:
        problem_count += 1
        if problem_count > only_first_k:
            sample = {
                'task_id': task_id,
                'completion': problems[task_id]["prompt"]
            }
            samples.append(sample)
            print("skip {}/{}".format(problem_count, total_problem_count))
        else:
            for _ in range(num_samples_per_task):
                sample = {
                    'task_id': task_id,
                    'completion': generate_one_completion(problems[task_id]["prompt"])
                }
                samples.append(sample)
            print("finished {}/{}".format(problem_count, total_problem_count))
    write_jsonl("samples_gpt.jsonl", samples)

        
