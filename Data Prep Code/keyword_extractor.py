from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import nltk
import re
import spacy
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import glob
import os 
import numpy as np
import networkx
import math

nltk.download('stopwords')
nltk.download('wordnet')
nlp = spacy.load("en_core_web_sm")

PATH = "D:/.Downloads/Database"
PATH_SAVE = "D:/.Downloads/Database/statistics"

# Requires the path of the file, path to save the output to, year (for file name purposes), and column numbers (starting at column 0) for the department name and course description for each column
# Returns data_{year}.csv for the given year which has the columns for department name, keywords, and similar departments
# Works by reading through all files in the path (assuming a course is present), running pre-process on them, using tf-idf, uses tf-idf output to determine keywords, and calculates the cosine similarity to find similar courses
def extract(path, path_save, year, column_name, column_description):
    depts_desc = {}
    depts_keywords = {}
    depts_similarities = {}

    files = glob.glob(os.path.join(path, "*.csv"))
    


    ### Gets Course Descriptions -- depts_desc

    # Grabs the department and its description and fills depts_desc with the pre-processed department description
    for dept in files:
        dept = pd.read_csv(dept)
        dept_name = None

        # Grabs the department name and un-processed description
        # Dept_name fails if only one course present (in which case cant extract info)
        try:
            dept_name = dept.iloc[:,column_name][0]
            dept_descriptions = " ".join(dept.iloc[:, column_description].astype(str))
        except:
            pass
        
        # Processes the description and fills depts_desc
        if dept_name:
            dept_descriptions = preprocess(dept_descriptions)
            depts_desc[dept_name] = dept_descriptions
        
    # Creates the word bank of all possible words that appear in every course description
    corpus = list(depts_desc.values())
    


    ### Runs NLP -- depts_keywords

    # Threshold for how important keywords shown to user are 
    tfidf_threshold = 0.15 # Lower value results in more keywords

    # Runs TF-IDF (Term Frequency - Inverse Document Frequency) and gets the keywords (feature names)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(corpus) 
    feature_names = np.array(tfidf.get_feature_names_out())

    # Adds the keywords from each department above the threshold to depts_keywords
    for i, dept in enumerate(depts_desc.keys()):
        tfidf_rating = tfidf_matrix[i].toarray().flatten()
        
        keywords = np.where(tfidf_rating > tfidf_threshold)[0]
        keywords = feature_names[keywords]
        
        depts_keywords[dept] = ", ".join([word.capitalize() for word in keywords.tolist()])



    ### Gets similarities -- depts_similarities

    # Compute the consine similarity getting the similarity distance between vectors based on keywords
    # dot_product_matrix = tfidf_matrix @ tfidf_matrix.T # Dot product
    # dot_product_matrix = dot_product_matrix.toarray()
    dot_product_matrix = cosine_similarity(tfidf_matrix) # Cosine similarity

    for i, dept in enumerate(depts_desc.keys()):
        similarities = dot_product_matrix[i]
        similar_indices = np.where(similarities > .2)[0] # Limits to only ones with threshold of .2 or higher
        similar_indices = similar_indices[similar_indices != i]  # Remove self-comparison

        # Sort indices by similarity in descending order
        similar_indices = similar_indices[np.argsort(similarities[similar_indices])[::-1]] # Sorts based on highest dot product
        top_indices = similar_indices[:10] # Gets the top 10

        # Fills dept_similarities with the similar departments or None 
        if len(top_indices) > 0:
            depts_similarities[dept] = []
            for idx in top_indices:
                depts_similarities[dept].append(list(depts_desc.keys())[idx])
            depts_similarities[dept] = ', '.join(depts_similarities[dept])
        else:
            depts_similarities[dept] = None



    ### Create CSV

    df = pd.concat([pd.DataFrame.from_dict(depts_keywords, orient="index", columns=["keywords"]), pd.DataFrame.from_dict(depts_similarities, orient="index", columns=["similar_depts"])], axis=1)
    df.to_csv(f"{path_save}/data_{year}.csv")
        


