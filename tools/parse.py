from json import loads

def parse(file, string):
    
    with open(file, "r") as f:
        buffer = f.readlines()

    for line in buffer:
        if "{" and "}" not in line:
            continue

        linep = "{" + line.split("{")[1].split("}")[0] + "}"
        
        try:
            parsed = loads(linep)
        except:
            continue

        # IGNORE THE BITCOIN GARBAGE - PROBABLY AT LEAST 1/12th OF THE ENITRE RESULTS
        if string in parsed["text"] and "@bit" not in parsed["text"]:
            print(parsed)   
            print()
         
# SIMPLE TOOL TO SEARCH FOR TEXT IN THE RESULT FILE/S       
#parse("data/text.json", "looking for this string!")