# Takes a piece of text and standardizes, removes stop words, lemmatizes, and returns the pre-processed output text
def preprocess(text):
    # Converts to lowercase, removes punctuation, removes numbers, and removes "equivalent to AAAA"
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"equivalent to\s+\S+", "", text)

    # Splits it into words instead of sentences
    text = text.split()

    # Removes stopwords (to, a, the, etc) as well as words specifically chosen as stopwords
    stop_words_1 = set(stopwords.words("english"))
    stop_words_2 = ["study", "apply", "examination", "examine", "develop", "cover", "lecture", "use", "learn", "need", "present", "explore", "corequisite", "prerequisite", "minor", "may", "three", "two", "one", "designed", "includes", "topic", "understanding", "specific", "using", "weekly", "first", "overview", "seminar", "within", "context", "theories", "applications", "must", "however", "repeated", "faculty", "program", "areas", "focus", "work", "repeatable", "provides", "required", "major", "selected", "information", "use", "semester", "related", "individual", "include", "public", "word", "credit", "various", "principles", "experience", "problems", "field", "registration", "application", "advanced", "student", "basic", "special", "concepts", "students", "course", "study", "hours", "research", "topics", "emphasis", "techniques", "design" "issues", "including", "systems", "introduction", "methods", "theory", "skills"]
    stop_words_3 = ['acct', 'actt', 'aded', 'aern', 'amrt', 'amst', 'anth', 'arab', 'arch', 'artc', 'arte', 'artf', 'arth', 'art', 'asbr', 'asl', 'astu', 'as', 'attr', 'bad', 'bmrt', 'bms', 'bsci', 'bst', 'btec', 'bus', 'cacm', 'cadt', 'ca', 'cci', 'chds', 'chem', 'chin', 'ci', 'clas', 'cls', 'comm', 'comt', 'cphy', 'cs', 'ctte', 'cult', 'dan', 'dsci', 'eced', 'ecet', 'econ', 'edad', 'edpf', 'educ', 'eert', 'ehs', 'eirt', 'els', 'emba', 'eng', 'entr', 'epi', 'epsy', 'eval', 'evhs', 'exph', 'expr', 'exsc', 'fdm', 'fin', 'fr', 'gcol', 'geog', 'geol', 'gero', 'ger', 'gre', 'hdfs', 'hebr', 'hed', 'hied', 'hist', 'hm', 'honr', 'hort', 'hpm', 'hrtg', 'hst', 'htmt', 'iakm', 'id', 'iert', 'ihs', 'ils', 'ital', 'itap', 'itec', 'japn', 'jmc', 'jus', 'kba', 'kbm', 'kbt', 'lat', 'legt', 'lib', 'lis', 'math', 'mced', 'mcls', 'mert', 'mftg', 'mis', 'mktg', 'mmtg', 'msci', 'mus', 'nrst', 'nurs', 'nutr', 'ocat', 'padm', 'pas', 'peb', 'pep', 'phil', 'phy', 'ph', 'plct', 'plst', 'pol', 'port', 'psyc', 'ptst', 'radt', 'rert', 'rhab', 'ris', 'rptm', 'rtt', 'russ', 'sbs', 'seed', 'soc', 'spad', 'span', 'spa', 'sped', 'spsy', 'srm', 'svcd', 'tech', 'thea', 'trst', 'ud', 'us', 'vcd', 'vin', 'vtec', 'wmst']
    text = [word for word in text if word not in stop_words_1]
    text = [word for word in text if word not in stop_words_2]
    text = [word for word in text if word not in stop_words_3]
    
    text = nlp(" ".join(text))

    # Lemmatizes each word (running -> run)
    text = [token.lemma_ for token in text]

    text = " ".join(text)
    return text



# Requires the path of the department files for a specific year (separated department and without headers)
# Requires the path to the data_{year}.csv for the given year output by the keyword extractor
# Works by reading through all files in the path (assuming a course is present) and adding the graph JSON-esque format used in cytoscape to its own column on the statistics file
def graphGrab(path_courses, path_stats):
    outfile = pd.read_csv(path_stats)

    files = glob.glob(os.path.join(path_courses, "*.csv"))
    debts_graphs = {}

    # Reads through each department catalog
    for dept in files:
        dept = pd.read_csv(dept)
        courselist = []
        nodes = []
        edges = []
        in_course = []
        out_course = []
        graph_string = ""

        # Grabs the department name-- if it fails then there is not 
        try:
            dept_name = dept.iloc[1,2]
        except:
            dept_name = ""

        # Grabs the course number, pre-reqs, and coreqs
        dept_info = dept.iloc[:, [0, 3, 4]]
        
        # Converts the prereqs and coreqs into edges 
        for coursenum, prereqs, coreqs in zip(dept_info.iloc[:, 0], dept_info.iloc[:, 1], dept_info.iloc[:, 2]):
            if dept_name + str(coursenum) not in courselist:
                courselist.append(dept_name + str(coursenum))
            if type(prereqs) == str:
                prereqs = re.findall(r'[A-Z]{2,5} \d{5}', prereqs)
            else:
                prereqs = []

            if type(coreqs) == str:
                coreqs = re.findall(r'[A-Z]{2,5} \d{5}', coreqs)
            else: 
                coreqs = []
            
            for edge in prereqs + coreqs:
                edge = edge.replace(" ", "")
                # Adds the edge to the edges and any courses not in the listed courses in the non-json version of the list 
                if edge not in courselist:
                    courselist.append(edge)
                edges.append(f"data: {chr(123)} id: '{edge + dept_name + str(coursenum)}', source: '{edge}', target: '{dept_name + str(coursenum)}' {chr(125)}")

                out_course.append(edge)
                in_course.append(dept_name + str(coursenum))
        
        # Converts the courses into json courses
        for course in courselist:
            nodes.append(f"data: {chr(123)} id: '{course}' {chr(125)}")

        # Computes max in-degrees, max out-degrees, and density 
        if len(in_course) != 0:
            max_indeg = max(map(in_course.count, in_course))
        else:
            max_indeg = 0
        if len(out_course) != 0:
            max_outdeg = max(map(out_course.count, out_course))
        else:
            max_outdeg = 0 
        num_nodes = len(nodes)
        num_edges = len(edges)
        if (num_nodes * (num_nodes - 1) != 0):
            density = num_edges / (num_nodes * (num_nodes - 1))
        else:
            density = None

        # Adds the edges and ndoes to the graph representation string
        for entry in nodes:
            graph_string += f"{chr(123)} {entry} {chr(125)},"
        for entry in edges:
            graph_string += f"{chr(123)} {entry} {chr(125)},"
        
        graph_string = "elements: [" + graph_string[:-1] + "]"
        
        # Saves the output in the csv location
        outfile.loc[outfile.iloc[:, 0] == dept_name, "graph_representation"] = graph_string
        outfile.loc[outfile.iloc[:, 0] == dept_name, "max_indegrees"] = max_indeg
        outfile.loc[outfile.iloc[:, 0] == dept_name, "max_outdegrees"] = max_outdeg
        outfile.loc[outfile.iloc[:, 0] == dept_name, "density"] = density
        outfile.loc[outfile.iloc[:, 0] == dept_name, "year"] = year
        outfile.to_csv(path_stats, index=False)  


# Main loop
# Goes through each year and extracts keywords, and constructs a graph
years = list(range(2009, 2025))
for year in years:
    extract(f"{PATH}/{year}", path_save=PATH_SAVE, year=year, column_name=2, column_description=5)
    print(f"Keywords Extracted for {year}")
    
    graphGrab(f"{PATH}/{year}", f"{PATH_SAVE}/data_{year}.csv")
    print(f"Graph constrcuted for {year}")


# Main loop pt 2
# Aggregates each stat into one file
newfile = pd.DataFrame()
path = f"D:/.Downloads/Database/statistics/"
files = glob.glob(os.path.join(path, "*.csv"))
for file in files:
    file_loc = file

    try:
        file = pd.read_csv(file)
        newfile = pd.concat([newfile, file], ignore_index=True)
    except:
        pass
newfile.to_csv(f"D:/.Downloads/Database/stats.csv", index=False)
print(f"All files aggregated")